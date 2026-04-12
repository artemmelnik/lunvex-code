"""Configuration for dependency management."""

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List

import yaml


class UpdateLevel(Enum):
    """Level of updates to apply."""

    PATCH = "patch"
    MINOR = "minor"
    MAJOR = "major"


@dataclass
class SecurityConfig:
    """Security-related configuration."""

    scan_on_change: bool = True
    fail_on_critical: bool = False
    allowed_licenses: List[str] = field(
        default_factory=lambda: [
            "MIT",
            "Apache-2.0",
            "BSD-3-Clause",
            "BSD-2-Clause",
            "ISC",
            "Unlicense",
        ]
    )
    blocked_licenses: List[str] = field(default_factory=lambda: ["GPL-3.0", "AGPL-3.0"])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "scan_on_change": self.scan_on_change,
            "fail_on_critical": self.fail_on_critical,
            "allowed_licenses": self.allowed_licenses,
            "blocked_licenses": self.blocked_licenses,
        }


@dataclass
class UpdateConfig:
    """Update-related configuration."""

    enabled: bool = True
    level: UpdateLevel = UpdateLevel.PATCH
    auto_apply: bool = False
    create_pr: bool = False
    schedule: str = "weekly"  # daily, weekly, monthly

    def to_dict(self) -> Dict[str, Any]:
        return {
            "enabled": self.enabled,
            "level": self.level.value,
            "auto_apply": self.auto_apply,
            "create_pr": self.create_pr,
            "schedule": self.schedule,
        }


@dataclass
class IgnoreConfig:
    """Configuration for ignoring specific items."""

    packages: List[str] = field(default_factory=list)
    vulnerabilities: List[str] = field(default_factory=list)  # CVE IDs
    licenses: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "packages": self.packages,
            "vulnerabilities": self.vulnerabilities,
            "licenses": self.licenses,
        }


@dataclass
class DependencyConfig:
    """Main dependency configuration."""

    security: SecurityConfig = field(default_factory=SecurityConfig)
    updates: UpdateConfig = field(default_factory=UpdateConfig)
    ignore: IgnoreConfig = field(default_factory=IgnoreConfig)

    @classmethod
    def from_file(cls, path: Path) -> "DependencyConfig":
        """Load configuration from YAML file."""
        if not path.exists():
            return cls()

        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}

        dep_data = data.get("dependency_policy", {})

        # Security config
        security_data = dep_data.get("security", {})
        security = SecurityConfig(
            scan_on_change=security_data.get("scan_on_change", True),
            fail_on_critical=security_data.get("fail_on_critical", False),
            allowed_licenses=security_data.get("allowed_licenses", []),
            blocked_licenses=security_data.get("blocked_licenses", []),
        )

        # Update config
        update_data = dep_data.get("auto_update", {})
        update_level = UpdateLevel(update_data.get("level", "patch"))
        updates = UpdateConfig(
            enabled=update_data.get("enabled", True),
            level=update_level,
            auto_apply=update_data.get("auto_apply", False),
            create_pr=update_data.get("create_pr", False),
            schedule=update_data.get("schedule", "weekly"),
        )

        # Ignore config
        ignore_data = dep_data.get("ignore", {})
        ignore = IgnoreConfig(
            packages=ignore_data.get("packages", []),
            vulnerabilities=ignore_data.get("vulnerabilities", []),
            licenses=ignore_data.get("licenses", []),
        )

        return cls(security=security, updates=updates, ignore=ignore)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "dependency_policy": {
                "security": self.security.to_dict(),
                "auto_update": self.updates.to_dict(),
                "ignore": self.ignore.to_dict(),
            }
        }

    def save(self, path: Path) -> None:
        """Save configuration to YAML file."""
        data = self.to_dict()
        with open(path, "w", encoding="utf-8") as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)

    def should_ignore_package(self, package_name: str) -> bool:
        """Check if a package should be ignored."""
        return package_name in self.ignore.packages

    def should_ignore_vulnerability(self, vulnerability_id: str) -> bool:
        """Check if a vulnerability should be ignored."""
        return vulnerability_id in self.ignore.vulnerabilities

    def is_license_allowed(self, license_name: str) -> bool:
        """Check if a license is allowed."""
        if not license_name:
            return True

        # Check blocked licenses first
        for blocked in self.ignore.licenses + self.security.blocked_licenses:
            if blocked.lower() in license_name.lower():
                return False

        # Check allowed licenses
        for allowed in self.security.allowed_licenses:
            if allowed.lower() in license_name.lower():
                return True

        # If no specific rules, allow by default
        return True


def get_default_config_path(project_root: Path) -> Path:
    """Get the default configuration file path."""
    return project_root / ".lunvex-deps.yaml"


def load_config(project_root: Path) -> DependencyConfig:
    """Load configuration from project root."""
    config_path = get_default_config_path(project_root)
    return DependencyConfig.from_file(config_path)
