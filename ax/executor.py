"""Execution logic for running tools."""

import subprocess
import sys

from ax.docker_manager import DockerManager
from ax.paths import get_mount_config
from ax.tools import Tool


def execute_local(tool: Tool, args: list[str]) -> int:
    """
    Execute tool locally via subprocess.

    Args:
        tool: Tool to execute
        args: Arguments to pass to tool

    Returns:
        Exit code from tool process
    """
    cmd = [tool.command] + (tool.default_args or []) + args

    try:
        result = subprocess.run(cmd)
        return result.returncode
    except FileNotFoundError:
        print(f"Error: Tool '{tool.command}' not found", file=sys.stderr)
        print(f"Ensure {tool.name} is installed and in PATH", file=sys.stderr)
        return 127
    except KeyboardInterrupt:
        return 130


def execute_sandbox(tool: Tool, args: list[str], image: str = "ax-sandbox") -> int:
    """
    Execute tool in Docker sandbox.

    Args:
        tool: Tool to execute
        args: Arguments to pass to tool
        image: Docker image name

    Returns:
        Exit code from container
    """
    mount_config = get_mount_config(tool.config_dirs)
    docker_mgr = DockerManager()

    container_name = docker_mgr.generate_container_name(
        tool.name, mount_config.project_dir
    )

    cmd = [tool.command] + (tool.default_args or []) + args

    return docker_mgr.run_in_container(image, cmd, container_name, mount_config)
