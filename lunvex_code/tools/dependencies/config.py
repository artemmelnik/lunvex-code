"""Dependency configuration tools."""

from pathlib import Path

from lunvex_code.dependencies import DependencyConfig

from ..base import Tool, ToolResult


class CheckDependencyConfigTool(Tool):
    """Check and display dependency configuration."""

    name = "check_dependency_config"
    description = "Check and display the current dependency configuration"
    permission_level = "auto"  # Read-only operation

    parameters = {
        "create_if_missing": {
            "type": "boolean",
            "description": "Create default configuration file if it doesn't exist",
            "required": False,
            "default": False,
        },
    }

    def execute(self, create_if_missing: bool = False) -> ToolResult:
        try:
            cwd = Path.cwd()
            config_path = cwd / ".lunvex-deps.yaml"

            if not config_path.exists():
                if create_if_missing:
                    # Create default config
                    config = DependencyConfig()
                    config.save(config_path)
                    output = f"Created default configuration at: {config_path}\n\n"
                    output += "Default configuration includes:\n"
                    output += "- Security scanning enabled\n"
                    output += "- Patch-level auto-updates\n"
                    output += "- Common license rules (MIT, Apache-2.0, etc.)\n"
                else:
                    return ToolResult(
                        success=True,
                        output=f"No dependency configuration found at: {config_path}\n"
                        f"Run with --create-if-missing to create a default configuration.",
                    )
            else:
                config = DependencyConfig.from_file(config_path)
                output = f"Configuration loaded from: {config_path}\n\n"

                # Security config
                output += "## Security Configuration\n"
                output += f"- Scan on change: {config.security.scan_on_change}\n"
                output += (
                    f"- Fail on critical vulnerabilities: {config.security.fail_on_critical}\n"
                )
                output += (
                    f"- Allowed licenses: {', '.join(config.security.allowed_licenses) or 'None'}\n"
                )
                output += f"- Blocked licenses: {', '.join(config.security.blocked_licenses) or 'None'}\n\n"

                # Update config
                output += "## Update Configuration\n"
                output += f"- Auto-updates enabled: {config.updates.enabled}\n"
                output += f"- Update level: {config.updates.level.value}\n"
                output += f"- Auto-apply updates: {config.updates.auto_apply}\n"
                output += f"- Create PR for updates: {config.updates.create_pr}\n"
                output += f"- Schedule: {config.updates.schedule}\n\n"

                # Ignore config
                output += "## Ignore Configuration\n"
                output += f"- Ignored packages: {', '.join(config.ignore.packages) or 'None'}\n"
                output += f"- Ignored vulnerabilities: {', '.join(config.ignore.vulnerabilities) or 'None'}\n"
                output += f"- Ignored licenses: {', '.join(config.ignore.licenses) or 'None'}\n"

            return ToolResult(
                success=True,
                output=output,
            )

        except Exception as e:
            return ToolResult(
                success=False,
                output="",
                error=f"Failed to check dependency configuration: {str(e)}",
            )


class UpdateDependencyConfigTool(Tool):
    """Update dependency configuration."""

    name = "update_dependency_config"
    description = "Update dependency configuration file"
    permission_level = "ask"  # Modifies files

    parameters = {
        "key": {
            "type": "string",
            "description": "Configuration key to update (e.g., 'security.scan_on_change')",
            "required": True,
        },
        "value": {
            "type": "string",
            "description": "New value for the configuration key",
            "required": True,
        },
    }

    def execute(self, key: str, value: str) -> ToolResult:
        try:
            cwd = Path.cwd()
            config_path = cwd / ".lunvex-deps.yaml"

            # Load existing config or create new
            if config_path.exists():
                config = DependencyConfig.from_file(config_path)
            else:
                config = DependencyConfig()

            # Parse key path
            key_parts = key.split(".")

            # Update configuration based on key path
            # This is simplified - in real implementation would need more robust parsing
            if len(key_parts) == 2:
                section, prop = key_parts

                if section == "security":
                    if hasattr(config.security, prop):
                        # Convert value to appropriate type
                        current_value = getattr(config.security, prop)
                        if isinstance(current_value, bool):
                            new_value = value.lower() in ("true", "yes", "1", "on")
                        elif isinstance(current_value, list):
                            new_value = [v.strip() for v in value.split(",")]
                        else:
                            new_value = value

                        setattr(config.security, prop, new_value)
                    else:
                        return ToolResult(
                            success=False, output="", error=f"Unknown security property: {prop}"
                        )

                elif section == "updates":
                    if hasattr(config.updates, prop):
                        current_value = getattr(config.updates, prop)
                        if prop == "level":
                            from ..dependencies.config import UpdateLevel

                            try:
                                new_value = UpdateLevel(value.lower())
                            except ValueError:
                                return ToolResult(
                                    success=False,
                                    output="",
                                    error=f"Invalid update level: {value}. Must be: patch, minor, major",
                                )
                        elif isinstance(current_value, bool):
                            new_value = value.lower() in ("true", "yes", "1", "on")
                        else:
                            new_value = value

                        setattr(config.updates, prop, new_value)
                    else:
                        return ToolResult(
                            success=False, output="", error=f"Unknown updates property: {prop}"
                        )

                elif section == "ignore":
                    if hasattr(config.ignore, prop):
                        current_value = getattr(config.ignore, prop)
                        if isinstance(current_value, list):
                            new_value = [v.strip() for v in value.split(",")]
                            setattr(config.ignore, prop, new_value)
                        else:
                            return ToolResult(
                                success=False, output="", error=f"Property {prop} is not a list"
                            )
                    else:
                        return ToolResult(
                            success=False, output="", error=f"Unknown ignore property: {prop}"
                        )

                else:
                    return ToolResult(
                        success=False, output="", error=f"Unknown configuration section: {section}"
                    )

            else:
                return ToolResult(
                    success=False, output="", error="Key must be in format 'section.property'"
                )

            # Save updated configuration
            config.save(config_path)

            return ToolResult(
                success=True,
                output=f"Updated configuration: {key} = {value}\n"
                f"Configuration saved to: {config_path}",
            )

        except Exception as e:
            return ToolResult(
                success=False,
                output="",
                error=f"Failed to update dependency configuration: {str(e)}",
            )
