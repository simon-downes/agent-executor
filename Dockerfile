FROM debian:bookworm-slim

# Build args for user creation
ARG USERNAME
ARG USER_UID
ARG TARGETARCH

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
RUN case ${TARGETARCH} in \
        amd64) KIRO_ARCH="x86_64" ;; \
        arm64) KIRO_ARCH="aarch64" ;; \
        *) echo "Unsupported architecture: ${TARGETARCH}" && exit 1 ;; \
    esac && \
    curl --proto '=https' --tlsv1.2 -sSf \
        "https://desktop-release.q.us-east-1.amazonaws.com/latest/kirocli-${KIRO_ARCH}-linux.zip" \
        -o kirocli.zip && \
    unzip kirocli.zip && \
    ./kirocli/install.sh --force --no-confirm && \
    rm -rf kirocli.zip kirocli

# Install toad
RUN uv tool install batrachian-toad

# Install jq
RUN curl -L "https://github.com/jqlang/jq/releases/latest/download/jq-linux-${TARGETARCH}" \
        -o /usr/local/bin/jq && \
    chmod +x /usr/local/bin/jq

# Install yq
RUN curl -L "https://github.com/mikefarah/yq/releases/latest/download/yq_linux_${TARGETARCH}" \
        -o /usr/local/bin/yq && \
    chmod +x /usr/local/bin/yq

# Install GitHub CLI
RUN GH_VERSION=$(curl -s https://api.github.com/repos/cli/cli/releases/latest | grep '"tag_name"' | cut -d'"' -f4 | sed 's/v//') && \
    curl -L "https://github.com/cli/cli/releases/download/v${GH_VERSION}/gh_${GH_VERSION}_linux_${TARGETARCH}.tar.gz" \
        -o /tmp/gh.tar.gz && \
    tar -xzf /tmp/gh.tar.gz -C /tmp && \
    mv /tmp/gh_${GH_VERSION}_linux_${TARGETARCH}/bin/gh /usr/local/bin/ && \
    rm -rf /tmp/gh*

# Install AWS CLI v2
RUN case ${TARGETARCH} in \
        amd64) AWS_ARCH="x86_64" ;; \
        arm64) AWS_ARCH="aarch64" ;; \
        *) echo "Unsupported architecture: ${TARGETARCH}" && exit 1 ;; \
    esac && \
    curl "https://awscli.amazonaws.com/awscli-exe-linux-${AWS_ARCH}.zip" -o /tmp/awscliv2.zip && \
    unzip /tmp/awscliv2.zip -d /tmp && \
    /tmp/aws/install && \
    rm -rf /tmp/aws*

# Install OpenTofu
RUN TOFU_VERSION=$(curl -s https://api.github.com/repos/opentofu/opentofu/releases/latest | grep '"tag_name"' | cut -d'"' -f4 | sed 's/v//') && \
    curl -L "https://github.com/opentofu/opentofu/releases/download/v${TOFU_VERSION}/tofu_${TOFU_VERSION}_linux_${TARGETARCH}.zip" \
        -o /tmp/tofu.zip && \
    unzip /tmp/tofu.zip -d /usr/local/bin && \
    chmod +x /usr/local/bin/tofu && \
    rm /tmp/tofu.zip

# Install Scalr CLI
RUN SCALR_VERSION=$(curl -fsSL https://api.github.com/repos/Scalr/scalr-cli/releases/latest | grep -oP '"tag_name": "\K(.*)(?=")') && \
    curl -fsSL "https://github.com/Scalr/scalr-cli/releases/download/${SCALR_VERSION}/scalr-cli_${SCALR_VERSION#v}_linux_${TARGETARCH}.zip" \
        -o scalr.zip && \
    unzip scalr.zip -d /tmp/scalr && \
    mv /tmp/scalr/scalr /usr/local/bin/scalr && \
    chmod +x /usr/local/bin/scalr && \
    rm -rf scalr.zip /tmp/scalr

# Create user with matching UID from host (group uses username)
RUN groupadd $USERNAME \
    && useradd --uid $USER_UID --gid $USERNAME -m -s /bin/bash $USERNAME \
    && mkdir -p /home/$USERNAME/dev \
    && chown -R $USERNAME:$USERNAME /home/$USERNAME

# Switch to user
USER $USERNAME
WORKDIR /home/$USERNAME

CMD ["/bin/bash"]
