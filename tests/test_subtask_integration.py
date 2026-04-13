#!/usr/bin/env python3
"""Integration test for subtask planning and execution."""

import asyncio
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

from lunvex_code.async_agent import AsyncAgent, AsyncAgentConfig
from lunvex_code.context import ProjectContext
from lunvex_code.llm import LunVexClient
from lunvex_code.task_planner import TaskPlanner
from lunvex_code.tools.base import ToolRegistry


async def test_subtask_planning_with_simple_task():
    """Test that simple tasks don't trigger subtask planning."""
    # Create a mock client
    client = Mock(spec=LunVexClient)

    # Mock response for simple task
    mock_response = Mock()
    mock_response.content = "I'll read the file for you."
    client.chat.return_value = mock_response

    # Create tool registry with mock tools
    tool_registry = Mock(spec=ToolRegistry)

    # Create context
    context = Mock(spec=ProjectContext)
    context.working_dir = "."

    # Create agent config
    config = AsyncAgentConfig(max_turns=10)

    # Create agent
    agent = AsyncAgent(client=client, context=context, config=config)
    agent.registry = tool_registry
    agent.history = Mock()
    agent.history.add_user_message = Mock()
    agent.history.messages = []

    # Mock the run_turn method to return a result
    agent.run_turn = Mock(return_value=asyncio.Future())
    agent.run_turn.return_value.set_result("File read successfully")

    # Test with simple task (should not use planning)
    simple_task = "Read file.txt"

    # Mock the _is_complex_task check
    with patch.object(TaskPlanner, "_is_complex_task", return_value=False):
        result = await agent.run(simple_task, use_planning=True)

    # Should have executed without planning
    assert result == "File read successfully"
    print("✓ Simple task executed without subtask planning")


async def test_subtask_planning_with_complex_task():
    """Test that complex tasks trigger subtask planning."""
    # Create a mock client
    client = Mock(spec=LunVexClient)

    # Create tool registry
    tool_registry = Mock(spec=ToolRegistry)

    # Create context
    context = Mock(spec=ProjectContext)
    context.working_dir = "."

    # Create agent config
    config = AsyncAgentConfig(max_turns=10)

    # Create agent
    agent = AsyncAgent(client=client, context=context, config=config)
    agent.registry = tool_registry
    agent.history = Mock()
    agent.history.add_user_message = Mock()
    agent.history.messages = []

    # Complex task that should trigger planning
    complex_task = (
        "First analyze the codebase, then refactor the main module, and finally run tests"
    )

    # Mock responses for planning
    mock_analysis_response = Mock()
    mock_analysis_response.content = '{"files_needed": ["main.py"], "tools_needed": ["read_file"], "phases": ["analyze", "refactor", "test"], "dependencies": {"refactor": ["analyze"], "test": ["refactor"]}}'

    mock_subtask_response = Mock()
    mock_subtask_response.content = """{
        "subtasks": [
            {
                "id": "analyze",
                "description": "Analyze the codebase",
                "dependencies": [],
                "expected_output": "Understanding of code structure",
                "context_files": ["main.py"],
                "tools_needed": ["read_file", "grep"]
            },
            {
                "id": "refactor",
                "description": "Refactor main module",
                "dependencies": ["analyze"],
                "expected_output": "Refactored code",
                "context_files": ["main.py"],
                "tools_needed": ["read_file", "edit_file"]
            },
            {
                "id": "test",
                "description": "Run tests",
                "dependencies": ["refactor"],
                "expected_output": "Test results",
                "context_files": [],
                "tools_needed": ["bash"]
            }
        ]
    }"""

    # Mock subtask execution responses
    mock_subtask1_response = Mock()
    mock_subtask1_response.content = "Analysis complete"

    mock_subtask2_response = Mock()
    mock_subtask2_response.content = "Refactoring complete"

    mock_subtask3_response = Mock()
    mock_subtask3_response.content = "Tests passed"

    # Set up mock responses
    client.chat.side_effect = [
        mock_analysis_response,  # For task analysis
        mock_subtask_response,  # For subtask generation
        mock_subtask1_response,  # For subtask 1 execution
        mock_subtask2_response,  # For subtask 2 execution
        mock_subtask3_response,  # For subtask 3 execution
    ]

    # Mock tool execution
    tool_registry.execute_tool = Mock(return_value=Mock(success=True, output="Tool executed"))

    # Mock agent's run method for subtask execution
    async def mock_agent_run(task, use_planning=False):
        # Return different responses based on task content
        if "Analyze" in task:
            return "Analysis complete"
        elif "Refactor" in task:
            return "Refactoring complete"
        elif "Run tests" in task:
            return "Tests passed"
        return "Task completed"

    agent.run = mock_agent_run

    # Test with complex task (should use planning)
    with patch.object(TaskPlanner, "_is_complex_task", return_value=True):
        # We need to mock the actual planning execution
        with patch.object(agent, "_run_with_planning") as mock_planning:
            mock_planning.return_value = "All subtasks completed successfully"

            result = await agent.run(complex_task, use_planning=True)

    # Should have used planning
    assert result == "All subtasks completed successfully"
    print("✓ Complex task triggered subtask planning")


def test_subtask_dependency_resolution():
    """Test that subtask dependencies are properly resolved."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)

        # Create test files
        file1 = tmp_path / "file1.py"
        file2 = tmp_path / "file2.py"

        file1.write_text("# File 1 content")
        file2.write_text("# File 2 content")

        # Create mock client
        client = Mock(spec=LunVexClient)

        # Create tool registry
        tool_registry = Mock(spec=ToolRegistry)

        # Create planner
        planner = TaskPlanner(client, tool_registry, str(tmp_path))

        # Test dependency analysis
        task = "Update file1.py and file2.py"

        # Mock analysis response
        mock_response = Mock()
        mock_response.content = """{
            "files_needed": ["file1.py", "file2.py"],
            "tools_needed": ["read_file", "edit_file"],
            "phases": ["update_file1", "update_file2"],
            "dependencies": {"update_file2": ["update_file1"]}
        }"""

        client.chat.return_value = mock_response

        analysis = planner._analyze_task_dependencies(task)

        assert "file1.py" in analysis["files_needed"]
        assert "file2.py" in analysis["files_needed"]
        assert "read_file" in analysis["tools_needed"]
        assert "edit_file" in analysis["tools_needed"]
        assert "update_file2" in analysis["dependencies"]["update_file1"]

        print("✓ Subtask dependency analysis works")


async def test_realistic_subtask_scenario():
    """Test a realistic scenario with file operations."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)

        # Create a simple Python project
        main_py = tmp_path / "main.py"
        test_py = tmp_path / "test_main.py"
        requirements_txt = tmp_path / "requirements.txt"

        main_py.write_text("""
def calculate_sum(a, b):
    return a + b

def main():
    result = calculate_sum(5, 3)
    print(f"Result: {result}")

if __name__ == "__main__":
    main()
""")

        test_py.write_text("""
import unittest

def test_calculate_sum():
    from main import calculate_sum
    assert calculate_sum(2, 3) == 5
    assert calculate_sum(-1, 1) == 0
    print("Tests passed!")

if __name__ == "__main__":
    test_calculate_sum()
""")

        requirements_txt.write_text("pytest\n")

        # Create a mock client for this test
        client = Mock(spec=LunVexClient)

        # Mock responses for a realistic refactoring task
        task = "Refactor the calculate_sum function to handle more operations and add proper tests"

        # Mock analysis response
        mock_analysis = Mock()
        mock_analysis.content = """{
            "files_needed": ["main.py", "test_main.py"],
            "tools_needed": ["read_file", "edit_file", "bash"],
            "phases": ["analyze", "refactor", "test"],
            "dependencies": {
                "refactor": ["analyze"],
                "test": ["refactor"]
            }
        }"""

        # Mock subtask generation
        mock_subtasks = Mock()
        mock_subtasks.content = """{
            "subtasks": [
                {
                    "id": "analyze-code",
                    "description": "Analyze current implementation",
                    "dependencies": [],
                    "expected_output": "Understanding of current code structure",
                    "context_files": ["main.py", "test_main.py"],
                    "tools_needed": ["read_file"]
                },
                {
                    "id": "refactor-function",
                    "description": "Refactor calculate_sum to handle more operations",
                    "dependencies": ["analyze-code"],
                    "expected_output": "Updated main.py with enhanced function",
                    "context_files": ["main.py"],
                    "tools_needed": ["read_file", "edit_file"]
                },
                {
                    "id": "update-tests",
                    "description": "Update tests for the refactored function",
                    "dependencies": ["refactor-function"],
                    "expected_output": "Updated test_main.py",
                    "context_files": ["test_main.py"],
                    "tools_needed": ["read_file", "edit_file"]
                },
                {
                    "id": "run-tests",
                    "description": "Run the updated tests",
                    "dependencies": ["update-tests"],
                    "expected_output": "Test execution results",
                    "context_files": [],
                    "tools_needed": ["bash"]
                }
            ]
        }"""

        client.chat.side_effect = [mock_analysis, mock_subtasks]

        # Create tool registry
        tool_registry = Mock(spec=ToolRegistry)

        # Create planner
        planner = TaskPlanner(client, tool_registry, str(tmp_path))

        # Create plan
        plan = planner.create_task_plan(task)

        # Verify plan
        assert plan.original_task == task
        assert len(plan.subtasks) == 4

        # Verify execution order respects dependencies
        assert plan.execution_order[0] == "analyze-code"
        assert plan.execution_order.index("refactor-function") > plan.execution_order.index(
            "analyze-code"
        )
        assert plan.execution_order.index("update-tests") > plan.execution_order.index(
            "refactor-function"
        )
        assert plan.execution_order.index("run-tests") > plan.execution_order.index("update-tests")

        print("✓ Realistic subtask scenario planned correctly")


async def main():
    """Run all integration tests."""
    print("Running subtask integration tests...\n")

    await test_subtask_planning_with_simple_task()
    await test_subtask_planning_with_complex_task()
    test_subtask_dependency_resolution()
    await test_realistic_subtask_scenario()

    print("\n✅ All subtask integration tests passed!")


if __name__ == "__main__":
    asyncio.run(main())
