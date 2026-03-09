# ax - AI Workflow Tool Executor

Unified execution hub for AI workflow tools (kiro, toad, etc.), running them in isolated Docker sandbox containers by default, or directly on the host system with the `--local` flag.

## Features

- **Sandbox Execution**: Run tools in isolated Docker containers by default
- **Local Execution**: Use `--local` flag to run tools directly on host
- **Project-Aware Mounting**: Automatically mounts project directory based on `~/dev` ancestry
- **Interactive I/O**: Full stdin/stdout/stderr passthrough for interactive tools
- **Session Management**: Named containers prevent duplicate sessions
- **Built-in Tools**: Pre-configured for kiro and toad

## Installation

```bash
# Install dependencies
uv sync

# Build the sandbox image
uv run ax build
```

## Usage

### Run Tools

```bash
# Run default tool (toad) in sandbox
ax

# Run kiro in sandbox
ax kiro chat

# Run kiro locally
ax kiro chat --local

# Run toad in sandbox
ax toad
```

### Manage Sessions

```bash
# List running sessions
ax list

# Stop a session
ax stop ax-kiro-myproject

# Open debug shell in sandbox
ax shell
```

### Build Image

```bash
# Build or rebuild the sandbox image
ax build
```

## How It Works

### Directory Mounting

When you run `ax` from a directory under `~/dev`, it automatically mounts:

- **Project directory**: First subdirectory under `~/dev` (e.g., `~/dev/myproject`)
- **CLI tools**: `~/cli-tools`
- **Plans**: `~/plans`
- **Tool configs**: Tool-specific directories (e.g., `~/.kiro`, `~/.toad`)

Example:
```bash
# From ~/dev/myproject/src
ax kiro chat
# Mounts ~/dev/myproject as /workspace in container
```

### Container Naming

Containers are named `ax-{tool}-{project}`:
- `ax-kiro-myproject`
- `ax-toad-myproject`

This prevents duplicate sessions on the same project.

## Requirements

- Python 3.11+
- Docker (for sandbox execution)
- uv (for dependency management)

## Sandbox Image

The sandbox image (`ax-sandbox`) includes:

**System Tools**:
- git, curl, bash, ca-certificates
- unzip, procps, dnsutils, wget, nano

**Python Environment**:
- uv package manager
- Python (latest stable)

**AI Agent Tools**:
- kiro-cli
- toad

**Infrastructure Tools**:
- jq (JSON processor)
- yq (YAML processor)
- GitHub CLI (gh)
- AWS CLI v2
- OpenTofu
- Scalr CLI

## Error Handling

- **Docker not available**: Clear error message with instructions
- **Container name collision**: Error with suggestion to stop existing session
- **Tool not found**: Helpful error message (local mode only)
- **Path outside ~/dev**: Error requiring project under ~/dev

## Development

```bash
# Install in development mode
uv pip install -e .

# Run locally
uv run ax --help
```
