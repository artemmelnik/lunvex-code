"""Rich terminal UI components."""

import json
import os
import sys
from contextlib import contextmanager
from typing import Any

from rich.console import Console
from rich.live import Live
from rich.markdown import Markdown
from rich.prompt import Prompt
from rich.text import Text
from rich.theme import Theme

from . import APP_CONTEXT_FILENAME, APP_DISPLAY_NAME

# Custom theme
THEME = Theme(
    {
        "info": "cyan",
        "warning": "yellow",
        "error": "red bold",
        "success": "green",
        "tool": "blue",
        "path": "magenta",
        "logo": "bold cyan",
        "logo.accent": "bold blue",
    }
)

console = Console(theme=THEME, force_terminal=True, color_system="auto")


# ASCII Art Logo
LOGO = r"""
[bold cyan]██╗     ██╗   ██╗███╗   ██╗██╗   ██╗███████╗██╗  ██╗[/bold cyan]
[bold cyan]██║     ██║   ██║████╗  ██║██║   ██║██╔════╝╚██╗██╔╝[/bold cyan]
[bold cyan]██║     ██║   ██║██╔██╗ ██║██║   ██║█████╗   ╚███╔╝ [/bold cyan]
[bold cyan]██║     ██║   ██║██║╚██╗██║╚██╗ ██╔╝██╔══╝   ██╔██╗ [/bold cyan]
[bold cyan]███████╗╚██████╔╝██║ ╚████║ ╚████╔╝ ███████╗██╔╝ ██╗[/bold cyan]
[bold cyan]╚══════╝ ╚═════╝ ╚═╝  ╚═══╝  ╚═══╝  ╚══════╝╚═╝  ╚═╝[/bold cyan]

[bold blue]  ██████╗ ██████╗ ██████╗ ███████╗[/bold blue]
[bold blue] ██╔════╝██╔═══██╗██╔══██╗██╔════╝[/bold blue]
[bold blue] ██║     ██║   ██║██║  ██║█████╗  [/bold blue]
[bold blue] ██║     ██║   ██║██║  ██║██╔══╝  [/bold blue]
[bold blue] ╚██████╗╚██████╔╝██████╔╝███████╗[/bold blue]
[bold blue]  ╚═════╝ ╚═════╝ ╚═════╝ ╚══════╝[/bold blue]
"""

LOGO_SMALL = r"""
[bold cyan]╔═══════════════════════════════════════╗[/bold cyan]
[bold cyan]║[/bold cyan]  [bold white]LunVex Code[/bold white] [dim]- AI Coding Assistant[/dim]   [bold cyan]║[/bold cyan]
[bold cyan]╚═══════════════════════════════════════╝[/bold cyan]
"""

LOGO_MINIMAL = r"""
[bold cyan]▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄[/bold cyan]
[bold cyan]█[/bold cyan] [bold white]⚡ LunVex Code[/bold white]                         [bold cyan]█[/bold cyan]
[bold cyan]█[/bold cyan] [dim]AI-powered coding assistant[/dim]            [bold cyan]█[/bold cyan]
[bold cyan]▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀[/bold cyan]
"""

FISH_LOGO = rf"""
[bold cyan]        ___[/bold cyan]
[bold cyan]      /`   `'.[/bold cyan]
[bold blue]     /  _ _   \[/bold blue]    [bold white]{APP_DISPLAY_NAME}[/bold white]
[bold blue]    | (@)(@)   |[/bold blue]   [dim]v{{version}}[/dim]
[bold cyan]    |    >    |[/bold cyan]
[bold cyan]     \  .__,  /[/bold cyan]    [dim]AI Coding Assistant[/dim]
[bold blue]      '.___.'[/bold blue]
"""


def print_banner(version: str) -> None:
    """Print the ASCII art banner."""
    console.print()
    console.print(LOGO)
    console.print(f"                    [dim]v{version}[/dim]")
    console.print()


def print_welcome(
    version: str, working_dir: str, context_loaded: bool = False, yolo_mode: bool = False
) -> None:
    """Print welcome message with ASCII art."""
    # Print the banner
    print_banner(version)

    # Print YOLO mode warning if enabled
    if yolo_mode:
        console.print()
        console.print("[bold red]  ⚠️  YOLO MODE ENABLED ⚠️[/bold red]")
        console.print("[yellow]  All permission prompts will be skipped![/yellow]")
        console.print("[dim]  (Dangerous operations like rm -rf / are still blocked)[/dim]")
        console.print()

    # Print status info
    console.print(f"  [dim]Directory:[/dim] [path]{working_dir}[/path]")
    if context_loaded:
        console.print(f"  [dim]Context:[/dim]   [success]{APP_CONTEXT_FILENAME} loaded[/success]")
    console.print()
    console.print(
        "  [dim]Type[/dim] [bold]help[/bold] [dim]for commands,[/dim] [bold]quit[/bold] [dim]to exit[/dim]"
    )
    console.print()
    console.print("[dim]─" * 50 + "[/dim]")
    console.print()


def print_assistant_message(content: str) -> None:
    """Print assistant's text response with markdown rendering."""
    if content:
        md = Markdown(content)
        console.print(md)
        console.print()


_current_live: Live | None = None
_thinking_prefix_pending = False


def print_stream_chunk(chunk: str) -> None:
    """Print a streaming chunk of text (no newline, immediate flush)."""
    global _current_live, _thinking_prefix_pending
    # Stop the whale animation if it's running
    if _current_live is not None:
        _current_live.stop()
        _current_live = None
    if _thinking_prefix_pending:
        print()
        print("  ", end="", flush=True)
        _thinking_prefix_pending = False
    # Use sys.stdout.write for immediate output without Rich formatting
    sys.stdout.write(chunk)
    sys.stdout.flush()


def end_stream() -> None:
    """End a streaming response (add newlines)."""
    print()
    print()


def print_tool_call(tool_name: str, tool_input: dict[str, Any]) -> None:
    """Print a tool call being made."""
    icon = get_tool_icon(tool_name)

    if tool_name == "bash":
        cmd = tool_input.get("command", "")
        console.print(f"{icon} [tool]bash[/tool]: {cmd}")
    elif tool_name == "read_file":
        path = tool_input.get("path", "")
        console.print(f"{icon} [tool]read_file[/tool]: [path]{path}[/path]")
    elif tool_name == "write_file":
        path = tool_input.get("path", "")
        console.print(f"{icon} [tool]write_file[/tool]: [path]{path}[/path]")
    elif tool_name == "edit_file":
        path = tool_input.get("path", "")
        old_preview = tool_input.get("old_str", "")[:50]
        console.print(f"{icon} [tool]edit_file[/tool]: [path]{path}[/path]")
        if old_preview:
            console.print(f'   old: "{old_preview}..."')
    elif tool_name == "glob":
        pattern = tool_input.get("pattern", "")
        console.print(f"{icon} [tool]glob[/tool]: {pattern}")
    elif tool_name == "grep":
        pattern = tool_input.get("pattern", "")
        path = tool_input.get("path", ".")
        console.print(f"{icon} [tool]grep[/tool]: '{pattern}' in [path]{path}[/path]")
    else:
        console.print(f"{icon} [tool]{tool_name}[/tool]: {json.dumps(tool_input)}")


def get_tool_icon(tool_name: str) -> str:
    """Get icon for a tool."""
    icons = {
        "read_file": "[cyan]>[/cyan]",
        "write_file": "[yellow]>[/yellow]",
        "edit_file": "[yellow]>[/yellow]",
        "bash": "[green]$[/green]",
        "glob": "[blue]>[/blue]",
        "grep": "[blue]>[/blue]",
    }
    return icons.get(tool_name, "[white]>[/white]")


def print_tool_result(result: str, success: bool = True, truncate: int = 500) -> None:
    """Print tool execution result."""
    if not result:
        return

    # Truncate for display
    display = result
    if len(result) > truncate:
        display = result[:truncate] + f"\n... ({len(result)} chars total)"

    if success:
        # Indent the output
        lines = display.split("\n")
        for line in lines:
            console.print(f"   {line}", highlight=False)
    else:
        console.print(f"   [error]{display}[/error]")


def print_error(message: str) -> None:
    """Print an error message."""
    console.print(f"[error]Error: {message}[/error]")


def print_success(message: str) -> None:
    """Print a success message."""
    console.print(f"[success]{message}[/success]")


def print_warning(message: str) -> None:
    """Print a warning message."""
    console.print(f"[warning]{message}[/warning]")


def print_info(message: str) -> None:
    """Print an info message."""
    console.print(f"[info]{message}[/info]")


def ask_permission(prompt: str, options: list[str] = None) -> str:
    """
    Ask user for permission.

    Args:
        prompt: The permission prompt to show
        options: List of options (default: y/n/always)

    Returns:
        User's choice as a string
    """
    if options is None:
        options = ["y", "n", "always"]

    options_str = "/".join(options)
    console.print(f"\n[warning]Permission required:[/warning] {prompt}")

    while True:
        choice = Prompt.ask(f"Allow? [{options_str}]", default="n").lower().strip()

        # Handle common inputs
        if choice in ("y", "yes"):
            return "y"
        elif choice in ("n", "no"):
            return "n"
        elif choice in ("a", "always"):
            return "always"
        elif choice in options:
            return choice
        else:
            console.print(f"Please enter one of: {options_str}")


def get_user_input(prompt: str = "> ") -> str:
    """Get input from user with nice prompt."""
    try:
        return Prompt.ask(f"[bold cyan]{prompt}[/bold cyan]")
    except (EOFError, KeyboardInterrupt):
        return ""


class CodingRobot:
    """Animated coding robot for thinking indicator."""

    # Robot frames (typing animation)
    ROBOT_FRAMES = [
        # Frame 1 - typing
        [
            r"    ╔══════════════╗    ",
            r"    ║ [green]█[/green] [green]█[/green] [green]█[/green] [green]█[/green] [green]█[/green] [green]█[/green] [green]█[/green] ║    ",
            r"    ╚══════════════╝    ",
            r"       /        \       ",
            r"      /  [blue]O[/blue]    [blue]O[/blue]  \      ",
            r"     /            \     ",
            r"    /    [yellow]────[/yellow]    \    ",
            r"   /              \   ",
        ],
        # Frame 2 - thinking
        [
            r"    ╔══════════════╗    ",
            r"    ║ [green]█[/green] [cyan]█[/cyan] [green]█[/green] [cyan]█[/cyan] [green]█[/green] [cyan]█[/cyan] [green]█[/green] ║    ",
            r"    ╚══════════════╝    ",
            r"       /        \       ",
            r"      /  [blue]●[/blue]    [blue]●[/blue]  \      ",
            r"     /            \     ",
            r"    /    [yellow]────[/yellow]    \    ",
            r"   /              \   ",
        ],
        # Frame 3 - processing
        [
            r"    ╔══════════════╗    ",
            r"    ║ [cyan]█[/cyan] [green]█[/green] [cyan]█[/cyan] [green]█[/green] [cyan]█[/cyan] [green]█[/green] [cyan]█[/cyan] ║    ",
            r"    ╚══════════════╝    ",
            r"       /        \       ",
            r"      /  [blue]O[/blue]    [blue]O[/blue]  \      ",
            r"     /            \     ",
            r"    /    [yellow]════[/yellow]    \    ",
            r"   /              \   ",
        ],
    ]

    # Code snippets that appear in the terminal
    CODE_SNIPPETS = [
        "print('Hello, World!')",
        "def solve():",
        "import numpy as np",
        "async def main():",
        "class Solution:",
        "const x = 42;",
        "<div>React</div>",
        "docker build -t app .",
        "git commit -m 'fix'",
        "SELECT * FROM users",
    ]

    # Terminal border animation
    TERMINAL_BORDERS = [
        "╔══════════════════════════════╗",
        "╠══════════════════════════════╣",
        "╟──────────────────────────────╢",
        "╠══════════════════════════════╣",
    ]

    def __init__(self, width: int = 40):
        self.width = width
        self.frame = 0
        self.code_index = 0
        self.border_index = 0

    def get_frame(self) -> Text:
        """Get the current animation frame as Rich Text."""
        robot_frame = self.ROBOT_FRAMES[self.frame % len(self.ROBOT_FRAMES)]
        border = self.TERMINAL_BORDERS[self.border_index % len(self.TERMINAL_BORDERS)]
        code = self.CODE_SNIPPETS[self.code_index % len(self.CODE_SNIPPETS)]

        # Build the frame
        lines = []

        # Add terminal border
        lines.append(f"[cyan]{border}[/cyan]")

        # Add code snippet in terminal
        code_padding = (len(border) - len(code) - 4) // 2
        code_line = f"[cyan]║[/cyan] {' ' * code_padding}[green]{code}[/green]{' ' * (len(border) - len(code) - code_padding - 4)}[cyan]║[/cyan]"
        lines.append(code_line)

        # Add bottom border
        lines.append(f"[cyan]{border}[/cyan]")
        lines.append("")

        # Add robot
        for line in robot_frame:
            lines.append(f"[blue]{line}[/blue]")

        # Add thinking text with animated dots
        dots = "." * ((self.frame % 4) + 1)
        status = ["Thinking", "Processing", "Analyzing", "Coding"][self.frame % 4]
        lines.append(f"\n[dim]  {status}{dots.ljust(4)}[/dim]")

        return "\n".join(lines)

    def update(self) -> None:
        """Update animation state."""
        self.frame += 1

        # Change code snippet every 3 frames
        if self.frame % 3 == 0:
            self.code_index += 1

        # Change border every 2 frames
        if self.frame % 2 == 0:
            self.border_index += 1

    def __rich__(self) -> Text:
        """Rich protocol for rendering."""
        self.update()
        return Text.from_markup(self.get_frame())


class NeuralNetwork:
    """Animated neural network for thinking indicator."""

    # Neural network frames
    NETWORK_FRAMES = [
        # Frame 1
        [
            r"    ○───○───○    ",
            r"   / \ / \ / \   ",
            r"  ○───○───○───○  ",
            r"   \ / \ / \ /   ",
            r"    ○───○───○    ",
        ],
        # Frame 2
        [
            r"    ●───○───○    ",
            r"   / \ / \ / \   ",
            r"  ○───●───○───○  ",
            r"   \ / \ / \ /   ",
            r"    ○───○───●    ",
        ],
        # Frame 3
        [
            r"    ○───●───○    ",
            r"   / \ / \ / \   ",
            r"  ○───○───●───○  ",
            r"   \ / \ / \ /   ",
            r"    ●───○───○    ",
        ],
        # Frame 4
        [
            r"    ○───○───●    ",
            r"   / \ / \ / \   ",
            r"  ●───○───○───○  ",
            r"   \ / \ / \ /   ",
            r"    ○───●───○    ",
        ],
    ]

    # Data flow patterns
    DATA_PATTERNS = [
        "01010101",
        "10101010",
        "00110011",
        "11001100",
        "11110000",
        "00001111",
    ]

    def __init__(self, width: int = 40):
        self.width = width
        self.frame = 0
        self.data_index = 0

    def get_frame(self) -> Text:
        """Get the current animation frame as Rich Text."""
        network_frame = self.NETWORK_FRAMES[self.frame % len(self.NETWORK_FRAMES)]
        data = self.DATA_PATTERNS[self.data_index % len(self.DATA_PATTERNS)]

        # Build the frame
        lines = []

        # Add title
        lines.append(f"[cyan]╔{'═' * (self.width - 2)}╗[/cyan]")
        lines.append("[cyan]║[/cyan][bold] Neural Network Processing [/bold][cyan]║[/cyan]")
        lines.append(f"[cyan]╚{'═' * (self.width - 2)}╝[/cyan]")
        lines.append("")

        # Add data flow
        data_padding = (self.width - len(data) - 4) // 2
        lines.append(f"[dim]{' ' * data_padding}[{data}][/dim]")
        lines.append("")

        # Add neural network
        for line in network_frame:
            padding = (self.width - len(line)) // 2
            lines.append(f"[blue]{' ' * padding}{line}[/blue]")

        # Add thinking text with animated dots
        dots = "." * ((self.frame % 4) + 1)
        status = ["Analyzing", "Processing", "Learning", "Optimizing"][self.frame % 4]
        lines.append(f"\n[dim]  {status}{dots.ljust(4)}[/dim]")

        return "\n".join(lines)

    def update(self) -> None:
        """Update animation state."""
        self.frame += 1

        # Change data pattern every 2 frames
        if self.frame % 2 == 0:
            self.data_index += 1

    def __rich__(self) -> Text:
        """Rich protocol for rendering."""
        self.update()
        return Text.from_markup(self.get_frame())


class PulsingOrb:
    """Animated pulsing orb for thinking indicator."""

    # Orb frames (pulsing animation)
    ORB_FRAMES = [
        # Small
        [
            r"         ",
            r"    ●    ",
            r"         ",
        ],
        # Medium
        [
            r"         ",
            r"   (●)   ",
            r"         ",
        ],
        # Large
        [
            r"    _    ",
            r"  ((●))  ",
            r"    ‾    ",
        ],
        # Medium
        [
            r"         ",
            r"   (●)   ",
            r"         ",
        ],
    ]

    # Ring patterns
    RING_PATTERNS = [
        "○ ○ ○ ○ ○",
        " ○ ○ ○ ○ ",
        "○ ○ ○ ○ ○",
        " ○ ○ ○ ○ ",
    ]

    def __init__(self, width: int = 40):
        self.width = width
        self.frame = 0
        self.ring_index = 0

    def get_frame(self) -> Text:
        """Get the current animation frame as Rich Text."""
        orb_frame = self.ORB_FRAMES[self.frame % len(self.ORB_FRAMES)]
        ring = self.RING_PATTERNS[self.ring_index % len(self.RING_PATTERNS)]

        # Build the frame
        lines = []

        # Add title
        lines.append(f"[cyan]╔{'═' * (self.width - 2)}╗[/cyan]")
        lines.append("[cyan]║[/cyan][bold] AI Processing Core [/bold][cyan]║[/cyan]")
        lines.append(f"[cyan]╚{'═' * (self.width - 2)}╝[/cyan]")
        lines.append("")

        # Add outer ring
        ring_padding = (self.width - len(ring) - 4) // 2
        lines.append(f"[dim]{' ' * ring_padding}{ring}[/dim]")
        lines.append("")

        # Add orb with padding
        for line in orb_frame:
            padding = (self.width - len(line)) // 2
            colored_line = line.replace("●", "[yellow]●[/yellow]")
            lines.append(f"[cyan]{' ' * padding}{colored_line}[/cyan]")

        # Add inner ring
        lines.append("")
        inner_ring = "◉ ◉ ◉ ◉ ◉" if self.frame % 2 == 0 else " ◉ ◉ ◉ ◉ "
        inner_padding = (self.width - len(inner_ring) - 4) // 2
        lines.append(f"[blue]{' ' * inner_padding}{inner_ring}[/blue]")

        # Add thinking text with animated dots
        dots = "." * ((self.frame % 4) + 1)
        status = ["Thinking", "Processing", "Computing", "Generating"][self.frame % 4]
        lines.append(f"\n[dim]  {status}{dots.ljust(4)}[/dim]")

        return "\n".join(lines)

    def update(self) -> None:
        """Update animation state."""
        self.frame += 1

        # Change ring pattern every frame
        self.ring_index += 1

    def __rich__(self) -> Text:
        """Rich protocol for rendering."""
        self.update()
        return Text.from_markup(self.get_frame())


class InlineDotsIndicator:
    """Compact inline thinking animation with animated dots only."""

    def __init__(self):
        self.frame = 0

    def get_frame(self) -> str:
        """Get the current inline frame."""
        dots = "." * ((self.frame % 3) + 1)
        return f"[dim]Thinking{dots.ljust(3)}[/dim]"

    def update(self) -> None:
        """Advance to the next frame."""
        self.frame += 1

    def __rich__(self) -> Text:
        """Rich protocol for rendering."""
        self.update()
        return Text.from_markup(self.get_frame())


def get_animation_type() -> str:
    """Get animation type from environment or default."""
    # Check if animations are disabled
    if os.environ.get("LUNVEX_NO_ANIMATION", "").lower() in ["1", "true", "yes", "on"]:
        return "none"

    # Check environment variable first
    env_type = os.environ.get("LUNVEX_ANIMATION", "").lower()
    if env_type in ["dots", "robot", "neural", "orb", "none"]:
        return env_type

    # Default to the compact inline dots indicator
    return "dots"


def get_animation(animation_type: str = None, width: int = 35):
    """Get animation instance by type."""
    if animation_type is None:
        animation_type = get_animation_type()

    if animation_type == "none":
        return None
    elif animation_type == "dots":
        return InlineDotsIndicator()
    elif animation_type == "neural":
        return NeuralNetwork(width=width)
    elif animation_type == "orb":
        return PulsingOrb(width=width)
    elif animation_type == "robot":
        return CodingRobot(width=width)
    else:
        # Default to none (no animation) for invalid types
        return None


@contextmanager
def print_thinking(animation_type: str = None):
    """Show an animation while thinking. Context manager that tracks the Live object."""
    global _current_live, _thinking_prefix_pending

    animation = get_animation(animation_type, width=35)

    # If animation is disabled, just print "Thinking..." and yield
    if animation is None:
        console.print("\n[dim]Thinking...[/dim]", end="")
        _thinking_prefix_pending = True
        try:
            yield
        finally:
            if _thinking_prefix_pending:
                console.print()
            _thinking_prefix_pending = False
        return

    # Otherwise show the animation
    live = Live(
        animation,
        console=console,
        refresh_per_second=8,
        transient=True,
    )
    _current_live = live
    _thinking_prefix_pending = True
    try:
        with live:
            yield
    finally:
        _current_live = None
        if _thinking_prefix_pending:
            console.print()
        _thinking_prefix_pending = False


def print_token_usage(prompt_tokens: int, completion_tokens: int, total_tokens: int) -> None:
    """Print token usage information."""
    console.print(
        f"\n[dim]Tokens: {prompt_tokens} prompt + {completion_tokens} completion = {total_tokens} total[/dim]"
    )


def print_goodbye() -> None:
    """Print goodbye message."""
    console.print("\n[cyan]Goodbye![/cyan]\n")
