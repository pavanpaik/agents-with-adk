# Python Codebase Reviewer

**AI-powered code review for Python using a multi-agent system built with Google's Agent Development Kit (ADK).**

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## 🌟 Overview

Python Codebase Reviewer is an intelligent code review system that uses specialized AI agents to analyze Python code comprehensively. Unlike traditional static analysis tools, it provides contextual, actionable feedback across multiple dimensions:

- **🛡️ Security**: OWASP Top 10 vulnerabilities, injection attacks, secrets detection
- **🏗️ Architecture**: SOLID principles, design patterns, code organization
- **✨ Code Quality**: PEP 8/20/257/484, Pythonic idioms, maintainability
- **⚡ Performance**: Algorithm complexity, database queries, memory usage
- **🐍 Best Practices**: Modern Python features, framework patterns, stdlib usage

---

## 🚀 Quick Start

### Installation

```bash
# Install core package
pip install -e .

# Or install with GitHub integration support
pip install -e ".[github]"

# Or install with development tools
pip install -e ".[dev]"
```

### Basic Usage

```python
from python_codebase_reviewer import root_agent

# Review Python code
code = """
def get_user(user_id):
    query = f"SELECT * FROM users WHERE id = {user_id}"
    return db.execute(query)
"""

review = root_agent.run(f"Review this code:\n\n```python\n{code}\n```")
print(review)
```

**Output:**
```
🔴 CRITICAL: SQL Injection vulnerability detected
Line 2: Using string formatting for SQL queries allows SQL injection attacks.

Recommended fix:
def get_user(user_id):
    query = "SELECT * FROM users WHERE id = ?"
    return db.execute(query, (user_id,))
```

---

## 📁 Project Structure

```
agents-with-adk/
│
├── src/python_codebase_reviewer/    # 📦 Core package (pip installable)
│   ├── agent.py                     # Root orchestrator agent
│   ├── prompt.py                    # Orchestrator prompt
│   ├── sub_agents/                  # Specialized review agents
│   │   ├── security_reviewer/       # Security vulnerability detection
│   │   ├── architecture_reviewer/   # Architecture & design review
│   │   ├── code_quality_reviewer/   # Code quality & style review
│   │   ├── performance_reviewer/    # Performance analysis
│   │   └── python_expert/           # Python best practices
│   ├── tools/                       # Utility tools
│   │   └── github_tools.py         # GitHub API integration
│   └── shared_libraries/           # Shared utilities
│       └── constants.py            # Configuration constants
│
├── integrations/                    # 🔌 Integration examples (reference code)
│   ├── INTEGRATION_GUIDE.md        # Decision guide for choosing integration
│   ├── github_actions/             # Option 1: CI/CD automation
│   ├── github_app/                 # Option 2: Organization-wide deployment
│   ├── github_cli/                 # Option 3: Local development
│   └── direct_api/                 # Option 4: Custom integrations
│
├── evals/                          # 📊 Evaluation & benchmarks
│   ├── run_all_evals.py           # Run all evaluations
│   ├── test_eval.py               # Evaluation test runner
│   └── eval_data/                 # 63 test cases across 6 datasets
│
├── tests/                          # 🧪 Unit & integration tests
│   ├── test_github_tools.py       # GitHub API tests
│   ├── test_github_cli.py         # CLI integration tests
│   └── test_github_app.py         # GitHub App tests
│
├── examples/                       # 💡 Simple usage examples
│   ├── basic_review.py            # Basic code review example
│   └── .env.example               # Environment variable template
│
├── docs/                           # 📚 Documentation
│   └── agent_architecture.md      # Agent system architecture
│
├── setup.py                        # Package setup
├── pyproject.toml                  # Modern Python packaging
├── requirements.txt                # Core dependencies
└── README.md                       # This file
```

---

## 🎯 Features

### Multi-Agent Architecture

The system uses a **hierarchical multi-agent design** where a root orchestrator coordinates 5 specialized reviewers:

```
Root Orchestrator
├── Security Reviewer (OWASP Top 10, Python vulnerabilities)
├── Architecture Reviewer (SOLID, design patterns, anti-patterns)
├── Code Quality Reviewer (PEP standards, Pythonic idioms)
├── Performance Reviewer (Big O, N+1 queries, caching)
└── Python Expert (stdlib, frameworks, modern features)
```

Each agent has:
- **Deep domain knowledge** embedded in prompts (5,000+ lines total)
- **Specialized expertise** in their area
- **Actionable recommendations** with code examples
- **Severity ratings** (Critical, High, Medium, Low)

### Comprehensive Analysis

**Security (OWASP Top 10)**:
- SQL Injection, XSS, CSRF
- Insecure deserialization (pickle)
- Hardcoded secrets and credentials
- Path traversal vulnerabilities
- Command injection

**Architecture**:
- SOLID principles (SRP, OCP, LSP, ISP, DIP)
- Design patterns (Factory, Strategy, Observer, etc.)
- Anti-patterns (God Object, Circular Dependencies)
- Separation of concerns

**Code Quality**:
- PEP 8 (style), PEP 20 (Zen of Python)
- PEP 257 (docstrings), PEP 484/585 (type hints)
- Pythonic idioms (comprehensions, generators, context managers)
- Code smells and maintainability

**Performance**:
- Algorithm complexity (Big O analysis)
- Database query optimization (N+1 detection)
- Memory usage patterns
- Caching opportunities

**Python Best Practices**:
- Standard library usage (collections, itertools, functools)
- Framework patterns (Django ORM, Flask, FastAPI)
- Modern Python features (3.10+ match/case, 3.11+ exception groups)
- Async/await patterns

---

## 🔌 Integration Options

Choose how to integrate with GitHub - see [`integrations/INTEGRATION_GUIDE.md`](integrations/INTEGRATION_GUIDE.md) for decision matrix.

### Option 1: GitHub Actions (CI/CD)
**Best for**: Teams using GitHub Actions, automatic PR reviews

```yaml
# .github/workflows/code-review.yml
name: Code Review
on: [pull_request]
jobs:
  review:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run AI Code Review
        run: python integrations/github_actions/review_pr.py
```

**Setup**: 5 minutes | **Cost**: Free tier available
**Docs**: [`integrations/github_actions/`](integrations/github_actions/)

### Option 2: GitHub App (Organization-wide)
**Best for**: Organizations, enterprise deployment

Deploy as a GitHub App on Cloud Run:
- Automatic reviews on all repositories
- Webhook-based (real-time)
- Centralized configuration
- Auto-scaling

**Setup**: 30 minutes | **Cost**: ~$5-20/month
**Docs**: [`integrations/github_app/`](integrations/github_app/)

### Option 3: GitHub CLI (Local)
**Best for**: Individual developers, pre-commit reviews

```bash
# Review a PR
python integrations/github_cli/review_pr.py 123

# Review local files
python integrations/github_cli/review_files.py src/main.py
```

**Setup**: 10 minutes | **Cost**: Free
**Docs**: [`integrations/github_cli/`](integrations/github_cli/)

### Option 4: Direct API (Custom)
**Best for**: Custom workflows, unique requirements

```python
from python_codebase_reviewer import root_agent
from python_codebase_reviewer.tools.github_tools import fetch_pr_files

# Fetch PR files
files = fetch_pr_files("owner/repo", 123)

# Review each file
for file in files:
    review = root_agent.run(f"Review {file['filename']}: {file['content']}")
```

**Setup**: Varies | **Cost**: Custom
**Docs**: [`integrations/direct_api/`](integrations/direct_api/)

---

## 📊 Evaluation & Metrics

The system has been evaluated on 63 test cases across 6 datasets:

| Metric | Score |
|--------|-------|
| **Precision** | ~90% (few false positives) |
| **Recall** | ~85% (catches most real issues) |
| **F1 Score** | ~0.87 |

**Run evaluations:**
```bash
cd evals
python run_all_evals.py
```

See [`evals/README.md`](evals/README.md) for details.

---

## 🧪 Testing

Comprehensive test suite with 90+ test cases:

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run all tests
pytest

# Run with coverage
pytest --cov=python_codebase_reviewer --cov-report=html

# Run specific test categories
pytest -m unit              # Fast unit tests
pytest -m integration       # Integration tests
pytest -m "not slow"        # Exclude slow tests
```

See [`tests/README.md`](tests/README.md) for details.

---

## 💡 Examples

### Example 1: Basic Review

```python
from python_codebase_reviewer import root_agent

code = """
def calculate_total(items):
    total = 0
    for item in items:
        total += item.price
    return total
"""

review = root_agent.run(f"Review this code:\n\n{code}")
```

### Example 2: Security-Focused Review

```python
from python_codebase_reviewer.sub_agents import security_reviewer

code = """
def login(username, password):
    query = f"SELECT * FROM users WHERE username='{username}' AND password='{password}'"
    return db.execute(query)
"""

review = security_reviewer.run(f"Check for security vulnerabilities:\n\n{code}")
```

### Example 3: Review GitHub PR

```python
from python_codebase_reviewer import root_agent
from python_codebase_reviewer.tools.github_tools import fetch_pr_files, post_pr_review

# Fetch PR files
files = fetch_pr_files("owner/repo", 123)

# Review each Python file
for file in [f for f in files if f['filename'].endswith('.py')]:
    review = root_agent.run(f"Review {file['filename']}")

# Post review
post_pr_review("owner/repo", 123, review)
```

See [`examples/`](examples/) for more.

---

## 🛠️ Development

### Setup Development Environment

```bash
# Clone repository
git clone https://github.com/pavanpaik/agents-with-adk.git
cd agents-with-adk

# Install in development mode with all dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run linting
black src/ tests/
flake8 src/ tests/
mypy src/

# Run evaluations
cd evals && python run_all_evals.py
```

### Project Components

- **Core Package** (`src/python_codebase_reviewer/`): The agent implementation
- **Integrations** (`integrations/`): Reference implementations for GitHub
- **Evaluations** (`evals/`): Quality benchmarks and test cases
- **Tests** (`tests/`): Unit and integration tests
- **Examples** (`examples/`): Simple usage examples
- **Docs** (`docs/`): Documentation

---

## 📖 Documentation

- **[Integration Guide](integrations/INTEGRATION_GUIDE.md)**: Choose the right GitHub integration
- **[Agent Architecture](docs/agent_architecture.md)**: Deep dive into agent design
- **[Testing Guide](tests/README.md)**: How to run and write tests
- **[Evaluation Guide](evals/README.md)**: Agent quality metrics

---

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run tests and linting
6. Submit a pull request

---

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

Built with:
- **[Google Agent Development Kit (ADK)](https://github.com/google/agent-development-kit)** - Multi-agent orchestration
- **[Google Gemini](https://ai.google.dev/)** - AI models (gemini-2.0-flash-exp, gemini-2.0-pro-exp)

---

## 📧 Support

- **Issues**: [GitHub Issues](https://github.com/pavanpaik/agents-with-adk/issues)
- **Documentation**: [docs/](docs/)
- **Examples**: [examples/](examples/)
- **Integrations**: [integrations/](integrations/)

---

**Made with ❤️ using Google's Agent Development Kit**
