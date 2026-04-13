"""
Task planning and decomposition system for handling complex tasks.
Breaks down large tasks into manageable subtasks that fit within context limits.
"""

import json
import re
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from .llm import LunVexClient
from .tools.base import ToolRegistry


@dataclass
class Subtask:
    """A single subtask in the decomposition."""

    id: str
    description: str
    dependencies: List[str]  # IDs of tasks that must complete first
    expected_output: str
    context_files: List[str]  # Files needed for this subtask
    tools_needed: List[str]  # Tools required for this subtask
    completed: bool = False
    result: Optional[str] = None
    error: Optional[str] = None


@dataclass
class TaskPlan:
    """Complete plan for executing a complex task."""

    original_task: str
    subtasks: List[Subtask]
    execution_order: List[str]  # Order of subtask IDs
    current_context: Dict[str, Any] = field(default_factory=dict)  # Shared context between subtasks
    completed: bool = False
    final_result: Optional[str] = None


class TaskPlanner:
    """Planner that decomposes complex tasks into manageable subtasks."""

    def __init__(self, client: LunVexClient, tool_registry: ToolRegistry, working_dir: str = "."):
        self.client = client
        self.tool_registry = tool_registry
        self.working_dir = Path(working_dir).resolve()

    def _is_complex_task(self, task: str) -> bool:
        """
        Determine if a task is complex enough to require decomposition.

        Heuristics:
        - Contains multiple actions (and, then, after, also)
        - Mentions multiple files/modules
        - Has clear sequential steps
        - Is long and descriptive
        """
        # Check for task complexity indicators
        complexity_indicators = [
            r"\b(and|then|after|also|next|first|second|finally|lastly)\b",
            r"\b(multiple|several|various|different|both|each)\b",
            r"\.\.\.",  # Ellipsis indicating continuation
            r"[;:]",  # Multiple clauses
            r"\b(refactor|implement|update|create|add|remove|fix|debug|test|document)\s+.*\s+(and|then)\s+",
            r"\b(set up|configure|install|deploy|build)\s+",
        ]

        task_lower = task.lower()

        # Count indicators
        indicator_count = sum(
            1 for pattern in complexity_indicators if re.search(pattern, task_lower, re.IGNORECASE)
        )

        # Check for multiple file mentions
        file_patterns = [
            r"\b(\w+\.(py|js|ts|java|cpp|h|go|rs|rb|php|md|txt|json|yaml|yml|toml|ini|cfg|conf))\b",
            r"\b(file|module|package|library|dependency|config|configuration|script)\b",
            r"in\s+(\w+/)*\w+",
            r"\b(main|app|index|setup|config|test|spec)\.\w+\b",
        ]

        file_mentions = sum(
            len(re.findall(pattern, task_lower, re.IGNORECASE)) for pattern in file_patterns
        )

        # Length-based complexity
        word_count = len(task.split())

        # Task is complex if:
        # - Has multiple complexity indicators OR
        # - Mentions multiple files OR
        # - Is very long (> 30 words) OR
        # - Has clear multi-step structure
        has_multi_step = bool(
            re.search(r"\b(first|second|third|step\s+\d+|phase\s+\d+)\b", task_lower, re.IGNORECASE)
        )

        # For async mode, we want to be more aggressive with planning
        # to leverage parallel execution capabilities
        # Check if we're in async context by checking if called from async agent
        import inspect

        is_async_context = False
        try:
            # Check call stack to see if we're called from async code
            for frame_info in inspect.stack():
                if "async" in frame_info.function.lower() or "_async" in frame_info.function:
                    is_async_context = True
                    break
        except Exception:
            pass

        if is_async_context:
            # In async mode, be more aggressive with planning
            # Even moderately complex tasks benefit from decomposition
            return indicator_count >= 1 or file_mentions >= 2 or word_count > 25 or has_multi_step
        else:
            # In sync mode, use original thresholds
            return indicator_count >= 2 or file_mentions >= 2 or word_count > 30 or has_multi_step

    def _analyze_task_dependencies(self, task: str) -> Dict[str, Any]:
        """
        Analyze task to understand dependencies and requirements.
        """
        prompt = f"""
        Analyze this programming task and identify:
        1. What files are likely needed
        2. What tools might be required
        3. Logical steps or phases
        4. Dependencies between steps

        Task: {task}

        Respond in JSON format:
        {{
            "files_needed": ["list", "of", "likely", "files"],
            "tools_needed": ["list", "of", "tools"],
            "phases": ["phase1", "phase2", "phase3"],
            "dependencies": {{
                "phase2": ["phase1"],
                "phase3": ["phase1", "phase2"]
            }}
        }}
        """

        try:
            response = self.client.chat([{"role": "user", "content": prompt}])
            analysis = json.loads(response.content)
            return analysis
        except (json.JSONDecodeError, KeyError):
            # Fallback analysis
            return {
                "files_needed": [],
                "tools_needed": ["read_file", "edit_file"],
                "phases": ["analysis", "implementation", "verification"],
                "dependencies": {
                    "implementation": ["analysis"],
                    "verification": ["implementation"],
                },
            }

    def create_task_plan(self, task: str) -> TaskPlan:
        """
        Create a detailed plan for executing a complex task.
        """
        # Analyze the task
        analysis = self._analyze_task_dependencies(task)

        # Generate subtasks using LLM
        subtasks = self._generate_subtasks(task, analysis)

        # Determine execution order (topological sort based on dependencies)
        execution_order = self._calculate_execution_order(subtasks)

        return TaskPlan(
            original_task=task,
            subtasks=subtasks,
            execution_order=execution_order,
            current_context={},
        )

    def _generate_subtasks(self, task: str, analysis: Dict[str, Any]) -> List[Subtask]:
        """
        Generate subtasks for the given task.
        """
        prompt = f"""
        Break down this programming task into manageable subtasks.

        Original task: {task}

        Analysis:
        - Files likely needed: {analysis.get("files_needed", [])}
        - Tools needed: {analysis.get("tools_needed", [])}
        - Phases: {analysis.get("phases", [])}

        Create 3-7 subtasks that:
        1. Each can be completed within reasonable context window
        2. Have clear dependencies
        3. Have specific expected outputs
        4. List specific files needed

        Respond in JSON format:
        {{
            "subtasks": [
                {{
                    "id": "unique_id_1",
                    "description": "Clear description of what to do",
                    "dependencies": ["id_of_previous_task"],
                    "expected_output": "What should be produced",
                    "context_files": ["file1.py", "file2.js"],
                    "tools_needed": ["read_file", "edit_file"]
                }},
                ...
            ]
        }}
        """

        try:
            response = self.client.chat([{"role": "user", "content": prompt}])
            subtask_data = json.loads(response.content)

            subtasks = []
            for subtask_dict in subtask_data.get("subtasks", []):
                subtask = Subtask(
                    id=subtask_dict.get("id", str(uuid.uuid4())[:8]),
                    description=subtask_dict["description"],
                    dependencies=subtask_dict.get("dependencies", []),
                    expected_output=subtask_dict["expected_output"],
                    context_files=subtask_dict.get("context_files", []),
                    tools_needed=subtask_dict.get("tools_needed", ["read_file", "edit_file"]),
                )
                subtasks.append(subtask)

            return subtasks

        except (json.JSONDecodeError, KeyError):
            # Fallback: create simple subtasks
            return [
                Subtask(
                    id="analyze",
                    description=f"Analyze the task: {task}",
                    dependencies=[],
                    expected_output="Understanding of requirements and approach",
                    context_files=[],
                    tools_needed=["read_file", "grep"],
                ),
                Subtask(
                    id="implement",
                    description="Implement the required changes",
                    dependencies=["analyze"],
                    expected_output="Code changes implemented",
                    context_files=analysis.get("files_needed", []),
                    tools_needed=["read_file", "edit_file", "write_file"],
                ),
                Subtask(
                    id="verify",
                    description="Verify the implementation",
                    dependencies=["implement"],
                    expected_output="Verification that changes work correctly",
                    context_files=analysis.get("files_needed", []),
                    tools_needed=["bash", "read_file"],
                ),
            ]

    def _calculate_execution_order(self, subtasks: List[Subtask]) -> List[str]:
        """
        Calculate topological order for subtask execution.
        """
        # Build dependency graph
        graph = {subtask.id: set(subtask.dependencies) for subtask in subtasks}
        visited = set()
        temp_visited = set()
        order = []

        def visit(node_id: str):
            if node_id in temp_visited:
                raise ValueError(f"Circular dependency detected involving {node_id}")
            if node_id in visited:
                return

            temp_visited.add(node_id)

            # Visit dependencies first
            for dep in graph.get(node_id, set()):
                visit(dep)

            temp_visited.remove(node_id)
            visited.add(node_id)
            order.append(node_id)

        # Visit all nodes
        for subtask in subtasks:
            if subtask.id not in visited:
                visit(subtask.id)

        return order

    def execute_plan(self, plan: TaskPlan, agent) -> str:
        """
        Execute a task plan using the provided agent.

        Args:
            plan: TaskPlan to execute
            agent: Agent instance (sync or async) to use for execution

        Returns:
            Final result of the task
        """
        from . import ui

        ui.print_info(f"📋 Executing task plan with {len(plan.subtasks)} subtasks")

        # Create subtask lookup
        subtask_map = {subtask.id: subtask for subtask in plan.subtasks}

        # Execute in order
        for subtask_id in plan.execution_order:
            subtask = subtask_map[subtask_id]

            # Check if all dependencies are completed
            for dep_id in subtask.dependencies:
                dep = subtask_map.get(dep_id)
                if not dep or not dep.completed:
                    ui.print_error(
                        f"Cannot execute {subtask_id}: dependency {dep_id} not completed"
                    )
                    plan.completed = False
                    return f"Task failed: dependency {dep_id} not completed"

            # Execute subtask
            ui.print_section(f"▶️ Executing subtask: {subtask.description}")

            # Prepare context for this subtask
            context_summary = self._prepare_subtask_context(subtask, plan.current_context)

            # Build subtask prompt with context
            subtask_prompt = self._build_subtask_prompt(subtask, context_summary)

            try:
                # Execute using agent
                if hasattr(agent, "run"):  # Sync agent
                    result = agent.run(subtask_prompt, use_planning=False)  # Don't plan subtasks
                elif hasattr(agent, "arun"):  # Async agent
                    import asyncio

                    result = asyncio.run(agent.arun(subtask_prompt, use_planning=False))
                else:
                    raise ValueError("Agent must have run() or arun() method")

                # Update subtask status
                subtask.completed = True
                subtask.result = result

                # Update shared context
                self._update_context_from_result(subtask, result, plan.current_context)

                ui.print_success(f"✅ Subtask {subtask_id} completed")

            except Exception as e:
                subtask.completed = False
                subtask.error = str(e)
                ui.print_error(f"❌ Subtask {subtask_id} failed: {e}")

                # Option: continue with other subtasks or abort
                # For now, abort on failure
                plan.completed = False
                return f"Task failed at subtask {subtask_id}: {e}"

        # All subtasks completed
        plan.completed = True

        # Generate final summary
        final_result = self._generate_final_summary(plan)
        plan.final_result = final_result

        return final_result

    async def execute_plan_async(self, plan: TaskPlan, agent) -> str:
        """
        Execute a task plan asynchronously using the provided agent.

        In async mode, independent subtasks can be executed in parallel for better performance.

        Args:
            plan: TaskPlan to execute
            agent: AsyncAgent instance to use for execution

        Returns:
            Final result of the task
        """
        from . import ui

        ui.print_info(f"📋 Executing task plan with {len(plan.subtasks)} subtasks")
        ui.print_info("⚡ Async mode: Independent subtasks may execute in parallel")

        # Create subtask lookup
        subtask_map = {subtask.id: subtask for subtask in plan.subtasks}

        # Track completed subtasks
        completed_subtasks = set()

        # Function to check if a subtask is ready to execute
        def is_subtask_ready(subtask_id: str) -> bool:
            subtask = subtask_map[subtask_id]
            # Check if all dependencies are completed
            for dep_id in subtask.dependencies:
                if dep_id not in completed_subtasks:
                    return False
            return True

        # Function to execute a single subtask
        async def execute_single_subtask(subtask_id: str) -> tuple[str, bool, str]:
            """Execute a single subtask and return (subtask_id, success, result/error)."""
            subtask = subtask_map[subtask_id]

            try:
                ui.print_section(f"▶️ Executing subtask: {subtask.description}")

                # Prepare context for this subtask
                context_summary = self._prepare_subtask_context(subtask, plan.current_context)

                # Build subtask prompt with context
                subtask_prompt = self._build_subtask_prompt(subtask, context_summary)

                # Execute using async agent
                if hasattr(agent, "arun"):
                    result = await agent.arun(subtask_prompt, use_planning=False)
                elif hasattr(agent, "run"):
                    # Fallback to sync if async not available
                    result = agent.run(subtask_prompt, use_planning=False)
                else:
                    raise ValueError("Agent must have arun() or run() method")

                # Update subtask status
                subtask.completed = True
                subtask.result = result

                # Update shared context
                self._update_context_from_result(subtask, result, plan.current_context)

                ui.print_success(f"✅ Subtask {subtask_id} completed")
                return (subtask_id, True, result)

            except Exception as e:
                subtask.completed = False
                subtask.error = str(e)
                ui.print_error(f"❌ Subtask {subtask_id} failed: {e}")
                return (subtask_id, False, str(e))

        # Execute subtasks with dependency-aware parallel execution
        import asyncio

        # Create a queue of subtasks to execute
        pending_subtasks = set(plan.execution_order)
        executing_tasks = {}

        while pending_subtasks or executing_tasks:
            # Find subtasks that are ready to execute
            ready_subtasks = [
                subtask_id for subtask_id in pending_subtasks if is_subtask_ready(subtask_id)
            ]

            # Start executing ready subtasks (up to 3 in parallel)
            for subtask_id in ready_subtasks[:3]:  # Limit parallel execution
                if subtask_id not in executing_tasks:
                    task = asyncio.create_task(execute_single_subtask(subtask_id))
                    executing_tasks[subtask_id] = task
                    pending_subtasks.remove(subtask_id)

            # Wait for at least one task to complete if we have tasks running
            if executing_tasks:
                done, _ = await asyncio.wait(
                    executing_tasks.values(), return_when=asyncio.FIRST_COMPLETED
                )

                # Process completed tasks
                for done_task in done:
                    # Find which subtask this task was for
                    for subtask_id, task in executing_tasks.items():
                        if task is done_task:
                            subtask_id_result, success, result = await task

                            if not success:
                                # Task failed - abort execution
                                plan.completed = False
                                return f"Task failed at subtask {subtask_id_result}: {result}"

                            # Mark subtask as completed
                            completed_subtasks.add(subtask_id_result)
                            del executing_tasks[subtask_id_result]
                            break

            # If no tasks are executing but we still have pending tasks,
            # there might be a circular dependency or logic error
            if not executing_tasks and pending_subtasks:
                # Check for circular dependencies
                for subtask_id in pending_subtasks:
                    if not is_subtask_ready(subtask_id):
                        ui.print_error("❌ Circular dependency or logic error detected")
                        ui.print_error(
                            f"   Subtask {subtask_id} cannot execute - dependencies not met"
                        )
                        plan.completed = False
                        return "Task failed: circular dependency or logic error"

                # If we get here, all pending subtasks should be ready
                # Continue to next iteration to start executing them

        # All subtasks completed
        plan.completed = True

        # Generate final summary
        final_result = self._generate_final_summary(plan)
        plan.final_result = final_result

        return final_result

    def _prepare_subtask_context(self, subtask: Subtask, shared_context: Dict[str, Any]) -> str:
        """
        Prepare context information for a subtask.
        """
        context_parts = []

        # Add shared context
        if shared_context:
            context_parts.append("## Shared Context from Previous Subtasks")
            for key, value in shared_context.items():
                if isinstance(value, str) and len(value) < 500:  # Don't include huge context
                    context_parts.append(f"- {key}: {value}")

        # Add file context
        if subtask.context_files:
            context_parts.append("\n## Files to Consider")
            for file in subtask.context_files:
                context_parts.append(f"- {file}")

        return "\n".join(context_parts)

    def _build_subtask_prompt(self, subtask: Subtask, context_summary: str) -> str:
        """
        Build the prompt for executing a subtask.
        """
        return f"""
        ## Subtask: {subtask.description}

        {context_summary}

        ## Expected Output
        {subtask.expected_output}

        ## Instructions
        1. Focus only on this specific subtask
        2. Use the provided context from previous subtasks
        3. Produce the expected output
        4. Be concise and specific

        Begin the subtask execution.
        """

    def _update_context_from_result(
        self, subtask: Subtask, result: str, shared_context: Dict[str, Any]
    ):
        """
        Update shared context with results from completed subtask.
        """
        # Extract key information from result
        key = f"subtask_{subtask.id}"

        # Truncate very long results
        if len(result) > 1000:
            summary = result[:500] + "...\n[truncated]" + result[-500:]
        else:
            summary = result

        shared_context[key] = {
            "description": subtask.description,
            "result_summary": summary,
            "completed": subtask.completed,
        }

    def _generate_final_summary(self, plan: TaskPlan) -> str:
        """
        Generate a final summary of the completed task.
        """
        summary_parts = []
        summary_parts.append("# Task Execution Summary")
        summary_parts.append(f"**Original Task:** {plan.original_task}")
        summary_parts.append("")

        # Summary of subtasks
        summary_parts.append("## Subtasks Completed")
        for subtask in plan.subtasks:
            status = "✅" if subtask.completed else "❌"
            summary_parts.append(f"{status} **{subtask.id}**: {subtask.description}")
            if subtask.error:
                summary_parts.append(f"   Error: {subtask.error}")

        # Final result
        summary_parts.append("\n## Final Result")
        summary_parts.append(
            "All subtasks completed successfully." if plan.completed else "Task failed to complete."
        )

        return "\n".join(summary_parts)


def create_task_planner(
    client: LunVexClient, tool_registry: ToolRegistry, working_dir: str = "."
) -> TaskPlanner:
    """Create a task planner instance."""
    return TaskPlanner(client, tool_registry, working_dir)
