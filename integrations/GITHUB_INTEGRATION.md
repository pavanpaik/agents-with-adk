# GitHub Integration Guide

Comprehensive guide for integrating the Python Codebase Reviewer with GitHub repositories and pull requests.

## Integration Options Overview

| Approach | Best For | Complexity | Access | Cost |
|----------|----------|------------|--------|------|
| **GitHub Actions** | CI/CD automation | Low | Automatic | Free tier available |
| **GitHub App** | Organization-wide deployment | Medium | OAuth/App auth | Free to build |
| **GitHub CLI (gh)** | Local/manual reviews | Low | Personal token | Free |
| **API + Webhooks** | Custom deployment | High | Fine-grained tokens | Free API |

---

## Option 1: GitHub Actions (⭐ RECOMMENDED for CI/CD)

**Best for**: Automated PR reviews in CI/CD pipeline

### Pros
✅ Built-in GitHub access (no auth setup needed)
✅ Triggered automatically on PR events
✅ Free for public repos, generous limits for private
✅ Easy to install (just add workflow file)
✅ Native integration with GitHub UI
✅ Can post review comments directly on PR

### Cons
❌ Runs in GitHub's infrastructure (not your servers)
❌ Limited to GitHub-hosted or self-hosted runners
❌ Timeout limits (6 hours max per job)

### Implementation

**1. Create GitHub Action Workflow**

```yaml
# .github/workflows/code-review.yml
name: Python Code Review

on:
  pull_request:
    types: [opened, synchronize, reopened]
    paths:
      - '**.py'  # Only run on Python file changes

jobs:
  review:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      pull-requests: write  # Needed to comment on PRs

    steps:
      - name: Checkout code
        uses: actions/checkout@v4
        with:
          fetch-depth: 0  # Full history for context

      - name: Get changed Python files
        id: changed-files
        uses: tj-actions/changed-files@v40
        with:
          files: |
            **.py

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install ADK and dependencies
        run: |
          pip install google-adk

      - name: Run Python Codebase Reviewer
        env:
          GOOGLE_API_KEY: ${{ secrets.GOOGLE_API_KEY }}
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          PR_NUMBER: ${{ github.event.pull_request.number }}
        run: |
          python .github/scripts/review_pr.py \
            --files "${{ steps.changed-files.outputs.all_changed_files }}" \
            --pr-number "$PR_NUMBER"

      - name: Post review comment
        if: always()
        uses: actions/github-script@v7
        with:
          script: |
            const fs = require('fs');
            const review = fs.readFileSync('review_results.md', 'utf8');

            github.rest.issues.createComment({
              owner: context.repo.owner,
              repo: context.repo.repo,
              issue_number: context.issue.number,
              body: review
            });
```

**2. Review Script (`review_pr.py`)**

```python
#!/usr/bin/env python3
"""
GitHub Actions script to review PR using Python Codebase Reviewer.
"""
import os
import sys
import argparse
from pathlib import Path
from python_codebase_reviewer import root_agent

def get_file_content(file_path):
    """Read file content."""
    try:
        return Path(file_path).read_text()
    except Exception as e:
        return f"# Error reading file: {e}"

def review_files(file_paths):
    """Review changed Python files."""
    results = []

    for file_path in file_paths:
        print(f"Reviewing: {file_path}")

        code = get_file_content(file_path)

        # Run review
        review_request = f"""
        Review this Python file for all issues:

        **File**: `{file_path}`

        ```python
        {code}
        ```
        """

        response = root_agent.run(review_request)
        results.append({
            'file': file_path,
            'review': response
        })

    return results

def format_review_markdown(results):
    """Format review results as GitHub-flavored markdown."""
    output = ["# 🔍 Python Code Review Results\n"]

    # Count total findings by severity
    total_critical = 0
    total_high = 0
    total_medium = 0

    for result in results:
        # Parse findings (simplified - actual parsing would be more robust)
        review_text = result['review']
        total_critical += review_text.count('CRITICAL')
        total_high += review_text.count('HIGH')
        total_medium += review_text.count('MEDIUM')

    output.append(f"## Summary\n")
    output.append(f"- 🔴 Critical: {total_critical}\n")
    output.append(f"- 🟠 High: {total_high}\n")
    output.append(f"- 🟡 Medium: {total_medium}\n")
    output.append(f"\n---\n\n")

    # Detailed results per file
    for result in results:
        output.append(f"## 📄 `{result['file']}`\n\n")
        output.append(result['review'])
        output.append("\n\n---\n\n")

    return ''.join(output)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--files', required=True, help='Space-separated list of files')
    parser.add_argument('--pr-number', required=True, help='PR number')
    args = parser.parse_args()

    # Parse file list
    files = [f for f in args.files.split() if f.endswith('.py')]

    if not files:
        print("No Python files to review")
        sys.exit(0)

    print(f"Reviewing {len(files)} Python files...")

    # Run reviews
    results = review_files(files)

    # Format as markdown
    markdown = format_review_markdown(results)

    # Save results
    Path('review_results.md').write_text(markdown)

    print(f"✅ Review complete! Results saved to review_results.md")

if __name__ == '__main__':
    main()
```

**3. Setup Instructions**

```bash
# 1. Add GitHub Action workflow
mkdir -p .github/workflows .github/scripts
# Copy code-review.yml and review_pr.py above

# 2. Add secrets to repository
# Go to: Settings → Secrets and variables → Actions
# Add: GOOGLE_API_KEY (your Google AI API key)

# 3. Commit and push
git add .github/
git commit -m "Add Python code review GitHub Action"
git push

# 4. Open a PR and watch it work!
```

---

## Option 2: GitHub App (⭐ RECOMMENDED for Organizations)

**Best for**: Organization-wide deployment, multiple repositories

### Pros
✅ Installed once, works across all repos
✅ Fine-grained permissions
✅ App identity separate from user accounts
✅ Can receive webhooks for events
✅ Professional deployment option

### Cons
❌ More complex setup
❌ Need to host webhook receiver
❌ OAuth flow for installation

### Architecture

```
┌─────────────┐
│   GitHub    │
│             │
│  PR Created │
└──────┬──────┘
       │ Webhook
       │
       ▼
┌─────────────────┐
│  Webhook Server │
│  (Cloud Run)    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Python Codebase │
│    Reviewer     │
│                 │
│  Fetch PR diff  │
│  Run review     │
│  Post comments  │
└────────┬────────┘
         │
         ▼
┌─────────────┐
│   GitHub    │
│             │
│ Post Review │
└─────────────┘
```

### Implementation

**1. GitHub App Manifest**

```yaml
# github-app-manifest.yml
name: Python Codebase Reviewer
description: AI-powered Python code review agent
url: https://your-app-url.com
hook_attributes:
  url: https://your-webhook-url.com/webhook
  active: true

default_permissions:
  contents: read
  pull_requests: write
  issues: write

default_events:
  - pull_request
  - pull_request_review_comment

public: false  # Set to true for public apps
```

**2. Webhook Handler**

```python
# webhook_handler.py
from flask import Flask, request, jsonify
import hmac
import hashlib
import os
from python_codebase_reviewer import root_agent
import requests

app = Flask(__name__)

GITHUB_WEBHOOK_SECRET = os.getenv('GITHUB_WEBHOOK_SECRET')
GITHUB_APP_ID = os.getenv('GITHUB_APP_ID')
GITHUB_PRIVATE_KEY = os.getenv('GITHUB_PRIVATE_KEY')

def verify_signature(payload_body, signature):
    """Verify webhook signature."""
    expected = 'sha256=' + hmac.new(
        GITHUB_WEBHOOK_SECRET.encode(),
        payload_body,
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected, signature)

def get_installation_token(installation_id):
    """Get GitHub App installation access token."""
    import jwt
    import time

    # Generate JWT
    payload = {
        'iat': int(time.time()),
        'exp': int(time.time()) + 600,
        'iss': GITHUB_APP_ID
    }
    token = jwt.encode(payload, GITHUB_PRIVATE_KEY, algorithm='RS256')

    # Get installation token
    headers = {
        'Authorization': f'Bearer {token}',
        'Accept': 'application/vnd.github+json'
    }
    response = requests.post(
        f'https://api.github.com/app/installations/{installation_id}/access_tokens',
        headers=headers
    )
    return response.json()['token']

def fetch_pr_diff(repo_full_name, pr_number, token):
    """Fetch PR diff from GitHub."""
    headers = {
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github.diff'
    }
    response = requests.get(
        f'https://api.github.com/repos/{repo_full_name}/pulls/{pr_number}',
        headers=headers
    )
    return response.text

def post_review_comment(repo_full_name, pr_number, review_body, token):
    """Post review comment on PR."""
    headers = {
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github+json'
    }
    data = {
        'body': review_body,
        'event': 'COMMENT'  # or 'APPROVE' / 'REQUEST_CHANGES'
    }
    response = requests.post(
        f'https://api.github.com/repos/{repo_full_name}/pulls/{pr_number}/reviews',
        headers=headers,
        json=data
    )
    return response.json()

@app.route('/webhook', methods=['POST'])
def webhook():
    """Handle GitHub webhook events."""
    # Verify signature
    signature = request.headers.get('X-Hub-Signature-256')
    if not verify_signature(request.data, signature):
        return jsonify({'error': 'Invalid signature'}), 401

    event = request.headers.get('X-GitHub-Event')
    payload = request.json

    # Handle pull request events
    if event == 'pull_request':
        action = payload['action']

        if action in ['opened', 'synchronize', 'reopened']:
            # Get installation token
            installation_id = payload['installation']['id']
            token = get_installation_token(installation_id)

            # Get PR info
            repo = payload['repository']['full_name']
            pr_number = payload['pull_request']['number']

            # Fetch PR diff
            diff = fetch_pr_diff(repo, pr_number, token)

            # Run review
            review_request = f"""
            Review this pull request:

            Repository: {repo}
            PR #{pr_number}: {payload['pull_request']['title']}

            Changes:
            ```diff
            {diff}
            ```
            """

            review_result = root_agent.run(review_request)

            # Post review comment
            post_review_comment(repo, pr_number, review_result, token)

            return jsonify({'status': 'review_posted'}), 200

    return jsonify({'status': 'ignored'}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 8080)))
```

**3. Deploy to Cloud Run**

```bash
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 webhook_handler:app
```

```bash
# Deploy
gcloud run deploy python-code-reviewer-webhook \
    --source . \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated \
    --set-env-vars GOOGLE_API_KEY=$GOOGLE_API_KEY \
    --set-secrets GITHUB_WEBHOOK_SECRET=github-webhook-secret:latest,GITHUB_PRIVATE_KEY=github-app-private-key:latest
```

---

## Option 3: GitHub CLI (gh) (⭐ RECOMMENDED for Local Use)

**Best for**: Manual reviews, local development, ad-hoc checks

### Pros
✅ Simplest setup
✅ Works locally
✅ Great for manual reviews
✅ Uses personal access token

### Cons
❌ Manual triggering
❌ Not automated
❌ Requires gh CLI installed

### Implementation

**1. Install GitHub CLI**

```bash
# macOS
brew install gh

# Linux
(type -p wget >/dev/null || (sudo apt update && sudo apt-get install wget -y)) \
&& sudo mkdir -p -m 755 /etc/apt/keyrings \
&& wget -qO- https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo tee /etc/apt/keyrings/githubcli-archive-keyring.gpg > /dev/null \
&& sudo chmod go+r /etc/apt/keyrings/githubcli-archive-keyring.gpg \
&& echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null \
&& sudo apt update \
&& sudo apt install gh -y

# Authenticate
gh auth login
```

**2. Review Script**

```python
# scripts/review_pr.py
#!/usr/bin/env python3
"""
Review a GitHub PR using the Python Codebase Reviewer.

Usage:
    python scripts/review_pr.py owner/repo 123
"""
import sys
import subprocess
import json
from pathlib import Path
from python_codebase_reviewer import root_agent

def run_gh_command(cmd):
    """Run gh CLI command and return output."""
    result = subprocess.run(
        cmd,
        shell=True,
        capture_output=True,
        text=True
    )
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
        sys.exit(1)
    return result.stdout

def get_pr_diff(repo, pr_number):
    """Get PR diff using gh CLI."""
    return run_gh_command(f'gh pr diff {pr_number} --repo {repo}')

def get_pr_files(repo, pr_number):
    """Get list of changed files."""
    output = run_gh_command(
        f'gh pr view {pr_number} --repo {repo} --json files --jq ".files[].path"'
    )
    return [f for f in output.strip().split('\n') if f.endswith('.py')]

def post_pr_comment(repo, pr_number, comment):
    """Post comment on PR."""
    # Escape quotes in comment
    comment_escaped = comment.replace('"', '\\"').replace('$', '\\$')
    run_gh_command(f'gh pr comment {pr_number} --repo {repo} --body "{comment_escaped}"')

def main():
    if len(sys.argv) != 3:
        print("Usage: python review_pr.py owner/repo pr_number")
        sys.exit(1)

    repo = sys.argv[1]
    pr_number = sys.argv[2]

    print(f"📥 Fetching PR #{pr_number} from {repo}...")

    # Get PR diff and files
    diff = get_pr_diff(repo, pr_number)
    files = get_pr_files(repo, pr_number)

    if not files:
        print("No Python files changed in this PR")
        sys.exit(0)

    print(f"📝 Reviewing {len(files)} Python files...")

    # Run review
    review_request = f"""
    Review this pull request:

    Repository: {repo}
    PR #{pr_number}

    Changed files: {', '.join(files)}

    Diff:
    ```diff
    {diff}
    ```

    Focus on Python files only.
    """

    review_result = root_agent.run(review_request)

    # Post comment
    print("💬 Posting review comment...")
    post_pr_comment(repo, pr_number, review_result)

    print("✅ Review complete!")

if __name__ == '__main__':
    main()
```

**3. Usage**

```bash
# Make script executable
chmod +x scripts/review_pr.py

# Review a PR
python scripts/review_pr.py owner/repo 123

# Or create an alias
alias review-pr='python scripts/review_pr.py'
review-pr owner/repo 123
```

---

## Option 4: Direct API + Tools for Agents

**Best for**: Giving agents direct GitHub access as tools

### Implementation

**Create GitHub tools for agents:**

```python
# python_codebase_reviewer/tools/github_tools.py
"""
GitHub integration tools for agents.
"""
import os
import requests
from typing import List, Dict, Optional

GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
GITHUB_API = 'https://api.github.com'

def github_request(method: str, endpoint: str, data: Optional[Dict] = None):
    """Make GitHub API request."""
    headers = {
        'Authorization': f'token {GITHUB_TOKEN}',
        'Accept': 'application/vnd.github+json',
        'X-GitHub-Api-Version': '2022-11-28'
    }

    url = f'{GITHUB_API}/{endpoint.lstrip("/")}'

    if method == 'GET':
        response = requests.get(url, headers=headers)
    elif method == 'POST':
        response = requests.post(url, headers=headers, json=data)
    else:
        raise ValueError(f'Unsupported method: {method}')

    response.raise_for_status()
    return response.json()

def fetch_pr_files(repo: str, pr_number: int) -> List[Dict]:
    """
    Fetch list of files changed in a PR.

    Args:
        repo: Repository in format "owner/repo"
        pr_number: PR number

    Returns:
        List of file objects with filename, status, changes, etc.
    """
    endpoint = f'/repos/{repo}/pulls/{pr_number}/files'
    return github_request('GET', endpoint)

def fetch_file_content(repo: str, path: str, ref: str = 'main') -> str:
    """
    Fetch content of a file from repository.

    Args:
        repo: Repository in format "owner/repo"
        path: File path in repository
        ref: Branch, tag, or commit SHA

    Returns:
        File content as string
    """
    endpoint = f'/repos/{repo}/contents/{path}?ref={ref}'
    response = github_request('GET', endpoint)

    import base64
    return base64.b64decode(response['content']).decode('utf-8')

def post_pr_review(
    repo: str,
    pr_number: int,
    body: str,
    event: str = 'COMMENT',
    comments: Optional[List[Dict]] = None
) -> Dict:
    """
    Post a review on a PR.

    Args:
        repo: Repository in format "owner/repo"
        pr_number: PR number
        body: Review summary
        event: 'COMMENT', 'APPROVE', or 'REQUEST_CHANGES'
        comments: List of line comments

    Returns:
        Review object
    """
    endpoint = f'/repos/{repo}/pulls/{pr_number}/reviews'
    data = {
        'body': body,
        'event': event
    }

    if comments:
        data['comments'] = comments

    return github_request('POST', endpoint, data)

def post_pr_comment(repo: str, pr_number: int, body: str) -> Dict:
    """
    Post a simple comment on a PR.

    Args:
        repo: Repository in format "owner/repo"
        pr_number: PR number
        body: Comment text

    Returns:
        Comment object
    """
    endpoint = f'/repos/{repo}/issues/{pr_number}/comments'
    data = {'body': body}
    return github_request('POST', endpoint, data)

# Wrap as ADK tools
from google.adk.tools import Tool

fetch_pr_files_tool = Tool(
    name="fetch_pr_files",
    description="Fetch list of files changed in a GitHub PR",
    function=fetch_pr_files
)

fetch_file_content_tool = Tool(
    name="fetch_file_content",
    description="Fetch content of a file from GitHub repository",
    function=fetch_file_content
)

post_pr_review_tool = Tool(
    name="post_pr_review",
    description="Post a code review on a GitHub PR",
    function=post_pr_review
)

post_pr_comment_tool = Tool(
    name="post_pr_comment",
    description="Post a comment on a GitHub PR",
    function=post_pr_comment
)
```

**Update root agent with GitHub tools:**

```python
# python_codebase_reviewer/agent.py
from .tools.github_tools import (
    fetch_pr_files_tool,
    fetch_file_content_tool,
    post_pr_review_tool,
    post_pr_comment_tool
)

root_agent = Agent(
    model=constants.ORCHESTRATOR_MODEL,
    name=constants.AGENT_NAME,
    description=constants.DESCRIPTION,
    instruction=prompt.ROOT_PROMPT,
    tools=[
        # Existing reviewer tools
        security_reviewer_tool,
        architecture_reviewer_tool,
        code_quality_reviewer_tool,
        performance_reviewer_tool,
        python_expert_tool,
        # GitHub integration tools
        fetch_pr_files_tool,
        fetch_file_content_tool,
        post_pr_review_tool,
        post_pr_comment_tool,
    ]
)
```

---

## Recommendations Summary

### For Your Use Case:

| Scenario | Recommended Approach |
|----------|---------------------|
| **CI/CD automation for teams** | ⭐ **GitHub Actions** |
| **Organization-wide deployment** | ⭐ **GitHub App** |
| **Local/manual reviews** | ⭐ **GitHub CLI (gh)** |
| **Custom integration** | **API + Tools** |

### Quick Start (Easiest):

1. **GitHub CLI approach** - 15 minutes setup:
   ```bash
   pip install gh
   gh auth login
   python scripts/review_pr.py owner/repo 123
   ```

2. **GitHub Actions** - 30 minutes setup:
   - Add workflow file
   - Add GOOGLE_API_KEY secret
   - Open a PR → automatic review!

### Production Deployment (Best):

**GitHub App** for organization-wide deployment:
- One-time setup
- Works across all repos
- Professional solution
- Scalable

---

Would you like me to implement any of these options fully?
