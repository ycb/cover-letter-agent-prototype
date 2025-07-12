#!/usr/bin/env python3
"""
Logging Configuration for Cover Letter Agent
===========================================

Configures logging for the application with different levels and handlers.
"""

import logging
import sys
from pathlib import Path
from typing import Optional


def setup_logging(level: str = "INFO", log_file: Optional[str] = None, user_id: Optional[str] = None) -> logging.Logger:
    """
    Set up logging configuration for the application.

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional path to log file
        user_id: Optional user ID for user-specific logging

    Returns:
        Configured logger instance
    """
    # Create logger
    logger_name = "cover_letter_agent"
    if user_id:
        logger_name = f"cover_letter_agent.{user_id}"

    logger = logging.getLogger(logger_name)
    logger.setLevel(getattr(logging, level.upper()))

    # Clear existing handlers to avoid duplicates
    logger.handlers.clear()

    # Create formatter
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S")

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, level.upper()))
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler (if specified)
    if log_file:
        try:
            log_path = Path(log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)

            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(logging.DEBUG)  # Always log everything to file
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        except Exception as e:
            logger.warning(f"Failed to set up file logging to {log_file}: {e}")

    return logger


def get_logger(name: str = "cover_letter_agent") -> logging.Logger:
    """
    Get a logger instance with the specified name.

    Args:
        name: Logger name

    Returns:
        Logger instance
    """
    return logging.getLogger(name)


def log_function_call(logger: logging.Logger, func_name: str, **kwargs):
    """
    Decorator helper to log function calls with parameters.

    Args:
        logger: Logger instance
        func_name: Name of the function being called
        **kwargs: Function parameters to log
    """
    params = ", ".join([f"{k}={v}" for k, v in kwargs.items()])
    logger.debug(f"Calling {func_name}({params})")


def log_function_result(logger: logging.Logger, func_name: str, result=None, error=None):
    """
    Log function results or errors.

    Args:
        logger: Logger instance
        func_name: Name of the function
        result: Function result (if successful)
        error: Error (if failed)
    """
    if error:
        logger.error(f"{func_name} failed: {error}")
    else:
        logger.debug(f"{func_name} completed successfully")


def setup_user_logging(user_id: str, log_dir: str = "logs") -> logging.Logger:
    """
    Set up user-specific logging.

    Args:
        user_id: User identifier
        log_dir: Directory for log files

    Returns:
        User-specific logger
    """
    log_dir_path = Path(log_dir)
    log_dir_path.mkdir(exist_ok=True)

    log_file = log_dir_path / f"{user_id}.log"

    return setup_logging(level="DEBUG", log_file=str(log_file), user_id=user_id)
