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
    from ax.tools import load_env_vars

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
        "-e",
        f"COLORTERM={os.environ.get('COLORTERM', 'truecolor')}",
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
    for config_entry in mount_config.tool_config_dirs:
        if isinstance(config_entry, tuple):
            # Explicit mapping: (host_path, container_path)
            host_path, container_path = config_entry
            # Replace ~ in container path with container home
            container_path = container_path.replace("~", container_home)
        else:
            # Auto-map: simple home directory replacement
            host_path = config_entry
            container_path = str(host_path).replace(str(Path.home()), container_home)

        cmd.extend(["-v", f"{host_path}:{container_path}"])

    # Add git config files
    for git_file in mount_config.git_config_files:
        container_git_path = str(git_file).replace(str(Path.home()), container_home)
        cmd.extend(["-v", f"{git_file}:{container_git_path}:ro"])

    # Add SSH keys
    for ssh_file in mount_config.ssh_key_files:
        container_ssh_path = str(ssh_file).replace(str(Path.home()), container_home)
        cmd.extend(["-v", f"{ssh_file}:{container_ssh_path}:ro"])

    # Add tool environment variables from kv store
    for env_name, env_value in load_env_vars(tool).items():
        cmd.extend(["-e", f"{env_name}={env_value}"])

    # Add image and command
    cmd.append(image)
    cmd.append(tool.command)
    if tool.default_args:
        cmd.extend(tool.default_args)
    cmd.extend(args)

    return cmd
