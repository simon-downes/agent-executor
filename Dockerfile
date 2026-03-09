FROM debian:bookworm-slim

# Install system packages
RUN apt-get update && apt-get install -y \
    git \
    curl \
    bash \
    ca-certificates \
    unzip \
    procps \
    dnsutils \
    wget \
    nano \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:$PATH"

# Install Python using uv
RUN uv python install

# Install kiro-cli
RUN ARCH=$(uname -m) && \
    if [ "$ARCH" = "x86_64" ]; then \
        KIRO_ARCH="x64"; \
    elif [ "$ARCH" = "aarch64" ] || [ "$ARCH" = "arm64" ]; then \
        KIRO_ARCH="arm64"; \
    else \
        echo "Unsupported architecture: $ARCH" && exit 1; \
    fi && \
    LIBC=$(ldd --version 2>&1 | grep -q musl && echo "musl" || echo "standard") && \
    if [ "$LIBC" = "musl" ]; then \
        KIRO_FILE="kiro-cli-linux-${KIRO_ARCH}-musl.zip"; \
    else \
        KIRO_FILE="kiro-cli-linux-${KIRO_ARCH}.zip"; \
    fi && \
    curl -L "https://desktop-release.q.us-east-1.amazonaws.com/latest/${KIRO_FILE}" -o /tmp/kiro.zip && \
    unzip /tmp/kiro.zip -d /usr/local/bin && \
    chmod +x /usr/local/bin/kiro-cli && \
    rm /tmp/kiro.zip

# Install toad
RUN ARCH=$(uname -m) && \
    if [ "$ARCH" = "x86_64" ]; then \
        TOAD_ARCH="x86_64"; \
    elif [ "$ARCH" = "aarch64" ] || [ "$ARCH" = "arm64" ]; then \
        TOAD_ARCH="aarch64"; \
    else \
        echo "Unsupported architecture: $ARCH" && exit 1; \
    fi && \
    TOAD_VERSION=$(curl -s https://api.github.com/repos/batrachianai/toad/releases/latest | grep '"tag_name"' | cut -d'"' -f4) && \
    curl -L "https://github.com/batrachianai/toad/releases/download/${TOAD_VERSION}/toad-${TOAD_VERSION}-${TOAD_ARCH}-unknown-linux-gnu.tar.gz" -o /tmp/toad.tar.gz && \
    tar -xzf /tmp/toad.tar.gz -C /usr/local/bin && \
    chmod +x /usr/local/bin/toad && \
    rm /tmp/toad.tar.gz

# Install jq
RUN ARCH=$(uname -m) && \
    if [ "$ARCH" = "x86_64" ]; then \
        JQ_ARCH="amd64"; \
    elif [ "$ARCH" = "aarch64" ] || [ "$ARCH" = "arm64" ]; then \
        JQ_ARCH="arm64"; \
    else \
        echo "Unsupported architecture: $ARCH" && exit 1; \
    fi && \
    curl -L "https://github.com/jqlang/jq/releases/latest/download/jq-linux-${JQ_ARCH}" -o /usr/local/bin/jq && \
    chmod +x /usr/local/bin/jq

# Install yq
RUN ARCH=$(uname -m) && \
    if [ "$ARCH" = "x86_64" ]; then \
        YQ_ARCH="amd64"; \
    elif [ "$ARCH" = "aarch64" ] || [ "$ARCH" = "arm64" ]; then \
        YQ_ARCH="arm64"; \
    else \
        echo "Unsupported architecture: $ARCH" && exit 1; \
    fi && \
    curl -L "https://github.com/mikefarah/yq/releases/latest/download/yq_linux_${YQ_ARCH}" -o /usr/local/bin/yq && \
    chmod +x /usr/local/bin/yq

# Install GitHub CLI
RUN ARCH=$(uname -m) && \
    if [ "$ARCH" = "x86_64" ]; then \
        GH_ARCH="amd64"; \
    elif [ "$ARCH" = "aarch64" ] || [ "$ARCH" = "arm64" ]; then \
        GH_ARCH="arm64"; \
    else \
        echo "Unsupported architecture: $ARCH" && exit 1; \
    fi && \
    GH_VERSION=$(curl -s https://api.github.com/repos/cli/cli/releases/latest | grep '"tag_name"' | cut -d'"' -f4 | sed 's/v//') && \
    curl -L "https://github.com/cli/cli/releases/download/v${GH_VERSION}/gh_${GH_VERSION}_linux_${GH_ARCH}.tar.gz" -o /tmp/gh.tar.gz && \
    tar -xzf /tmp/gh.tar.gz -C /tmp && \
    mv /tmp/gh_${GH_VERSION}_linux_${GH_ARCH}/bin/gh /usr/local/bin/ && \
    rm -rf /tmp/gh*

# Install AWS CLI v2
RUN ARCH=$(uname -m) && \
    if [ "$ARCH" = "x86_64" ]; then \
        curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o /tmp/awscliv2.zip; \
    elif [ "$ARCH" = "aarch64" ] || [ "$ARCH" = "arm64" ]; then \
        curl "https://awscli.amazonaws.com/awscli-exe-linux-aarch64.zip" -o /tmp/awscliv2.zip; \
    else \
        echo "Unsupported architecture: $ARCH" && exit 1; \
    fi && \
    unzip /tmp/awscliv2.zip -d /tmp && \
    /tmp/aws/install && \
    rm -rf /tmp/aws*

# Install OpenTofu
RUN ARCH=$(uname -m) && \
    if [ "$ARCH" = "x86_64" ]; then \
        TOFU_ARCH="amd64"; \
    elif [ "$ARCH" = "aarch64" ] || [ "$ARCH" = "arm64" ]; then \
        TOFU_ARCH="arm64"; \
    else \
        echo "Unsupported architecture: $ARCH" && exit 1; \
    fi && \
    TOFU_VERSION=$(curl -s https://api.github.com/repos/opentofu/opentofu/releases/latest | grep '"tag_name"' | cut -d'"' -f4 | sed 's/v//') && \
    curl -L "https://github.com/opentofu/opentofu/releases/download/v${TOFU_VERSION}/tofu_${TOFU_VERSION}_linux_${TOFU_ARCH}.zip" -o /tmp/tofu.zip && \
    unzip /tmp/tofu.zip -d /usr/local/bin && \
    chmod +x /usr/local/bin/tofu && \
    rm /tmp/tofu.zip

# Install Scalr CLI
RUN ARCH=$(uname -m) && \
    if [ "$ARCH" = "x86_64" ]; then \
        SCALR_ARCH="amd64"; \
    elif [ "$ARCH" = "aarch64" ] || [ "$ARCH" = "arm64" ]; then \
        SCALR_ARCH="arm64"; \
    else \
        echo "Unsupported architecture: $ARCH" && exit 1; \
    fi && \
    SCALR_VERSION=$(curl -s https://api.github.com/repos/Scalr/scalr-cli/releases/latest | grep '"tag_name"' | cut -d'"' -f4 | sed 's/v//') && \
    curl -L "https://github.com/Scalr/scalr-cli/releases/download/v${SCALR_VERSION}/scalr-cli_${SCALR_VERSION}_linux_${SCALR_ARCH}.tar.gz" -o /tmp/scalr.tar.gz && \
    tar -xzf /tmp/scalr.tar.gz -C /usr/local/bin && \
    chmod +x /usr/local/bin/scalr && \
    rm /tmp/scalr.tar.gz

WORKDIR /workspace

CMD ["/bin/bash"]
