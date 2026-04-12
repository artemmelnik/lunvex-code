"""Permission system for tool execution with extensible rule-based architecture."""

import re
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Pattern, Set, Tuple


class PermissionLevel(Enum):
    """Permission levels for operations."""

    AUTO = "auto"  # Automatically allowed (safe operations)
    ASK = "ask"  # Requires user confirmation
    DENY = "deny"  # Blocked entirely


@dataclass
class PermissionRequest:
    """A request for permission to perform an action."""

    tool_name: str
    tool_input: Dict[str, Any]
    level: PermissionLevel
    reason: Optional[str] = None


@dataclass
class PermissionResult:
    """Result of a permission check."""

    allowed: bool
    reason: Optional[str] = None


class PermissionRule(ABC):
    """Base class for permission rules."""

    @abstractmethod
    def check(self, tool_name: str, tool_input: Dict[str, Any]) -> Optional[PermissionLevel]:
        """
        Check if this rule applies to the tool call.

        Returns:
            PermissionLevel if rule applies, None otherwise
        """
        pass

    @abstractmethod
    def get_reason(self) -> Optional[str]:
        """Get reason for the decision."""
        pass


class ToolNameRule(PermissionRule):
    """Rule based on tool name."""

    def __init__(self, tool_name: str, level: PermissionLevel, reason: Optional[str] = None):
        self.tool_name = tool_name
        self.level = level
        self._reason = reason

    def check(self, tool_name: str, tool_input: Dict[str, Any]) -> Optional[PermissionLevel]:
        if tool_name == self.tool_name:
            return self.level
        return None

    def get_reason(self) -> Optional[str]:
        return self._reason


class ToolNamePatternRule(PermissionRule):
    """Rule based on tool name pattern (regex)."""

    def __init__(self, pattern: Pattern, level: PermissionLevel, reason: Optional[str] = None):
        self.pattern = pattern
        self.level = level
        self._reason = reason

    def check(self, tool_name: str, tool_input: Dict[str, Any]) -> Optional[PermissionLevel]:
        if self.pattern.match(tool_name):
            return self.level
        return None

    def get_reason(self) -> Optional[str]:
        return self._reason


class InputPatternRule(PermissionRule):
    """Rule based on tool input pattern."""

    def __init__(
        self,
        tool_name: str,
        input_key: str,
        pattern: Pattern,
        level: PermissionLevel,
        reason: Optional[str] = None,
    ):
        self.tool_name = tool_name
        self.input_key = input_key
        self.pattern = pattern
        self.level = level
        self._reason = reason

    def check(self, tool_name: str, tool_input: Dict[str, Any]) -> Optional[PermissionLevel]:
        if tool_name != self.tool_name:
            return None

        value = tool_input.get(self.input_key, "")
        if isinstance(value, str) and self.pattern.search(value):
            return self.level

        return None

    def get_reason(self) -> Optional[str]:
        return self._reason


class CompositeRule(PermissionRule):
    """Composite rule that combines multiple rules with logical operators."""

    def __init__(self, rules: List[PermissionRule], operator: str = "AND"):
        """
        Args:
            rules: List of rules to combine
            operator: "AND" (all rules must match) or "OR" (any rule matches)
        """
        self.rules = rules
        self.operator = operator.upper()

    def check(self, tool_name: str, tool_input: Dict[str, Any]) -> Optional[PermissionLevel]:
        results = []
        for rule in self.rules:
            result = rule.check(tool_name, tool_input)
            if result is not None:
                results.append((result, rule.get_reason()))

        if not results:
            return None

        if self.operator == "AND":
            # For AND, all rules must return the same level
            if len(results) == len(self.rules):
                levels = {level for level, _ in results}
                if len(levels) == 1:
                    return next(iter(levels))
        elif self.operator == "OR":
            # For OR, return the first matching rule's level
            # Prefer DENY over ASK over AUTO
            level_order = {PermissionLevel.DENY: 0, PermissionLevel.ASK: 1, PermissionLevel.AUTO: 2}
            return min(results, key=lambda x: level_order[x[0]])[0]

        return None

    def get_reason(self) -> Optional[str]:
        return f"Composite rule ({self.operator})"


class SessionRule(PermissionRule):
    """Rule for session-specific allow/deny lists."""

    def __init__(self):
        self.allowlist: Set[str] = set()
        self.denylist: Set[str] = set()

    def add_to_allowlist(self, pattern: str) -> None:
        """Add a pattern to the session allowlist."""
        self.allowlist.add(pattern)

    def add_to_denylist(self, pattern: str) -> None:
        """Add a pattern to the session denylist."""
        self.denylist.add(pattern)

    def _parse_pattern(self, pattern: str) -> Tuple[Optional[str], Optional[str], Optional[str]]:
        """Parse pattern like 'bash(ls:*)' into (tool_name, input_key, pattern_str)."""
        if "(" in pattern and pattern.endswith(")"):
            tool_part, pattern_part = pattern.split("(", 1)
            pattern_part = pattern_part[:-1]  # Remove trailing ")"

            if ":" in pattern_part:
                input_key, pattern_str = pattern_part.split(":", 1)
                return tool_part, input_key, pattern_str
            else:
                return tool_part, None, pattern_part

        return None, None, None

    def _matches_pattern(self, text: str, pattern: str) -> bool:
        """Check if text matches a simple wildcard pattern."""
        # Handle special case: pattern like "ls:*" should match commands starting with "ls"
        if pattern.endswith(":*"):
            prefix = pattern[:-2]
            return text.strip().startswith(prefix)

        # Convert simple wildcard pattern to regex
        escaped_pattern = re.escape(pattern)
        regex_pattern = escaped_pattern.replace(r"\*", ".*").replace(r"\?", ".")
        if not pattern.startswith("*"):
            regex_pattern = "^" + regex_pattern
        return bool(re.search(regex_pattern, text))

    def check(self, tool_name: str, tool_input: Dict[str, Any]) -> Optional[PermissionLevel]:
        # Check allowlist
        for pattern in self.allowlist:
            parsed = self._parse_pattern(pattern)
            if not parsed[0]:
                continue

            tool_pattern, input_key, pattern_str = parsed

            if tool_pattern != tool_name:
                continue

            if input_key and pattern_str:
                value = tool_input.get(input_key, "")
                if isinstance(value, str) and self._matches_pattern(value, pattern_str):
                    return PermissionLevel.AUTO

        # Check denylist
        for pattern in self.denylist:
            parsed = self._parse_pattern(pattern)
            if not parsed[0]:
                continue

            tool_pattern, input_key, pattern_str = parsed

            if tool_pattern != tool_name:
                continue

            if input_key and pattern_str:
                value = tool_input.get(input_key, "")
                if isinstance(value, str) and self._matches_pattern(value, pattern_str):
                    return PermissionLevel.DENY

        return None

    def get_reason(self) -> Optional[str]:
        return "Session rule"


class PermissionManager:
    """Manages permissions for tool execution with extensible rule-based architecture."""

    def __init__(self, trust_mode: bool = False, yolo_mode: bool = False):
        """
        Initialize permission manager.

        Args:
            trust_mode: If True, auto-approve all non-blocked operations
            yolo_mode: If True, skip ALL permission prompts (like Claude Code's --dangerously-skip-permissions)
        """
        self.trust_mode = trust_mode
        self.yolo_mode = yolo_mode
        self.rules: List[PermissionRule] = []
        self.session_rule = SessionRule()

        # Add session rule first (so it can be overridden by other rules)
        self.rules.append(self.session_rule)

        # Initialize with default rules
        self._setup_default_rules()

    def add_to_allowlist(self, pattern: str) -> None:
        """Add a pattern to the session allowlist."""
        self.session_rule.add_to_allowlist(pattern)

    def add_to_denylist(self, pattern: str) -> None:
        """Add a pattern to the session denylist."""
        self.session_rule.add_to_denylist(pattern)

    def add_rule(self, rule: PermissionRule) -> None:
        """Add a custom permission rule."""
        self.rules.append(rule)

    def _setup_default_rules(self) -> None:
        """Setup default permission rules with smart defaults."""

        # Read-only operations are always safe
        self.rules.append(ToolNameRule("read_file", PermissionLevel.AUTO, "Read-only operation"))
        self.rules.append(ToolNameRule("glob", PermissionLevel.AUTO, "Read-only operation"))
        self.rules.append(ToolNameRule("grep", PermissionLevel.AUTO, "Read-only operation"))

        # Safe bash commands (common development commands) - AUTO
        safe_bash_patterns = [
            (r"^ls\b", "List directory"),
            (r"^pwd\b", "Print working directory"),
            (r"^cd\b", "Change directory"),
            (r"^cat\b", "View file"),
            (r"^head\b", "View beginning of file"),
            (r"^tail\b", "View end of file"),
            (r"^wc\b", "Word count"),
            (r"^find\b.*-name", "Find files by name"),
            (r"^grep\b", "Search in files"),
            (r"^git\s+(status|diff|log|show|pull|fetch|clone)", "Safe git operations"),
            (r"^git\s+branch$", "Git list branches"),
            (r"^git\s+branch\s+-(v|r|a|--remote|--all)\b", "Git branch listing options"),
            (r"^git\s+branch\s+--verbose\b", "Git branch verbose"),
            (r"^git\s+branch\s+--list\b", "Git branch list"),
            (r"^git\s+checkout\s+[^-]", "Git checkout (non-force)"),
            (r"^git\s+checkout\s+-b\s+", "Git checkout create branch"),
            (r"^git\s+branch\s+-d$", "Git branch delete check"),
            (r"^git\s+branch\s+--delete$", "Git branch delete check"),
            (r"^npm\s+(run|test|install|ci)", "NPM operations"),
            (r"^python\s+-m\s+pytest", "Run tests"),
            (r"^python\s+-m\s+black", "Code formatting"),
            (r"^python\s+-m\s+ruff", "Linting"),
            (r"^make\s+(test|lint|format|check)", "Make safe targets"),
            (r"^echo\b", "Echo command"),
            (r"^which\b", "Find command"),
            (r"^whereis\b", "Find command"),
            (r"^file\b", "File type"),
            (r"^stat\b", "File statistics"),
            (r"^du\b", "Disk usage"),
            (r"^df\b", "Disk free"),
            (r"^ps\b", "Process status"),
            (r"^top\b", "Process monitor"),
            (r"^htop\b", "Process monitor"),
            (r"^kill\s+-9", "Kill process (force)"),
            (r"^killall\b", "Kill processes by name"),
            (r"^pgrep\b", "Find process"),
            (r"^pkill\b", "Kill process by name"),
            (r"^uname\b", "System info"),
            (r"^whoami\b", "Current user"),
            (r"^hostname\b", "Hostname"),
            (r"^date\b", "Current date"),
            (r"^time\b", "Time command"),
            (r"^curl\s+-I", "HTTP HEAD request"),
            (r"^curl\s+-L", "HTTP GET with redirect"),
            (r"^wget\s+--spider", "Wget test"),
            (r"^ping\b", "Network ping"),
            (r"^traceroute\b", "Network trace"),
            (r"^dig\b", "DNS lookup"),
            (r"^nslookup\b", "DNS lookup"),
            (r"^ssh\s+-T", "SSH test"),
            (r"^scp\s+.*\.(py|js|ts|md|txt|json|yml|yaml)$", "Copy source files"),
            (r"^rsync\s+.*\.(py|js|ts|md|txt|json|yml|yaml)$", "Sync source files"),
            (r"^tar\s+-(c|t|z|x)f", "Archive operations"),
            (r"^gzip\b", "Compression"),
            (r"^gunzip\b", "Decompression"),
            (r"^zip\b", "Compression"),
            (r"^unzip\b", "Decompression"),
            (r"^docker\s+(ps|images|logs|inspect|stats)", "Docker safe commands"),
            (r"^docker-compose\s+(ps|logs|config)", "Docker compose safe commands"),
        ]

        for pattern, reason in safe_bash_patterns:
            # Git patterns should be case-sensitive to distinguish -d from -D
            if pattern.startswith("^git"):
                rule = InputPatternRule(
                    "bash",
                    "command",
                    re.compile(pattern),  # Case-sensitive for Git
                    PermissionLevel.AUTO,
                    f"Safe command: {reason}",
                )
            else:
                rule = InputPatternRule(
                    "bash",
                    "command",
                    re.compile(pattern, re.IGNORECASE),
                    PermissionLevel.AUTO,
                    f"Safe command: {reason}",
                )
            self.rules.append(rule)

        # Safe file operations (test files, temp files) - AUTO
        safe_file_patterns = [
            (r".*test\.py$", "Test file"),
            (r".*_test\.py$", "Test file"),
            (r".*spec\.js$", "Test file"),
            (r".*test\.js$", "Test file"),
            (r".*\.test\.(js|ts|jsx|tsx)$", "Test file"),
            (r".*\.spec\.(js|ts|jsx|tsx)$", "Test file"),
            (r"/tmp/.*", "Temp directory"),
            (r"/var/tmp/.*", "Temp directory"),
            (r".*/__pycache__/.*", "Python cache"),
            (r".*\.pyc$", "Python bytecode"),
            (r".*\.log$", "Log file"),
            (r".*\.tmp$", "Temporary file"),
            (r".*\.bak$", "Backup file"),
            (r".*\.swp$", "Vim swap file"),
            (r".*\.swo$", "Vim swap file"),
            (r"^\.pytest_cache/.*", "Pytest cache"),
            (r"^\.coverage$", "Coverage file"),
            (r"^coverage\.xml$", "Coverage file"),
            (r"^htmlcov/.*", "Coverage HTML"),
            (r"^\.hypothesis/.*", "Hypothesis cache"),
            (r"^\.mypy_cache/.*", "Mypy cache"),
            (r"^\.ruff_cache/.*", "Ruff cache"),
            (r"^\.tox/.*", "Tox directory"),
            (r"^\.venv/.*", "Virtual environment"),
            (r"^venv/.*", "Virtual environment"),
            (r"^node_modules/.*", "Node modules"),
            (r"^\.next/.*", "Next.js build"),
            (r"^dist/.*", "Distribution directory"),
            (r"^build/.*", "Build directory"),
            (r"^out/.*", "Output directory"),
            (r"^\.git/.*", "Git directory"),
        ]

        for pattern, reason in safe_file_patterns:
            # Auto-approve writes to safe files
            write_rule = InputPatternRule(
                "write_file",
                "path",
                re.compile(pattern),
                PermissionLevel.AUTO,
                f"Safe file: {reason}",
            )
            self.rules.append(write_rule)

            # Auto-approve edits to safe files
            edit_rule = InputPatternRule(
                "edit_file",
                "path",
                re.compile(pattern),
                PermissionLevel.AUTO,
                f"Safe file: {reason}",
            )
            self.rules.append(edit_rule)

        # Dangerous bash patterns - DENY
        dangerous_patterns = [
            (r"rm\s+-rf?\s+/", "Recursive delete from root"),
            (r"rm\s+-rf?\s+~", "Recursive delete from home"),
            (r"rm\s+-rf?\s+\*", "Recursive delete with wildcard"),
            (r"sudo\s+", "Sudo command"),
            (r"chmod\s+777", "World-writable permissions"),
            (r">\s*/dev/sd", "Write to disk device"),
            (r"\|\s*sh\s*$", "Piping to shell"),
            (r"\|\s*bash\s*$", "Piping to bash"),
            (r"curl.*\|\s*(sh|bash)", "Curl piping to shell"),
            (r"wget.*\|\s*(sh|bash)", "Wget piping to shell"),
            (r":\(\)\s*\{\s*:\|:&\s*\}", "Fork bomb"),
            (r"mkfs\.", "Filesystem format"),
            (r"dd\s+.*of=/dev/", "DD to device"),
            (r"fdisk\s+/dev/", "Disk partitioning"),
            (r"parted\s+/dev/", "Disk partitioning"),
            (r"mkfs\s+/dev/", "Filesystem creation"),
            (r"mount\s+/dev/", "Mount device"),
            (r"umount\s+/", "Unmount root"),
            (r"chroot\s+", "Change root"),
            (r">\s*/etc/", "Write to system config"),
            (r">\s*/boot/", "Write to boot"),
            (r">\s*/lib/", "Write to libraries"),
            (r">\s*/bin/", "Write to binaries"),
            (r">\s*/sbin/", "Write to system binaries"),
            (r"systemctl\s+(stop|disable|mask|kill)", "System service control"),
            (r"service\s+.*\s+(stop|kill)", "Service control"),
            (r"iptables\s+.*DROP", "Firewall DROP rule"),
            (r"iptables\s+.*REJECT", "Firewall REJECT rule"),
            (r"ufw\s+(disable|reset)", "Firewall control"),
            (r"passwd\s+", "Password change"),
            (r"user(del|mod)\s+", "User management"),
            (r"group(del|mod)\s+", "Group management"),
            (r"crontab\s+.*-r", "Remove crontab"),
            (r">\s*/var/spool/cron/", "Write to cron"),
            (r"history\s+-c", "Clear history"),
            (r"shutdown\s+", "System shutdown"),
            (r"reboot\s+", "System reboot"),
            (r"halt\s+", "System halt"),
            (r"poweroff\s+", "Power off"),
        ]

        for pattern, reason in dangerous_patterns:
            rule = InputPatternRule(
                "bash",
                "command",
                re.compile(pattern, re.IGNORECASE),
                PermissionLevel.DENY,
                f"Dangerous pattern: {reason}",
            )
            self.rules.append(rule)

        # Git-specific dangerous patterns - DENY
        dangerous_git_patterns = [
            # Force pushes (very dangerous - can lose remote history)
            (r"git\s+push\s+.*--force", "Git force push"),
            (r"git\s+push\s+.*-f\b", "Git force push (short)"),
            (r"git\s+push\s+.*--force-with-lease", "Git force push with lease"),
            # Hard resets (dangerous - can lose local work)
            (r"git\s+reset\s+.*--hard", "Git hard reset"),
            # Force clean (dangerous - removes untracked files)
            (r"git\s+clean\s+.*-f", "Git force clean"),
            (r"git\s+clean\s+.*--force", "Git force clean"),
            # Force branch deletion
            (r"git\s+branch\s+.*-D(\s|$)", "Git force delete branch"),
            (r"git\s+branch\s+.*--delete\s+.*--force", "Git force delete branch"),
            # Force checkout (overwrites changes)
            (r"git\s+checkout\s+.*--force", "Git force checkout"),
            (r"git\s+checkout\s+.*-f\b", "Git force checkout (short)"),
            # Remote branch deletion
            (r"git\s+push\s+.*--delete", "Git delete remote branch"),
            (r"git\s+push\s+.*:.*", "Git push with colon (delete ref)"),
            # Submodule force operations
            (r"git\s+submodule\s+.*--force", "Git submodule force"),
            # Worktree force operations
            (r"git\s+worktree\s+.*--force", "Git worktree force"),
            # Update-ref (low-level, dangerous)
            (r"git\s+update-ref\s+", "Git update-ref (low-level)"),
            # Prune with force
            (r"git\s+prune\s+.*--force", "Git prune force"),
        ]

        for pattern, reason in dangerous_git_patterns:
            rule = InputPatternRule(
                "bash",
                "command",
                re.compile(pattern),  # Case-sensitive for Git
                PermissionLevel.DENY,
                f"Dangerous Git pattern: {reason}",
            )
            self.rules.append(rule)

        # Completely blocked commands
        blocked_commands = [
            "rm -rf /",
            "rm -rf /*",
            "dd if=/dev/zero of=/dev/sda",
            "dd if=/dev/zero of=/dev/sdb",
            "dd if=/dev/zero of=/dev/sdc",
            ":(){ :|:& };:",  # Fork bomb
            "mkfs.ext4 /dev/sda",
            "mkfs.ext4 /dev/sdb",
            "chmod 777 -R /",
            "chown root:root -R /",
        ]

        for cmd in blocked_commands:
            pattern = re.escape(cmd)
            rule = InputPatternRule(
                "bash",
                "command",
                re.compile(pattern, re.IGNORECASE),
                PermissionLevel.DENY,
                f"Blocked command: {cmd}",
            )
            self.rules.append(rule)

        # File modifications default to ASK (unless overridden by safe file patterns)
        self.rules.append(ToolNameRule("write_file", PermissionLevel.ASK, "File modification"))
        self.rules.append(ToolNameRule("edit_file", PermissionLevel.ASK, "File modification"))

        # Bash commands default to ASK (unless overridden by safe/dangerous patterns)
        self.rules.append(ToolNameRule("bash", PermissionLevel.ASK, "Shell command execution"))

    def check_permission(self, tool_name: str, tool_input: Dict[str, Any]) -> PermissionRequest:
        """
        Check what permission level is needed for a tool call.

        Returns a PermissionRequest indicating the required level.
        """
        # YOLO mode: auto-approve everything except truly dangerous commands
        if self.yolo_mode:
            # Still check for DENY rules (safety first)
            for rule in self.rules:
                level = rule.check(tool_name, tool_input)
                if level == PermissionLevel.DENY:
                    return PermissionRequest(
                        tool_name=tool_name,
                        tool_input=tool_input,
                        level=level,
                        reason=rule.get_reason(),
                    )
            # Auto-approve everything else in YOLO mode
            return PermissionRequest(
                tool_name=tool_name,
                tool_input=tool_input,
                level=PermissionLevel.AUTO,
            )

        # Check all rules in order
        for rule in self.rules:
            level = rule.check(tool_name, tool_input)
            if level is not None:
                # Trust mode doesn't override DENY
                if level == PermissionLevel.ASK and self.trust_mode:
                    level = PermissionLevel.AUTO

                return PermissionRequest(
                    tool_name=tool_name,
                    tool_input=tool_input,
                    level=level,
                    reason=rule.get_reason(),
                )

        # Default: ASK (or AUTO in trust mode)
        default_level = PermissionLevel.ASK if not self.trust_mode else PermissionLevel.AUTO
        return PermissionRequest(
            tool_name=tool_name,
            tool_input=tool_input,
            level=default_level,
            reason="Default rule",
        )

    def format_permission_prompt(self, request: PermissionRequest) -> str:
        """Format a human-readable permission prompt."""
        tool_name = request.tool_name
        tool_input = request.tool_input

        if tool_name == "bash":
            return f"Run command: {tool_input.get('command', '')}"
        elif tool_name == "write_file":
            return f"Write to file: {tool_input.get('path', '')}"
        elif tool_name == "edit_file":
            return f"Edit file: {tool_input.get('path', '')}"
        else:
            return f"{tool_name}: {tool_input}"
