"""
Python Codebase Reviewer

A multi-agent system for comprehensive Python code review with domain-specific knowledge.

This agent system includes:
- Security Reviewer: OWASP Top 10, Python security vulnerabilities
- Architecture Reviewer: Design patterns, SOLID principles
- Code Quality Reviewer: PEP standards, Pythonic idioms
- Performance Reviewer: Algorithm optimization, memory efficiency
- Python Expert: Standard library, frameworks, advanced features
"""
from .agent import root_agent

__version__ = "1.0.0"
__all__ = ['root_agent']
