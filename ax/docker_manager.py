"""Docker container operations."""

import subprocess
from dataclasses import dataclass
from pathlib import Path

import docker
from docker.errors import DockerException, NotFound

from ax.constants import CONTAINER_PREFIX


@dataclass
class ContainerInfo:
    """Essential container information."""

    name: str
    status: str
    image: str
    created: str


class DockerManager:
    """Manages Docker container operations."""

    def __init__(self) -> None:
        """Initialize Docker client with socket detection.

        Raises:
            DockerException: If Docker is not available or connection fails
        """
        # Try Colima socket first (macOS)
        colima_socket = Path.home() / ".colima" / "default" / "docker.sock"

        if colima_socket.exists():
            socket_url = f"unix://{colima_socket}"
            try:
                self.client = docker.DockerClient(base_url=socket_url)
                # Test connection
                self.client.ping()
                return
            except DockerException:
                pass  # Fall through to standard socket

        # Try standard Docker socket
        try:
            self.client = docker.from_env()
            self.client.ping()
        except DockerException as e:
            raise DockerException(f"Docker is not available: {e}") from e

    def generate_container_name(self, tool_name: str, project_dir: Path) -> str:
        """Generate container name from tool and project."""
        project_name = project_dir.name
        return f"{CONTAINER_PREFIX}{tool_name}-{project_name}"

    def check_container_exists(self, container_name: str) -> bool:
        """Check if container with given name exists."""
        try:
            self.client.containers.get(container_name)
            return True
        except NotFound:
            return False

    def build_image(self, image_name: str, context_path: Path = Path(".")) -> None:
        """Build Docker image with host user baked in."""
        from ax.constants import HOST_UID, HOST_USERNAME

        result = subprocess.run(
            [
                "docker",
                "build",
                "--build-arg",
                f"USERNAME={HOST_USERNAME}",
                "--build-arg",
                f"USER_UID={HOST_UID}",
                "-t",
                image_name,
                str(context_path),
            ],
            check=False,
        )
        if result.returncode != 0:
            raise DockerException(f"Build failed with exit code {result.returncode}")

    def list_containers(self, name_prefix: str) -> list[ContainerInfo]:
        """List containers matching name prefix."""
        containers = self.client.containers.list(all=True, filters={"name": name_prefix})
        return [
            ContainerInfo(
                name=c.name,
                status=c.status,
                image=c.image.tags[0] if c.image.tags else c.image.short_id,
                created=c.attrs["Created"],
            )
            for c in containers
        ]

    def stop_container(self, name: str) -> None:
        """Stop container by name. Raises NotFound if doesn't exist."""
        container = self.client.containers.get(name)
        container.stop()

    def run_container(self, cmd: list[str]) -> int:
        """Run container via subprocess. Return exit code."""
        try:
            result = subprocess.run(cmd, check=False)
            return result.returncode
        except KeyboardInterrupt:
            return 130
