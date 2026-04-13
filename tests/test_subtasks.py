#!/usr/bin/env python3
"""Test subtask planning and execution."""

import json
from unittest.mock import Mock

from lunvex_code.task_planner import Subtask, TaskPlan, TaskPlanner


def test_subtask_creation():
    """Test basic subtask creation."""
    subtask = Subtask(
        id="test-1",
        description="Test subtask",
        dependencies=[],
        expected_output="Test output",
        context_files=["file1.py", "file2.py"],
        tools_needed=["read_file", "edit_file"],
    )

    assert subtask.id == "test-1"
    assert subtask.description == "Test subtask"
    assert subtask.dependencies == []
    assert subtask.expected_output == "Test output"
    assert subtask.context_files == ["file1.py", "file2.py"]
    assert subtask.tools_needed == ["read_file", "edit_file"]
    assert subtask.completed is False
    assert subtask.result is None
    assert subtask.error is None


def test_task_plan_creation():
    """Test task plan creation."""
    subtask1 = Subtask(
        id="task1",
        description="First task",
        dependencies=[],
        expected_output="Output 1",
        context_files=[],
        tools_needed=[],
    )

    subtask2 = Subtask(
        id="task2",
        description="Second task",
        dependencies=["task1"],
        expected_output="Output 2",
        context_files=[],
        tools_needed=[],
    )

    plan = TaskPlan(
        original_task="Test complex task",
        subtasks=[subtask1, subtask2],
        execution_order=["task1", "task2"],
        current_context={"key": "value"},
    )

    assert plan.original_task == "Test complex task"
    assert len(plan.subtasks) == 2
    assert plan.execution_order == ["task1", "task2"]
    assert plan.current_context == {"key": "value"}
    assert plan.completed is False
    assert plan.final_result is None


def test_is_complex_task():
    """Test task complexity detection."""
    client = Mock()
    tool_registry = Mock()

    planner = TaskPlanner(client, tool_registry, ".")

    # Simple task - should not be complex
    simple_task = "Read file.txt"
    assert not planner._is_complex_task(simple_task)

    # Complex task with multiple steps
    complex_task = "First read file1.py, then edit file2.py, and finally run tests"
    assert planner._is_complex_task(complex_task)

    # Complex task with multiple files
    multi_file_task = "Update config.yaml and main.py files"
    assert planner._is_complex_task(multi_file_task)

    # Long task
    long_task = " ".join(["word"] * 60)  # 60 words
    assert planner._is_complex_task(long_task)


def test_calculate_execution_order():
    """Test topological sort for subtask execution order."""
    client = Mock()
    tool_registry = Mock()

    planner = TaskPlanner(client, tool_registry, ".")

    # Create subtasks with dependencies
    subtask1 = Subtask(
        id="analyze",
        description="Analyze",
        dependencies=[],
        expected_output="",
        context_files=[],
        tools_needed=[],
    )

    subtask2 = Subtask(
        id="implement",
        description="Implement",
        dependencies=["analyze"],
        expected_output="",
        context_files=[],
        tools_needed=[],
    )

    subtask3 = Subtask(
        id="test",
        description="Test",
        dependencies=["implement"],
        expected_output="",
        context_files=[],
        tools_needed=[],
    )

    subtask4 = Subtask(
        id="document",
        description="Document",
        dependencies=["implement"],
        expected_output="",
        context_files=[],
        tools_needed=[],
    )

    subtasks = [subtask1, subtask2, subtask3, subtask4]

    execution_order = planner._calculate_execution_order(subtasks)

    # Analyze should come first (no dependencies)
    assert execution_order[0] == "analyze"

    # Implement should come after analyze
    assert execution_order.index("implement") > execution_order.index("analyze")

    # Test and document should come after implement
    assert execution_order.index("test") > execution_order.index("implement")
    assert execution_order.index("document") > execution_order.index("implement")


def test_prepare_subtask_context():
    """Test context preparation for subtasks."""
    client = Mock()
    tool_registry = Mock()

    planner = TaskPlanner(client, tool_registry, ".")

    subtask = Subtask(
        id="test",
        description="Test task",
        dependencies=[],
        expected_output="",
        context_files=["file1.py", "file2.py"],
        tools_needed=[],
    )

    shared_context = {
        "previous_result": "Previous task completed successfully",
        "data": "Some data",
    }

    context = planner._prepare_subtask_context(subtask, shared_context)

    # Should contain shared context
    assert "Shared Context from Previous Subtasks" in context
    assert "previous_result" in context
    assert "data" in context

    # Should contain file context
    assert "Files to Consider" in context
    assert "file1.py" in context
    assert "file2.py" in context


def test_build_subtask_prompt():
    """Test subtask prompt building."""
    client = Mock()
    tool_registry = Mock()

    planner = TaskPlanner(client, tool_registry, ".")

    subtask = Subtask(
        id="test",
        description="Test task description",
        dependencies=[],
        expected_output="Expected output text",
        context_files=[],
        tools_needed=[],
    )

    context_summary = "Context from previous tasks"

    prompt = planner._build_subtask_prompt(subtask, context_summary)

    # Should contain subtask description
    assert "Test task description" in prompt

    # Should contain context
    assert "Context from previous tasks" in prompt

    # Should contain expected output
    assert "Expected output text" in prompt

    # Should contain instructions
    assert "Instructions" in prompt
    assert "Focus only on this specific subtask" in prompt


def test_update_context_from_result():
    """Test updating shared context from subtask result."""
    client = Mock()
    tool_registry = Mock()

    planner = TaskPlanner(client, tool_registry, ".")

    subtask = Subtask(
        id="test-task",
        description="Test description",
        dependencies=[],
        expected_output="",
        context_files=[],
        tools_needed=[],
    )

    shared_context = {}
    result = "This is the result of the subtask execution."

    planner._update_context_from_result(subtask, result, shared_context)

    # Should add subtask result to context
    assert "subtask_test-task" in shared_context
    context_entry = shared_context["subtask_test-task"]

    assert context_entry["description"] == "Test description"
    assert "result_summary" in context_entry
    assert context_entry["completed"] is False  # subtask.completed is still False


def test_generate_final_summary():
    """Test final summary generation."""
    client = Mock()
    tool_registry = Mock()

    planner = TaskPlanner(client, tool_registry, ".")

    # Create completed subtasks
    subtask1 = Subtask(
        id="task1",
        description="First task",
        dependencies=[],
        expected_output="",
        context_files=[],
        tools_needed=[],
    )
    subtask1.completed = True
    subtask1.result = "Result 1"

    subtask2 = Subtask(
        id="task2",
        description="Second task",
        dependencies=["task1"],
        expected_output="",
        context_files=[],
        tools_needed=[],
    )
    subtask2.completed = True
    subtask2.result = "Result 2"

    subtask3 = Subtask(
        id="task3",
        description="Failed task",
        dependencies=["task2"],
        expected_output="",
        context_files=[],
        tools_needed=[],
    )
    subtask3.completed = False
    subtask3.error = "Task failed"

    plan = TaskPlan(
        original_task="Test original task",
        subtasks=[subtask1, subtask2, subtask3],
        execution_order=["task1", "task2", "task3"],
        current_context={},
    )
    plan.completed = False  # Because task3 failed

    summary = planner._generate_final_summary(plan)

    # Should contain original task
    assert "Test original task" in summary

    # Should contain subtask summaries
    assert "First task" in summary
    assert "Second task" in summary
    assert "Failed task" in summary

    # Should show completion status
    assert "✅" in summary  # For completed tasks
    assert "❌" in summary  # For failed task

    # Should show error for failed task
    assert "Task failed" in summary


def test_create_task_plan_with_mock():
    """Test creating a task plan with mocked LLM."""
    client = Mock()
    tool_registry = Mock()

    # Mock LLM response for task analysis
    mock_analysis_response = Mock()
    mock_analysis_response.content = json.dumps(
        {
            "files_needed": ["main.py", "config.yaml"],
            "tools_needed": ["read_file", "edit_file"],
            "phases": ["analyze", "implement", "test"],
            "dependencies": {"implement": ["analyze"], "test": ["implement"]},
        }
    )

    # Mock LLM response for subtask generation
    mock_subtask_response = Mock()
    mock_subtask_response.content = json.dumps(
        {
            "subtasks": [
                {
                    "id": "analyze-1",
                    "description": "Analyze the requirements",
                    "dependencies": [],
                    "expected_output": "Understanding of what needs to be done",
                    "context_files": ["main.py"],
                    "tools_needed": ["read_file", "grep"],
                },
                {
                    "id": "implement-1",
                    "description": "Implement the changes",
                    "dependencies": ["analyze-1"],
                    "expected_output": "Code changes implemented",
                    "context_files": ["main.py", "config.yaml"],
                    "tools_needed": ["read_file", "edit_file"],
                },
                {
                    "id": "test-1",
                    "description": "Test the implementation",
                    "dependencies": ["implement-1"],
                    "expected_output": "Tests passing",
                    "context_files": ["main.py"],
                    "tools_needed": ["bash"],
                },
            ]
        }
    )

    client.chat.side_effect = [mock_analysis_response, mock_subtask_response]

    planner = TaskPlanner(client, tool_registry, ".")

    task = "Update the main.py file to add error handling and update config.yaml"
    plan = planner.create_task_plan(task)

    # Verify plan was created
    assert plan.original_task == task
    assert len(plan.subtasks) == 3
    assert len(plan.execution_order) == 3

    # Verify subtask properties
    subtask_ids = [st.id for st in plan.subtasks]
    assert "analyze-1" in subtask_ids
    assert "implement-1" in subtask_ids
    assert "test-1" in subtask_ids

    # Verify execution order respects dependencies
    assert plan.execution_order[0] == "analyze-1"
    assert plan.execution_order.index("implement-1") > plan.execution_order.index("analyze-1")
    assert plan.execution_order.index("test-1") > plan.execution_order.index("implement-1")


if __name__ == "__main__":
    print("Running subtask tests...")

    test_subtask_creation()
    print("✓ test_subtask_creation passed")

    test_task_plan_creation()
    print("✓ test_task_plan_creation passed")

    test_is_complex_task()
    print("✓ test_is_complex_task passed")

    test_calculate_execution_order()
    print("✓ test_calculate_execution_order passed")

    test_prepare_subtask_context()
    print("✓ test_prepare_subtask_context passed")

    test_build_subtask_prompt()
    print("✓ test_build_subtask_prompt passed")

    test_update_context_from_result()
    print("✓ test_update_context_from_result passed")

    test_generate_final_summary()
    print("✓ test_generate_final_summary passed")

    test_create_task_plan_with_mock()
    print("✓ test_create_task_plan_with_mock passed")

    print("\n✅ All subtask tests passed!")
