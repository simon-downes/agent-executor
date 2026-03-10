"""Tool registry and metadata."""

import subprocess
from dataclasses import dataclass


# Default environment variables loaded from kv store for all tools
# Keys are environment variable names, values are kv keys
DEFAULT_ENV_VARS = {
    "GH_TOKEN": "github.token",
}


@dataclass
class Tool:
    """Metadata for an executable tool."""

    name: str
    command: str
    config_dirs: list[str]
    default_args: list[str] | None = None
    env_vars: dict[str, str] | None = None  # Additional tool-specific env vars


def load_env_vars(tool: Tool) -> dict[str, str]:
    """
    Load environment variables from kv store.

    Merges DEFAULT_ENV_VARS with tool-specific env_vars.
    Silently skips any keys that aren't available.

    Args:
        tool: Tool to load environment variables for

    Returns:
        Dictionary of environment variable names to values
    """
    # Merge default and tool-specific env vars
    all_env_vars = {**DEFAULT_ENV_VARS}
    if tool.env_vars:
        all_env_vars.update(tool.env_vars)

    env = {}
    for env_name, kv_key in all_env_vars.items():
        try:
            result = subprocess.run(
                ["ak", "kv", "get", kv_key],
                capture_output=True,
                text=True,
                check=True,
            )
            value = result.stdout.strip()
            if value:
                env[env_name] = value
        except (subprocess.CalledProcessError, FileNotFoundError):
            # Skip if kv not available or key not found
            pass

    return env


TOOLS: dict[str, Tool] = {
    "toad": Tool(
        name="toad",
        command="toad",
        config_dirs=["~/.toad"],
    ),
    "kiro": Tool(
        name="kiro",
        command="kiro-cli",
        config_dirs=["~/.kiro", "~/Library/Application Support/kiro-cli"],
        default_args=["chat", "--agent", "principal-engineer-sandbox"],
    ),
}

DEFAULT_TOOL = "toad"
