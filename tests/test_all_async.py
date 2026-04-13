"""Main test file to run all async tests."""

import asyncio
import sys


def run_all_async_tests():
    """Run all async tests using pytest."""
    print("=" * 70)
    print("RUNNING ALL ASYNC TESTS")
    print("=" * 70)

    # List of all async test files
    test_files = [
        "tests/test_async_system.py",
        "tests/test_async_cli.py",
        "tests/test_async_web_tools_simple.py",
        "tests/test_async_agent_simple.py",
        "tests/test_async_cache.py",
        "tests/test_async_git_simple.py",
        "tests/test_async_performance.py",
        "tests/test_async_compatibility.py",
        "tests/test_async_error_handling.py",
        "tests/test_async_dependency_tools.py",
    ]

    # Run pytest on each file
    total_passed = 0
    total_failed = 0
    total_skipped = 0

    for test_file in test_files:
        print(f"\n{'=' * 70}")
        print(f"Running: {test_file}")
        print("=" * 70)

        # Run pytest and capture output
        import subprocess

        result = subprocess.run(
            [sys.executable, "-m", "pytest", test_file, "-v", "--tb=short"],
            capture_output=True,
            text=True,
        )

        # Parse output to get results
        output = result.stdout

        # Count results from output
        lines = output.split("\n")
        for line in lines:
            if "passed" in line and "failed" in line and "skipped" in line:
                # Parse line like: "11 passed, 0 failed, 5 skipped in 1.38s"
                parts = line.split()
                for i, part in enumerate(parts):
                    if part == "passed,":
                        total_passed += int(parts[i - 1])
                    elif part == "failed,":
                        total_failed += int(parts[i - 1])
                    elif part == "skipped":
                        if i > 0 and parts[i - 1].isdigit():
                            total_skipped += int(parts[i - 1])

        # Print the output
        print(output)

        if result.stderr:
            print("STDERR:", result.stderr)

    # Print summary
    print(f"\n{'=' * 70}")
    print("ASYNC TESTS SUMMARY")
    print("=" * 70)
    print(f"Total passed:  {total_passed}")
    print(f"Total failed:  {total_failed}")
    print(f"Total skipped: {total_skipped}")
    print(f"Total tests:   {total_passed + total_failed + total_skipped}")
    print("=" * 70)

    return total_failed == 0


async def run_individual_test_suites():
    """Run individual test suites directly (alternative to pytest)."""
    print("=" * 70)
    print("RUNNING ASYNC TEST SUITES DIRECTLY")
    print("=" * 70)

    # Import and run each test suite
    suites = []

    try:
        from tests.test_async_system import run_all_tests as run_system_tests

        suites.append(("Async System Tests", run_system_tests))
    except ImportError as e:
        print(f"Warning: Could not import system tests: {e}")

    try:
        # from tests.test_async_cli import run_all_tests as run_cli_tests  # Unused import

        # CLI tests don't have run_all_tests function, skip
        pass
    except ImportError as e:
        print(f"Warning: Could not import CLI tests: {e}")

    try:
        from tests.test_async_web_tools import run_all_tests as run_web_tests

        suites.append(("Async Web Tools Tests", run_web_tests))
    except ImportError as e:
        print(f"Warning: Could not import web tools tests: {e}")

    try:
        from tests.test_async_agent_integration import run_all_tests as run_agent_tests

        suites.append(("Async Agent Integration Tests", run_agent_tests))
    except ImportError as e:
        print(f"Warning: Could not import agent integration tests: {e}")

    try:
        from tests.test_async_performance import run_all_tests as run_perf_tests

        suites.append(("Async Performance Tests", run_perf_tests))
    except ImportError as e:
        print(f"Warning: Could not import performance tests: {e}")

    try:
        from tests.test_async_compatibility import run_all_tests as run_compat_tests

        suites.append(("Async Compatibility Tests", run_compat_tests))
    except ImportError as e:
        print(f"Warning: Could not import compatibility tests: {e}")

    try:
        from tests.test_async_error_handling import run_all_tests as run_error_tests

        suites.append(("Async Error Handling Tests", run_error_tests))
    except ImportError as e:
        print(f"Warning: Could not import error handling tests: {e}")

    # Run all suites
    all_passed = True

    for suite_name, suite_runner in suites:
        print(f"\n{'=' * 70}")
        print(f"Running: {suite_name}")
        print("=" * 70)

        try:
            success = await suite_runner()
            if success:
                print(f"✅ {suite_name} PASSED")
            else:
                print(f"❌ {suite_name} FAILED")
                all_passed = False
        except Exception as e:
            print(f"❌ {suite_name} ERROR: {e}")
            import traceback

            traceback.print_exc()
            all_passed = False

    return all_passed


def list_all_async_tests():
    """List all async tests available."""
    print("=" * 70)
    print("AVAILABLE ASYNC TESTS")
    print("=" * 70)

    test_categories = {
        "Core System Tests": [
            "test_async_system.py - Basic async tool tests",
            "  • test_async_read_file_tool",
            "  • test_async_write_file_tool",
            "  • test_async_edit_file_tool",
            "  • test_async_glob_tool",
            "  • test_async_grep_tool",
            "  • test_async_bash_tool",
            "  • test_async_tools_parallel_execution",
            "  • test_async_grep_parallel_search",
            "  • test_sync_and_async_tool_compatibility",
        ],
        "CLI Tests": [
            "test_async_cli.py - Async CLI tests",
            "  • test_async_cli_agent_creation",
            "  • test_async_agent_config",
            "  • test_async_agent_creation",
            "  • test_async_cli_imports",
            "  • test_async_tool_registry",
        ],
        "Web Tools Tests": [
            "test_async_web_tools_simple.py - Async web tool tests",
            "  • test_async_fetch_url_tool_validation",
            "  • test_async_fetch_url_tool_parameters",
            "  • test_async_fetch_url_tool_schema",
        ],
        "Agent Tests": [
            "test_async_agent_simple.py - Async agent tests",
            "  • test_async_agent_config",
            "  • test_async_agent_initialization",
            "  • test_async_agent_tool_registry",
            "  • test_async_agent_system_prompt",
        ],
        "Performance Tests": [
            "test_async_performance.py - Async performance tests",
            "  • test_async_tools_parallel_performance",
            "  • test_async_grep_parallel_performance",
            "  • test_async_agent_concurrent_tasks",
            "  • test_async_tool_memory_usage",
            "  • test_async_system_scalability",
            "  • test_async_tool_cancellation",
        ],
        "Compatibility Tests": [
            "test_async_compatibility.py - Sync/async compatibility tests",
            "  • test_tool_schema_compatibility",
            "  • test_sync_async_equivalent_results",
            "  • test_mixed_sync_async_workflow",
            "  • test_tool_registry_compatibility",
            "  • test_async_wrapper_for_sync_tools",
        ],
        "Cache Tests": [
            "test_async_cache.py - Async cache tests",
            "  • test_async_tool_caching_basic",
            "  • test_async_tool_cache_invalidation",
            "  • test_async_concurrent_cache_access",
            "  • test_async_tool_cache_different_files",
            "  • test_async_tool_cache_with_limits",
            "  • test_async_tool_cache_performance",
        ],
        "Git Tools Tests": [
            "test_async_git_simple.py - Simple Git tool tests",
            "  • test_git_tool_imports",
            "  • test_git_tool_schemas",
            "  • test_git_tool_compatibility",
        ],
        "Dependency Tools Tests": [
            "test_async_dependency_tools.py - Async dependency tool tests",
            "  • test_async_dependency_analysis",
            "  • test_async_dependency_list",
            "  • test_async_vulnerability_scan",
            "  • test_async_dependency_update",
            "  • test_async_dependency_concurrent_operations",
            "  • test_async_dependency_error_handling",
        ],
        "Error Handling Tests": [
            "test_async_error_handling.py - Async error handling tests",
            "  • test_async_read_file_nonexistent",
            "  • test_async_read_file_permission_denied",
            "  • test_async_write_file_invalid_path",
            "  • test_async_edit_file_nonexistent",
            "  • test_async_edit_file_string_not_found",
            "  • test_async_glob_invalid_pattern",
            "  • test_async_grep_invalid_regex",
            "  • test_async_bash_dangerous_command",
            "  • test_async_bash_command_not_found",
            "  • test_async_fetch_url_network_error",
            "  • test_async_agent_tool_execution_error",
            "  • test_async_agent_llm_error",
            "  • test_async_tool_timeout_propagation",
            "  • test_async_agent_with_failing_tools_continues",
            "  • test_async_tool_concurrent_errors",
        ],
    }

    for category, tests in test_categories.items():
        print(f"\n{category}:")
        print("-" * 40)
        for test in tests:
            print(f"  {test}")

    print(f"\n{'=' * 70}")
    print(f"Total test files: {len(test_categories)}")
    print(f"Total test categories: {len(test_categories)}")
    print("=" * 70)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run async tests")
    parser.add_argument(
        "--mode",
        choices=["pytest", "direct", "list"],
        default="pytest",
        help="Test mode: pytest (default), direct, or list",
    )
    parser.add_argument("--file", help="Run specific test file")

    args = parser.parse_args()

    if args.mode == "list":
        list_all_async_tests()
        sys.exit(0)

    elif args.mode == "direct":
        # Run tests directly
        success = asyncio.run(run_individual_test_suites())
        sys.exit(0 if success else 1)

    else:  # pytest mode (default)
        if args.file:
            # Run specific file with pytest
            import subprocess

            result = subprocess.run([sys.executable, "-m", "pytest", args.file, "-v"])
            sys.exit(result.returncode)
        else:
            # Run all tests
            success = run_all_async_tests()
            sys.exit(0 if success else 1)
