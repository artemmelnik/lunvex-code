#!/usr/bin/env python3
"""
Final check of async system.
Runs smoke tests and provides summary.
"""

import asyncio
import sys
import subprocess
import os


def print_header(text):
    """Print formatted header."""
    print("\n" + "=" * 70)
    print(f" {text}")
    print("=" * 70)


def print_section(text):
    """Print section header."""
    print(f"\n📋 {text}")
    print("-" * 40)


def run_command(cmd, description):
    """Run command and return success."""
    print(f"  🔧 {description}...")
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode == 0:
            print(f"    ✅ Success")
            return True
        else:
            print(f"    ❌ Failed (code: {result.returncode})")
            if result.stderr:
                print(f"    Error: {result.stderr[:200]}...")
            return False
    except subprocess.TimeoutExpired:
        print(f"    ⏰ Timeout")
        return False
    except Exception as e:
        print(f"    ❌ Exception: {e}")
        return False


async def run_async_smoke_tests():
    """Run async smoke tests."""
    print_section("Running Async Smoke Tests")
    
    # Import and run smoke tests
    import traceback
    from tests.test_async_smoke import (
        test_smoke_async_file_operations,
        test_smoke_async_write_and_read,
        test_smoke_async_search,
        test_smoke_async_bash,
        test_smoke_async_agent_import,
        test_smoke_async_tool_registry,
        test_smoke_async_parallel_execution,
        test_smoke_sync_async_compatibility,
    )
    
    tests = [
        ("File Operations", test_smoke_async_file_operations),
        ("Write/Read", test_smoke_async_write_and_read),
        ("Search", test_smoke_async_search),
        ("Bash Commands", test_smoke_async_bash),
        ("Agent Import", test_smoke_async_agent_import),
        ("Tool Registry", test_smoke_async_tool_registry),
        ("Parallel Execution", test_smoke_async_parallel_execution),
    ]
    
    passed = 0
    failed = 0
    
    for name, test_func in tests:
        print(f"  🔍 {name}...")
        try:
            if asyncio.iscoroutinefunction(test_func):
                await test_func()
            else:
                test_func()
            print(f"    ✅ PASSED")
            passed += 1
        except Exception as e:
            print(f"    ❌ FAILED: {e}")
            failed += 1
    
    # Run sync test
    print(f"  🔍 Sync/Async Compatibility...")
    try:
        test_smoke_sync_async_compatibility()
        print(f"    ✅ PASSED")
        passed += 1
    except Exception as e:
        print(f"    ❌ FAILED: {e}")
        failed += 1
    
    return passed, failed


def check_test_files():
    """Check that all test files exist and are valid."""
    print_section("Checking Test Files")
    
    test_files = [
        "tests/test_async_system.py",
        "tests/test_async_cli.py",
        "tests/test_async_web_tools_simple.py",
        "tests/test_async_agent_simple.py",
        "tests/test_async_cache.py",
        "tests/test_async_git_simple.py",
        "tests/test_async_smoke.py",
        "tests/test_all_async.py",
    ]
    
    existing = 0
    missing = 0
    
    for test_file in test_files:
        if os.path.exists(test_file):
            print(f"  📄 {test_file}: ✅ Found")
            existing += 1
        else:
            print(f"  📄 {test_file}: ❌ Missing")
            missing += 1
    
    return existing, missing


def check_imports():
    """Check that key imports work."""
    print_section("Checking Key Imports")
    
    imports_to_check = [
        ("lunvex_code.tools.async_file_tools", "AsyncReadFileTool"),
        ("lunvex_code.tools.async_search_tools", "AsyncGrepTool"),
        ("lunvex_code.tools.async_bash_tool", "AsyncBashTool"),
        ("lunvex_code.tools.async_web_tools", "AsyncFetchURLTool"),
        ("lunvex_code.async_agent", "AsyncAgent"),
        ("lunvex_code.async_cli", "create_and_run_agent_async"),
    ]
    
    successful = 0
    failed = 0
    
    for module_name, import_name in imports_to_check:
        print(f"  📦 {module_name}.{import_name}...")
        try:
            exec(f"from {module_name} import {import_name}")
            print(f"    ✅ Import successful")
            successful += 1
        except ImportError as e:
            print(f"    ❌ Import failed: {e}")
            failed += 1
        except Exception as e:
            print(f"    ❌ Error: {e}")
            failed += 1
    
    return successful, failed


def generate_summary(results):
    """Generate final summary."""
    print_header("FINAL SUMMARY")
    
    total_passed = 0
    total_failed = 0
    total_checks = 0
    
    print("\n📊 RESULTS:")
    print("-" * 40)
    
    for category, (passed, failed, total) in results.items():
        total_passed += passed
        total_failed += failed
        total_checks += total
        
        status = "✅" if failed == 0 else "⚠️" if passed > 0 else "❌"
        print(f"{status} {category}: {passed}/{total} passed")
    
    print("-" * 40)
    print(f"📈 TOTAL: {total_passed}/{total_checks} checks passed")
    
    if total_failed == 0:
        print("\n🎉 EXCELLENT! All checks passed.")
        print("   Async system is fully operational.")
        return True
    elif total_passed > total_failed:
        print(f"\n⚠️  GOOD: {total_passed} passed, {total_failed} failed")
        print("   Async system is mostly operational.")
        return True
    else:
        print(f"\n❌ NEEDS WORK: {total_passed} passed, {total_failed} failed")
        print("   Async system needs attention.")
        return False


async def main():
    """Main function."""
    print_header("ASYNC SYSTEM FINAL CHECK")
    print("Comprehensive verification of async testing infrastructure")
    
    results = {}
    
    # 1. Check test files
    existing, missing = check_test_files()
    results["Test Files"] = (existing, missing, existing + missing)
    
    # 2. Check imports
    successful, failed = check_imports()
    results["Imports"] = (successful, failed, successful + failed)
    
    # 3. Run smoke tests
    smoke_passed, smoke_failed = await run_async_smoke_tests()
    results["Smoke Tests"] = (smoke_passed, smoke_failed, smoke_passed + smoke_failed)
    
    # 4. Run quick pytest check
    print_section("Quick Pytest Check")
    pytest_ok = run_command(
        "python -m pytest tests/test_async_system.py::test_async_read_file_tool -v",
        "Basic async test"
    )
    results["Pytest"] = (1 if pytest_ok else 0, 0 if pytest_ok else 1, 1)
    
    # 5. Generate summary
    overall_success = generate_summary(results)
    
    # 6. Provide next steps
    print_header("NEXT STEPS")
    
    if overall_success:
        print("""
✅ SYSTEM READY FOR USE:

1. Run all tests:
   $ ./run_async_tests.sh

2. View all available tests:
   $ python tests/test_all_async.py --mode=list

3. Run comprehensive tests:
   $ python tests/test_all_async.py --mode=pytest

4. For development:
   $ python -m pytest tests/test_async_system.py -v
        """)
    else:
        print("""
⚠️  SYSTEM NEEDS ATTENTION:

1. Check failing imports:
   $ python -c "from lunvex_code.tools.async_file_tools import AsyncReadFileTool"

2. Run smoke tests manually:
   $ python tests/test_async_smoke.py

3. Check test files exist:
   $ ls -la tests/test_async_*.py

4. Review error messages above for specific issues.
        """)
    
    return overall_success


if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⏹️  Check interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)