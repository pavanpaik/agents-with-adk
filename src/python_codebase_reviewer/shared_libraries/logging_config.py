"""
Logging configuration for Python Codebase Reviewer.

Provides structured logging with JSON output for production and
human-readable format for development.
"""
import logging
import sys
import json
import os
from datetime import datetime
from typing import Dict, Any


class JSONFormatter(logging.Formatter):
    """
    JSON formatter for structured logging in production.

    Outputs log records as JSON objects for easy parsing by log aggregation tools.
    """

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
        }

        # Add exception info if present
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)

        # Add extra fields
        if hasattr(record, 'request_id'):
            log_data['request_id'] = record.request_id

        if hasattr(record, 'repo'):
            log_data['repo'] = record.repo

        if hasattr(record, 'pr_number'):
            log_data['pr_number'] = record.pr_number

        return json.dumps(log_data)


def configure_logging(
    level: str = None,
    format_type: str = None,
    output: str = 'stdout'
) -> None:
    """
    Configure application logging.

    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
               Defaults to INFO in production, DEBUG in development
        format_type: 'json' for structured logging or 'text' for human-readable
                     Defaults to json in production, text in development
        output: 'stdout' or 'stderr' for output destination
    """
    # Determine environment
    environment = os.getenv('ENVIRONMENT', 'development')

    # Set defaults based on environment
    if level is None:
        level = 'INFO' if environment == 'production' else 'DEBUG'

    if format_type is None:
        format_type = 'json' if environment == 'production' else 'text'

    # Convert level string to logging constant
    numeric_level = getattr(logging, level.upper(), logging.INFO)

    # Create formatter
    if format_type == 'json':
        formatter = JSONFormatter()
    else:
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)

    # Remove existing handlers
    root_logger.handlers.clear()

    # Add handler
    handler = logging.StreamHandler(sys.stdout if output == 'stdout' else sys.stderr)
    handler.setFormatter(formatter)
    root_logger.addHandler(handler)

    # Log configuration
    logging.info(f"Logging configured: level={level}, format={format_type}, environment={environment}")


class StructuredLogger:
    """
    Utility class for structured logging with context.

    Provides convenience methods for logging with additional context fields.
    """

    def __init__(self, logger: logging.Logger):
        """
        Initialize structured logger.

        Args:
            logger: Base logger instance
        """
        self.logger = logger

    def log_with_context(
        self,
        level: int,
        message: str,
        context: Dict[str, Any] = None
    ) -> None:
        """
        Log message with additional context.

        Args:
            level: Logging level (logging.INFO, logging.ERROR, etc.)
            message: Log message
            context: Additional context fields (request_id, repo, pr_number, etc.)
        """
        extra = context or {}
        self.logger.log(level, message, extra=extra)

    def log_review_started(self, repo: str, pr_number: int, request_id: str = None) -> None:
        """Log review start."""
        context = {'repo': repo, 'pr_number': pr_number}
        if request_id:
            context['request_id'] = request_id
        self.log_with_context(logging.INFO, f"Code review started for PR #{pr_number}", context)

    def log_review_completed(
        self,
        repo: str,
        pr_number: int,
        duration_seconds: float,
        findings_count: int,
        request_id: str = None
    ) -> None:
        """Log review completion with metrics."""
        context = {
            'repo': repo,
            'pr_number': pr_number,
            'duration_seconds': duration_seconds,
            'findings_count': findings_count,
            'event': 'review_completed'
        }
        if request_id:
            context['request_id'] = request_id
        self.log_with_context(
            logging.INFO,
            f"Code review completed for PR #{pr_number}: {findings_count} findings in {duration_seconds:.2f}s",
            context
        )

    def log_api_call(
        self,
        method: str,
        endpoint: str,
        status_code: int = None,
        duration_ms: float = None,
        request_id: str = None
    ) -> None:
        """Log API call with metrics."""
        context = {
            'method': method,
            'endpoint': endpoint,
            'event': 'api_call'
        }
        if status_code:
            context['status_code'] = status_code
        if duration_ms:
            context['duration_ms'] = duration_ms
        if request_id:
            context['request_id'] = request_id

        message = f"API call: {method} {endpoint}"
        if status_code:
            message += f" -> {status_code}"
        if duration_ms:
            message += f" ({duration_ms:.0f}ms)"

        self.log_with_context(logging.DEBUG, message, context)

    def log_error(
        self,
        message: str,
        error: Exception = None,
        request_id: str = None,
        **kwargs
    ) -> None:
        """Log error with context."""
        context = kwargs
        if request_id:
            context['request_id'] = request_id
        if error:
            context['error_type'] = type(error).__name__
            context['error_message'] = str(error)

        self.logger.error(message, exc_info=error is not None, extra=context)


# Default configuration on import
configure_logging()
