"""Proxy module for backward compatibility.

This module re-exports all dependency tools from the new modular structure.
It allows existing code that imports from `lunvex_code.tools.dependency_tools`
to continue working without modification.
"""

from .dependencies import (
    AnalyzeDependenciesTool,
    ListDependenciesTool,
    CheckDependencyConfigTool,
    UpdateDependencyConfigTool,
    AddDependencyTool,
    RemoveDependencyTool,
    UpdateDependencyTool,
    ScanVulnerabilitiesTool,
    UpgradeDependenciesTool,
    VisualizeDependenciesTool,
)

__all__ = [
    "AnalyzeDependenciesTool",
    "ListDependenciesTool",
    "CheckDependencyConfigTool",
    "UpdateDependencyConfigTool",
    "AddDependencyTool",
    "RemoveDependencyTool",
    "UpdateDependencyTool",
    "ScanVulnerabilitiesTool",
    "UpgradeDependenciesTool",
    "VisualizeDependenciesTool",
]