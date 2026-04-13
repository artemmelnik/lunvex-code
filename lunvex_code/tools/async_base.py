"""Async base classes for tools."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class AsyncToolResult:
    """Result from async tool execution."""

    success: bool
    output: str
    error: Optional[str] = None

    def __str__(self) -> str:
        if self.success:
            return self.output
        else:
            error_msg = f"Error: {self.error}" if self.error else "Unknown error"
            return f"{self.output}\n{error_msg}" if self.output else error_msg


class AsyncTool(ABC):
    """Abstract base class for async tools."""

    name: str
    description: str
    permission_level: str = "ask"  # auto, ask, deny

    parameters: Dict[str, Dict[str, Any]] = {}

    @abstractmethod
    async def execute(self, **kwargs) -> AsyncToolResult:
        """Execute the tool asynchronously."""
        pass

    def get_schema(self) -> Dict[str, Any]:
        """Get the tool schema for LLM function calling."""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": {
                        param_name: {
                            "type": param_info.get("type", "string"),
                            "description": param_info.get("description", ""),
                        }
                        for param_name, param_info in self.parameters.items()
                    },
                    "required": [
                        param_name
                        for param_name, param_info in self.parameters.items()
                        if param_info.get("required", False)
                    ],
                },
            },
        }
