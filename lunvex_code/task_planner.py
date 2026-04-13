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
            r"\b(and|then|after|also|next|first|second|finally)\b",
            r"\b(multiple|several|various|different)\b",
            r"\.\.\.",  # Ellipsis indicating continuation
            r"[;:]",  # Multiple clauses
        ]

        task_lower = task.lower()

        # Count indicators
        indicator_count = sum(
            1 for pattern in complexity_indicators if re.search(pattern, task_lower, re.IGNORECASE)
        )

        # Check for multiple file mentions
        file_patterns = [
            r"\b(\w+\.(py|js|ts|java|cpp|h|go|rs|rb|php|md|txt|json|yaml|yml|toml))\b",
            r"in\s+(\w+/)*\w+",
            r"file[s]?\s+\w+",
        ]

        file_mentions = sum(
            len(re.findall(pattern, task_lower, re.IGNORECASE)) for pattern in file_patterns
        )

        # Length-based complexity
        word_count = len(task.split())

        # Task is complex if:
        # - Has multiple complexity indicators OR
        # - Mentions multiple files OR
        # - Is very long (> 50 words)
        return indicator_count >= 2 or file_mentions >= 2 or word_count > 50

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
            response = self.client.chat_complete([{"role": "user", "content": prompt}])
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
            response = self.client.chat_complete([{"role": "user", "content": prompt}])
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

        Args:
            plan: TaskPlan to execute
            agent: AsyncAgent instance to use for execution

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
