"""Dependency management tools for LunVex Code.

This module is now a proxy for the modular dependency tools.
All classes have been moved to `lunvex_code.tools.dependencies.*` modules.

For backward compatibility, this module re-exports all the tools.
New code should import directly from the specific submodules.
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