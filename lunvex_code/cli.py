"""CLI entry point for LunVex Code."""

import os
import sys
from typing import Optional

import typer
from dotenv import load_dotenv
from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory, InMemoryHistory
from rich.console import Console

from . import (
    APP_COMMAND_NAME,
    APP_CONTEXT_FILENAME,
    APP_DISPLAY_NAME,
    APP_STATE_DIRNAME,
    CACHE_MAX_SIZE,
    CACHE_TTL_SECONDS,
    LLM_CACHE_MAX_SIZE,
    LLM_CACHE_TTL_SECONDS,
    __version__,
    ui,
)
from .agent import Agent, AgentConfig
from .cache import configure_cache
from .context import get_project_context
from .llm import LunVexClient
from .llm_cache import configure_llm_cache

# Load environment variables from .env file
load_dotenv()

# Configure caches from environment variables
configure_cache(max_size=CACHE_MAX_SIZE, ttl_seconds=CACHE_TTL_SECONDS)
# Note: LLM cache is configured lazily when first accessed

app = typer.Typer(
    name=APP_COMMAND_NAME,
    help="Terminal AI coding assistant for real projects",
    add_completion=False,
)

console = Console()


def get_prompt_session() -> PromptSession:
    """Create a prompt session with history."""
    history_dir = os.path.expanduser(f"~/{APP_STATE_DIRNAME}")
    history_file = os.path.join(history_dir, "prompt_history")

    try:
        os.makedirs(history_dir, exist_ok=True)
        with open(history_file, "ab"):
            pass
        history = FileHistory(history_file)
    except OSError:
        history = InMemoryHistory()

    return PromptSession(history=history)


def interactive_loop(agent: Agent) -> None:
    """Run the interactive REPL loop."""
    session = get_prompt_session()

    while True:
        try:
            # Get user input
            user_input = session.prompt("\n> ").strip()

            if not user_input:
                continue

            # Handle special commands
            if user_input.lower() in ("quit", "exit", "q"):
                ui.print_goodbye()
                break

            if user_input.lower() == "clear":
                agent.reset()
                console.print("[info]Conversation cleared.[/info]")
                continue

            if user_input.lower() == "help":
                print_help(agent)
                continue

            # Toggle YOLO mode
            if user_input.lower() in ("/yolo", "yolo"):
                agent.permissions.yolo_mode = not agent.permissions.yolo_mode
                agent.config.yolo_mode = agent.permissions.yolo_mode
                if agent.permissions.yolo_mode:
                    console.print("[bold red]⚠️  YOLO MODE ENABLED ⚠️[/bold red]")
                    console.print("[yellow]All permission prompts will be skipped![/yellow]")
                else:
                    console.print("[green]YOLO mode disabled.[/green]")
                    console.print("[dim]Permission prompts are now active.[/dim]")
                continue

            # Toggle trust mode
            if user_input.lower() in ("/trust", "trust"):
                agent.permissions.trust_mode = not agent.permissions.trust_mode
                agent.config.trust_mode = agent.permissions.trust_mode
                if agent.permissions.trust_mode:
                    console.print("[cyan]Trust mode enabled.[/cyan]")
                else:
                    console.print("[dim]Trust mode disabled.[/dim]")
                continue

            # Show current mode status
            if user_input.lower() in ("/status", "status"):
                print_status(agent)
                continue

            # Process the message
            agent.chat(user_input)

        except KeyboardInterrupt:
            console.print("\n[dim]Use 'quit' to exit[/dim]")
            continue

        except EOFError:
            ui.print_goodbye()
            break


def print_help(agent: Agent) -> None:
    """Print help information."""
    yolo_status = "[red]ON[/red]" if agent.permissions.yolo_mode else "[dim]off[/dim]"
    trust_status = "[cyan]ON[/cyan]" if agent.permissions.trust_mode else "[dim]off[/dim]"

    console.print(f"""
[bold]Commands:[/bold]
  quit, exit, q  - Exit the program
  clear          - Clear conversation history
  help           - Show this help message

[bold]Mode Commands:[/bold]
  /yolo          - Toggle YOLO mode (currently {yolo_status})
  /trust         - Toggle trust mode (currently {trust_status})
  /status        - Show current mode status

[bold]Tips:[/bold]
  - Ask the AI to read files before editing them
  - Use 'always' when prompted to auto-approve similar operations
  - Create a LUNVEX.md file in your project root for project-specific context
""")


def print_status(agent: Agent) -> None:
    """Print current mode status."""
    console.print("\n[bold]Current Status:[/bold]")

    if agent.permissions.yolo_mode:
        console.print("  YOLO Mode:  [bold red]ON[/bold red] (all prompts skipped)")
    else:
        console.print("  YOLO Mode:  [dim]off[/dim]")

    if agent.permissions.trust_mode:
        console.print("  Trust Mode: [cyan]ON[/cyan] (safe ops auto-approved)")
    else:
        console.print("  Trust Mode: [dim]off[/dim]")

    console.print(f"  Model:      [blue]{agent.client.model}[/blue]")
    console.print()


def create_and_run_agent(
    task: Optional[str],
    model: str,
    trust: bool,
    yolo: bool,
    max_turns: int,
    verbose: bool,
    no_context: bool,
    no_animation: bool = False,
    no_planning: bool = False,
) -> None:
    """Create an agent and run it with the given task or in interactive mode."""
    api_key = os.environ.get("DEEPSEEK_API_KEY")
    if not api_key:
        console.print(
            "[error]Error: API key environment variable not set.[/error]\n"
            "Get your API key from: https://platform.deepseek.com/\n"
            "Then set it: export DEEPSEEK_API_KEY=your_key_here"
        )
        raise typer.Exit(1)

    # Set animation preference
    if no_animation:
        os.environ["LUNVEX_NO_ANIMATION"] = "1"

    # Get project context
    context = get_project_context(".")
    context_loaded = context.project_md is not None

    if no_context:
        context.project_md = None
        context_loaded = False

    # Print welcome
    ui.print_welcome(__version__, context.working_dir, context_loaded, yolo_mode=yolo)

    # Create agent
    try:
        client = LunVexClient(api_key=api_key, model=model)
        config = AgentConfig(
            max_turns=max_turns,
            trust_mode=trust,
            yolo_mode=yolo,
            verbose=verbose,
        )
        agent = Agent(client=client, context=context, config=config)

    except Exception as e:
        console.print(f"[error]Failed to initialize: {e}[/error]")
        raise typer.Exit(1)

    # Run task or interactive mode
    if task:
        # Single task mode
        try:
            agent.run(task, use_planning=not no_planning)
        except KeyboardInterrupt:
            console.print("\n[warning]Interrupted[/warning]")
            raise typer.Exit(130)
    else:
        # Interactive mode
        interactive_loop(agent)


@app.command()
def run(
    task: Optional[str] = typer.Argument(
        None,
        help="Task to execute (if not provided, starts interactive mode)",
    ),
    model: str = typer.Option(
        "deepseek-chat",
        "--model",
        "-m",
        help="Model to use",
    ),
    trust: bool = typer.Option(
        False,
        "--trust",
        "-t",
        help="Trust mode: auto-approve safe operations",
    ),
    yolo: bool = typer.Option(
        False,
        "--dangerously-skip-permissions",
        "--yolo",
        help="YOLO mode: skip ALL permission prompts (use with caution!)",
    ),
    max_turns: int = typer.Option(
        50,
        "--max-turns",
        help="Maximum turns per task",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Verbose output",
    ),
    no_context: bool = typer.Option(
        False,
        "--no-context",
        help="Don't load project context from LUNVEX.md",
    ),
    no_animation: bool = typer.Option(
        False,
        "--no-animation",
        help="Disable thinking animations (show 'Thinking...' instead)",
    ),
    no_planning: bool = typer.Option(
        False,
        "--no-planning",
        help="Disable automatic task planning for complex tasks",
    ),
) -> None:
    """
    Run LunVex Code with a task or in interactive mode.

    Examples:
        lunvex-code run
        lunvex-code run "Fix the bug in auth.py"
        lunvex-code run --trust "Run the tests"
        lunvex-code run --yolo "Refactor the entire codebase"
        lunvex-code run --no-animation "Analyze the code"
        lunvex-code run --no-planning "Simple task"  # Disable task planning
    """
    create_and_run_agent(task, model, trust, yolo, max_turns, verbose, no_context, no_animation, no_planning)


@app.command()
def init() -> None:
    """Initialize a LUNVEX.md file in the current directory."""
    context_md_path = APP_CONTEXT_FILENAME

    if os.path.exists(context_md_path):
        console.print(f"[warning]{context_md_path} already exists[/warning]")
        raise typer.Exit(1)

    template = f"""# {APP_CONTEXT_FILENAME}

## Project Overview
Describe your project here.

## Key Commands
- `make test`: Run tests
- `make lint`: Run linting
- `npm run dev`: Start development server

## Architecture
- `src/`: Source code
- `tests/`: Test files
- `docs/`: Documentation

## Conventions
- List your coding conventions here
- Style guides, patterns to follow

## Known Issues
- Document any known issues or gotchas
"""

    with open(context_md_path, "w") as f:
        f.write(template)

    console.print(f"[success]Created {context_md_path}[/success]")
    console.print(f"Edit {context_md_path} to add project-specific context for the AI.")


@app.command()
def history(
    limit: int = typer.Option(20, "--limit", "-n", help="Number of sessions to show"),
) -> None:
    """Show recent conversation history."""
    from .conversation import ConversationStore

    store = ConversationStore()
    sessions = store.list_sessions(limit=limit)

    if not sessions:
        console.print("[dim]No conversation history found.[/dim]")
        return

    console.print("[bold]Recent sessions:[/bold]\n")
    for session in sessions:
        console.print(f"  {session['id']}  {session['timestamp']}")


@app.command()
def version() -> None:
    """Show version information."""
    console.print(f"{APP_DISPLAY_NAME} v{__version__}")


@app.command()
def cache_stats() -> None:
    """Show file cache statistics."""
    from .cache import get_file_cache
    
    cache = get_file_cache()
    stats = cache.get_stats()
    
    console.print("[bold]File Cache Statistics:[/bold]")
    console.print(f"  Size: {stats['size']}/{stats['max_size']} files")
    console.print(f"  Hits: {stats['hits']}")
    console.print(f"  Misses: {stats['misses']}")
    console.print(f"  Hit Rate: {stats['hit_rate']}")
    console.print(f"  TTL: {stats['ttl_seconds']} seconds")


@app.command()
def clear_cache() -> None:
    """Clear all entries from the file cache."""
    from .cache import get_file_cache
    
    cache = get_file_cache()
    cache.clear()
    
    console.print("[green]✓[/green] File cache cleared successfully.")


@app.command()
def configure_cache(
    max_size: int = typer.Option(100, help="Maximum number of files to cache"),
    ttl_seconds: int = typer.Option(300, help="Time-to-live for cache entries in seconds"),
) -> None:
    """Configure file cache settings."""
    from .cache import configure_cache
    
    if max_size <= 0:
        console.print("[red]Error:[/red] max_size must be positive")
        raise typer.Exit(1)
    
    if ttl_seconds <= 0:
        console.print("[red]Error:[/red] ttl_seconds must be positive")
        raise typer.Exit(1)
    
    configure_cache(max_size=max_size, ttl_seconds=ttl_seconds)
    console.print(f"[green]✓[/green] Cache configured: max_size={max_size}, ttl_seconds={ttl_seconds}")


@app.command()
def llm_cache_stats() -> None:
    """Show LLM cache statistics."""
    from .llm_cache import get_llm_cache

    cache = get_llm_cache()
    stats = cache.get_stats()

    console.print("[bold]LLM Cache Statistics:[/bold]")
    console.print(f"  Size: {stats['current_size']}/{stats['max_size']} responses")
    console.print(f"  Hits: {stats['hits']}")
    console.print(f"  Misses: {stats['misses']}")
    console.print(f"  Hit Rate: {stats['hit_rate']:.1%}")
    console.print(f"  Tokens Saved: {stats['tokens_saved']:,}")
    console.print(f"  TTL: {stats['ttl_seconds']} seconds ({stats['ttl_seconds']/3600:.1f} hours)")
    
    if stats['current_size'] > 0:
        oldest_age = int(time.time() - stats['oldest_entry'])
        console.print(f"  Oldest Entry: {oldest_age} seconds ago")
        console.print(f"  Most Accessed: {stats['most_accessed']} hits")


@app.command()
def clear_llm_cache() -> None:
    """Clear all entries from the LLM cache."""
    from .llm_cache import get_llm_cache

    cache = get_llm_cache()
    cache.clear()

    console.print("[green]✓[/green] LLM cache cleared successfully.")


@app.command()
def configure_llm_cache(
    max_size: int = typer.Option(100, help="Maximum number of responses to cache"),
    ttl_seconds: int = typer.Option(3600, help="Time-to-live for cache entries in seconds"),
) -> None:
    """Configure LLM cache settings."""
    from .llm_cache import configure_llm_cache, save_llm_cache

    if max_size <= 0:
        console.print("[red]Error:[/red] max_size must be positive")
        raise typer.Exit(1)

    if ttl_seconds <= 0:
        console.print("[red]Error:[/red] ttl_seconds must be positive")
        raise typer.Exit(1)

    configure_llm_cache(max_size=max_size, ttl_seconds=ttl_seconds)
    save_llm_cache()
    console.print(f"[green]✓[/green] LLM cache configured: max_size={max_size}, ttl_seconds={ttl_seconds}")
    console.print(f"[dim]Configuration saved to persistent storage[/dim]")


# Import time for llm_cache_stats
import time


def main():
    """Main entry point - defaults to interactive mode if no args."""
    # If no arguments provided, default to 'run' command
    if len(sys.argv) == 1:
        sys.argv.append("run")
    app()


if __name__ == "__main__":
    main()
