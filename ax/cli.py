"""CLI entry point for ax."""

import sys

import click

from ax.executor import execute_local, execute_sandbox
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
        context_settings={
            "ignore_unknown_options": True,
            "allow_extra_args": True,
        },
        add_help_option=False,
    )
    @click.option("--local", is_flag=True, help="Execute tool locally instead of in sandbox")
    @click.pass_context
    def tool_cmd(ctx: click.Context, local: bool) -> None:
        """Execute the tool."""
        tool = TOOLS[tool_name]
        args = ctx.args

        if local:
            exit_code = execute_local(tool, args)
        else:
            exit_code = execute_sandbox(tool, args)

        sys.exit(exit_code)

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
        tool = TOOLS[DEFAULT_TOOL]
        exit_code = execute_sandbox(tool, [])
        sys.exit(exit_code)


@click.command()
def build() -> None:
    """Build the sandbox Docker image."""
    import subprocess

    click.echo("Building ax-sandbox image...")
    try:
        result = subprocess.run(
            ["docker", "build", "-t", "ax-sandbox", "."],
            check=False,
        )
        sys.exit(result.returncode)
    except FileNotFoundError:
        click.echo("Error: docker command not found", err=True)
        sys.exit(1)
    except KeyboardInterrupt:
        sys.exit(130)


@click.command()
def list_sessions() -> None:
    """List running ax sessions."""
    import subprocess

    try:
        subprocess.run(["docker", "ps", "--filter", "name=ax-*"], check=False)
    except FileNotFoundError:
        click.echo("Error: docker command not found", err=True)
        sys.exit(1)


@click.command()
@click.argument("session")
def stop(session: str) -> None:
    """Stop a running ax session."""
    import subprocess

    try:
        result = subprocess.run(["docker", "stop", session], check=False)
        sys.exit(result.returncode)
    except FileNotFoundError:
        click.echo("Error: docker command not found", err=True)
        sys.exit(1)


@click.command()
def shell() -> None:
    """Open a shell in the sandbox container."""
    from ax.docker_manager import DockerManager
    from ax.paths import get_mount_config

    mount_config = get_mount_config([])
    docker_mgr = DockerManager()

    container_name = f"ax-shell-{mount_config.project_dir.name}"

    volumes = {
        str(mount_config.project_dir): {"bind": "/workspace", "mode": "rw"},
        str(mount_config.cli_tools_dir): {"bind": str(mount_config.cli_tools_dir), "mode": "rw"},
        str(mount_config.plans_dir): {"bind": str(mount_config.plans_dir), "mode": "rw"},
    }

    try:
        docker_mgr.client.containers.run(
            "ax-sandbox",
            "bash",
            name=container_name,
            volumes=volumes,
            working_dir="/workspace",
            stdin_open=True,
            tty=True,
            detach=False,
            remove=True,
            auto_remove=True,
        )
    except KeyboardInterrupt:
        pass
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
