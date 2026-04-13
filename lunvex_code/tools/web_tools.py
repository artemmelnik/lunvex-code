"""Web access tools for fetching external URLs."""

import json
import re
from html import unescape
from html.parser import HTMLParser
from urllib.parse import urlparse

import requests

from .base import Tool, ToolResult


class _HTMLTextExtractor(HTMLParser):
    """Extract readable text from HTML while skipping non-content tags."""

    SKIP_TAGS = {"script", "style", "noscript"}
    BLOCK_TAGS = {
        "article",
        "aside",
        "blockquote",
        "br",
        "div",
        "footer",
        "h1",
        "h2",
        "h3",
        "h4",
        "h5",
        "h6",
        "header",
        "li",
        "main",
        "nav",
        "p",
        "pre",
        "section",
        "tr",
        "ul",
        "ol",
    }

    def __init__(self):
        super().__init__()
        self._skip_depth = 0
        self._parts: list[str] = []
        self._title: list[str] = []
        self._in_title = False

    @property
    def title(self) -> str:
        """Get the parsed page title."""
        return " ".join("".join(self._title).split())

    def handle_starttag(self, tag: str, attrs) -> None:
        if tag in self.SKIP_TAGS:
            self._skip_depth += 1
            return
        if tag == "title":
            self._in_title = True
        if tag in self.BLOCK_TAGS and self._parts and self._parts[-1] != "\n":
            self._parts.append("\n")

    def handle_endtag(self, tag: str) -> None:
        if tag in self.SKIP_TAGS and self._skip_depth > 0:
            self._skip_depth -= 1
            return
        if tag == "title":
            self._in_title = False
        if tag in self.BLOCK_TAGS and self._parts and self._parts[-1] != "\n":
            self._parts.append("\n")

    def handle_data(self, data: str) -> None:
        if self._skip_depth > 0:
            return
        if self._in_title:
            self._title.append(data)
        text = unescape(data)
        if text.strip():
            self._parts.append(text)

    def get_text(self) -> str:
        """Get normalized text output."""
        text = "".join(self._parts)
        text = text.replace("\xa0", " ")
        text = re.sub(r"[ \t]+", " ", text)
        text = re.sub(r"\n\s*\n\s*\n+", "\n\n", text)
        lines = [line.strip() for line in text.splitlines()]
        return "\n".join(line for line in lines if line).strip()


class FetchURLTool(Tool):
    """Fetch and summarize readable content from an external URL."""

    name = "fetch_url"
    description = (
        "Fetch content from an external HTTP or HTTPS URL and return readable text. "
        "Useful for reading documentation pages, blog posts, raw text, or JSON responses."
    )
    permission_level = "ask"

    parameters = {
        "url": {
            "type": "string",
            "description": "The external HTTP or HTTPS URL to fetch",
            "required": True,
        },
        "max_chars": {
            "type": "integer",
            "description": "Maximum number of characters to return (default: 12000)",
            "required": False,
        },
    }

    USER_AGENT = "lunvex-code/0.1.0 (+https://github.com/artemmelnik/lunvex-code)"
    MAX_RESPONSE_BYTES = 1_000_000

    def execute(self, url: str, max_chars: int = 12000) -> ToolResult:
        try:
            parsed = urlparse(url)
            if parsed.scheme not in {"http", "https"} or not parsed.netloc:
                return ToolResult(
                    success=False,
                    output="",
                    error="URL must be a valid http:// or https:// address.",
                )

            response = requests.get(
                url,
                timeout=15,
                allow_redirects=True,
                headers={"User-Agent": self.USER_AGENT},
                stream=True,
            )
            response.raise_for_status()

            chunks: list[bytes] = []
            total_bytes = 0
            for chunk in response.iter_content(chunk_size=8192):
                if not chunk:
                    continue
                total_bytes += len(chunk)
                if total_bytes > self.MAX_RESPONSE_BYTES:
                    break
                chunks.append(chunk)

            raw_bytes = b"".join(chunks)
            content_type = response.headers.get("content-type", "").lower()
            encoding = response.encoding or "utf-8"
            content = raw_bytes.decode(encoding, errors="replace")

            if "application/json" in content_type:
                readable = json.dumps(json.loads(content), ensure_ascii=False, indent=2)
                title = ""
            elif "html" in content_type or "<html" in content[:500].lower():
                extractor = _HTMLTextExtractor()
                extractor.feed(content)
                extractor.close()
                readable = extractor.get_text()
                title = extractor.title
            else:
                readable = content.strip()
                title = ""

            if not readable:
                readable = "[No readable text content found]"

            truncated = False
            if max_chars > 0 and len(readable) > max_chars:
                readable = readable[:max_chars].rstrip() + "\n... [truncated]"
                truncated = True

            header_lines = [f"Fetched URL: {response.url}"]
            if title:
                header_lines.append(f"Title: {title}")
            if truncated or total_bytes > self.MAX_RESPONSE_BYTES:
                header_lines.append("Note: content was truncated.")

            return ToolResult(
                success=True,
                output="\n".join(header_lines) + "\n\n" + readable,
            )

        except requests.RequestException as e:
            return ToolResult(success=False, output="", error=f"Failed to fetch URL: {e}")
        except json.JSONDecodeError as e:
            return ToolResult(success=False, output="", error=f"Invalid JSON response: {e}")
        except Exception as e:
            return ToolResult(success=False, output="", error=str(e))
