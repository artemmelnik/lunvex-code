#!/usr/bin/env python3
"""
Real example of using subtask mode with LunVex Code.

This example shows how to:
1. Create an agent with subtask planning enabled
2. Execute complex tasks that get broken into subtasks
3. Monitor subtask execution progress
"""

import asyncio
import os
import tempfile
from pathlib import Path

# Try to import LunVex modules
try:
    from lunvex_code.async_agent import create_async_agent

    HAS_LUNVEX = True
except ImportError:
    HAS_LUNVEX = False
    print("⚠️  LunVex Code not installed. Running in demo mode.")


async def run_real_example_with_api():
    """Run a real example with actual API calls (requires API key)."""
    if not HAS_LUNVEX:
        print("❌ LunVex Code not available. Please install it first.")
        return

    api_key = os.environ.get("DEEPSEEK_API_KEY")
    if not api_key:
        print("❌ DEEPSEEK_API_KEY environment variable not set.")
        print("   Please set it to your DeepSeek API key.")
        return

    print("🚀 Starting real subtask example with API...")

    # Create a temporary project directory
    with tempfile.TemporaryDirectory() as tmpdir:
        project_path = Path(tmpdir)

        # Create a simple Python project
        (project_path / "main.py").write_text("""
def calculate(a, b):
    return a + b

def main():
    result = calculate(5, 3)
    print(f"Result: {result}")

if __name__ == "__main__":
    main()
""")

        (project_path / "test_main.py").write_text("""
def test_calculate():
    from main import calculate
    assert calculate(2, 3) == 5
    print("Test passed!")

if __name__ == "__main__":
    test_calculate()
""")

        print(f"📁 Created test project at: {project_path}")
        print("📄 Project files:")
        for file in project_path.iterdir():
            print(f"  - {file.name}")

        # Create the agent
        print("\n🤖 Creating LunVex agent...")
        try:
            agent = create_async_agent(
                api_key=api_key,
                working_dir=str(project_path),
                trust_mode=True,  # Auto-approve safe operations
                max_turns=30,
            )
            print("✅ Agent created successfully!")
        except Exception as e:
            print(f"❌ Failed to create agent: {e}")
            return

        # Define a complex task
        complex_task = """
        Refactor the calculate function to handle subtraction and multiplication as well.
        Update main.py to include the new operations, add proper error handling for invalid inputs,
        update test_main.py to test all operations, and ensure the code follows PEP 8 guidelines.
        """

        print("\n🎯 Task to execute:")
        print(f'   "{complex_task.strip()}"')

        print("\n🔍 The agent will:")
        print("   1. Analyze if the task is complex enough for subtask planning")
        print("   2. If complex, create a plan with subtasks")
        print("   3. Execute subtasks in optimal order")
        print("   4. Share context between subtasks")
        print("   5. Return the final result")

        input("\n⏎ Press Enter to start execution...")

        try:
            # Run the task with subtask planning (default)
            print("\n🚀 Executing task with subtask planning...")
            result = await agent.run(complex_task, use_planning=True)

            print("\n✅ Task completed!")
            print("\n📋 Result summary:")
            print(result[:500] + "..." if len(result) > 500 else result)

        except Exception as e:
            print(f"❌ Error during execution: {e}")
            import traceback

            traceback.print_exc()


def run_demo_example():
    """Run a demo example without API calls."""
    print("🎭 Running demo example (no API calls)...")

    print("\n📋 How subtask planning works:")

    print("\n1. Task Analysis:")
    print('   Agent receives: "Refactor calculate function, add operations, update tests"')
    print("   Detection: Complex task (multiple actions, file mentions)")

    print("\n2. Subtask Generation:")
    print("   Generated subtasks:")
    print("   ┌─ analyze: Understand current code")
    print("   ├─ refactor: Update calculate function")
    print("   ├─ test: Add new test cases")
    print("   └─ verify: Run tests and check style")

    print("\n3. Dependency Analysis:")
    print("   analyze → refactor → test → verify")

    print("\n4. Execution:")
    print("   Step 1: Execute 'analyze'")
    print("   Step 2: Execute 'refactor' (depends on 'analyze')")
    print("   Step 3: Execute 'test' (depends on 'refactor')")
    print("   Step 4: Execute 'verify' (depends on 'test')")

    print("\n5. Context Sharing:")
    print("   Each subtask receives context from previous subtasks")
    print("   Final result combines all subtask outputs")

    print("\n💡 Benefits demonstrated:")
    print("   • Complex task broken into manageable pieces")
    print("   • Clear execution order based on dependencies")
    print("   • Context preserved between steps")
    print("   • Progress tracking at subtask level")


async def test_complexity_detection():
    """Test the complexity detection algorithm."""
    print("\n🔬 Testing complexity detection algorithm...")

    # Test cases
    test_cases = [
        ("Read config.yaml", False, "Simple file read"),
        ("Update main.py and utils.py", True, "Multiple files"),
        ("First analyze the code, then refactor it", True, "Sequential steps"),
        (
            "Create a new project with proper structure, add dependencies, configure tests, and write documentation",
            True,
            "Long multi-step task",
        ),
        ("Fix the bug in login.py", False, "Single action"),
        (
            "Refactor the authentication system to use JWT tokens, update all API endpoints, write comprehensive tests, and update documentation",
            True,
            "Complex refactoring",
        ),
    ]

    # Simple complexity detector (mimicking the real one)
    def is_complex(task: str) -> bool:
        task_lower = task.lower()

        # Check for complexity indicators
        indicators = [
            r"\b(and|then|after|also|next|first|second|finally)\b",
            r"\b(multiple|several|various|different)\b",
            r"\.\.\.",
            r"[;:]",
        ]

        import re

        indicator_count = sum(1 for pattern in indicators if re.search(pattern, task_lower))

        # Check for file mentions
        file_patterns = [
            r"\b(\w+\.(py|js|ts|json|yaml|md))\b",
            r"\b(file|module|config)\b",
        ]

        file_mentions = sum(len(re.findall(pattern, task_lower)) for pattern in file_patterns)

        # Word count
        word_count = len(task.split())

        # Multi-step detection
        has_multi_step = bool(re.search(r"\b(first|second|step\s+\d+)\b", task_lower))

        return indicator_count >= 2 or file_mentions >= 2 or word_count > 30 or has_multi_step

    print("\n" + "=" * 80)
    print(f"{'Task':<60} {'Expected':<10} {'Actual':<10} {'Match':<6}")
    print("=" * 80)

    all_match = True
    for task, expected, description in test_cases:
        actual = is_complex(task)
        matches = "✅" if actual == expected else "❌"
        if actual != expected:
            all_match = False

        # Truncate long tasks for display
        display_task = task[:57] + "..." if len(task) > 60 else task
        print(f"{display_task:<60} {str(expected):<10} {str(actual):<10} {matches:<6}")

    print("=" * 80)

    if all_match:
        print("✅ All complexity detections match expectations!")
    else:
        print("⚠️  Some complexity detections don't match expectations.")


async def main():
    """Main function to run all examples."""
    print("=" * 70)
    print("LUNVEX CODE - SUBTASK MODE DEMONSTRATION")
    print("=" * 70)

    # Check if we have LunVex and API key
    api_key = os.environ.get("DEEPSEEK_API_KEY")
    has_api_key = bool(api_key)

    print(f"\n🔑 API Key available: {'✅ Yes' if has_api_key else '❌ No'}")
    print(f"📦 LunVex installed: {'✅ Yes' if HAS_LUNVEX else '❌ No'}")

    # Run appropriate example
    if has_api_key and HAS_LUNVEX:
        choice = input(
            "\nChoose mode:\n1. Real example with API (requires credits)\n2. Demo example only\n\nEnter choice (1 or 2): "
        ).strip()

        if choice == "1":
            await run_real_example_with_api()
        else:
            run_demo_example()
    else:
        print("\n⚠️  Running in demo mode (no API calls)")
        run_demo_example()

    # Always run complexity detection test
    await test_complexity_detection()

    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)

    print("\n🎯 Subtask planning is useful for:")
    print("   • Multi-step refactoring tasks")
    print("   • Project setup and configuration")
    print("   • Complex bug fixes with investigation")
    print("   • Feature implementation with multiple components")

    print("\n⚙️  How to enable/disable:")
    print("   • Default: use_planning=True (auto-detects complexity)")
    print("   • Force planning: agent.run(task, use_planning=True)")
    print("   • Disable planning: agent.run(task, use_planning=False)")

    print("\n📈 Benefits:")
    print("   • Handles tasks longer than context window")
    print("   • Better success rate for complex tasks")
    print("   • Clear progress tracking")
    print("   • Optimal execution order")

    print("\n" + "=" * 70)
    print("DEMONSTRATION COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())
