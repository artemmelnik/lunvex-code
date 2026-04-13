#!/usr/bin/env python3
"""Simple test for task planner."""

import sys
sys.path.insert(0, '.')

from lunvex_code.task_planner import TaskPlanner, Subtask, TaskPlan, create_task_planner
from lunvex_code.llm import LunVexClient
from lunvex_code.tools.base import ToolRegistry
from unittest.mock import Mock
import json

print("🧪 Testing Task Planner System")

# Test 1: Basic subtask creation
print("\n1. Testing subtask creation...")
subtask = Subtask(
    id="test_id",
    description="Test description",
    dependencies=["dep1", "dep2"],
    expected_output="Expected output",
    context_files=["file1.py", "file2.py"],
    tools_needed=["read_file", "edit_file"]
)

assert subtask.id == "test_id"
assert subtask.description == "Test description"
assert subtask.dependencies == ["dep1", "dep2"]
assert subtask.expected_output == "Expected output"
assert subtask.context_files == ["file1.py", "file2.py"]
assert subtask.tools_needed == ["read_file", "edit_file"]
assert not subtask.completed
assert subtask.result is None
assert subtask.error is None
print("✅ Subtask creation passed")

# Test 2: Task plan creation
print("\n2. Testing task plan creation...")
subtasks = [
    Subtask(id="task1", description="Task 1", dependencies=[], 
            expected_output="Output 1", context_files=[], tools_needed=[]),
    Subtask(id="task2", description="Task 2", dependencies=["task1"], 
            expected_output="Output 2", context_files=[], tools_needed=[]),
]

plan = TaskPlan(
    original_task="Test task",
    subtasks=subtasks,
    execution_order=["task1", "task2"],
    current_context={"key": "value"}
)

assert plan.original_task == "Test task"
assert len(plan.subtasks) == 2
assert plan.execution_order == ["task1", "task2"]
assert plan.current_context == {"key": "value"}
assert not plan.completed
assert plan.final_result is None
print("✅ Task plan creation passed")

# Test 3: Task complexity detection
print("\n3. Testing task complexity detection...")
mock_client = Mock(spec=LunVexClient)
mock_registry = Mock(spec=ToolRegistry)
planner = TaskPlanner(mock_client, mock_registry, ".")

# Complex task (multiple actions)
complex_task = "First read the auth.py file, then fix the bug in user authentication, and finally run tests"
assert planner._is_complex_task(complex_task)

# Simple task
simple_task = "Read the README.md file"
assert not planner._is_complex_task(simple_task)

# Complex task with multiple files
multi_file_task = "Update config.py and settings.py to use new environment variables"
assert planner._is_complex_task(multi_file_task)

# Very long task
long_task = " ".join(["word"] * 60)  # 60 words
assert planner._is_complex_task(long_task)
print("✅ Task complexity detection passed")

# Test 4: Dependency analysis
print("\n4. Testing dependency analysis...")
# Mock LLM response
mock_response = Mock()
mock_response.content = json.dumps({
    "files_needed": ["auth.py", "config.py"],
    "tools_needed": ["read_file", "edit_file"],
    "phases": ["analysis", "implementation"],
    "dependencies": {"implementation": ["analysis"]}
})
mock_client.chat_complete.return_value = mock_response

task = "Fix authentication bug"
analysis = planner._analyze_task_dependencies(task)

assert "files_needed" in analysis
assert "tools_needed" in analysis
assert "phases" in analysis
assert "dependencies" in analysis
assert analysis["files_needed"] == ["auth.py", "config.py"]
print("✅ Dependency analysis passed")

# Test 5: Execution order calculation
print("\n5. Testing execution order calculation...")
subtasks_for_order = [
    Subtask(id="task1", description="Task 1", dependencies=[], 
            expected_output="", context_files=[], tools_needed=[]),
    Subtask(id="task2", description="Task 2", dependencies=["task1"], 
            expected_output="", context_files=[], tools_needed=[]),
    Subtask(id="task3", description="Task 3", dependencies=["task2"], 
            expected_output="", context_files=[], tools_needed=[]),
]

order = planner._calculate_execution_order(subtasks_for_order)
assert order == ["task1", "task2", "task3"]
print("✅ Execution order calculation passed")

# Test 6: Context preparation
print("\n6. Testing context preparation...")
subtask_for_context = Subtask(
    id="test_task",
    description="Test task",
    dependencies=[],
    expected_output="Test output",
    context_files=["file1.py", "file2.py"],
    tools_needed=[]
)

shared_context = {
    "previous_result": "Previous task completed successfully",
    "config": {"key": "value"}
}

context = planner._prepare_subtask_context(subtask_for_context, shared_context)
assert "Shared Context from Previous Subtasks" in context
assert "Files to Consider" in context
assert "file1.py" in context
assert "file2.py" in context
print("✅ Context preparation passed")

# Test 7: Prompt building
print("\n7. Testing prompt building...")
subtask_for_prompt = Subtask(
    id="test_task",
    description="Fix the authentication bug",
    dependencies=[],
    expected_output="Working authentication with proper error handling",
    context_files=["auth.py"],
    tools_needed=["read_file", "edit_file"]
)

context_summary = "## Shared Context\nPrevious: User model updated\n## Files\n- auth.py"
prompt = planner._build_subtask_prompt(subtask_for_prompt, context_summary)

assert "Subtask: Fix the authentication bug" in prompt
assert "Expected Output" in prompt
assert "Working authentication" in prompt
assert "Instructions" in prompt
assert "auth.py" in prompt
print("✅ Prompt building passed")

# Test 8: Context updating
print("\n8. Testing context updating...")
subtask_for_update = Subtask(
    id="auth_fix",
    description="Fix authentication",
    dependencies=[],
    expected_output="",
    context_files=[],
    tools_needed=[]
)

shared_context_for_update = {}
result = "Authentication fixed. Added JWT token validation and error handling."

planner._update_context_from_result(subtask_for_update, result, shared_context_for_update)

assert "subtask_auth_fix" in shared_context_for_update
context_entry = shared_context_for_update["subtask_auth_fix"]
assert context_entry["description"] == "Fix authentication"
assert "Authentication fixed" in context_entry["result_summary"]
assert context_entry["completed"] is True
print("✅ Context updating passed")

# Test 9: Factory function
print("\n9. Testing factory function...")
planner_from_factory = create_task_planner(mock_client, mock_registry, ".")
assert isinstance(planner_from_factory, TaskPlanner)
assert planner_from_factory.client == mock_client
assert planner_from_factory.tool_registry == mock_registry
print("✅ Factory function passed")

print("\n🎉 All tests passed successfully!")
print("\n📋 Summary:")
print(f"  - Created subtask: {subtask.id}")
print(f"  - Created task plan with {len(plan.subtasks)} subtasks")
print(f"  - Detected complex tasks correctly")
print(f"  - Analyzed dependencies for: {task}")
print(f"  - Calculated execution order: {order}")
print(f"  - Prepared context with {len(subtask_for_context.context_files)} files")
print(f"  - Built prompt for: {subtask_for_prompt.description}")
print(f"  - Updated context with result")
print(f"  - Created planner via factory function")