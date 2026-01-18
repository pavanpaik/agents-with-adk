# Setup Guide - Direct API Integration

Quick guide to using the GitHub API tools and Python Codebase Reviewer directly.

---

## Prerequisites

- Python 3.8+
- GitHub account with a personal access token
- Google AI API key

---

## Step 1: Install Dependencies (1 minute)

```bash
pip install google-adk requests
```

---

## Step 2: Get GitHub Token (2 minutes)

1. **Go to GitHub settings**:
   - Visit: https://github.com/settings/tokens

2. **Generate new token (classic)**:
   - Click "Generate new token" → "Generate new token (classic)"
   - Name: `Code Review Token`
   - Select scopes:
     - ✅ `repo` (all)
     - ✅ `read:org` (if reviewing org repositories)
   - Click "Generate token"

3. **Copy token**:
   - Starts with `ghp_...`
   - ⚠️ Save it securely - you won't see it again!

---

## Step 3: Get Google AI API Key (2 minutes)

1. Visit: https://aistudio.google.com/app/apikey
2. Click "Create API key"
3. Copy the API key (starts with `AIza...`)

---

## Step 4: Set Environment Variables (1 minute)

**Linux/macOS**:
```bash
export GITHUB_TOKEN="ghp_your_token_here"
export GOOGLE_API_KEY="AIza_your_key_here"

# Make permanent (add to ~/.bashrc or ~/.zshrc)
echo 'export GITHUB_TOKEN="ghp_your_token_here"' >> ~/.bashrc
echo 'export GOOGLE_API_KEY="AIza_your_key_here"' >> ~/.bashrc
source ~/.bashrc
```

**Windows (PowerShell)**:
```powershell
$env:GITHUB_TOKEN="ghp_your_token_here"
$env:GOOGLE_API_KEY="AIza_your_key_here"

# Make permanent
[System.Environment]::SetEnvironmentVariable('GITHUB_TOKEN', 'ghp_your_token_here', 'User')
[System.Environment]::SetEnvironmentVariable('GOOGLE_API_KEY', 'AIza_your_key_here', 'User')
```

---

## Step 5: Run Examples (5 minutes)

Navigate to the direct_api directory:
```bash
cd /path/to/agents-with-adk/python_codebase_reviewer/direct_api
```

### Example 1: Simple Review

Review a public PR:
```bash
python example_simple_review.py facebook/react 12345
```

**Expected output**:
```
============================================================
Reviewing PR #12345 in facebook/react
============================================================

📋 Fetching PR files...
   Found 3 file(s) changed

📝 Found 2 Python file(s):
   - src/main.py (+10 -5)
   - lib/utils.py (+3 -1)

📄 Reviewing: src/main.py
   🤖 Running AI review...
   ✅ Review complete

📄 Reviewing: lib/utils.py
   🤖 Running AI review...
   ✅ Review complete

📝 Formatting results...

Review complete! Here's the result:
[Review output...]
```

### Example 2: Custom Workflow

Review with multi-stage analysis:
```bash
python example_custom_workflow.py facebook/react 12345
```

This runs:
- Stage 1: Security review (blocks on critical issues)
- Stage 2: Code quality review
- Stage 3: Performance review

### Example 3: Post to GitHub

Review and post comment:
```bash
python example_simple_review.py facebook/react 12345 --post
```

⚠️ This will post a comment on the actual PR!

---

## Step 6: Build Your Own (10+ minutes)

### Basic Usage

Create a Python script:

```python
#!/usr/bin/env python3
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from python_codebase_reviewer import root_agent
from python_codebase_reviewer.tools.github_tools import (
    fetch_pr_files,
    fetch_file_content
)

# Fetch PR files
repo = "owner/repo"
pr_number = 123

files = fetch_pr_files(repo, pr_number)

# Review Python files
for file in files:
    if file['filename'].endswith('.py'):
        # Get file content
        code = fetch_file_content(repo, file['filename'])

        # Run review
        review = root_agent.run(f"""
Review this Python file:

File: {file['filename']}

```python
{code}
```

Focus on security, quality, and performance.
""")

        print(f"\n{'='*60}")
        print(f"Review of {file['filename']}")
        print('='*60)
        print(review)
```

Save as `my_review.py` and run:
```bash
python my_review.py
```

### Use Specialized Reviewers

```python
from python_codebase_reviewer.sub_agents import (
    security_reviewer,
    code_quality_reviewer
)

# Security review only
security = security_reviewer.run(f"Check security: {code}")

# Code quality only
quality = code_quality_reviewer.run(f"Review quality: {code}")
```

### Post Results

```python
from python_codebase_reviewer.tools.github_tools import post_pr_review

# Post review as comment
post_pr_review(
    repo="owner/repo",
    pr_number=123,
    body="# Review Results\n\n✅ No issues found!",
    event='COMMENT'  # or 'APPROVE' or 'REQUEST_CHANGES'
)
```

---

## Common Patterns

### Pattern 1: Review Single File

```python
from python_codebase_reviewer import root_agent

code = Path('my_file.py').read_text()
review = root_agent.run(f"Review this code:\n\n```python\n{code}\n```")
print(review)
```

### Pattern 2: Review Changed Files in Git

```python
import subprocess

# Get changed files
result = subprocess.run(
    ['git', 'diff', '--name-only', 'main...HEAD'],
    capture_output=True,
    text=True
)

changed_files = [
    f for f in result.stdout.strip().split('\n')
    if f.endswith('.py')
]

# Review each
for filename in changed_files:
    code = Path(filename).read_text()
    review = root_agent.run(f"Review {filename}:\n\n{code}")
    print(f"\n{filename}:\n{review}")
```

### Pattern 3: Filter by Severity

```python
def extract_critical_issues(review_text):
    """Extract only critical issues from review."""
    lines = review_text.split('\n')
    critical_lines = []

    for i, line in enumerate(lines):
        if 'CRITICAL' in line.upper():
            # Include context (5 lines before and after)
            start = max(0, i - 5)
            end = min(len(lines), i + 6)
            critical_lines.extend(lines[start:end])
            critical_lines.append('---')

    return '\n'.join(critical_lines)

review = root_agent.run(f"Review: {code}")
critical_only = extract_critical_issues(review)

if critical_only:
    print("🔴 Critical issues found:")
    print(critical_only)
```

---

## Troubleshooting

### "GitHubAPIError: 401 Unauthorized"

**Cause**: Invalid or missing GitHub token

**Fix**:
```bash
# Check if token is set
echo $GITHUB_TOKEN

# Regenerate token at: https://github.com/settings/tokens
export GITHUB_TOKEN="ghp_new_token"
```

### "GitHubAPIError: 404 Not Found"

**Cause**: Repository or PR doesn't exist, or no access

**Fix**:
- Verify repository name: `owner/repo` (case-sensitive)
- Verify PR number
- Check if repository is private (token needs `repo` scope)

### "GOOGLE_API_KEY environment variable not set"

**Fix**:
```bash
export GOOGLE_API_KEY="your_key"
```

### "ImportError: No module named 'google_adk'"

**Fix**:
```bash
pip install google-adk
```

### Rate Limits

**GitHub API**:
- Authenticated: 5,000 requests/hour
- Unauthenticated: 60 requests/hour

**Fix**: Always use `GITHUB_TOKEN`

**Google AI API**:
- Check quota: https://aistudio.google.com/app/apikey
- During preview: Usually generous limits

---

## Next Steps

### 1. Explore All Examples

```bash
# Simple review
python example_simple_review.py owner/repo 123

# Custom workflow
python example_custom_workflow.py owner/repo 123

# Autonomous agent
python example_agent_with_github_tools.py
```

### 2. Read the Code

Study the examples to understand:
- How to use GitHub API tools
- How to structure review workflows
- How to format and post results

### 3. Build Your Integration

Use the patterns from README.md:
- Webhook handler
- Scheduled reviews
- Pre-merge gates
- Custom CLI
- Database integration

### 4. Deploy

Deploy your custom integration:
- As a web service (Flask, FastAPI)
- As a serverless function (AWS Lambda, Google Cloud Functions)
- As a scheduled job (cron, Kubernetes CronJob)
- As a GitHub Action (custom action)

---

## Verification Checklist

- [ ] Dependencies installed (`pip list | grep google-adk`)
- [ ] GITHUB_TOKEN set (`echo $GITHUB_TOKEN` shows token)
- [ ] GOOGLE_API_KEY set (`echo $GOOGLE_API_KEY` shows key)
- [ ] Can run `example_simple_review.py` successfully
- [ ] Understand basic usage pattern
- [ ] Ready to build custom integration

---

## Resources

- **GitHub API Docs**: https://docs.github.com/en/rest
- **Google AI API**: https://ai.google.dev/
- **ADK Documentation**: https://github.com/google/agent-development-kit
- **Examples**: All `.py` files in this directory
- **README**: Detailed patterns and advanced usage

---

**Setup complete!** 🎉

You can now use the GitHub API tools and Python Codebase Reviewer directly in your applications.

**Quick test**:
```bash
python example_simple_review.py facebook/react 30000
```
