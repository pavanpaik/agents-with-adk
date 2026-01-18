# Proposed Project Reorganization

## Current Issues

The project currently mixes three distinct concerns in one directory:
1. **Core agent code** (the actual agent implementation)
2. **Integration examples** (how to use agents with GitHub)
3. **Evaluation suite** (testing agent quality)

This makes it unclear:
- What's the core library users should import
- What's example/reference code
- What's testing/validation code

## Proposed Structure

```
agents-with-adk/
│
├── src/
│   └── python_codebase_reviewer/      # Core package (installable)
│       ├── __init__.py
│       ├── agent.py
│       ├── prompt.py
│       ├── constants.py
│       ├── sub_agents/
│       │   ├── __init__.py
│       │   ├── security_reviewer/
│       │   ├── architecture_reviewer/
│       │   ├── code_quality_reviewer/
│       │   ├── performance_reviewer/
│       │   └── python_expert/
│       └── tools/
│           ├── __init__.py
│           └── github_tools.py
│
├── integrations/                       # Integration examples (reference)
│   ├── README.md                      # Overview of all options
│   ├── INTEGRATION_GUIDE.md           # Decision guide
│   │
│   ├── github_actions/                # Option 1
│   │   ├── README.md
│   │   ├── SETUP.md
│   │   ├── code-review.yml
│   │   └── review_pr.py
│   │
│   ├── github_app/                    # Option 2
│   │   ├── README.md
│   │   ├── SETUP.md
│   │   ├── webhook_handler.py
│   │   ├── Dockerfile
│   │   ├── deploy.sh
│   │   └── setup_secrets.sh
│   │
│   ├── github_cli/                    # Option 3
│   │   ├── README.md
│   │   ├── SETUP.md
│   │   ├── review_pr.py
│   │   └── review_files.py
│   │
│   └── direct_api/                    # Option 4
│       ├── README.md
│       ├── SETUP.md
│       ├── example_simple_review.py
│       ├── example_agent_with_github_tools.py
│       └── example_custom_workflow.py
│
├── evals/                             # Evaluation suite (validation)
│   ├── README.md
│   ├── run_all_evals.py
│   ├── test_eval.py
│   ├── datasets/
│   │   ├── security_eval.json
│   │   ├── architecture_eval.json
│   │   ├── code_quality_eval.json
│   │   ├── performance_eval.json
│   │   ├── python_expert_eval.json
│   │   └── end_to_end_eval.json
│   └── metrics/
│       └── calculate_metrics.py
│
├── tests/                             # Unit tests
│   ├── README.md
│   ├── conftest.py
│   ├── test_agents.py
│   ├── test_github_tools.py
│   ├── test_integration_github_actions.py
│   ├── test_integration_github_cli.py
│   └── test_integration_github_app.py
│
├── docs/                              # Documentation
│   ├── index.md
│   ├── quickstart.md
│   ├── agent_architecture.md
│   ├── integration_options.md
│   └── evaluation_metrics.md
│
├── examples/                          # Simple usage examples
│   ├── basic_review.py
│   ├── custom_agent.py
│   └── multi_stage_review.py
│
├── setup.py                          # Package installation
├── pyproject.toml                    # Modern Python packaging
├── requirements.txt                  # Core dependencies
├── requirements-dev.txt              # Development dependencies
├── pytest.ini
├── .github/
│   └── workflows/
│       ├── tests.yml
│       └── evals.yml
└── README.md
```

## Key Improvements

### 1. Clear Separation of Concerns

**Core Package** (`src/python_codebase_reviewer/`)
- Only the agent implementation
- Minimal dependencies
- Clean imports
- Installable via pip

**Integrations** (`integrations/`)
- How to use the agents
- Not installed by default
- Users copy what they need
- Reference implementations

**Evaluations** (`evals/`)
- Agent quality testing
- Not needed for usage
- Separate from unit tests
- Can be run independently

**Tests** (`tests/`)
- Unit tests for core package
- Integration tests for GitHub options
- Fast, isolated tests

### 2. Installation Clarity

```bash
# Install core package only
pip install .

# Or install from PyPI (if published)
pip install python-codebase-reviewer

# Development installation (includes dev dependencies)
pip install -e ".[dev]"
```

### 3. Usage Clarity

```python
# Import core agent - clear what's the library
from python_codebase_reviewer import root_agent
from python_codebase_reviewer.tools.github_tools import fetch_pr_files

# Use integration examples
# Users copy files from integrations/ to their project
```

### 4. Clear Documentation Structure

**Top-level README.md**:
```markdown
# Python Codebase Reviewer

AI-powered code review for Python using multi-agent system.

## Installation
pip install python-codebase-reviewer

## Quick Start
...

## Integration Options
See [integrations/](integrations/) for GitHub integration examples.

## Evaluation
See [evals/](evals/) for agent quality metrics and benchmarks.
```

**integrations/README.md**:
```markdown
# GitHub Integration Options

Choose how to integrate with GitHub:
1. GitHub Actions - CI/CD automation
2. GitHub App - Organization-wide deployment
3. GitHub CLI - Local development
4. Direct API - Custom integrations

See INTEGRATION_GUIDE.md for decision matrix.
```

**evals/README.md**:
```markdown
# Evaluation Suite

Benchmarks and metrics for agent quality.

- 63 test cases across 6 datasets
- Precision/Recall/F1 metrics
- Run: python run_all_evals.py
```

## Migration Steps

Would you like me to reorganize the project with this structure?

### Option A: Full Reorganization (Recommended)
- Move all files to new structure
- Update all imports
- Update documentation
- Create new setup.py/pyproject.toml
- Test everything still works

### Option B: Incremental Migration
- Keep current structure for now
- Add clear README markers
- Document which parts are core vs. examples
- Migrate in phases

### Option C: Hybrid
- Core package stays in python_codebase_reviewer/
- Move integrations/ and evals/ to top level
- Keep backward compatibility

## Benefits of Reorganization

✅ **Clarity**: Clear separation of core vs. examples vs. validation
✅ **Installability**: Can pip install just the core package
✅ **Maintainability**: Easy to see what's core vs. optional
✅ **Scalability**: Easy to add new integrations without bloating core
✅ **Documentation**: Natural documentation structure
✅ **Testing**: Separate unit tests from integration tests from evals
✅ **Distribution**: Can publish to PyPI cleanly

## Trade-offs

**Pros**:
- Professional project structure
- Clear boundaries
- Better for open source
- Easier for contributors

**Cons**:
- Breaking change (need to update imports)
- More directories to navigate
- Migration effort required

## Recommendation

I recommend **Option A: Full Reorganization** because:
1. Project is still new (early stage)
2. No published package yet (no breaking changes for users)
3. Sets good foundation for growth
4. Makes project more professional and maintainable

The structure would make it clear:
- **Core**: What you import (`from python_codebase_reviewer import ...`)
- **Integrations**: What you copy/deploy (choose your option)
- **Evals**: How to validate quality (run benchmarks)
- **Tests**: How to verify correctness (run unit tests)

What do you think? Should I proceed with the reorganization?
