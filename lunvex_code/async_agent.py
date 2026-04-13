"""Async agent implementation."""

from dataclasses import dataclass
from typing import Any

from . import ui
from .context import ProjectContext, build_system_prompt
from .conversation import ConversationHistory
from .llm import LunVexClient, ToolCall
from .permissions import PermissionLevel, PermissionManager, PermissionRequest
from .tools.async_base import AsyncTool
from .tools.base import ToolRegistry


@dataclass
class AsyncAgentConfig:
    """Configuration for the async agent."""

    max_turns: int = 50
    trust_mode: bool = False
    yolo_mode: bool = (
        False  # Skip all permission prompts (like Claude Code's --dangerously-skip-permissions)
    )
    verbose: bool = False


class AsyncAgent:
    """Async agent that orchestrates the LLM and tools."""

    def __init__(
        self,
        client: LunVexClient,
        context: ProjectContext,
        config: AsyncAgentConfig | None = None,
        registry: ToolRegistry | None = None,
    ):
        self.client = client
        self.context = context
        self.config = config or AsyncAgentConfig()
        self.registry = registry or self._create_default_registry()
        self.permissions = PermissionManager(
            trust_mode=self.config.trust_mode,
            yolo_mode=self.config.yolo_mode,
        )

        # Build system prompt
        self.system_prompt = build_system_prompt(context)

        # Initialize conversation
        self.history = ConversationHistory(system_prompt=self.system_prompt)

    def _create_default_registry(self) -> ToolRegistry:
        """Create default async tool registry."""
        from .tools.async_bash_tool import AsyncBashTool

        # Import async tools
        from .tools.async_file_tools import AsyncEditFileTool, AsyncReadFileTool, AsyncWriteFileTool
        from .tools.async_search_tools import AsyncGlobTool, AsyncGrepTool
        from .tools.async_web_tools import AsyncFetchURLTool
        from .tools.base import ToolRegistry
        from .tools.git_tools import (
            GitAddTool,
            GitBranchTool,
            GitCheckoutTool,
            GitCommitTool,
            GitDiffTool,
            GitFetchTool,
            GitLogTool,
            GitMergeTool,
            GitPullTool,
            GitPushTool,
            GitShowTool,
            GitStashTool,
            GitStatusTool,
        )

        registry = ToolRegistry()

        # Register async tools
        registry.register(AsyncReadFileTool())
        registry.register(AsyncWriteFileTool())
        registry.register(AsyncEditFileTool())
        registry.register(AsyncGlobTool())
        registry.register(AsyncGrepTool())
        registry.register(AsyncBashTool())
        registry.register(AsyncFetchURLTool())

        # Register sync Git tools (they're fast enough)
        registry.register(GitStatusTool())
        registry.register(GitDiffTool())
        registry.register(GitLogTool())
        registry.register(GitShowTool())
        registry.register(GitBranchTool())
        registry.register(GitAddTool())
        registry.register(GitCommitTool())
        registry.register(GitPushTool())
        registry.register(GitPullTool())
        registry.register(GitStashTool())
        registry.register(GitCheckoutTool())
        registry.register(GitMergeTool())
        registry.register(GitFetchTool())

        return registry

    def _get_permission(self, request: PermissionRequest) -> bool:
        """
        Check permission for a tool call, prompting user if needed.

        Returns True if allowed, False if denied.
        """
        if request.level == PermissionLevel.AUTO:
            return True

        if request.level == PermissionLevel.DENY:
            if request.reason:
                ui.print_error(f"Blocked: {request.reason}")
            else:
                ui.print_error("This operation is blocked for safety.")
            return False

        # ASK level - prompt user
        prompt = self.permissions.format_permission_prompt(request)
        choice = ui.ask_permission(prompt)

        if choice == "y":
            return True
        elif choice == "always":
            # Add to session allowlist
            tool_name = request.tool_name
            if tool_name == "bash":
                cmd = request.tool_input.get("command", "")
                # Extract command prefix for allowlist
                cmd_prefix = cmd.split()[0] if cmd else ""
                if cmd_prefix:
                    self.permissions.add_to_allowlist(f"bash({cmd_prefix}:*)")
                    ui.print_info(f"Added 'bash({cmd_prefix}:*)' to session allowlist")
            elif tool_name in ("write_file", "edit_file"):
                # "always" for file modifications should apply at the tool level,
                # not just to the exact file path that happened to trigger the prompt.
                pattern = f"{tool_name}(*)"
                self.permissions.add_to_allowlist(pattern)
                ui.print_info(f"Added '{pattern}' to session allowlist")
            return True
        else:
            return False

    async def _execute_tool(self, tool_call: ToolCall) -> str:
        """Execute a single tool call asynchronously and return the result."""
        tool = self.registry.get(tool_call.name)

        if not tool:
            return f"Error: Unknown tool '{tool_call.name}'"

        if set(tool_call.arguments.keys()) == {"raw"}:
            raw_args = str(tool_call.arguments.get("raw", "")).strip()
            raw_preview = raw_args if len(raw_args) <= 200 else raw_args[:200] + "..."
            expected_args = ", ".join(tool.parameters.keys())
            return (
                f"Error: Invalid tool arguments for '{tool_call.name}'. "
                f"The model sent malformed JSON instead of tool parameters. "
                f"Expected keys: {expected_args}. "
                f"Raw arguments: {raw_preview}"
            )

        # Check permissions
        perm_request = self.permissions.check_permission(tool_call.name, tool_call.arguments)

        if not self._get_permission(perm_request):
            return "Permission denied by user."

        # Execute the tool asynchronously
        try:
            if isinstance(tool, AsyncTool):
                result = await tool.execute(**tool_call.arguments)
            else:
                # Fall back to sync execution for sync tools
                result = tool.execute(**tool_call.arguments)
            return str(result)
        except Exception as e:
            return f"Error executing tool: {e}"

    async def _process_tool_calls(self, tool_calls: list[ToolCall]) -> list[dict[str, Any]]:
        """Process all tool calls asynchronously and return results."""
        results = []

        # Execute tool calls in parallel when possible
        tasks = []
        for tc in tool_calls:
            # Show tool call
            ui.print_tool_call(tc.name, tc.arguments)

            # Create task for tool execution
            task = self._execute_tool(tc)
            tasks.append((tc, task))

        # Execute all tasks
        for tc, task in tasks:
            result = await task

            # Show result (truncated)
            success = not result.startswith("Error")
            ui.print_tool_result(result, success=success)

            # Format for API
            results.append(
                {
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": result,
                }
            )

        return results

    async def run_turn(self, user_message: str | None = None) -> str | None:
        """
        Run a single agent turn asynchronously with streaming support.

        Args:
            user_message: Optional user message to add before the turn

        Returns:
            Final text response from assistant, or None if still processing
        """
        # Add user message if provided
        if user_message:
            self.history.add_user_message(user_message)

        # Get tool schemas
        tool_schemas = self.registry.get_schemas()

        # Build messages for API
        messages = self.history.get_full_context()

        # Track if we've started streaming content
        streaming_started = False

        def on_content_chunk(chunk: str) -> None:
            """Called for each streamed content chunk."""
            nonlocal streaming_started
            if not streaming_started:
                streaming_started = True
            ui.print_stream_chunk(chunk)

        # Call LLM with streaming
        with ui.print_thinking():
            response = self.client.chat_stream(
                messages,
                tools=tool_schemas,
                on_content=on_content_chunk,
            )

        # End the streaming line if we streamed content
        if streaming_started:
            ui.end_stream()

        # Add assistant message to history
        assistant_msg = self.client.format_assistant_message(response)
        self.history.add_assistant_message(assistant_msg)

        # Check if done (no tool calls)
        if not response.has_tool_calls:
            # Content was already streamed, just return it
            return response.content

        # Process tool calls asynchronously
        tool_results = await self._process_tool_calls(response.tool_calls)
        self.history.add_tool_results(tool_results)

        # Continue processing (tool results added, ready for next turn)
        return None

    async def run(self, task: str, use_planning: bool = True) -> str:
        """
        Run the agent loop asynchronously until task is complete.

        Args:
            task: The task/prompt to execute
            use_planning: Whether to use task planning
                         In async mode, planning is always used by default
                         for better task decomposition and context management

        Returns:
            Final response from the agent
        """
        # In async mode, ALWAYS use planning by default when enabled
        # This ensures consistent behavior and better handling of all tasks
        if use_planning:
            return await self._run_with_planning(task)

        # Only use standard execution if planning is explicitly disabled
        return await self._run_standard(task)

    async def _should_use_planning(self, task: str) -> bool:
        """
        Determine if task planning should be used.

        Can be overridden for custom logic.
        """
        # Simple heuristic: use planning for complex tasks
        from .task_planner import TaskPlanner

        planner = TaskPlanner(self.client, self.registry, self.context.working_dir)
        return planner._is_complex_task(task)

    async def _run_with_planning(self, task: str) -> str:
        """
        Run task with automatic decomposition into subtasks.
        """
        from . import ui
        from .task_planner import TaskPlanner

        ui.print_info("🔍 Analyzing task complexity...")

        # Create task planner
        planner = TaskPlanner(self.client, self.registry, self.context.working_dir)

        # Create task plan
        ui.print_info("📋 Creating task plan...")
        plan = planner.create_task_plan(task)

        ui.print_success(f"✅ Created plan with {len(plan.subtasks)} subtasks")

        # Display plan
        self._display_task_plan(plan)

        # Execute plan
        ui.print_info("🚀 Executing task plan...")
        result = await planner.execute_plan_async(plan, self)

        return result

    async def _run_standard(self, task: str) -> str:
        """
        Run task using standard agent loop.
        """
        from . import ui

        # Add initial task
        self.history.add_user_message(task)

        for turn in range(self.config.max_turns):
            # Run a turn (don't add message, already added)
            result = await self.run_turn(user_message=None)

            if result is not None:
                # Agent is done
                return result

        # Max turns reached
        ui.print_warning(f"Reached maximum turns ({self.config.max_turns})")
        return "Task incomplete - maximum turns reached."

    def _display_task_plan(self, plan):
        """Display the task plan to user."""
        from . import ui

        ui.print_section("📋 Task Execution Plan")
        ui.print_info(f"Original task: {plan.original_task}")
        ui.print_info(f"Number of subtasks: {len(plan.subtasks)}")

        for i, subtask_id in enumerate(plan.execution_order, 1):
            subtask = next(st for st in plan.subtasks if st.id == subtask_id)
            deps = ", ".join(subtask.dependencies) if subtask.dependencies else "none"
            ui.print_info(f"{i}. {subtask.id}: {subtask.description}")
            ui.print_info(f"   Dependencies: {deps}")
            ui.print_info(
                f"   Files: {', '.join(subtask.context_files[:3])}"
                + ("..." if len(subtask.context_files) > 3 else "")
            )

    async def arun(self, task: str, use_planning: bool = True) -> str:
        """
        Alias for async run method.
        """
        return await self.run(task, use_planning)

    async def chat(self, message: str) -> str:
        """
        Send a chat message and get response asynchronously (for interactive mode).

        This runs the full agent loop for a single user message.
        """
        for turn in range(self.config.max_turns):
            if turn == 0:
                result = await self.run_turn(user_message=message)
            else:
                result = await self.run_turn(user_message=None)

            if result is not None:
                return result

        ui.print_warning(f"Reached maximum turns ({self.config.max_turns})")
        return "Response incomplete - maximum turns reached."

    def reset(self) -> None:
        """Reset conversation history."""
        self.history = ConversationHistory(system_prompt=self.system_prompt)


def create_async_agent(
    api_key: str | None = None,
    model: str | None = None,
    working_dir: str = ".",
    trust_mode: bool = False,
    yolo_mode: bool = False,
    max_turns: int = 50,
) -> AsyncAgent:
    """
    Create an async agent with default configuration.

    Args:
        api_key: API key (or use DEEPSEEK_API_KEY env var)
        model: Model to use (default: deepseek-chat)
        working_dir: Working directory
        trust_mode: Auto-approve safe operations
        yolo_mode: Skip ALL permission prompts (dangerous!)
        max_turns: Maximum turns per task

    Returns:
        Configured AsyncAgent instance
    """
    from .context import get_project_context

    client = LunVexClient(api_key=api_key, model=model)
    context = get_project_context(working_dir)
    config = AsyncAgentConfig(max_turns=max_turns, trust_mode=trust_mode, yolo_mode=yolo_mode)

    return AsyncAgent(client=client, context=context, config=config)
