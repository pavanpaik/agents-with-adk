"""
Configuration constants for Python Codebase Reviewer agent system.

This module loads and validates configuration from environment variables.
In production, missing required configuration will raise an error.
"""
import os
import logging
from dotenv import load_dotenv
from typing import List

load_dotenv()

logger = logging.getLogger(__name__)

# Environment
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

# Agent Configuration
AGENT_NAME = "python_codebase_reviewer"
DESCRIPTION = "Multi-agent Python codebase review system with deep domain expertise"

# Model Configuration
ORCHESTRATOR_MODEL = os.getenv("ORCHESTRATOR_MODEL", "gemini-2.0-pro-exp")
REVIEWER_MODEL = os.getenv("REVIEWER_MODEL", "gemini-2.0-flash-thinking-exp")
ANALYZER_MODEL = os.getenv("ANALYZER_MODEL", "gemini-2.0-flash-exp")
PYTHON_EXPERT_MODEL = os.getenv("PYTHON_EXPERT_MODEL", "gemini-2.0-flash-thinking-exp")

# Google Cloud Configuration
PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT", "")
LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")

# Review Configuration
SEVERITY_THRESHOLD = os.getenv("SEVERITY_THRESHOLD", "LOW")  # CRITICAL, HIGH, MEDIUM, LOW
MAX_FILES_PER_REVIEW = int(os.getenv("MAX_FILES_PER_REVIEW", "50"))
ENABLE_AUTO_FIX = os.getenv("ENABLE_AUTO_FIX", "False") == "True"
MIN_PYTHON_VERSION = os.getenv("MIN_PYTHON_VERSION", "3.8")

# Tool Configuration
ENABLE_SECURITY_SCANNER = os.getenv("ENABLE_SECURITY_SCANNER", "True") == "True"
ENABLE_PERFORMANCE_PROFILING = os.getenv("ENABLE_PERFORMANCE_PROFILING", "True") == "True"
ENABLE_TYPE_CHECKING = os.getenv("ENABLE_TYPE_CHECKING", "True") == "True"

# Python-Specific Configuration
SUPPORTED_FRAMEWORKS = ["django", "flask", "fastapi", "pytest", "numpy", "pandas"]
REQUIRE_TYPE_HINTS = os.getenv("REQUIRE_TYPE_HINTS", "True") == "True"
REQUIRE_DOCSTRINGS = os.getenv("REQUIRE_DOCSTRINGS", "True") == "True"
MAX_COMPLEXITY = int(os.getenv("MAX_COMPLEXITY", "10"))  # McCabe complexity threshold
MAX_LINE_LENGTH = int(os.getenv("MAX_LINE_LENGTH", "88"))  # Black default


def validate_configuration() -> List[str]:
    """
    Validate configuration and return list of errors.

    Returns:
        List of validation error messages (empty if valid)
    """
    errors = []

    # Validate severity threshold
    valid_severities = ["CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO"]
    if SEVERITY_THRESHOLD not in valid_severities:
        errors.append(
            f"SEVERITY_THRESHOLD must be one of {valid_severities}, got '{SEVERITY_THRESHOLD}'"
        )

    # Validate max files
    if MAX_FILES_PER_REVIEW < 1 or MAX_FILES_PER_REVIEW > 1000:
        errors.append(
            f"MAX_FILES_PER_REVIEW must be between 1 and 1000, got {MAX_FILES_PER_REVIEW}"
        )

    # Validate complexity
    if MAX_COMPLEXITY < 1 or MAX_COMPLEXITY > 100:
        errors.append(
            f"MAX_COMPLEXITY must be between 1 and 100, got {MAX_COMPLEXITY}"
        )

    # Validate line length
    if MAX_LINE_LENGTH < 50 or MAX_LINE_LENGTH > 200:
        errors.append(
            f"MAX_LINE_LENGTH must be between 50 and 200, got {MAX_LINE_LENGTH}"
        )

    # In production, validate required fields
    if ENVIRONMENT == "production":
        if not PROJECT:
            errors.append("GOOGLE_CLOUD_PROJECT must be set in production")

    return errors


def validate_or_exit() -> None:
    """
    Validate configuration and exit if invalid in production.

    In development, only logs warnings.
    In production, raises RuntimeError on invalid configuration.
    """
    errors = validate_configuration()

    if errors:
        for error in errors:
            if ENVIRONMENT == "production":
                logger.critical(f"Configuration error: {error}")
            else:
                logger.warning(f"Configuration warning: {error}")

        if ENVIRONMENT == "production":
            raise RuntimeError(
                f"Invalid configuration in production environment. "
                f"Errors: {', '.join(errors)}"
            )

    logger.info(f"Configuration validated successfully (environment: {ENVIRONMENT})")


# Validate configuration on module import
validate_or_exit()
