"""Data models for dependency management."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class Ecosystem(Enum):
    """Supported package ecosystems."""

    PYTHON = "python"
    JAVASCRIPT = "javascript"
    RUST = "rust"
    GO = "go"
    RUBY = "ruby"
    PHP = "php"
    UNKNOWN = "unknown"


class DependencyType(Enum):
    """Types of dependencies."""

    PRODUCTION = "production"
    DEVELOPMENT = "development"
    OPTIONAL = "optional"
    PEER = "peer"
    BUNDLED = "bundled"


@dataclass
class Dependency:
    """Represents a single dependency."""

    name: str
    version: str
    ecosystem: Ecosystem
    dep_type: DependencyType = DependencyType.PRODUCTION
    required_by: List[str] = field(default_factory=list)
    transitive_deps: List["Dependency"] = field(default_factory=list)
    license: Optional[str] = None
    homepage: Optional[str] = None
    description: Optional[str] = None
    latest_version: Optional[str] = None
    is_outdated: bool = False
    has_vulnerabilities: bool = False
    vulnerabilities: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "name": self.name,
            "version": self.version,
            "ecosystem": self.ecosystem.value,
            "type": self.dep_type.value,
            "required_by": self.required_by,
            "license": self.license,
            "homepage": self.homepage,
            "description": self.description,
            "latest_version": self.latest_version,
            "is_outdated": self.is_outdated,
            "has_vulnerabilities": self.has_vulnerabilities,
            "vulnerability_count": len(self.vulnerabilities),
        }


@dataclass
class DependencyReport:
    """Comprehensive dependency analysis report."""

    ecosystem: Ecosystem
    dependencies: List[Dependency]
    timestamp: datetime = field(default_factory=datetime.now)

    # Summary statistics
    total_deps: int = 0
    outdated_deps: int = 0
    vulnerable_deps: int = 0
    license_issues: int = 0

    # File information
    source_files: List[str] = field(default_factory=list)

    def __post_init__(self):
        """Calculate summary statistics."""
        self.total_deps = len(self.dependencies)
        self.outdated_deps = sum(1 for d in self.dependencies if d.is_outdated)
        self.vulnerable_deps = sum(1 for d in self.dependencies if d.has_vulnerabilities)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "ecosystem": self.ecosystem.value,
            "timestamp": self.timestamp.isoformat(),
            "summary": {
                "total_dependencies": self.total_deps,
                "outdated_dependencies": self.outdated_deps,
                "vulnerable_dependencies": self.vulnerable_deps,
                "license_issues": self.license_issues,
            },
            "dependencies": [d.to_dict() for d in self.dependencies],
            "source_files": self.source_files,
        }

    def to_markdown(self) -> str:
        """Generate markdown report."""
        lines = [
            "# Dependency Analysis Report",
            f"**Ecosystem**: {self.ecosystem.value.title()}",
            f"**Generated**: {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "## Summary",
            f"- **Total Dependencies**: {self.total_deps}",
            f"- **Outdated**: {self.outdated_deps}",
            f"- **Vulnerable**: {self.vulnerable_deps}",
            f"- **License Issues**: {self.license_issues}",
            "",
            "## Dependencies",
        ]

        for dep in self.dependencies:
            status = []
            if dep.is_outdated:
                status.append("⚠️ outdated")
            if dep.has_vulnerabilities:
                status.append("🔴 vulnerable")

            status_str = f" ({', '.join(status)})" if status else ""

            lines.extend(
                [
                    f"### {dep.name} `{dep.version}`{status_str}",
                    f"- **Type**: {dep.dep_type.value}",
                    f"- **License**: {dep.license or 'Unknown'}",
                    f"- **Latest**: {dep.latest_version or 'Unknown'}",
                ]
            )

            if dep.required_by:
                lines.append(f"- **Required by**: {', '.join(dep.required_by)}")

            if dep.description:
                lines.append(f"- **Description**: {dep.description}")

            lines.append("")

        return "\n".join(lines)


@dataclass
class Vulnerability:
    """Represents a security vulnerability."""

    id: str  # CVE-ID or advisory ID
    severity: str  # critical, high, medium, low
    description: str
    affected_versions: str
    fixed_versions: List[str]
    references: List[str] = field(default_factory=list)
    published_date: Optional[datetime] = None
