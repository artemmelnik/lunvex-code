#!/usr/bin/env python3
"""
Example demonstrating the task planning system in LunVex Code.

This example shows how complex tasks are automatically decomposed
into manageable subtasks with proper dependencies.
"""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from lunvex_code.agent import create_agent
from lunvex_code.task_planner import create_task_planner
from lunvex_code.llm import LunVexClient
from lunvex_code.tools.base import ToolRegistry
from unittest.mock import Mock


def demonstrate_task_planning():
    """Demonstrate task planning with a mock agent."""
    
    print("🎯 Task Planning System Demonstration")
    print("=" * 50)
    
    # Create mock components for demonstration
    mock_client = Mock(spec=LunVexClient)
    mock_registry = Mock(spec=ToolRegistry)
    
    # Create task planner
    planner = create_task_planner(mock_client, mock_registry, ".")
    
    # Example 1: Complex task that needs planning
    print("\n📋 Example 1: Complex Refactoring Task")
    print("-" * 40)
    
    complex_task = """
    First, analyze the current authentication system in auth.py to identify 
    security vulnerabilities. Then, fix any issues found and update the code 
    to use JWT tokens instead of session-based authentication. Finally, 
    update the user model in models.py to support two-factor authentication 
    and write comprehensive tests for all new functionality.
    """
    
    print(f"Original task: {complex_task[:100]}...")
    
    # Check if task is complex
    is_complex = planner._is_complex_task(complex_task)
    print(f"Task is complex: {is_complex}")
    
    if is_complex:
        print("✅ This task would be automatically decomposed into subtasks")
    
    # Example 2: Simple task that doesn't need planning
    print("\n📋 Example 2: Simple File Operation")
    print("-" * 40)
    
    simple_task = "Read the contents of README.md and summarize it"
    
    print(f"Original task: {simple_task}")
    
    is_complex = planner._is_complex_task(simple_task)
    print(f"Task is complex: {is_complex}")
    
    if not is_complex:
        print("✅ This task would be executed directly without planning")
    
    # Example 3: Task with multiple file operations
    print("\n📋 Example 3: Multi-file Update")
    print("-" * 40)
    
    multi_file_task = """
    Update config.py to use environment variables instead of hardcoded values,
    then update settings.py to read from the new config, and finally update
    all import statements in the codebase to use the new configuration system.
    """
    
    print(f"Original task: {multi_file_task[:120]}...")
    
    is_complex = planner._is_complex_task(multi_file_task)
    print(f"Task is complex: {is_complex}")
    
    if is_complex:
        print("✅ This task would be broken down into:")
        print("   1. Analyze current config system")
        print("   2. Update config.py")
        print("   3. Update settings.py")
        print("   4. Update import statements")
        print("   5. Verify all changes work together")
    
    # Example 4: Demonstration of subtask creation
    print("\n📋 Example 4: Subtask Structure")
    print("-" * 40)
    
    from lunvex_code.task_planner import Subtask
    
    # Create example subtasks
    subtasks = [
        Subtask(
            id="analyze",
            description="Analyze current authentication system",
            dependencies=[],
            expected_output="List of security vulnerabilities and improvement suggestions",
            context_files=["auth.py"],
            tools_needed=["read_file", "grep"]
        ),
        Subtask(
            id="implement_jwt",
            description="Implement JWT token authentication",
            dependencies=["analyze"],
            expected_output="JWT authentication working with token generation and validation",
            context_files=["auth.py", "config.py"],
            tools_needed=["edit_file", "write_file"]
        ),
        Subtask(
            id="add_2fa",
            description="Add two-factor authentication support",
            dependencies=["implement_jwt"],
            expected_output="User model updated with 2FA fields and methods",
            context_files=["models.py"],
            tools_needed=["edit_file"]
        ),
        Subtask(
            id="write_tests",
            description="Write tests for new authentication features",
            dependencies=["implement_jwt", "add_2fa"],
            expected_output="Comprehensive test suite covering JWT and 2FA",
            context_files=["tests/test_auth.py", "tests/test_models.py"],
            tools_needed=["write_file", "bash"]
        )
    ]
    
    print("Example subtasks for authentication refactoring:")
    for i, subtask in enumerate(subtasks, 1):
        print(f"\n{i}. {subtask.id}: {subtask.description}")
        print(f"   Dependencies: {', '.join(subtask.dependencies) if subtask.dependencies else 'none'}")
        print(f"   Files: {', '.join(subtask.context_files)}")
        print(f"   Tools: {', '.join(subtask.tools_needed)}")
    
    # Example 5: Execution order calculation
    print("\n📋 Example 5: Execution Order")
    print("-" * 40)
    
    execution_order = planner._calculate_execution_order(subtasks)
    print("Optimal execution order based on dependencies:")
    for i, task_id in enumerate(execution_order, 1):
        subtask = next(st for st in subtasks if st.id == task_id)
        print(f"{i}. {task_id}: {subtask.description}")
    
    # Example 6: Context sharing
    print("\n📋 Example 6: Context Sharing Between Subtasks")
    print("-" * 40)
    
    shared_context = {}
    
    # Simulate completing first subtask
    subtask1 = subtasks[0]
    result1 = "Analysis complete. Found 3 security vulnerabilities: 1) Weak password hashing, 2) No rate limiting, 3) Session fixation risk."
    
    planner._update_context_from_result(subtask1, result1, shared_context)
    print("After completing 'analyze' subtask:")
    print(f"Shared context keys: {list(shared_context.keys())}")
    
    # Prepare context for next subtask
    context_summary = planner._prepare_subtask_context(subtasks[1], shared_context)
    print("\nContext prepared for 'implement_jwt' subtask:")
    print(context_summary[:200] + "..." if len(context_summary) > 200 else context_summary)
    
    print("\n🎉 Demonstration Complete!")
    print("\nKey Takeaways:")
    print("1. Complex tasks are automatically decomposed into manageable subtasks")
    print("2. Dependencies ensure logical execution order")
    print("3. Context is shared between subtasks to maintain continuity")
    print("4. Each subtask has clear expected outputs and required tools")
    print("5. The system handles both simple and complex tasks appropriately")


def demonstrate_cli_usage():
    """Demonstrate CLI usage with task planning."""
    
    print("\n🖥️  CLI Usage Examples")
    print("=" * 50)
    
    print("\n1. Complex task with automatic planning (default):")
    print('   lunvex-code run "Refactor authentication system to use JWT tokens and add 2FA support"')
    print("   → System will automatically create and execute a task plan")
    
    print("\n2. Simple task without planning:")
    print('   lunvex-code run --no-planning "Read config.py"')
    print("   → Task executed directly without decomposition")
    
    print("\n3. Async execution with planning:")
    print('   lunvex-code run-async "Migrate database schema and update all models"')
    print("   → Async agent with task planning for complex migration")
    
    print("\n4. Trust mode with planning:")
    print('   lunvex-code run --trust --no-planning "Update version in package.json"')
    print("   → Simple task with auto-approval for safe operations")


if __name__ == "__main__":
    demonstrate_task_planning()
    demonstrate_cli_usage()
    
    print("\n" + "=" * 50)
    print("📚 For more information, see:")
    print("   - TASK_PLANNING.md - Detailed documentation")
    print("   - README.md - Quick start guide")
    print("   - tests/test_task_planner.py - Test cases")
    print("\n🚀 Start using task planning today for complex coding tasks!")