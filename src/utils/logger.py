"""
Logger Utility
==============

Centralized logging configuration for the MAS platform.

Features:
- Structured JSON logging
- Log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- Contextual logging with agent/request IDs
- Integration with Databricks logging

Author: AI Ops Team
Version: 1.0.0
"""

import logging
import sys
import json
from typing import Optional, Dict, Any
from datetime import datetime

try:
    import structlog
    HAS_STRUCTLOG = True
except ImportError:
    HAS_STRUCTLOG = False


def get_logger(name: str, log_level: str = "INFO") -> logging.Logger:
    """
    Get a configured logger instance.
    
    Args:
        name: Logger name (typically __name__)
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    
    Returns:
        Configured logger instance
    """
    # Configure structlog for structured logging if available
    if HAS_STRUCTLOG:
        try:
            structlog.configure(
                processors=[
                    structlog.stdlib.filter_by_level,
                    structlog.stdlib.add_logger_name,
                    structlog.stdlib.add_log_level,
                    structlog.stdlib.PositionalArgumentsFormatter(),
                    structlog.processors.TimeStamper(fmt="iso"),
                    structlog.processors.StackInfoRenderer(),
                    structlog.processors.format_exc_info,
                    structlog.processors.UnicodeDecoder(),
                    structlog.processors.JSONRenderer()
                ],
                context_class=dict,
                logger_factory=structlog.stdlib.LoggerFactory(),
                wrapper_class=structlog.stdlib.BoundLogger,
                cache_logger_on_first_use=True,
            )
        except Exception:
            pass  # Fall back to standard logging
    
    # Get standard library logger
    logger = logging.getLogger(name)
    
    # Set log level
    level = getattr(logging, log_level.upper(), logging.INFO)
    logger.setLevel(level)
    
    # Add console handler if not already present
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(level)
        
        # Use JSON formatter for structured logging
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    
    return logger


def log_with_context(
    logger: logging.Logger,
    level: str,
    message: str,
    context: Optional[Dict[str, Any]] = None
) -> None:
    """
    Log a message with additional context.
    
    Args:
        logger: Logger instance
        level: Log level
        message: Log message
        context: Additional context dictionary
    """
    log_func = getattr(logger, level.lower(), logger.info)
    
    if context:
        context_str = json.dumps(context)
        log_func(f"{message} | Context: {context_str}")
    else:
        log_func(message)

