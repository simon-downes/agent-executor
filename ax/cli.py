"""CLI entry point for ax."""

import sys

import click

from ax.tools import DEFAULT_TOOL, TOOLS


class ToolCLI(click.MultiCommand):
    """Custom CLI that treats unknown commands as tool names."""

    def list_commands(self, ctx: click.Context) -> list[str]:
        """List all available commands (built-ins + tools)."""
        builtin = ["build", "list", "stop", "shell"]
        return builtin + sorted(TOOLS.keys())

    def get_command(self, ctx: click.Context, cmd_name: str) -> click.Command | None:
        """Get command by name, treating unknown commands as tools."""
        # Check if it's a built-in command
        builtin_commands = {
            "build": build,
            "list": list_sessions,
            "stop": stop,
            "shell": shell,
        }

        if cmd_name in builtin_commands:
            return builtin_commands[cmd_name]

        # Check if it's a tool
        if cmd_name in TOOLS:
            return create_tool_command(cmd_name)

        return None


def create_tool_command(tool_name: str) -> click.Command:
    """Create a Click command for a specific tool."""

    @click.command(
        name=tool_name,
        context_settings={"ignore_unknown_options": True, "allow_extra_args": True},
    )
    @click.option("--local", is_flag=True, help="Execute tool locally instead of in sandbox")
    @click.pass_context
    def tool_cmd(ctx: click.Context, local: bool) -> None:
        """Execute the tool."""
        args = ctx.args
        mode = "locally" if local else "in sandbox"
        click.echo(f"Would execute {tool_name} {mode} with args: {args}")

    return tool_cmd


@click.command(cls=ToolCLI, invoke_without_command=True)
@click.pass_context
def main(ctx: click.Context) -> None:
    """
    Unified execution hub for AI workflow tools.

    Runs tools in Docker sandbox by default, or locally with --local flag.
    """
    if ctx.invoked_subcommand is None:
        # No subcommand provided, run default tool
        click.echo(f"Would execute {DEFAULT_TOOL} in sandbox with args: []")


@click.command()
def build() -> None:
    """Build the sandbox Docker image."""
    click.echo("Build command not yet implemented")


@click.command()
def list_sessions() -> None:
    """List running ax sessions."""
    click.echo("List command not yet implemented")


@click.command()
@click.argument("session")
def stop(session: str) -> None:
    """Stop a running ax session."""
    click.echo(f"Stop command not yet implemented: {session}")


@click.command()
def shell() -> None:
    """Open a shell in the sandbox container."""
    click.echo("Shell command not yet implemented")


if __name__ == "__main__":
    main()
