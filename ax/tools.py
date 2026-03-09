"""Tool registry and metadata."""

from dataclasses import dataclass


@dataclass
class Tool:
    """Metadata for an executable tool."""

    name: str
    command: str
    config_dirs: list[str]
    default_args: list[str] | None = None


TOOLS: dict[str, Tool] = {
    "toad": Tool(
        name="toad",
        command="toad",
        config_dirs=["~/.toad"],
    ),
    "kiro": Tool(
        name="kiro",
        command="kiro-cli",
        config_dirs=["~/.kiro"],
    ),
}

DEFAULT_TOOL = "toad"
