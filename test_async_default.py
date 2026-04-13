#!/usr/bin/env python3
"""Test that async mode with subtasks is the default."""

import asyncio
import os
import sys
import tempfile
from pathlib import Path

# Add the project to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from lunvex_code.async_agent import AsyncAgent, AsyncAgentConfig
from lunvex_code.context import ProjectContext
from lunvex_code.task_planner import TaskPlanner


async def test_async_planning_default():
    """Test that async agent uses planning by default."""
    print("🧪 Testing async agent with planning by default...")

    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)

        # Create a simple project structure
        (tmpdir_path / "src").mkdir()
        (tmpdir_path / "src" / "main.py").write_text("# Main application\nprint('Hello')")
        (tmpdir_path / "tests").mkdir()
        (tmpdir_path / "tests" / "test_main.py").write_text("# Tests\nimport unittest")

        # Create context
        context = ProjectContext(working_dir=str(tmpdir_path), project_md=None)

        # Create mock client
        class MockClient:
            model = "deepseek-chat"

            async def chat(self, messages):
                class MockResponse:
                    class Choice:
                        class Message:
                            content = '{"subtasks": [{"id": "analyze", "description": "Analyze the code", "dependencies": [], "expected_output": "Understanding of code structure", "context_files": ["src/main.py"], "tools_needed": ["read_file"]}, {"id": "implement", "description": "Implement changes", "dependencies": ["analyze"], "expected_output": "Code changes made", "context_files": ["src/main.py"], "tools_needed": ["edit_file"]}]}'
                            tool_calls = []

                    choices = [self.Choice()]

                return MockResponse()

            def chat_stream(self, messages, tools=None, on_content=None):
                class MockStreamResponse:
                    content = "I'll help you with this task."
                    has_tool_calls = False
                    tool_calls = []

                return MockStreamResponse()

            def format_assistant_message(self, response):
                return {"role": "assistant", "content": response.content}

        # Create agent
        client = MockClient()
        config = AsyncAgentConfig(max_turns=5, trust_mode=True)
        agent = AsyncAgent(client=client, context=context, config=config)

        # Test that planning is used by default
        print("  Testing: run() method with default parameters...")

        # Mock the _run_with_planning method to track if it's called
        planning_called = False

        async def mock_run_with_planning(task):
            nonlocal planning_called
            planning_called = True
            print(f"    ✓ Planning called for task: {task}")
            return "Task completed with planning"

        agent._run_with_planning = mock_run_with_planning

        # Run a task
        await agent.run("Add a new feature to the code")

        # Verify planning was used
        assert planning_called, "Planning should be used by default in async mode"
        print("  ✓ Planning was used by default")

        # Test with planning explicitly disabled
        print("  Testing: run() method with planning disabled...")
        planning_called = False

        await agent.run("Simple task", use_planning=False)

        assert not planning_called, "Planning should not be used when explicitly disabled"
        print("  ✓ Planning was correctly disabled when requested")

        print("✅ All tests passed!")


async def test_task_planner_async_optimization():
    """Test that task planner optimizes for async execution."""
    print("\n🧪 Testing task planner async optimization...")

    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)

        # Create mock client and registry
        class MockClient:
            model = "deepseek-chat"

            async def chat(self, messages):
                class MockResponse:
                    class Choice:
                        class Message:
                            content = '{"subtasks": [{"id": "task1", "description": "Task 1", "dependencies": [], "expected_output": "Output 1", "context_files": [], "tools_needed": ["read_file"]}, {"id": "task2", "description": "Task 2", "dependencies": [], "expected_output": "Output 2", "context_files": [], "tools_needed": ["read_file"]}, {"id": "task3", "description": "Task 3", "dependencies": ["task1", "task2"], "expected_output": "Output 3", "context_files": [], "tools_needed": ["edit_file"]}]}'
                            tool_calls = []

                    choices = [self.Choice()]

                return MockResponse()

        class MockRegistry:
            def get_schemas(self):
                return []

        # Create planner
        client = MockClient()
        registry = MockRegistry()
        planner = TaskPlanner(client, registry, str(tmpdir_path))

        # Create a plan
        plan = planner.create_task_plan("Test multiple independent tasks")

        # Check that we have independent tasks that could run in parallel
        independent_tasks = [t for t in plan.subtasks if not t.dependencies]
        print(f"  Found {len(independent_tasks)} independent tasks (can run in parallel)")

        assert len(independent_tasks) > 0, "Should have independent tasks for parallel execution"
        print("  ✓ Independent tasks identified for parallel execution")

        print("✅ Task planner async optimization test passed!")


def test_cli_entry_point():
    """Test that the CLI entry point is correctly configured."""
    print("\n🧪 Testing CLI entry point configuration...")

    # Check pyproject.toml
    import tomli

    with open("pyproject.toml", "rb") as f:
        config = tomli.load(f)

    scripts = config.get("project", {}).get("scripts", {})

    assert "lunvex-code" in scripts, "lunvex-code script should be defined"
    assert "lvc" in scripts, "lvc shortcut should be defined"

    entry_point = scripts["lunvex-code"]
    print(f"  Entry point: {entry_point}")

    # Verify it points to the new async main
    assert "main:main" in entry_point, "Should point to main.py (async version)"
    print("  ✓ CLI entry point correctly configured for async mode")

    print("✅ CLI entry point test passed!")


async def main():
    """Run all tests."""
    print("=" * 60)
    print("Testing Async Mode as Default with Subtasks")
    print("=" * 60)

    try:
        await test_async_planning_default()
        await test_task_planner_async_optimization()
        test_cli_entry_point()

        print("\n" + "=" * 60)
        print("🎉 All tests passed! Async mode with subtasks is now the default.")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
