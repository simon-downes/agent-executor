"""Execution logic for running tools."""

import os
import subprocess
import sys
from pathlib import Path

from ax.constants import IMAGE_NAME
from ax.docker_manager import DockerManager
from ax.output import print_error
from ax.paths import MountConfig
from ax.tools import Tool


def execute_local(tool: Tool, args: list[str], mount_config: MountConfig) -> int:
    """
    Execute tool locally via subprocess.

    Args:
        tool: Tool to execute
        args: Arguments to pass to tool
        mount_config: Mount configuration (unused for local execution)

    Returns:
        Exit code from tool process
    """
    cmd = [tool.command] + (tool.default_args or []) + args

    try:
        result = subprocess.run(cmd, check=False)
        return result.returncode
    except FileNotFoundError:
        print(f"Error: Tool '{tool.command}' not found", file=sys.stderr)
        print(f"Ensure {tool.name} is installed and in PATH", file=sys.stderr)
        return 127
    except KeyboardInterrupt:
        return 130


def execute_sandbox(
    tool: Tool, args: list[str], mount_config: MountConfig, image: str = IMAGE_NAME
) -> int:
    """
    Execute tool in Docker sandbox.

    Args:
        tool: Tool to execute
        args: Arguments to pass to tool
        mount_config: Mount configuration
        image: Docker image name

    Returns:
        Exit code from container
    """
    docker_mgr = DockerManager()

    container_name = docker_mgr.generate_container_name(tool.name, mount_config.project_dir)

    # Check if container already exists
    if docker_mgr.check_container_exists(container_name):
        print_error(f"Container [bright_blue]{container_name}[/bright_blue] already exists")
        print(
            f"Another session may be running. Stop it with: ax stop {container_name}",
            file=sys.stderr,
        )
        return 1

    cmd = build_docker_run_cmd(container_name, mount_config, image, tool, args)
    return docker_mgr.run_container(cmd)


def build_docker_run_cmd(
    container_name: str, mount_config: MountConfig, image: str, tool: Tool, args: list[str]
) -> list[str]:
    """Build docker run command with standard mounts."""
    from ax.constants import HOST_USERNAME

    # Mount project to ~/dev/<project> in container
    project_name = mount_config.project_dir.name
    container_project_path = f"/home/{HOST_USERNAME}/dev/{project_name}"
    container_home = f"/home/{HOST_USERNAME}"

    cmd = [
        "docker",
        "run",
        "--rm",
        "--name",
        container_name,
        "-e",
        f"TERM={os.environ.get('TERM', 'xterm-256color')}",
        "-v",
        f"{mount_config.project_dir}:{container_project_path}",
        "-v",
        f"{mount_config.cli_tools_dir}:{container_home}/cli-tools",
        "-v",
        f"{mount_config.plans_dir}:{container_home}/plans",
        "-w",
        container_project_path,
    ]

    # Add -it only if stdin is a TTY
    if sys.stdin.isatty():
        cmd.insert(3, "-it")

    # Add tool config directories
    for config_dir in mount_config.tool_config_dirs:
        # Mount to same path in container (e.g., ~/.kiro -> /home/user/.kiro)
        container_config_path = str(config_dir).replace(str(Path.home()), container_home)
        cmd.extend(["-v", f"{config_dir}:{container_config_path}"])

    # Add image and command
    cmd.append(image)
    cmd.append(tool.command)
    if tool.default_args:
        cmd.extend(tool.default_args)
    cmd.extend(args)

    return cmd
