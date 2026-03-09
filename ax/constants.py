"""Shared constants for ax."""

import os
import pwd

IMAGE_NAME = "ax-sandbox"
CONTAINER_PREFIX = "ax-"

# Get host user info (cached at module load)
_user_info = pwd.getpwuid(os.getuid())
HOST_USERNAME = _user_info.pw_name
HOST_UID = _user_info.pw_uid
HOST_GID = _user_info.pw_gid
