# Python Codebase Reviewer

**AI-powered code review for Python using autonomous agents with GitHub MCP integration.**

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![GitHub MCP](https://img.shields.io/badge/MCP-GitHub-blue.svg)](https://github.com/github/github-mcp-server)

---

## 🌟 What's New: GitHub MCP Integration

**Python Codebase Reviewer now uses the [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) with GitHub's official MCP server!**

### ✨ What This Means:
- ✅ **Autonomous agents** that fetch files, post reviews, and manage PRs themselves
- ✅ **51+ GitHub tools** available (vs 7 custom tools before)
- ✅ **Natural language control** - just tell the agent what you want
- ✅ **69% less code** to maintain
- ✅ **Standardized protocol** for tool integration

### Before vs After:
```python
# ❌ Before (Manual orchestration)
from python_codebase_reviewer.tools import fetch_pr_files, fetch_file_content
files = fetch_pr_files(repo, pr)
for file in files:
    content = fetch_file_content(repo, file['filename'])
    review = root_agent.run(f"Review: {content}")
    # ... more manual steps

# ✅ After (Agent-driven with MCP)
from python_codebase_reviewer import root_agent
review = root_agent.run("""
Review PR #123 in owner/repo.
Fetch files, analyze them, post your findings.
""")
# Agent autonomously uses 51+ GitHub MCP tools!
```

---

## 🚀 Quick Start

### Installation

```bash
# Install the package
pip install -e .

# Install GitHub MCP server
npm install -g @modelcontextprotocol/server-github

# Set environment variables
export GOOGLE_API_KEY=your_google_api_key
export GITHUB_TOKEN=your_github_token
```

### Basic Code Review

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

### Review a GitHub PR (Agent-Driven)

```python
from python_codebase_reviewer import root_agent

# Just tell the agent what you want - it figures out the tools!
review = root_agent.run("""
Review pull request #456 in microsoft/vscode-python.

1. Fetch changed Python files using MCP tools
2. Analyze for security, architecture, quality, performance
3. Generate markdown report with severity levels
4. Post review as PR comment
""")
```

**The agent autonomously uses GitHub MCP tools to:**
- Fetch PR files (`get_pull_request_files`)
- Get file contents (`get_file_contents`)
- Post reviews (`create_pull_request_review`)
- And 48+ other GitHub operations!

---

## 📚 Documentation

| Document | Description |
|----------|-------------|
| **[MCP_COOKBOOK.md](integrations/direct_api/MCP_COOKBOOK.md)** | 15 natural language patterns for code review |
| **[MEANINGFUL_INTEGRATIONS.md](MEANINGFUL_INTEGRATIONS.md)** | Integration options and recommendations |
| **[MCP_MIGRATION_SUMMARY.md](MCP_MIGRATION_SUMMARY.md)** | Migration details and benefits |
| **[INTEGRATION_GUIDE.md](integrations/INTEGRATION_GUIDE.md)** | Choose the right integration method |

---

## 🎯 Features

### Multi-Agent Architecture + GitHub MCP

The system combines **specialized AI reviewers** with **autonomous GitHub operations**:

```
Root Orchestrator (gemini-2.0-pro-exp)
│
├── 🛡️ Security Reviewer (OWASP Top 10, Python vulnerabilities)
├── 🏗️ Architecture Reviewer (SOLID, design patterns, anti-patterns)
├── ✨ Code Quality Reviewer (PEP standards, Pythonic idioms)
├── ⚡ Performance Reviewer (Big O, N+1 queries, caching)
├── 🐍 Python Expert (stdlib, frameworks, modern features)
└── 🔧 GitHub MCP Toolset (51+ GitHub API tools)
```

Each specialized agent provides:
- **Deep domain knowledge** (5,000+ lines of prompts)
- **Actionable recommendations** with code examples
- **Severity ratings** (Critical, High, Medium, Low)

GitHub MCP tools enable:
- **Autonomous file fetching** from repositories
- **PR comment posting** and review creation
- **CI/CD integration** (check workflow status)
- **Security scanning** (code scanning alerts)
- **Auto-fix and push** capabilities

### Comprehensive Analysis

**🛡️ Security (OWASP Top 10)**:
- SQL Injection, XSS, CSRF
- Insecure deserialization (pickle)
- Hardcoded secrets and credentials
- Path traversal vulnerabilities
- Command injection

**🏗️ Architecture**:
- SOLID principles (SRP, OCP, LSP, ISP, DIP)
- Design patterns (Factory, Strategy, Observer, etc.)
- Anti-patterns (God Object, Circular Dependencies)
- Separation of concerns

**✨ Code Quality**:
- PEP 8 (style), PEP 20 (Zen of Python)
- PEP 257 (docstrings), PEP 484/585 (type hints)
- Pythonic idioms (comprehensions, generators, context managers)
- Code smells and maintainability

**⚡ Performance**:
- Algorithm complexity (Big O analysis)
- Database query optimization (N+1 detection)
- Memory usage patterns
- Caching opportunities

**🐍 Python Best Practices**:
- Standard library usage (collections, itertools, functools)
- Framework patterns (Django ORM, Flask, FastAPI)
- Modern Python features (3.10+ match/case, 3.11+ exception groups)
- Async/await patterns

---

## 🔌 Integration Options

### Option 1: GitHub Actions (Recommended)
**Best for**: Teams using CI/CD, automatic PR reviews

```yaml
# .github/workflows/ai-review.yml
name: AI Code Review
on: [pull_request]
jobs:
  review:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
      - uses: actions/setup-node@v4
      - run: npm install -g @modelcontextprotocol/server-github
      - run: pip install -e .
      - name: Run AI Review
        env:
          GOOGLE_API_KEY: ${{ secrets.GOOGLE_API_KEY }}
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: python integrations/github_actions/review_pr.py --repo ${{ github.repository }} --pr-number ${{ github.event.pull_request.number }}
```

**Setup**: 5 minutes | **Cost**: Free tier available
**Docs**: [`integrations/github_actions/`](integrations/github_actions/)

---

### Option 2: CLI Tool (Simplified)
**Best for**: Individual developers, manual reviews

```bash
# Review a PR
cd your-repo
python integrations/github_cli/review_pr.py 123

# Review current branch's PR
python integrations/github_cli/review_pr.py

# Review and post comment
python integrations/github_cli/review_pr.py 123 --post
```

**Setup**: 10 minutes | **Cost**: Free
**Note**: Now just 183 lines (was 498 lines) - agent does the heavy lifting via MCP!

---

### Option 3: Direct API (Custom Workflows)
**Best for**: Custom integrations, automation scripts

```python
from python_codebase_reviewer import root_agent

# Example: Security-only review
review = root_agent.run("""
Review PR #456 in owner/repo for SECURITY ONLY.
Focus on: SQL injection, XSS, secrets, auth bugs.
Report only Critical and High severity.
""")

# Example: Auto-fix and push
root_agent.run("""
Review PR #789 in owner/repo.
Auto-fix PEP 8 violations.
Use push_files to update the PR branch.
Report what was auto-fixed.
""")
```

**See [MCP_COOKBOOK.md](integrations/direct_api/MCP_COOKBOOK.md) for 15 natural language patterns!**

---

### Option 4: GitHub App (Organizations)
**Best for**: Organization-wide deployment, scalability

Deploy as a GitHub App on Cloud Run for centralized review automation.

**Setup**: 30 minutes | **Cost**: ~$5-20/month
**Docs**: [`integrations/github_app/`](integrations/github_app/)

---

## 📁 Project Structure

```
agents-with-adk/
│
├── src/python_codebase_reviewer/    # Core package
│   ├── agent.py                     # Root orchestrator + GitHub MCP toolset
│   ├── prompt.py                    # Orchestrator instructions
│   ├── sub_agents/                  # Specialized reviewers
│   │   ├── security_reviewer/       # Security analysis
│   │   ├── architecture_reviewer/   # Architecture & design
│   │   ├── code_quality_reviewer/   # Code quality & style
│   │   ├── performance_reviewer/    # Performance optimization
│   │   └── python_expert/           # Python best practices
│   ├── tools/                       # (Now uses GitHub MCP)
│   └── shared_libraries/           # Configuration
│       └── constants.py            # Model configuration
│
├── integrations/                    # Integration examples
│   ├── MCP_COOKBOOK.md              # 15 natural language patterns
│   ├── INTEGRATION_GUIDE.md        # Choose your integration
│   ├── MIGRATION_TO_MCP.md         # Migration guide
│   ├── github_actions/             # CI/CD automation (updated for MCP)
│   ├── github_app/                 # Organization deployment
│   ├── github_cli/                 # Local CLI (simplified: 498→183 lines)
│   └── direct_api/                 # Custom workflows
│       ├── MCP_COOKBOOK.md         # Natural language examples
│       └── example_simple_review.py # Simple MCP example
│
├── evals/                          # Evaluation & benchmarks
│   └── eval_data/                 # 63 test cases
│
├── tests/                          # Unit tests
│
├── docs/                           # Architecture docs
│   └── agent_architecture.md
│
├── MCP_MIGRATION_SUMMARY.md        # MCP migration details
├── MEANINGFUL_INTEGRATIONS.md      # Integration recommendations
├── pyproject.toml                  # Package config (uses google-adk[mcp])
└── README.md                       # This file
```

---

## 🎨 Usage Examples

### 1. Basic PR Review
```python
root_agent.run("""
Review PR #123 in owner/repo.
Fetch files, analyze them, generate markdown report.
""")
```

### 2. Security-Focused Review
```python
root_agent.run("""
Review PR #456 in owner/repo for SECURITY ONLY.
Check: SQL injection, XSS, secrets, auth bugs.
Report Critical and High severity issues only.
""")
```

### 3. Review with Context
```python
root_agent.run("""
Review PR #789 in owner/repo.

CONTEXT:
- Production hotfix for issue #100
- Security critical, performance secondary
- Python 3.8 compatible (no 3.10+ features)
- Deploys to 10M+ users

Review accordingly.
""")
```

### 4. Auto-Fix and Push
```python
root_agent.run("""
Review PR #321 in owner/repo.
Auto-fix PEP 8 violations (imports, whitespace, line length).
Use push_files to update the PR branch.
Report what was fixed and what needs manual attention.
""")
```

### 5. Multi-Stage Review
```python
# Stage 1: Security gate
security = root_agent.run("""
Review PR #555 in owner/repo for SECURITY.
If Critical issues found, create security advisory and STOP.
""")

if "CRITICAL" not in security:
    # Stage 2: Full review
    root_agent.run("""
    Review PR #555 for architecture, quality, performance.
    """)
```

**See [MCP_COOKBOOK.md](integrations/direct_api/MCP_COOKBOOK.md) for 15 complete examples!**

---

## 🧪 Testing & Evaluation

### Run Tests
```bash
# Unit tests
pytest tests/

# With coverage
pytest --cov=src/python_codebase_reviewer tests/
```

### Run Evaluations
```bash
# All evaluations (63 test cases)
python evals/run_all_evals.py

# Specific dataset
python evals/test_eval.py --dataset security
```

**Evaluation datasets:**
- Security vulnerabilities (OWASP Top 10)
- Architecture anti-patterns
- Code quality issues
- Performance problems
- Python best practices
- Real-world bugs

---

## ⚙️ Configuration

### Environment Variables

```bash
# Required
export GOOGLE_API_KEY=your_google_api_key          # For Gemini models
export GITHUB_TOKEN=your_github_personal_token      # For GitHub MCP tools

# Optional: Override model configurations
export ORCHESTRATOR_MODEL=gemini-2.0-pro-exp        # Root orchestrator
export REVIEWER_MODEL=gemini-2.0-flash-thinking-exp # Security & Architecture
export ANALYZER_MODEL=gemini-2.0-flash-exp          # Code Quality & Performance
export PYTHON_EXPERT_MODEL=gemini-2.0-flash-thinking-exp # Python Expert
```

### Model Configuration

The system uses Google's Gemini models by default:
- **Orchestrator**: `gemini-2.0-pro-exp` (high-quality coordination)
- **Reviewers**: `gemini-2.0-flash-thinking-exp` (deep reasoning)
- **Analyzers**: `gemini-2.0-flash-exp` (fast analysis)

**All configurable via environment variables!**

---

## 📊 Why Use This?

### vs Traditional Static Analysis
| Feature | Static Analysis | Python Codebase Reviewer |
|---------|----------------|-------------------------|
| **Context** | Limited | Full codebase context via MCP |
| **Flexibility** | Fixed rules | Adapts to your context |
| **Explanations** | Generic | Specific with examples |
| **Security** | Known patterns | Logical vulnerabilities too |
| **Auto-fix** | Limited | Natural language commands |

### vs Manual Code Review
| Feature | Manual Review | Python Codebase Reviewer |
|---------|--------------|-------------------------|
| **Speed** | Hours | Minutes |
| **Consistency** | Varies | Always comprehensive |
| **Availability** | Business hours | 24/7 |
| **Expertise** | Depends on reviewer | 5 specialized agents |
| **Cost** | High (developer time) | Low (API costs) |

---

## 🚀 Roadmap

### ✅ Completed
- [x] Multi-agent architecture with 5 specialized reviewers
- [x] GitHub MCP integration (51+ tools)
- [x] GitHub Actions integration
- [x] CLI tool
- [x] 63 evaluation test cases
- [x] Natural language control via MCP

### 🔄 In Progress (Phase 1)
- [ ] Pre-commit hook package
- [ ] VS Code extension
- [ ] Enhanced auto-fix capabilities

### 🔮 Future (Phase 2+)
- [ ] JetBrains plugin (PyCharm)
- [ ] GitHub Copilot integration
- [ ] Support for more languages (JavaScript, TypeScript, Go)
- [ ] Review analytics dashboard
- [ ] Team-specific custom rules

---

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

---

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- Built with [Google Agent Development Kit (ADK)](https://github.com/google/adk)
- Powered by [Gemini models](https://ai.google.dev/gemini-api)
- GitHub integration via [GitHub MCP Server](https://github.com/github/github-mcp-server)
- Inspired by the [Model Context Protocol](https://modelcontextprotocol.io/)

---

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/pavanpaik/agents-with-adk/issues)
- **Documentation**: Check the [`docs/`](docs/) and [`integrations/`](integrations/) directories
- **Examples**: See [`integrations/direct_api/MCP_COOKBOOK.md`](integrations/direct_api/MCP_COOKBOOK.md)

---

**⭐ Star this repo if you find it useful!**
