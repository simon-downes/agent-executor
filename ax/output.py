"""Rich terminal output utilities."""

import sys
from pathlib import Path

from rich.console import Console
from rich.panel import Panel

console = Console()
console_err = Console(stderr=True)


def print_success(message: str) -> None:
    """Print success message with green keyword."""
    console.print(f"[green]Success:[/green] {message}")


def print_error(message: str) -> None:
    """Print error message with red keyword."""
    console_err.print(f"[red]Error:[/red] {message}")


def print_warning(message: str) -> None:
    """Print warning message with yellow keyword."""
    console.print(f"[yellow]Warning:[/yellow] {message}")


def print_info(message: str) -> None:
    """Print info message with blue keyword."""
    console.print(f"[blue]Info:[/blue] {message}")


def highlight(text: str, color: str = "bright_blue") -> str:
    """Highlight identifier text."""
    return f"[{color}]{text}[/{color}]"


def display_header(
    tool_name: str,
    is_local: bool,
    project_dir: Path,
    container_name: str | None = None,
) -> None:
    """
    Display execution context header.
    
    Args:
        tool_name: Name of the tool being executed
        is_local: True if running locally, False if in sandbox
        project_dir: Project directory path
        container_name: Container name (sandbox only)
    """
    mode = "Local" if is_local else "Sandbox"
    mode_color = "yellow" if is_local else "green"
    border_style = "yellow" if is_local else "green"
    
    # Line 1: Mode and tool
    line1 = f"[{mode_color}]{mode}[/{mode_color}] • {highlight(tool_name, 'bright_magenta')}"
    
    # Line 2: Project info
    project_name = project_dir.name
    project_path = str(project_dir)
    
    if container_name:
        line2 = f"{highlight(project_name)} • {project_path} • {highlight(container_name, 'bright_blue')}"
    else:
        line2 = f"{highlight(project_name)} • {project_path}"
    
    content = f"{line1}\n{line2}"
    
    panel = Panel(
        content,
        border_style=border_style,
        padding=(0, 1),
    )
    
    console.print(panel)
