"""Docker container operations."""

import sys
from pathlib import Path

import docker
from docker.errors import DockerException, NotFound

from ax.paths import MountConfig


class DockerManager:
    """Manages Docker container operations."""

    def __init__(self) -> None:
        """Initialize Docker client."""
        try:
            self.client = docker.from_env()
        except DockerException as e:
            print(f"Error: Docker is not available: {e}", file=sys.stderr)
            print("Ensure Docker daemon is running", file=sys.stderr)
            sys.exit(1)

    def generate_container_name(self, tool_name: str, project_dir: Path) -> str:
        """Generate container name from tool and project."""
        project_name = project_dir.name
        return f"ax-{tool_name}-{project_name}"

    def check_container_exists(self, container_name: str) -> bool:
        """Check if container with given name exists."""
        try:
            self.client.containers.get(container_name)
            return True
        except NotFound:
            return False

    def run_in_container(
        self,
        image: str,
        command: list[str],
        container_name: str,
        mounts: MountConfig,
    ) -> int:
        """
        Run command in Docker container.

        Args:
            image: Docker image name
            command: Command to execute
            container_name: Name for the container
            mounts: Mount configuration

        Returns:
            Exit code from container
        """
        if self.check_container_exists(container_name):
            print(
                f"Error: Container '{container_name}' already exists",
                file=sys.stderr,
            )
            print(
                f"Another session may be running. Stop it with: ax stop {container_name}",
                file=sys.stderr,
            )
            sys.exit(1)

        volumes = {
            str(mounts.project_dir): {"bind": "/workspace", "mode": "rw"},
            str(mounts.cli_tools_dir): {"bind": str(mounts.cli_tools_dir), "mode": "rw"},
            str(mounts.plans_dir): {"bind": str(mounts.plans_dir), "mode": "rw"},
        }

        for config_dir in mounts.tool_config_dirs:
            volumes[str(config_dir)] = {"bind": str(config_dir), "mode": "rw"}

        try:
            container = self.client.containers.run(
                image,
                command,
                name=container_name,
                volumes=volumes,
                working_dir="/workspace",
                stdin_open=True,
                tty=True,
                detach=False,
                remove=True,
                auto_remove=True,
            )
            return 0
        except KeyboardInterrupt:
            return 130
        except DockerException as e:
            print(f"Error running container: {e}", file=sys.stderr)
            return 1
