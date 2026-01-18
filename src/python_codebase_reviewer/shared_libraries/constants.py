"""
Configuration constants for Python Codebase Reviewer agent system.
"""
import os
from dotenv import load_dotenv

load_dotenv()

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
