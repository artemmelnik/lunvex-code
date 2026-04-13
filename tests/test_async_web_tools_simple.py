"""Simple tests for async web tools."""

import asyncio
import pytest

from lunvex_code.tools.async_web_tools import AsyncFetchURLTool


@pytest.mark.asyncio
async def test_async_fetch_url_tool_validation():
    """Test async fetch URL tool URL validation."""
    tool = AsyncFetchURLTool()
    
    # Test invalid URL
    result = await tool.execute(url="not-a-valid-url")
    assert not result.success
    assert "URL must be a valid http:// or https:// address" in result.error
    
    # Test missing scheme
    result = await tool.execute(url="example.com")
    assert not result.success
    
    # Test file URL (not allowed)
    result = await tool.execute(url="file:///etc/passwd")
    assert not result.success


@pytest.mark.asyncio
async def test_async_fetch_url_tool_parameters():
    """Test async fetch URL tool parameters."""
    tool = AsyncFetchURLTool()
    
    # Check tool properties
    assert tool.name == "fetch_url"
    assert "Fetch content from an external HTTP or HTTPS URL" in tool.description
    assert tool.permission_level == "ask"
    
    # Check parameters
    assert "url" in tool.parameters
    assert tool.parameters["url"]["required"] is True
    assert "max_chars" in tool.parameters
    assert tool.parameters["max_chars"]["required"] is False


@pytest.mark.asyncio
async def test_async_fetch_url_tool_schema():
    """Test async fetch URL tool schema generation."""
    tool = AsyncFetchURLTool()
    
    schema = tool.get_schema()
    
    assert schema["function"]["name"] == "fetch_url"
    assert "Fetch content from an external HTTP or HTTPS URL" in schema["function"]["description"]
    assert "url" in schema["function"]["parameters"]["properties"]
    assert "max_chars" in schema["function"]["parameters"]["properties"]


if __name__ == "__main__":
    # Run tests
    import sys
    
    async def run_all_tests():
        """Run all simple async web tool tests."""
        tests = [
            test_async_fetch_url_tool_validation,
            test_async_fetch_url_tool_parameters,
            test_async_fetch_url_tool_schema,
        ]
        
        passed = 0
        failed = 0
        
        for test in tests:
            print(f"\n{'='*60}")
            print(f"Running: {test.__name__}")
            print('='*60)
            
            try:
                await test()
                print(f"✅ {test.__name__} PASSED")
                passed += 1
            except Exception as e:
                print(f"❌ {test.__name__} FAILED: {e}")
                import traceback
                traceback.print_exc()
                failed += 1
        
        print(f"\n{'='*60}")
        print(f"TEST SUMMARY: {passed} passed, {failed} failed")
        print('='*60)
        
        return failed == 0
    
    # Run async tests
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1)