#!/usr/bin/env python3
"""Test CLI with --no-animation option."""

import os
import subprocess
import sys


def test_cli_help():
    """Test that CLI shows --no-animation option in help."""
    print("Testing CLI help for --no-animation option...")

    try:
        result = subprocess.run(
            [sys.executable, "-m", "lunvex_code.cli", "run", "--help"],
            capture_output=True,
            text=True,
            cwd=os.path.dirname(os.path.abspath(__file__)),
        )

        if "--no-animation" in result.stdout:
            print("✅ --no-animation option found in help")
            return True
        else:
            print("❌ --no-animation option NOT found in help")
            print("Output:", result.stdout)
            return False

    except Exception as e:
        print(f"❌ Error running CLI: {e}")
        return False


def test_environment_variable():
    """Test that LUNVEX_NO_ANIMATION environment variable works."""
    print("\nTesting LUNVEX_NO_ANIMATION environment variable...")

    # Save original environment
    original_env = os.environ.copy()

    try:
        # Test with an explicit animation selection
        os.environ["LUNVEX_ANIMATION"] = "robot"
        from lunvex_code.ui import get_animation_type

        result = get_animation_type()
        if result == "robot":
            print(f"✅ LUNVEX_ANIMATION=robot -> animation enabled ({result})")
        else:
            print(f"❌ LUNVEX_ANIMATION=robot -> animation disabled ({result})")
            return False

        # Clean up for next test
        del os.environ["LUNVEX_ANIMATION"]

        # Test with animation disabled
        os.environ["LUNVEX_NO_ANIMATION"] = "1"
        result = get_animation_type()
        if result == "none":
            print(f"✅ LUNVEX_NO_ANIMATION=1 -> animation disabled ({result})")
        else:
            print(f"❌ LUNVEX_NO_ANIMATION=1 -> animation enabled ({result})")
            return False

        # Test with other truthy values
        for value in ["true", "yes", "on"]:
            os.environ["LUNVEX_NO_ANIMATION"] = value
            result = get_animation_type()
            if result == "none":
                print(f"✅ LUNVEX_NO_ANIMATION={value} -> animation disabled")
            else:
                print(f"❌ LUNVEX_NO_ANIMATION={value} -> animation enabled")
                return False

        return True

    finally:
        # Restore original environment
        os.environ.clear()
        os.environ.update(original_env)


def main():
    print("🔧 Testing CLI Animation Disabling Feature")
    print("=" * 60)

    all_passed = True

    # Test 1: CLI help
    if not test_cli_help():
        all_passed = False

    # Test 2: Environment variable
    if not test_environment_variable():
        all_passed = False

    print("\n" + "=" * 60)
    if all_passed:
        print("✅ All CLI animation tests passed!")
        print("\nUsage examples:")
        print('  lunvex-code run --no-animation "Analyze the code"')
        print("  export LUNVEX_NO_ANIMATION=1 && lunvex-code run")
        print("  lunvex-code run --help (to see all options)")
    else:
        print("❌ Some tests failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
