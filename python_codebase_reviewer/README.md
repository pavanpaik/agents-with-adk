# Python Codebase Reviewer

A production-ready multi-agent system for comprehensive Python code review with deep domain-specific knowledge.

## Overview

This agent system performs expert-level code reviews by coordinating five specialized reviewer agents:

1. **Security Reviewer** - Identifies security vulnerabilities using OWASP Top 10 and Python-specific security knowledge
2. **Architecture Reviewer** - Evaluates design patterns, SOLID principles, and code structure
3. **Code Quality Reviewer** - Enforces PEP standards and Pythonic idioms
4. **Performance Reviewer** - Analyzes algorithm complexity, memory usage, and optimization opportunities
5. **Python Expert** - Provides deep expertise in standard library, frameworks, and advanced Python features

## Features

- ✅ **Comprehensive Reviews**: Security, architecture, quality, performance, and Python expertise
- ✅ **Production-Ready Prompts**: Extensive domain knowledge embedded in agent instructions
- ✅ **Actionable Findings**: Every issue includes code examples and concrete fixes
- ✅ **Smart Prioritization**: Critical issues highlighted, quick wins identified
- ✅ **Framework Support**: Django, Flask, FastAPI, pytest, and more
- ✅ **Modern Python**: Support for Python 3.8-3.12+ features
- ✅ **Structured Output**: Clear, formatted reports with severity levels

## Architecture

```
Root Orchestrator (gemini-2.0-pro-exp)
├── Security Reviewer (gemini-2.0-flash-thinking-exp)
│   ├── OWASP Top 10 knowledge
│   ├── Python-specific vulnerabilities
│   └── Framework security patterns
├── Architecture Reviewer (gemini-2.0-flash-thinking-exp)
│   ├── SOLID principles
│   ├── Design patterns
│   └── Anti-pattern detection
├── Code Quality Reviewer (gemini-2.0-flash-exp)
│   ├── PEP 8, PEP 20, PEP 257, PEP 484/585
│   ├── Pythonic idioms
│   └── Code smell detection
├── Performance Reviewer (gemini-2.0-flash-exp)
│   ├── Algorithm complexity (Big O)
│   ├── Memory optimization
│   └── Database query patterns
└── Python Expert (gemini-2.0-flash-thinking-exp)
    ├── Standard library expertise
    ├── Framework best practices
    └── Advanced Python features
```

## Installation

1. **Clone the repository**:
   ```bash
   cd agents-with-adk/python_codebase_reviewer
   ```

2. **Install dependencies**:
   ```bash
   pip install google-adk
   ```

3. **Configure environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

## Configuration

### Environment Variables

Create a `.env` file with the following variables:

```bash
# Google Cloud Configuration
GOOGLE_CLOUD_PROJECT="your-project-id"
GOOGLE_CLOUD_LOCATION="us-central1"
GOOGLE_API_KEY="your-api-key"  # Or use GOOGLE_GENAI_USE_VERTEXAI="True"

# Model Configuration (optional - defaults provided)
ORCHESTRATOR_MODEL="gemini-2.0-pro-exp"
REVIEWER_MODEL="gemini-2.0-flash-thinking-exp"
ANALYZER_MODEL="gemini-2.0-flash-exp"
PYTHON_EXPERT_MODEL="gemini-2.0-flash-thinking-exp"

# Review Configuration (optional)
SEVERITY_THRESHOLD="LOW"  # CRITICAL, HIGH, MEDIUM, LOW
MAX_FILES_PER_REVIEW="50"
MIN_PYTHON_VERSION="3.8"
MAX_COMPLEXITY="10"
MAX_LINE_LENGTH="88"

# Feature Flags (optional)
REQUIRE_TYPE_HINTS="True"
REQUIRE_DOCSTRINGS="True"
ENABLE_AUTO_FIX="False"
```

## Usage

### Running a Code Review

```python
from python_codebase_reviewer import root_agent

# Review a single file
code = """
def login(username, password):
    query = f"SELECT * FROM users WHERE username='{username}' AND password='{password}'"
    return db.execute(query)
"""

response = root_agent.run(f"Review this code:\n{code}")
print(response)
```

### Running with ADK CLI

```bash
# Deploy the agent
adk deploy cloud_run \
    --project=$GOOGLE_CLOUD_PROJECT \
    --region=$GOOGLE_CLOUD_LOCATION \
    --service_name=python-code-reviewer \
    --app_name=python_codebase_reviewer \
    --with_ui \
    python_codebase_reviewer

# Test locally
adk test python_codebase_reviewer
```

### Example Review Request

```
Review the following Python module for security issues, code quality, and performance:

[Paste your Python code here]

Focus on:
- Security vulnerabilities
- PEP 8 compliance
- Performance bottlenecks
```

## Output Format

Reviews are structured with:

### Executive Summary
- Overall health score (0-100)
- Total findings by severity
- Top critical issues
- Production readiness assessment

### Detailed Findings
- 🔴 **Critical Issues**: Immediate action required
- 🟠 **High Priority**: Important improvements
- 🟡 **Medium Priority**: Quality improvements
- 🔵 **Low Priority**: Optional enhancements
- ℹ️ **Info**: Recommendations

### Per-Finding Format
Each finding includes:
- **Location**: `file.py:line`
- **Severity**: CRITICAL/HIGH/MEDIUM/LOW/INFO
- **Type**: SECURITY/ARCHITECTURE/PERFORMANCE/QUALITY/PYTHONIC
- **Current Code**: The problematic code
- **Fixed Code**: The corrected version
- **Impact**: Why this matters
- **References**: Links to PEPs, OWASP, etc.

## Agent Capabilities

### Security Reviewer
- OWASP Top 10 (2021) vulnerabilities
- SQL injection, XSS, CSRF detection
- Secrets detection (API keys, passwords)
- Insecure deserialization (pickle, YAML)
- Authentication/authorization flaws
- Framework-specific security (Django, Flask, FastAPI)

### Architecture Reviewer
- SOLID principles (SRP, OCP, LSP, ISP, DIP)
- Design patterns (Factory, Strategy, Observer, etc.)
- Anti-patterns (God Object, Circular Dependencies, etc.)
- Module organization and dependency direction
- Coupling and cohesion analysis

### Code Quality Reviewer
- PEP 8 (Style Guide)
- PEP 20 (Zen of Python)
- PEP 257 (Docstring Conventions)
- PEP 484/585 (Type Hints)
- Pythonic idioms (comprehensions, generators, context managers)
- Code smell detection (Long Method, Duplicated Code, Magic Numbers)

### Performance Reviewer
- Algorithm complexity (Big O) analysis
- Data structure optimization (list vs set vs dict)
- Generator vs list usage
- Database query optimization (N+1 queries, eager loading)
- Caching opportunities
- Concurrency patterns (asyncio, multiprocessing)
- Memory optimization (\_\_slots\_\_, generators)

### Python Expert
- Standard library best practices (collections, itertools, functools)
- Framework expertise (Django ORM, Flask blueprints, FastAPI dependencies)
- Advanced features (descriptors, metaclasses, protocols)
- Type system (TypeVar, Generic, Protocol, Literal)
- Async/await patterns
- Testing best practices (pytest fixtures, mocking)
- Modern Python features (3.10+ match/case, 3.11+ exception groups)

## Customization

### Adjusting Severity Thresholds

Set `SEVERITY_THRESHOLD` in `.env`:
- `CRITICAL`: Only show critical security issues
- `HIGH`: Show critical and high-priority issues
- `MEDIUM`: Show medium and above (default for most reviews)
- `LOW`: Show all findings including minor improvements

### Customizing Review Focus

You can request targeted reviews:

```
Review this code focusing only on security issues.
```

```
Review this Django app for performance bottlenecks.
```

```
Check if this code follows PEP 8 and Pythonic idioms.
```

## Project Structure

```
python_codebase_reviewer/
├── agent.py                          # Root orchestrator agent
├── prompt.py                         # Orchestrator prompt
├── __init__.py
├── README.md
├── .env.example
│
├── shared_libraries/
│   ├── constants.py                  # Configuration constants
│   ├── models.py                     # Data models for findings
│   └── __init__.py
│
└── sub_agents/
    ├── security_reviewer/
    │   ├── agent.py                  # Security reviewer agent
    │   ├── prompt.py                 # Security domain knowledge
    │   └── __init__.py
    │
    ├── architecture_reviewer/
    │   ├── agent.py                  # Architecture reviewer agent
    │   ├── prompt.py                 # Design patterns knowledge
    │   └── __init__.py
    │
    ├── code_quality_reviewer/
    │   ├── agent.py                  # Code quality reviewer agent
    │   ├── prompt.py                 # PEP standards knowledge
    │   └── __init__.py
    │
    ├── performance_reviewer/
    │   ├── agent.py                  # Performance reviewer agent
    │   ├── prompt.py                 # Optimization knowledge
    │   └── __init__.py
    │
    └── python_expert/
        ├── agent.py                  # Python expert agent
        ├── prompt.py                 # Deep Python expertise
        └── __init__.py
```

## Best Practices

1. **Start with Security**: Always review security issues first
2. **Batch Reviews**: Review related files together for context
3. **Iterative Improvement**: Fix critical issues first, then iterate
4. **Use with CI/CD**: Integrate into your development pipeline
5. **Customize Thresholds**: Adjust based on your project's maturity

## Troubleshooting

### No findings reported
- Check if code is actually Python (`.py` files)
- Verify the code has actual issues to report
- Lower `SEVERITY_THRESHOLD` to see minor issues

### Too many findings
- Increase `SEVERITY_THRESHOLD` to focus on critical issues
- Request targeted reviews (e.g., "only security issues")

### Agent timeout
- Reduce the amount of code in a single review
- Split large files into smaller chunks
- Increase timeout in ADK configuration

## Contributing

To add a new reviewer agent:

1. Create a new directory in `sub_agents/`
2. Add `agent.py` and `prompt.py` with domain knowledge
3. Import and wrap the agent in `agent.py` (root)
4. Update this README

## License

See the main repository license.

## Support

For issues or questions:
1. Check the [ADK documentation](https://github.com/GoogleCloudPlatform/adk)
2. Review the example prompts in `prompt.py` files
3. Open an issue in the repository

## Version History

- **1.0.0** (2025-01): Initial production-ready release
  - 5 specialized reviewer agents
  - Comprehensive Python expertise
  - Production-ready prompts
  - Full PEP standard coverage
  - Framework support (Django, Flask, FastAPI)

---

Built with ❤️ using Google Agent Development Kit (ADK)
