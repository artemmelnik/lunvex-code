"""Backward compatibility shims for the pre-rename ``deepseek_code`` package."""

from importlib import import_module
import sys

from lunvex_code import (
    APP_COMMAND_NAME,
    APP_CONTEXT_FILENAME,
    APP_DISPLAY_NAME,
    APP_STATE_DIRNAME,
    LEGACY_CONTEXT_FILENAME,
    __version__,
)

_ALIASED_MODULES = (
    "agent",
    "cli",
    "context",
    "conversation",
    "llm",
    "permissions",
    "ui",
    "dependencies",
    "dependencies.analyzer",
    "dependencies.config",
    "dependencies.models",
    "dependencies.security",
    "dependencies.security_fixed",
    "dependencies.visualizer",
    "tools",
    "tools.base",
    "tools.bash_tool",
    "tools.dependency_tools",
    "tools.file_tools",
    "tools.search_tools",
)

for module_name in _ALIASED_MODULES:
    legacy_module_name = f"{__name__}.{module_name}"
    target_module = import_module(f"lunvex_code.{module_name}")
    sys.modules[legacy_module_name] = target_module

    if "." not in module_name:
        globals()[module_name] = target_module

__all__ = [
    "__version__",
    "APP_COMMAND_NAME",
    "APP_CONTEXT_FILENAME",
    "APP_DISPLAY_NAME",
    "APP_STATE_DIRNAME",
    "LEGACY_CONTEXT_FILENAME",
    "agent",
    "cli",
    "context",
    "conversation",
    "llm",
    "permissions",
    "ui",
    "dependencies",
    "tools",
]
