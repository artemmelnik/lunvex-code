#!/usr/bin/env python3
"""
Demonstration of subtask planning and execution.

This script shows how LunVex Code automatically breaks down complex tasks
into manageable subtasks.
"""

import asyncio
import tempfile
from pathlib import Path

from lunvex_code.task_planner import TaskPlanner


async def demo_subtask_planning():
    """Demonstrate subtask planning without actual LLM calls."""
    print("=" * 70)
    print("DEMONSTRATION: SUBTASK PLANNING SYSTEM")
    print("=" * 70)

    # Create a temporary directory for our demo
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)

        # Create some test files
        main_py = tmp_path / "main.py"
        utils_py = tmp_path / "utils.py"
        test_py = tmp_path / "test_main.py"

        main_py.write_text("""
def calculate_sum(a, b):
    return a + b

def main():
    result = calculate_sum(5, 3)
    print(f"Result: {result}")

if __name__ == "__main__":
    main()
""")

        utils_py.write_text("""
def helper_function():
    return "Helper"
""")

        test_py.write_text("""
def test_calculate_sum():
    from main import calculate_sum
    assert calculate_sum(2, 3) == 5
    print("Test passed!")
""")

        print(f"\n📁 Created test project in: {tmp_path}")
        print("📄 Files created:")
        print(f"  - {main_py.name}")
        print(f"  - {utils_py.name}")
        print(f"  - {test_py.name}")

        # Create a mock LLM client for demonstration
        class MockLunVexClient:
            def __init__(self):
                self.model = "mock-model"

            def chat(self, messages, tools=None, temperature=0.0, max_tokens=4096, use_cache=True):
                # Return a mock response based on the prompt
                prompt = messages[0]["content"]

                import json

                if "Analyze this programming task" in prompt:
                    # Return analysis response
                    response = type(
                        "obj",
                        (object,),
                        {
                            "content": json.dumps(
                                {
                                    "files_needed": ["main.py", "utils.py", "test_main.py"],
                                    "tools_needed": ["read_file", "edit_file", "bash"],
                                    "phases": ["analyze", "refactor", "test", "document"],
                                    "dependencies": {
                                        "refactor": ["analyze"],
                                        "test": ["refactor"],
                                        "document": ["refactor"],
                                    },
                                }
                            )
                        },
                    )
                    return response

                elif "Break down this programming task" in prompt:
                    # Return subtask breakdown
                    response = type(
                        "obj",
                        (object,),
                        {
                            "content": json.dumps(
                                {
                                    "subtasks": [
                                        {
                                            "id": "analyze-code",
                                            "description": "Analyze the current code structure",
                                            "dependencies": [],
                                            "expected_output": "Understanding of current implementation",
                                            "context_files": [
                                                "main.py",
                                                "utils.py",
                                                "test_main.py",
                                            ],
                                            "tools_needed": ["read_file", "grep"],
                                        },
                                        {
                                            "id": "refactor-main",
                                            "description": "Refactor main.py to add error handling",
                                            "dependencies": ["analyze-code"],
                                            "expected_output": "Updated main.py with error handling",
                                            "context_files": ["main.py"],
                                            "tools_needed": ["read_file", "edit_file"],
                                        },
                                        {
                                            "id": "update-utils",
                                            "description": "Update utils.py with new helper functions",
                                            "dependencies": ["analyze-code"],
                                            "expected_output": "Enhanced utils.py",
                                            "context_files": ["utils.py"],
                                            "tools_needed": ["read_file", "edit_file"],
                                        },
                                        {
                                            "id": "run-tests",
                                            "description": "Run tests to verify changes",
                                            "dependencies": ["refactor-main", "update-utils"],
                                            "expected_output": "Test results",
                                            "context_files": ["test_main.py"],
                                            "tools_needed": ["bash"],
                                        },
                                        {
                                            "id": "update-docs",
                                            "description": "Update documentation",
                                            "dependencies": ["refactor-main", "update-utils"],
                                            "expected_output": "Updated README.md",
                                            "context_files": [],
                                            "tools_needed": ["write_file"],
                                        },
                                    ]
                                }
                            )
                        },
                    )
                    return response

        # Create mock tool registry
        mock_tool_registry = type("obj", (object,), {})()

        # Create task planner
        client = MockLunVexClient()
        planner = TaskPlanner(client, mock_tool_registry, str(tmp_path))

        # Define a complex task
        complex_task = """
        Refactor the codebase to add proper error handling and input validation.
        Update main.py to handle edge cases, enhance utils.py with additional helper functions,
        run tests to ensure nothing is broken, and update documentation.
        """

        print("\n🎯 Complex task to execute:")
        print(f'   "{complex_task.strip()}"')

        print("\n🔍 Step 1: Analyzing task complexity...")
        is_complex = planner._is_complex_task(complex_task)
        print(f"   Task is complex: {is_complex}")

        if is_complex:
            print("\n📋 Step 2: Creating task plan...")
            plan = planner.create_task_plan(complex_task)

            print(f"   Created plan with {len(plan.subtasks)} subtasks")

            print("\n📊 Step 3: Task Plan Overview:")
            print(f"   Original task: {plan.original_task[:100]}...")
            print(f"   Number of subtasks: {len(plan.subtasks)}")
            print(f"   Execution order: {plan.execution_order}")

            print("\n📝 Step 4: Subtask Details:")
            for i, subtask_id in enumerate(plan.execution_order, 1):
                subtask = next(st for st in plan.subtasks if st.id == subtask_id)
                deps = ", ".join(subtask.dependencies) if subtask.dependencies else "none"
                files = ", ".join(subtask.context_files[:2])
                if len(subtask.context_files) > 2:
                    files += f"... (+{len(subtask.context_files) - 2} more)"

                print(f"\n   {i}. {subtask.id}:")
                print(f"      Description: {subtask.description}")
                print(f"      Dependencies: {deps}")
                print(f"      Expected output: {subtask.expected_output}")
                print(f"      Files: {files}")
                print(f"      Tools needed: {', '.join(subtask.tools_needed)}")

            print("\n🔄 Step 5: Dependency Graph:")
            print("   analyze-code")
            print("   ├── refactor-main")
            print("   │   ├── run-tests")
            print("   │   └── update-docs")
            print("   └── update-utils")
            print("       ├── run-tests")
            print("       └── update-docs")

            print("\n🚀 Step 6: Execution Strategy:")
            print("   1. Execute 'analyze-code' (no dependencies)")
            print(
                "   2. Execute 'refactor-main' and 'update-utils' in parallel (both depend on 'analyze-code')"
            )
            print("   3. Execute 'run-tests' (depends on 'refactor-main' and 'update-utils')")
            print("   4. Execute 'update-docs' (depends on 'refactor-main' and 'update-utils')")

            print("\n💡 Benefits of subtask planning:")
            print("   • Breaks complex tasks into manageable pieces")
            print("   • Identifies dependencies between steps")
            print("   • Allows parallel execution where possible")
            print("   • Maintains context between subtasks")
            print("   • Provides clear progress tracking")

        else:
            print("\nℹ️  Task is simple enough to execute directly without planning.")

        print("\n" + "=" * 70)
        print("DEMONSTRATION COMPLETE")
        print("=" * 70)


async def demo_real_agent_with_subtasks():
    """Demonstrate using the actual agent with subtask planning."""
    print("\n" + "=" * 70)
    print("DEMONSTRATION: REAL AGENT WITH SUBTASKS")
    print("=" * 70)

    print("\n⚠️  Note: This would require a real API key and actual LLM calls.")
    print("   For this demo, we'll show the structure without making real calls.")

    # Example of how to use the agent with subtask planning
    print("\nExample code structure:")
    print("""
    from lunvex_code.async_agent import create_async_agent

    # Create an agent
    agent = create_async_agent(
        api_key="your-api-key-here",  # Or set DEEPSEEK_API_KEY env var
        working_dir=".",
        trust_mode=True  # Auto-approve safe operations
    )

    # Define a complex task
    complex_task = '''
    Refactor the authentication system to use JWT tokens instead of sessions.
    Update the user model, add token generation logic, update API endpoints,
    write tests for the new functionality, and update documentation.
    '''

    # Run with automatic subtask planning (default)
    result = await agent.run(complex_task, use_planning=True)

    print(f"Task completed: {result}")
    """)

    print("\nHow it works:")
    print("1. Agent analyzes if task is complex enough for decomposition")
    print("2. If complex, creates a plan with subtasks")
    print("3. Executes subtasks in optimal order")
    print("4. Shares context between subtasks")
    print("5. Returns final result")

    print("\n" + "=" * 70)
    print("DEMONSTRATION COMPLETE")
    print("=" * 70)


async def main():
    """Run all demonstrations."""
    await demo_subtask_planning()
    await demo_real_agent_with_subtasks()

    print("\n🎉 Summary:")
    print("LunVex Code's subtask planning system automatically breaks down")
    print("complex coding tasks into manageable subtasks, solving the problem")
    print("of limited LLM context windows and improving task execution success.")


if __name__ == "__main__":
    asyncio.run(main())
