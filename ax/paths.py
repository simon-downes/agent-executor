"""Path resolution and mount logic."""

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass
class MountConfig:
    """Configuration for directory mounts."""

    project_dir: Path
    cli_tools_dir: Path
    plans_dir: Path
    tool_config_dirs: list[Path]


class PathResolutionError(Exception):
    """Raised when path resolution fails."""

    pass


def resolve_project_mount(cwd: Path, dev_root: Path) -> Path:
    """
    Resolve project mount directory based on ~/dev ancestry.

    If CWD is ~/dev/foo/bar, returns ~/dev/foo
    If CWD is ~/dev/foo, returns ~/dev/foo
    If CWD is outside ~/dev, raises PathResolutionError

    Args:
        cwd: Current working directory
        dev_root: Path to ~/dev directory

    Returns:
        Path to project root (first subdirectory under ~/dev)

    Raises:
        PathResolutionError: If CWD is not under ~/dev
    """
    try:
        relative = cwd.relative_to(dev_root)
    except ValueError:
        raise PathResolutionError(
            f"Current directory must be under {dev_root}\n"
            f"Current directory: {cwd}"
        )

    parts = relative.parts
    if not parts:
        raise PathResolutionError(
            f"Cannot run from {dev_root} directly\n"
            "Change to a project directory under ~/dev"
        )

    return dev_root / parts[0]


def get_mount_config(tool_config_dirs: list[str]) -> MountConfig:
    """
    Get mount configuration for current context.

    Args:
        tool_config_dirs: List of tool-specific config directories (may contain ~)

    Returns:
        MountConfig with resolved paths

    Raises:
        PathResolutionError: If path resolution fails
    """
    cwd = Path.cwd()
    home = Path.home()
    dev_root = home / "dev"

    project_dir = resolve_project_mount(cwd, dev_root)
    cli_tools_dir = home / "cli-tools"
    plans_dir = home / "plans"

    tool_configs = [Path(d).expanduser() for d in tool_config_dirs]

    return MountConfig(
        project_dir=project_dir,
        cli_tools_dir=cli_tools_dir,
        plans_dir=plans_dir,
        tool_config_dirs=tool_configs,
    )
