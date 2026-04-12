"""Tests for LLM tool-call argument parsing."""

from lunvex_code.llm import LunVexClient


class TestLlmToolArgumentParsing:
    """Test best-effort normalization of tool call arguments."""

    def _make_client(self) -> LunVexClient:
        """Create a client instance without running API-key-dependent init."""
        return LunVexClient.__new__(LunVexClient)

    def test_normalize_tool_arguments_parses_valid_json(self):
        """Valid JSON should parse directly."""
        client = self._make_client()

        parsed = client._normalize_tool_arguments('{"path":"file.tsx","content":"hello"}')

        assert parsed == {"path": "file.tsx", "content": "hello"}

    def test_normalize_tool_arguments_recovers_embedded_json(self):
        """Parser should recover JSON embedded in surrounding prose."""
        client = self._make_client()

        parsed = client._normalize_tool_arguments(
            'Please use this payload: {"path":"file.tsx","content":"hello"}'
        )

        assert parsed == {"path": "file.tsx", "content": "hello"}

    def test_normalize_tool_arguments_recovers_double_encoded_json(self):
        """Parser should handle providers that wrap arguments in a JSON string."""
        client = self._make_client()

        parsed = client._normalize_tool_arguments(
            '"{\\"path\\":\\"file.tsx\\",\\"content\\":\\"hello\\"}"'
        )

        assert parsed == {"path": "file.tsx", "content": "hello"}

    def test_normalize_tool_arguments_returns_raw_when_unrecoverable(self):
        """Irrecoverable argument payloads should be marked as raw."""
        client = self._make_client()

        parsed = client._normalize_tool_arguments('{"path":"file.tsx", content:"hello"}')

        assert parsed == {"raw": '{"path":"file.tsx", content:"hello"}'}
