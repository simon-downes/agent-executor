"""Rich terminal output utilities."""

from rich.console import Console

console = Console()


def print_success(message: str) -> None:
    """Print success message with green keyword."""
    console.print(f"[green]Success:[/green] {message}")


def print_error(message: str) -> None:
    """Print error message with red keyword."""
    console.print(f"[red]Error:[/red] {message}", err=True)


def print_warning(message: str) -> None:
    """Print warning message with yellow keyword."""
    console.print(f"[yellow]Warning:[/yellow] {message}")


def print_info(message: str) -> None:
    """Print info message with blue keyword."""
    console.print(f"[blue]Info:[/blue] {message}")


def highlight(text: str, color: str = "bright_blue") -> str:
    """Highlight identifier text."""
    return f"[{color}]{text}[/{color}]"
