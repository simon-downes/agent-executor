"""Execution logic for running tools."""

import subprocess
import sys

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
