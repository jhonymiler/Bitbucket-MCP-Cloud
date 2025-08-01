"""
Bitbucket MCP Server
A Model Context Protocol server for Bitbucket Cloud API integration
"""

from .models import (
    BitbucketBranch,
    BitbucketComment,
    BitbucketProject,
    BitbucketPullRequest,
    BitbucketRepository,
    BitbucketUser,
)
from .utils import get_env_var, setup_logger

__version__ = "1.0.0"
__author__ = "Bitbucket MCP Developer"
__email__ = "dev@example.com"

__all__ = [
    "setup_logger",
    "get_env_var",
    "BitbucketUser",
    "BitbucketRepository",
    "BitbucketPullRequest",
    "BitbucketProject",
    "BitbucketBranch",
    "BitbucketComment",
]
