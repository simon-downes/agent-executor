# ax - AI Agent Executor

Unified execution hub for AI agent tools, running them in isolated Docker sandbox containers by default, or directly on the host system with the `--local` flag.

## Overview

`ax` provides a consistent interface for running AI agent tools (like kiro and toad) with automatic project detection, directory mounting, and session management. By default, tools run in isolated Docker containers with pre-configured development tooling, ensuring consistent environments across different projects and machines.

## Quick Start

```bash
# Install dependencies
uv sync

# Build the sandbox image
ax build

# Run default tool (toad) in sandbox
ax

# Run kiro in sandbox
ax kiro chat

# Run kiro locally (no container)
ax kiro chat --local

# List active sessions
ax list

# Stop a session
ax stop ax-kiro-myproject

# Open debug shell in sandbox
ax shell
```

## Supported Tools

### kiro
AI coding assistant with access to your codebase, skills, and development tools.

```bash
ax kiro chat              # Interactive chat mode
ax kiro chat --local      # Run locally without sandbox
```

### toad
AI workflow automation tool for task execution and orchestration.

```bash
ax toad                   # Run toad (default tool)
ax toad --local           # Run locally without sandbox
```

## Sandbox Environment

The `ax-sandbox` Docker image includes a complete development environment:

### Language Runtimes
- **Python** (latest stable via uv)
- **uv** - Fast Python package manager

### AI Agent Tools
- **kiro-cli** - AI coding assistant
- **toad** - AI workflow automation

### Infrastructure & Cloud Tools
- **AWS CLI v2** - AWS command-line interface
- **OpenTofu** - Open-source Terraform alternative
- **Scalr CLI** - Scalr platform management
- **GitHub CLI (gh)** - GitHub command-line tool

### Data Processing
- **jq** - JSON processor
- **yq** - YAML processor

### System Utilities
- git, curl, wget, bash, nano
- Standard Unix tools (procps, dnsutils, ca-certificates)

## Behavior

### Project Detection

`ax` must be run from within a project directory under `~/dev`. It automatically detects your project root:

```bash
# From ~/dev/myproject/src
ax kiro chat
# Mounts ~/dev/myproject as /workspace in container
```

If you're in `~/dev/myproject/src/components`, the project root is still `~/dev/myproject` (first subdirectory under `~/dev`).

### Container Sessions

Each tool + project combination gets a unique container name:

```
ax-{tool}-{project}
```

Examples:
- `ax-kiro-myproject`
- `ax-toad-api-service`
- `ax-shell-myproject`

This prevents duplicate sessions on the same project. If a container already exists, `ax` will display an error with instructions to stop it.

### Mounted Directories

When running in sandbox mode, `ax` automatically mounts:

| Host Path | Container Path | Purpose |
|-----------|---------------|---------|
| `~/dev/myproject` | `/workspace` | Your project directory (working directory) |
| `~/.kiro` | `~/.kiro` | Kiro configuration and skills |
| `~/.toad` | `~/.toad` | Toad configuration |
| `~/cli-tools` | `~/cli-tools` | Shared CLI tools and scripts |
| `~/plans` | `~/plans` | Project plans and documentation |

Tool-specific config directories are only mounted when running that tool.

### Local Mode

Use `--local` to run tools directly on your host system without Docker:

```bash
ax kiro chat --local
```

Local mode:
- Skips container creation
- Runs tool command directly
- Requires tool to be installed on host
- Still performs project detection and displays context

## Requirements

- **Python 3.11+**
- **Docker** (for sandbox execution)
- **uv** (for dependency management)
- **Project under ~/dev** (required for project detection)

## Development

```bash
# Install in development mode with linting tools
uv sync --extra dev

# Run linter
uv run ruff check ax/

# Run formatter
uv run black ax/

# Test locally
uv run ax --help
```

## Error Handling

- **Docker not available**: Clear error with instructions to start Docker daemon
- **Container already exists**: Error with command to stop existing session
- **Tool not found** (local mode): Helpful error with installation instructions
- **Path outside ~/dev**: Error requiring project under ~/dev

## Architecture

```
ax (CLI)
├── DockerManager - Docker operations (build, run, list, stop)
├── Executor - Tool execution (local and sandbox)
├── PathResolver - Project detection and mount configuration
└── Tools Registry - Tool definitions and metadata
```
