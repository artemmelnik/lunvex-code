"""Tests for async web tools."""

import asyncio
from unittest.mock import AsyncMock, patch

import pytest

from lunvex_code.tools.async_web_tools import AsyncFetchURLTool


@pytest.mark.asyncio
async def test_async_fetch_url_tool_success():
    """Test async fetch URL tool with successful response."""
    tool = AsyncFetchURLTool()

    # Mock aiohttp session to avoid actual network calls
    with patch("aiohttp.ClientSession") as mock_session:
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.headers = {"Content-Type": "text/html"}

        # Mock response content
        async def mock_iter_chunked(chunk_size):
            yield b"<html><body>Mocked response content</body></html>"

        mock_response.content.iter_chunked = mock_iter_chunked
        mock_response.raise_for_status = AsyncMock()

        mock_session_instance = AsyncMock()

        async def mock_session_get(url, **kwargs):
            return mock_response

        mock_session_instance.get = mock_session_get
        mock_session.return_value.__aenter__.return_value = mock_session_instance

        result = await tool.execute(url="https://example.com")

        assert result.success
        assert "Mocked response content" in result.output


@pytest.mark.asyncio
async def test_async_fetch_url_tool_with_max_chars():
    """Test async fetch URL tool with custom max_chars."""
    tool = AsyncFetchURLTool()

    # Mock the fetch_url function
    with patch("lunvex_code.tools.async_web_tools.fetch_url", new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = "Short content"

        result = await tool.execute(url="https://example.com", max_chars=100)

        assert result.success
        mock_fetch.assert_called_once_with("https://example.com", max_chars=100)


@pytest.mark.asyncio
async def test_async_fetch_url_tool_error():
    """Test async fetch URL tool with error."""
    tool = AsyncFetchURLTool()

    # Mock the fetch_url function to raise an exception
    with patch("lunvex_code.tools.async_web_tools.fetch_url", new_callable=AsyncMock) as mock_fetch:
        mock_fetch.side_effect = Exception("Network error")

        result = await tool.execute(url="https://example.com")

        assert not result.success
        assert "Network error" in result.error or "Failed to fetch" in result.error


@pytest.mark.asyncio
async def test_async_fetch_url_tool_invalid_url():
    """Test async fetch URL tool with invalid URL."""
    tool = AsyncFetchURLTool()

    result = await tool.execute(url="not-a-valid-url")

    assert not result.success
    assert "Invalid URL" in result.error or "failed" in result.error.lower()


@pytest.mark.asyncio
async def test_async_fetch_url_tool_http_error():
    """Test async fetch URL tool with HTTP error."""
    tool = AsyncFetchURLTool()

    # Mock the fetch_url function to simulate HTTP error
    with patch("lunvex_code.tools.async_web_tools.fetch_url", new_callable=AsyncMock) as mock_fetch:
        mock_fetch.side_effect = Exception("HTTP 404: Not Found")

        result = await tool.execute(url="https://example.com/not-found")

        assert not result.success
        assert "404" in result.error or "Not Found" in result.error


@pytest.mark.asyncio
async def test_async_fetch_url_tool_timeout():
    """Test async fetch URL tool with timeout."""
    tool = AsyncFetchURLTool()

    # Mock the fetch_url function to simulate timeout
    with patch("lunvex_code.tools.async_web_tools.fetch_url", new_callable=AsyncMock) as mock_fetch:
        mock_fetch.side_effect = asyncio.TimeoutError("Request timed out")

        result = await tool.execute(url="https://example.com")

        assert not result.success
        assert "timeout" in result.error.lower() or "timed out" in result.error


@pytest.mark.asyncio
async def test_async_fetch_url_tool_large_content():
    """Test async fetch URL tool with large content truncation."""
    tool = AsyncFetchURLTool()

    # Create large content
    large_content = "A" * 15000

    # Mock the fetch_url function
    with patch("lunvex_code.tools.async_web_tools.fetch_url", new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = large_content

        result = await tool.execute(url="https://example.com", max_chars=10000)

        assert result.success
        # Should be truncated to max_chars
        assert len(result.output) <= 10000 + 100  # Allow for some metadata text
        mock_fetch.assert_called_once_with("https://example.com", max_chars=10000)


@pytest.mark.asyncio
async def test_async_fetch_url_tool_empty_response():
    """Test async fetch URL tool with empty response."""
    tool = AsyncFetchURLTool()

    # Mock the fetch_url function
    with patch("lunvex_code.tools.async_web_tools.fetch_url", new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = ""

        result = await tool.execute(url="https://example.com")

        assert result.success
        assert "empty" in result.output.lower() or "no content" in result.output.lower()


if __name__ == "__main__":
    # Run tests
    import sys

    async def run_all_tests():
        """Run all async web tool tests."""
        tests = [
            test_async_fetch_url_tool_success,
            test_async_fetch_url_tool_with_max_chars,
            test_async_fetch_url_tool_error,
            test_async_fetch_url_tool_invalid_url,
            test_async_fetch_url_tool_http_error,
            test_async_fetch_url_tool_timeout,
            test_async_fetch_url_tool_large_content,
            test_async_fetch_url_tool_empty_response,
        ]

        passed = 0
        failed = 0

        for test in tests:
            print(f"\n{'=' * 60}")
            print(f"Running: {test.__name__}")
            print("=" * 60)

            try:
                await test()
                print(f"✅ {test.__name__} PASSED")
                passed += 1
            except Exception as e:
                print(f"❌ {test.__name__} FAILED: {e}")
                import traceback

                traceback.print_exc()
                failed += 1

        print(f"\n{'=' * 60}")
        print(f"TEST SUMMARY: {passed} passed, {failed} failed")
        print("=" * 60)

        return failed == 0

    # Run async tests
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1)
