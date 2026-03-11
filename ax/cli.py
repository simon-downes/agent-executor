"""CLI entry point for ax."""

import sys

import click

from ax.constants import CONTAINER_PREFIX, IMAGE_NAME
from ax.executor import execute_local, execute_sandbox
from ax.output import display_header, print_error, print_info, print_success
from ax.paths import get_mount_config
from ax.tools import DEFAULT_TOOL, TOOLS


class ToolCLI(click.MultiCommand):
    """Custom CLI that treats unknown commands as tool names."""

    def list_commands(self, ctx: click.Context) -> list[str]:
        """List all available commands (built-ins + tools)."""
        builtin = ["build", "list", "stop"]
        return builtin + sorted(TOOLS.keys())

    def get_command(self, ctx: click.Context, cmd_name: str) -> click.Command | None:
        """Get command by name, treating unknown commands as tools."""
        # Check if it's a built-in command
        builtin_commands = {
            "build": build,
            "list": list_sessions,
            "stop": stop,
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

        # Get mount config and display header
        try:
            mount_config = get_mount_config(tool.config_dirs)

            if local:
                display_header(tool_name, is_local=True, project_dir=mount_config.project_dir)
                exit_code = execute_local(tool, args, mount_config)
            else:
                from docker.errors import DockerException

                from ax.docker_manager import DockerManager

                try:
                    docker_mgr = DockerManager()
                except DockerException as e:
                    print_error(str(e))
                    print("Ensure Docker daemon is running", file=sys.stderr)
                    sys.exit(1)

                container_name = docker_mgr.generate_container_name(
                    tool_name, mount_config.project_dir
                )
                display_header(
                    tool_name,
                    is_local=False,
                    project_dir=mount_config.project_dir,
                    container_name=container_name,
                )
                exit_code = execute_sandbox(tool, args, mount_config)
        except Exception as e:
            print_error(str(e))
            sys.exit(1)

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
        try:
            mount_config = get_mount_config(tool.config_dirs)
            exit_code = execute_sandbox(tool, [], mount_config)
        except Exception as e:
            print_error(str(e))
            sys.exit(1)
        sys.exit(exit_code)


@click.command()
def build() -> None:
    """Build the sandbox Docker image."""
    from docker.errors import DockerException

    from ax.docker_manager import DockerManager

    print_info(f"Building {IMAGE_NAME} image...")
    try:
        docker_mgr = DockerManager()
        docker_mgr.build_image(IMAGE_NAME)
        print_success(f"Built {IMAGE_NAME}")
    except DockerException as e:
        print_error(f"Docker error: {e}")
        sys.exit(1)


@click.command()
def list_sessions() -> None:
    """List running ax sessions."""
    from docker.errors import DockerException

    from ax.docker_manager import DockerManager
    from ax.output import console, highlight

    try:
        docker_mgr = DockerManager()
        containers = docker_mgr.list_containers(CONTAINER_PREFIX)

        if not containers:
            print("No active sessions")
            return

        for c in containers:
            name = highlight(c.name, "bright_blue")
            status_color = "green" if c.status == "running" else "yellow"
            status = f"[{status_color}]{c.status}[/{status_color}]"
            console.print(f"{name}  {status}  {c.image}")
    except DockerException as e:
        print_error(f"Docker error: {e}")
        sys.exit(1)


@click.command()
@click.argument("session")
def stop(session: str) -> None:
    """Stop a running ax session."""
    from docker.errors import DockerException, NotFound

    from ax.docker_manager import DockerManager

    try:
        docker_mgr = DockerManager()
        docker_mgr.stop_container(session)
        print_success(f"Stopped {session}")
    except NotFound:
        print_error(f"Container {session} not found")
        sys.exit(1)
    except DockerException as e:
        print_error(f"Docker error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
