# GitHub CLI Integration - Python Codebase Reviewer

Review pull requests and Python files locally using the GitHub CLI (gh).

## Overview

This integration lets you review code on your local machine using GitHub CLI commands. Perfect for:
- Individual developers who want manual control
- Pre-commit reviews before opening PRs
- Local development and testing
- Teams without CI/CD infrastructure

**Deployment**: Runs locally on your machine
**Cost**: Free (just API costs)
**Best for**: Manual, on-demand reviews by individual developers

---

## Quick Start

### 1. Install Prerequisites

**GitHub CLI**:
```bash
# macOS
brew install gh

# Linux (Debian/Ubuntu)
sudo apt install gh

# Linux (Fedora/CentOS)
sudo dnf install gh

# Windows
winget install GitHub.cli

# Or download from: https://cli.github.com/
```

**Python Dependencies**:
```bash
pip install google-adk requests
```

### 2. Authenticate

```bash
# Login to GitHub
gh auth login

# Verify authentication
gh auth status
```

### 3. Get Google API Key

1. Visit: https://aistudio.google.com/app/apikey
2. Click "Create API key"
3. Copy the key

### 4. Set Environment Variable

```bash
# Add to ~/.bashrc or ~/.zshrc
export GOOGLE_API_KEY="your-api-key-here"

# Or set for current session
export GOOGLE_API_KEY="your-api-key-here"
```

### 5. Review a Pull Request

```bash
# Navigate to this directory
cd python_codebase_reviewer/github_cli

# Review a specific PR
python review_pr.py 123

# Review current branch's PR
python review_pr.py

# Review and post comment
python review_pr.py 123 --post
```

**Output**: Creates `review_results.md` with detailed findings.

---

## Features

### 📋 Review Pull Requests

Review any PR with a single command:

```bash
# Review specific PR
python review_pr.py 123

# Review current branch
python review_pr.py

# Post review as comment
python review_pr.py 123 --post-comment

# Custom output file
python review_pr.py 123 --output my_review.md

# Print to console only (no file)
python review_pr.py 123 --no-save
```

### 📄 Review Individual Files

Review Python files directly without PR context:

```bash
# Review specific files
python review_files.py src/main.py src/utils.py

# Review all files in directory
python review_files.py src/**/*.py

# Review with custom output
python review_files.py src/main.py --output review.md
```

### 🔍 Comprehensive Analysis

Every review includes:
- **Security**: SQL injection, XSS, hardcoded secrets, unsafe operations
- **Architecture**: SOLID principles, design patterns, code organization
- **Code Quality**: PEP 8/20/257/484, Pythonic idioms, readability
- **Performance**: Algorithm complexity, database queries, memory usage
- **Best Practices**: Framework patterns, Python features, stdlib usage

### 🚦 Severity Levels

Findings categorized by impact:
- 🔴 **CRITICAL**: Security vulnerabilities, data loss
- 🟠 **HIGH**: Major bugs, design flaws
- 🟡 **MEDIUM**: Code quality issues
- 🔵 **LOW**: Style issues, minor improvements

---

## Usage Examples

### Pre-Commit Review

Review staged changes before committing:

```bash
#!/bin/bash
# pre-commit-review.sh

# Get staged Python files
STAGED_FILES=$(git diff --cached --name-only --diff-filter=ACM | grep '.py$')

if [ -z "$STAGED_FILES" ]; then
    echo "No Python files staged"
    exit 0
fi

# Review files
python review_files.py $STAGED_FILES

# Exit code 1 if critical issues found
```

Add to git hooks:
```bash
cp pre-commit-review.sh .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

### Review Before Opening PR

```bash
#!/bin/bash
# review-before-pr.sh

# Ensure we're on a feature branch
if [ "$(git branch --show-current)" == "main" ]; then
    echo "Cannot run on main branch"
    exit 1
fi

# Get changed files vs main
CHANGED_FILES=$(git diff --name-only main... | grep '.py$')

if [ -z "$CHANGED_FILES" ]; then
    echo "No Python files changed"
    exit 0
fi

echo "Reviewing changes before PR..."
python review_files.py $CHANGED_FILES --output review_before_pr.md

echo ""
echo "Review saved to: review_before_pr.md"
echo ""
echo "If satisfied, create PR with:"
echo "  gh pr create"
```

### Batch Review Multiple PRs

```bash
#!/bin/bash
# review-all-open-prs.sh

# Get all open PRs
PRS=$(gh pr list --json number --jq '.[].number')

for pr in $PRS; do
    echo "Reviewing PR #$pr..."
    python review_pr.py $pr --output "review_pr_${pr}.md"
    echo ""
done

echo "All reviews complete!"
echo "Files: review_pr_*.md"
```

### Review Specific Commit

```bash
# Get files changed in specific commit
COMMIT_SHA="abc123"
FILES=$(git diff-tree --no-commit-id --name-only -r $COMMIT_SHA | grep '.py$')

python review_files.py $FILES
```

### Daily Review Workflow

```bash
#!/bin/bash
# daily-review.sh - Review all PRs assigned to you

# Get PRs where you're requested as reviewer
PRS=$(gh pr list --search "review-requested:@me" --json number --jq '.[].number')

if [ -z "$PRS" ]; then
    echo "No PRs pending your review"
    exit 0
fi

echo "You have reviews pending for PRs: $PRS"
echo ""

for pr in $PRS; do
    echo "===================================="
    echo "Reviewing PR #$pr"
    echo "===================================="

    # Review and save
    python review_pr.py $pr --output "review_${pr}.md"

    # Ask if user wants to post
    echo ""
    read -p "Post this review as comment? [y/N] " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        gh pr comment $pr --body-file "review_${pr}.md"
        echo "✅ Comment posted"
    fi

    echo ""
done
```

---

## Integration with Git Workflow

### As Git Alias

Add to `.gitconfig`:

```ini
[alias]
    review-pr = "!f() { python /path/to/review_pr.py \"$@\"; }; f"
    review-files = "!f() { python /path/to/review_files.py \"$@\"; }; f"
```

Usage:
```bash
git review-pr 123
git review-files src/main.py
```

### With gh Extension

Create `~/.local/share/gh/extensions/gh-review/gh-review`:

```bash
#!/bin/bash
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
python "$SCRIPT_DIR/review_pr.py" "$@"
```

Usage:
```bash
gh review 123
gh review --post-comment
```

### Pre-Push Hook

Review all commits before pushing:

`.git/hooks/pre-push`:
```bash
#!/bin/bash

# Get files changed in commits being pushed
FILES=$(git diff --name-only @{u}.. | grep '.py$')

if [ ! -z "$FILES" ]; then
    echo "Reviewing files before push..."
    python review_files.py $FILES

    if [ $? -ne 0 ]; then
        echo ""
        echo "⚠️  Critical issues found!"
        read -p "Continue push anyway? [y/N] " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
fi
```

---

## Customization

### Custom Review Focus

Edit `review_pr.py` line 63 or `review_files.py` line 42:

```python
review_request = f"""
Review this Python file for our company standards:

**Project Context**:
- Framework: FastAPI
- Database: PostgreSQL with SQLAlchemy
- Deployment: Kubernetes
- Python: 3.11+

**Critical Requirements**:
- All endpoints must have rate limiting
- All database queries must use connection pooling
- All async code must use asyncio, not threads
- All secrets from environment variables only

**Style Requirements**:
- PEP 8 + Black formatting
- Google-style docstrings
- Type hints required (mypy strict mode)

{code}

Focus on security, performance, and our standards above.
"""
```

### Filter Files

Only review certain files:

```bash
# Only review files in src/ directory
git diff --name-only main... | grep '^src/.*\.py$' | xargs python review_files.py

# Exclude test files
git diff --name-only main... | grep '\.py$' | grep -v 'test_' | xargs python review_files.py

# Only review modified files (not new ones)
git diff --name-only --diff-filter=M main... | grep '\.py$' | xargs python review_files.py
```

### Customize Output Format

Edit `format_markdown()` function in scripts:

```python
def format_markdown(results, pr_info, repo):
    """Custom output format for your organization."""
    output = []

    # Custom header with logo
    output.append("# 🏢 ACME Corp Code Review\n\n")
    output.append(f"**Reviewed by**: {os.getenv('USER', 'AI')}\n")
    output.append(f"**Date**: {datetime.now().strftime('%Y-%m-%d')}\n\n")

    # ... rest of formatting

    # Custom footer
    output.append("---\n\n")
    output.append("**Need help?** Contact #engineering-help on Slack\n")

    return ''.join(output)
```

---

## Troubleshooting

### Issue: "gh: command not found"

**Fix**: Install GitHub CLI
```bash
# macOS
brew install gh

# Or visit: https://cli.github.com/
```

### Issue: "gh: not authenticated"

**Fix**: Login to GitHub
```bash
gh auth login

# Follow prompts to authenticate
```

### Issue: "GOOGLE_API_KEY environment variable not set"

**Fix**: Set environment variable
```bash
export GOOGLE_API_KEY="your-key-here"

# Add to ~/.bashrc or ~/.zshrc to persist
echo 'export GOOGLE_API_KEY="your-key-here"' >> ~/.bashrc
source ~/.bashrc
```

### Issue: "PR not found" when using `python review_pr.py`

**Cause**: Current branch doesn't have an associated PR

**Fix**: Specify PR number
```bash
python review_pr.py 123
```

Or create PR first:
```bash
gh pr create
python review_pr.py
```

### Issue: "Could not read file"

**Cause**: File doesn't exist on the PR branch

**Debug**:
```bash
# Check if file exists on branch
git ls-tree -r --name-only PR_BRANCH | grep filename.py

# Check file changes
gh pr diff PR_NUMBER
```

### Issue: Review takes too long

**Cause**: Large files or many files

**Fix**: Review files in batches
```bash
# Review 5 files at a time
gh pr view 123 --json files --jq '.files[].path' | \
    grep '.py$' | \
    head -5 | \
    xargs python review_files.py
```

### Issue: "ImportError: No module named 'python_codebase_reviewer'"

**Cause**: Script can't find the reviewer module

**Fix 1**: Run from correct directory
```bash
cd python_codebase_reviewer/github_cli
python review_pr.py 123
```

**Fix 2**: Add to PYTHONPATH
```bash
export PYTHONPATH="/path/to/agents-with-adk:$PYTHONPATH"
python review_pr.py 123
```

**Fix 3**: Install as package
```bash
cd agents-with-adk
pip install -e .
python /path/to/review_pr.py 123
```

---

## Performance & Costs

### Execution Time

- **Small file** (< 100 lines): ~10-20 seconds
- **Medium file** (100-500 lines): ~20-40 seconds
- **Large file** (500+ lines): ~40-60 seconds

**Per PR**: Depends on number of files (sequential processing)

### Google AI API Costs

**Gemini models** (as of Jan 2025):
- gemini-2.0-flash-exp: FREE during preview
- gemini-2.0-pro-exp: FREE during preview
- After preview: ~$0.01-0.05 per file (estimate)

**Monitoring**: https://aistudio.google.com/app/apikey

### Local Resources

- **CPU**: Minimal (network-bound, not compute-bound)
- **Memory**: ~100-200 MB
- **Network**: ~10-50 KB per request

---

## Comparison with Other Options

| Feature | GitHub CLI (Option 3) | GitHub Actions (Option 1) | GitHub App (Option 2) | Direct API (Option 4) |
|---------|----------------------|---------------------------|------------------------|------------------------|
| **Deployment** | Local scripts | Add workflow file | Cloud Run service | Custom integration |
| **Automation** | ❌ Manual | ✅ Automatic | ✅ Automatic | ⚙️ Custom |
| **Setup time** | 10 minutes | 5 minutes | 30 minutes | Custom |
| **Cost** | Free (API only) | Free tier available | ~$5-20/month | Varies |
| **Control** | ✅ Full control | Limited | Limited | ✅ Full control |
| **Best for** | Individual devs | Teams | Organizations | Custom workflows |

**Choose GitHub CLI if**:
- ✅ You want manual, on-demand reviews
- ✅ You're an individual developer or small team
- ✅ You want to review before committing/pushing
- ✅ You don't want to set up CI/CD infrastructure
- ✅ You want full control over when reviews run

**Choose other options if**:
- ❌ You want automatic reviews on every PR (use Actions or App)
- ❌ You need organization-wide deployment (use App)
- ❌ You have custom integration requirements (use Direct API)

---

## Advanced Usage

### Parallel Reviews

Review multiple files in parallel:

```bash
#!/bin/bash
# parallel-review.sh

FILES=($@)  # All files as array

# Function to review one file
review_one() {
    python review_files.py "$1" --output "review_$(basename $1).md"
}

export -f review_one

# Review 4 files in parallel
printf '%s\n' "${FILES[@]}" | xargs -n 1 -P 4 -I {} bash -c 'review_one "$@"' _ {}

echo "All reviews complete!"
```

### Integrate with Code Editors

**VS Code task** (`.vscode/tasks.json`):
```json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "Review Current File",
      "type": "shell",
      "command": "python",
      "args": [
        "${workspaceFolder}/python_codebase_reviewer/github_cli/review_files.py",
        "${file}",
        "--output",
        "${file}.review.md"
      ],
      "problemMatcher": []
    }
  ]
}
```

**Vim/Neovim**:
```vim
" Add to .vimrc or init.vim
command! ReviewFile !python /path/to/review_files.py % --output %.review.md
```

### CI/CD Integration

Use in CI even without GitHub Actions:

```yaml
# .gitlab-ci.yml (GitLab)
code_review:
  script:
    - pip install google-adk gh
    - export PR_NUMBER=$(echo $CI_MERGE_REQUEST_IID)
    - python review_pr.py $PR_NUMBER --post
```

```yaml
# .circleci/config.yml (CircleCI)
jobs:
  code_review:
    steps:
      - checkout
      - run: pip install google-adk gh
      - run: python review_pr.py $CIRCLE_PR_NUMBER
```

---

## Next Steps

### 1. Automate Your Workflow

Create shell functions in `~/.bashrc`:

```bash
# Quick PR review
review() {
    cd /path/to/agents-with-adk/python_codebase_reviewer/github_cli
    python review_pr.py "$@"
}

# Review staged changes
review-staged() {
    cd /path/to/agents-with-adk/python_codebase_reviewer/github_cli
    git diff --cached --name-only | grep '.py$' | xargs python review_files.py
}
```

### 2. Customize for Your Stack

Edit review prompts to focus on:
- Your framework (Django, Flask, FastAPI)
- Your deployment environment (AWS Lambda, K8s, etc.)
- Your coding standards
- Your security requirements

### 3. Track Review Quality

Keep a log of reviews:
```bash
# review-log.sh
echo "$(date): Reviewed PR #$1" >> ~/review_log.txt
python review_pr.py "$1"
```

Analyze effectiveness:
```bash
# How many PRs reviewed this month?
grep "$(date +%Y-%m)" ~/review_log.txt | wc -l
```

### 4. Try Other Integration Options

- **Option 1 (GitHub Actions)**: For automatic PR reviews
- **Option 2 (GitHub App)**: For organization-wide deployment
- **Option 4 (Direct API)**: For custom integrations

See parent directory README for comparison.

---

## Support

- **Documentation**: See parent directory README
- **Issues**: Report bugs at your repository
- **Other options**: Explore other integration methods

---

**Ready to start?** Just run:

```bash
cd python_codebase_reviewer/github_cli
python review_pr.py --help
```
