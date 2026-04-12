"""Base class and utilities for tools."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


@dataclass
class ToolResult:
    """Result from tool execution."""

    success: bool
    output: str
    error: str | None = None

    def __str__(self) -> str:
        if self.success:
            return self.output
        return f"Error: {self.error or self.output}"


class Tool(ABC):
    """Base class for all tools."""

    name: str
    description: str
    parameters: dict[str, Any]

    # Permission level: "auto" (safe), "ask" (needs permission), "deny" (blocked)
    permission_level: str = "ask"

    @abstractmethod
    def execute(self, **kwargs) -> ToolResult:
        """Execute the tool with given parameters."""
        pass

    def get_schema(self) -> dict[str, Any]:
        """Get the OpenAI-compatible tool schema."""
        # Build properties without the 'required' field (it goes in the array, not in properties)
        properties = {}
        required = []

        for param_name, param_config in self.parameters.items():
            # Copy config but exclude 'required' key from properties
            prop = {
                "type": param_config["type"],
                "description": param_config["description"],
            }
            properties[param_name] = prop

            # Track required parameters separately
            if param_config.get("required", False):
                required.append(param_name)

        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": properties,
                    "required": required,
                },
            },
        }


class ToolRegistry:
    """Registry of available tools."""

    def __init__(self):
        self._tools: dict[str, Tool] = {}

    def register(self, tool: Tool) -> None:
        """Register a tool."""
        self._tools[tool.name] = tool

    def get(self, name: str) -> Tool | None:
        """Get a tool by name."""
        return self._tools.get(name)

    def get_all(self) -> list[Tool]:
        """Get all registered tools."""
        return list(self._tools.values())

    def list_tools(self) -> list[str]:
        """List names of all registered tools."""
        return list(self._tools.keys())

    def get_schemas(self) -> list[dict[str, Any]]:
        """Get schemas for all tools."""
        return [tool.get_schema() for tool in self._tools.values()]

    def execute(self, name: str, **kwargs) -> ToolResult:
        """Execute a tool by name."""
        tool = self.get(name)
        if not tool:
            return ToolResult(success=False, output="", error=f"Unknown tool: {name}")
        return tool.execute(**kwargs)


def create_default_registry() -> ToolRegistry:
    """Create a registry with all default tools."""
    from .bash_tool import BashTool
    from .dependency_tools import (
        AddDependencyTool,
        AnalyzeDependenciesTool,
        CheckDependencyConfigTool,
        ListDependenciesTool,
        RemoveDependencyTool,
        ScanVulnerabilitiesTool,
        UpdateDependencyConfigTool,
        UpdateDependencyTool,
        UpgradeDependenciesTool,
        VisualizeDependenciesTool,
    )
    from .file_tools import EditFileTool, ReadFileTool, WriteFileTool
    from .git_tools import (
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
    from .search_tools import GlobTool, GrepTool
    from .web_tools import FetchURLTool

    registry = ToolRegistry()
    registry.register(ReadFileTool())
    registry.register(WriteFileTool())
    registry.register(EditFileTool())
    registry.register(GlobTool())
    registry.register(GrepTool())
    registry.register(FetchURLTool())
    registry.register(BashTool())
    registry.register(AnalyzeDependenciesTool())
    registry.register(ListDependenciesTool())
    registry.register(CheckDependencyConfigTool())
    registry.register(UpdateDependencyConfigTool())
    registry.register(AddDependencyTool())
    registry.register(RemoveDependencyTool())
    registry.register(UpdateDependencyTool())
    registry.register(UpgradeDependenciesTool())
    registry.register(ScanVulnerabilitiesTool())
    registry.register(VisualizeDependenciesTool())
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
