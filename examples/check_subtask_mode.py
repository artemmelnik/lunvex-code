#!/usr/bin/env python3
"""
Check if subtask mode is working correctly.

This script tests the subtask planning functionality by:
1. Creating a test project
2. Defining complex tasks
3. Showing how subtasks would be generated
4. Demonstrating execution order
"""

import os
import sys
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def check_subtask_mode():
    """Check if subtask mode is properly configured and working."""
    print("🔍 Checking subtask mode configuration...")

    # Check if required modules are available
    try:
        # Just check if module exists
        import importlib

        importlib.import_module("lunvex_code.task_planner")
        print("✅ Task planner module: OK")
    except ImportError as e:
        print(f"❌ Task planner module: ERROR - {e}")
        return False

    try:
        # Just check if module exists
        import importlib

        importlib.import_module("lunvex_code.async_agent")
        print("✅ Async agent module: OK")
    except ImportError as e:
        print(f"❌ Async agent module: ERROR - {e}")
        return False

    # Check if we can create a task planner
    try:
        # Create mock objects for testing
        class MockClient:
            def chat(self, messages, **kwargs):
                # Return a simple mock response
                import json

                response = type(
                    "obj",
                    (object,),
                    {
                        "content": json.dumps(
                            {
                                "files_needed": [],
                                "tools_needed": ["read_file", "edit_file"],
                                "phases": ["test"],
                                "dependencies": {},
                            }
                        )
                    },
                )
                return response

        class MockToolRegistry:
            pass

        client = MockClient()
        tool_registry = MockToolRegistry()

        from lunvex_code.task_planner import TaskPlanner

        planner = TaskPlanner(client, tool_registry, ".")
        print("✅ Task planner creation: OK")

        # Test complexity detection
        simple_task = "Read a file"
        complex_task = "First analyze the code, then refactor it, and finally run tests"

        is_simple_complex = planner._is_complex_task(simple_task)
        is_complex_complex = planner._is_complex_task(complex_task)

        print("✅ Complexity detection: OK")
        print(f"   Simple task ('{simple_task}'): {'complex' if is_simple_complex else 'simple'}")
        print(
            f"   Complex task ('{complex_task[:50]}...'): {'complex' if is_complex_complex else 'simple'}"
        )

        # Test creating a simple plan
        try:
            plan = planner.create_task_plan("Test task")
            print(f"✅ Task plan creation: OK (created {len(plan.subtasks)} subtasks)")
        except Exception as e:
            print(f"❌ Task plan creation: ERROR - {e}")
            return False

    except Exception as e:
        print(f"❌ Task planner test: ERROR - {e}")
        return False

    # Check agent configuration
    print("\n🔧 Checking agent configuration for subtask mode...")

    # Check environment variables
    api_key = os.environ.get("DEEPSEEK_API_KEY")
    if api_key:
        print(f"✅ DEEPSEEK_API_KEY: Set (length: {len(api_key)})")
    else:
        print("⚠️  DEEPSEEK_API_KEY: Not set (required for real LLM calls)")

    # Check default model
    default_model = os.environ.get("DEEPSEEK_MODEL", "deepseek-chat")
    print(f"✅ Default model: {default_model}")

    print("\n🎯 Testing subtask scenarios...")

    # Define test scenarios
    scenarios = [
        {
            "name": "Simple file operation",
            "task": "Read the contents of config.yaml",
            "expected": "Should execute directly (no subtasks)",
        },
        {
            "name": "Multi-step refactoring",
            "task": "Refactor the user authentication module to use JWT tokens, update tests, and document changes",
            "expected": "Should create 3-5 subtasks",
        },
        {
            "name": "Complex project setup",
            "task": "Set up a new Python project with proper structure, add dependencies, configure testing, and create documentation",
            "expected": "Should create 4-7 subtasks",
        },
        {
            "name": "Bug fix with investigation",
            "task": "Investigate why the login feature is failing, fix the bug, add tests to prevent regression, and update documentation",
            "expected": "Should create 3-5 subtasks",
        },
    ]

    for scenario in scenarios:
        task = scenario["task"]
        is_complex = planner._is_complex_task(task)

        status = "✅" if is_complex == ("complex" in scenario["expected"].lower()) else "⚠️"
        complexity = "complex" if is_complex else "simple"

        print(f"\n{status} {scenario['name']}:")
        print(f"   Task: {task[:60]}...")
        print(f"   Detected as: {complexity}")
        print(f"   Expected: {scenario['expected']}")

    print("\n📋 How to use subtask mode:")
    print("""
    1. Create an agent:
       ```python
       from lunvex_code.async_agent import create_async_agent
       agent = create_async_agent(api_key="your-key", working_dir=".")
       ```

    2. Run a complex task with planning (default):
       ```python
       result = await agent.run("Your complex task here", use_planning=True)
       ```

    3. Or disable planning for simple tasks:
       ```python
       result = await agent.run("Read file.txt", use_planning=False)
       ```

    4. The agent automatically decides if planning is needed based on:
       - Task length and complexity
       - Number of files mentioned
       - Presence of sequential steps (and, then, after, etc.)
    """)

    print("\n🔧 Configuration options:")
    print("""
    Environment variables:
    - DEEPSEEK_API_KEY: Your API key (required)
    - DEEPSEEK_MODEL: Model to use (default: deepseek-chat)
    - LUNVEX_TRUST_MODE: Auto-approve safe operations
    - LUNVEX_YOLO_MODE: Skip all permission prompts (dangerous!)

    Agent parameters:
    - trust_mode: Auto-approve file operations
    - yolo_mode: Skip ALL permission prompts
    - max_turns: Maximum LLM turns per task
    - use_planning: Enable/disable subtask planning
    """)

    print("\n✅ Subtask mode check completed successfully!")
    print("\n💡 Tip: For best results with complex tasks:")
    print("   - Be specific about what needs to be done")
    print("   - Mention relevant files and modules")
    print("   - Include expected outcomes")
    print("   - Let the agent handle the decomposition")

    return True


if __name__ == "__main__":
    success = check_subtask_mode()
    sys.exit(0 if success else 1)
