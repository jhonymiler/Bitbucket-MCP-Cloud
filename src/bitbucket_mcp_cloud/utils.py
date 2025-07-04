"""
Utility functions for the Bitbucket MCP Server
"""

import logging
import os
from typing import Any


def get_env_var(var_name: str, default: Any = None) -> str:
    """
    Get environment variable with optional default value.

    Args:
        var_name: Name of the environment variable
        default: Default value if variable is not set

    Returns:
        Environment variable value or default

    Raises:
        ValueError: If variable is required but not set
    """
    value = os.getenv(var_name, default)
    if value is None:
        raise ValueError(f"Environment variable {var_name} is required but not set")
    return str(value)


def setup_logger(name: str, level: str = "INFO") -> logging.Logger:
    """
    Setup logger with consistent formatting.

    Args:
        name: Logger name
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)

    # Only configure if no handlers exist (avoid duplicate logs)
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    # Set level
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))

    return logger
