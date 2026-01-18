# Direct API Integration - Python Codebase Reviewer

Use the GitHub API tools and Python Codebase Reviewer directly in your own applications.

## Overview

This integration method gives you full control by letting you use the code review components directly in your Python applications. Perfect for:
- Custom automation workflows
- Integration with existing tools/platforms
- Building custom review pipelines
- Research and experimentation
- Unique deployment scenarios

**Deployment**: Your own Python application
**Flexibility**: ✅ Complete control over all aspects
**Best for**: Custom integrations, unique workflows, maximum flexibility

---

## Quick Start

### 1. Install Dependencies

```bash
pip install google-adk requests
```

### 2. Set Environment Variables

```bash
export GITHUB_TOKEN="your_github_token"      # From https://github.com/settings/tokens
export GOOGLE_API_KEY="your_google_api_key"  # From https://aistudio.google.com/app/apikey
```

### 3. Run an Example

```bash
cd python_codebase_reviewer/direct_api

# Simple PR review
python example_simple_review.py owner/repo 123

# Custom workflow with multi-stage reviews
python example_custom_workflow.py owner/repo 123

# Autonomous agent with GitHub tools
python example_agent_with_github_tools.py
```

---

## What You Can Build

### 1. Simple PR Review

**Use case**: Basic PR review with minimal code

```python
from python_codebase_reviewer import root_agent
from python_codebase_reviewer.tools.github_tools import (
    fetch_pr_files,
    fetch_file_content,
    post_pr_review
)

# Fetch PR files
files = fetch_pr_files("owner/repo", 123)

# Review each Python file
for file in files:
    if file['filename'].endswith('.py'):
        code = fetch_file_content("owner/repo", file['filename'])
        review = root_agent.run(f"Review this code:\n\n{code}")

        # Post result
        post_pr_review("owner/repo", 123, review)
```

See: `example_simple_review.py`

### 2. Autonomous Agent with GitHub Tools

**Use case**: Create an agent that can autonomously fetch and review PRs

```python
from google_adk import Agent, AgentTool
from python_codebase_reviewer import root_agent
from python_codebase_reviewer.tools import github_tools

# Create agent with GitHub tools
agent = Agent(
    model="gemini-2.0-flash-exp",
    name="github_reviewer",
    instruction="You can fetch PRs from GitHub and review them",
    tools=[
        AgentTool(function=github_tools.fetch_pr_files),
        AgentTool(function=github_tools.fetch_file_content),
        AgentTool(agent=root_agent, name="code_reviewer")
    ]
)

# Agent can now understand natural language
response = agent.run("Review PR #123 in owner/repo")
```

See: `example_agent_with_github_tools.py`

### 3. Custom Review Workflow

**Use case**: Multi-stage reviews with custom filtering and routing

```python
class CustomWorkflow:
    def should_review_file(self, filename):
        # Custom logic: only review src/ files, skip tests
        return filename.startswith('src/') and 'test_' not in filename

    def run_multi_stage(self, code):
        # Stage 1: Security (critical)
        security = security_reviewer.run(code)
        if 'CRITICAL' in security:
            return {'block_merge': True, 'reason': security}

        # Stage 2: Code quality
        quality = code_quality_reviewer.run(code)

        # Stage 3: Performance (optional)
        performance = performance_reviewer.run(code)

        return aggregate_results(security, quality, performance)
```

See: `example_custom_workflow.py`

### 4. Integration with Other Tools

**Use case**: Combine with linters, formatters, security scanners

```python
import subprocess

def comprehensive_review(filename, code):
    """Run multiple tools and aggregate results."""
    results = {}

    # 1. AI Code Review
    results['ai_review'] = root_agent.run(f"Review: {code}")

    # 2. Run Black formatter
    black_result = subprocess.run(['black', '--check', filename], capture_output=True)
    results['formatting'] = 'PASS' if black_result.returncode == 0 else 'FAIL'

    # 3. Run mypy type checker
    mypy_result = subprocess.run(['mypy', filename], capture_output=True)
    results['type_check'] = mypy_result.stdout.decode()

    # 4. Run bandit security scanner
    bandit_result = subprocess.run(['bandit', filename], capture_output=True)
    results['security_scan'] = bandit_result.stdout.decode()

    return results
```

### 5. Custom Output Formats

**Use case**: Export to JSON, database, Slack, email, etc.

```python
def review_and_export(repo, pr_number):
    """Review PR and export to multiple formats."""
    results = review_pr(repo, pr_number)

    # Export to JSON
    with open('review.json', 'w') as f:
        json.dump(results, f, indent=2)

    # Save to database
    db.reviews.insert({
        'repo': repo,
        'pr': pr_number,
        'results': results,
        'timestamp': datetime.now()
    })

    # Send to Slack
    slack_client.post_message(
        channel='#code-reviews',
        text=format_slack_message(results)
    )

    # Email to team
    send_email(
        to='team@company.com',
        subject=f'Code Review: PR #{pr_number}',
        body=format_email(results)
    )
```

---

## Available Components

### GitHub Tools

Located in: `python_codebase_reviewer/tools/github_tools.py`

#### `fetch_pr_files(repo: str, pr_number: int) -> List[Dict]`

Fetch list of files changed in a PR.

```python
files = fetch_pr_files("facebook/react", 12345)
# Returns: [
#     {
#         'filename': 'src/main.py',
#         'status': 'modified',
#         'additions': 10,
#         'deletions': 5,
#         'changes': 15,
#         'sha': 'abc123...'
#     },
#     ...
# ]
```

#### `fetch_file_content(repo: str, path: str, ref: str = 'main') -> str`

Fetch content of a file from repository.

```python
code = fetch_file_content("facebook/react", "src/main.py", ref="feature-branch")
# Returns: "import os\n\ndef main():\n    ..."
```

#### `fetch_pr_info(repo: str, pr_number: int) -> Dict`

Fetch detailed PR information.

```python
pr = fetch_pr_info("facebook/react", 12345)
# Returns: {
#     'number': 12345,
#     'title': 'Fix security issue',
#     'body': 'Description...',
#     'state': 'open',
#     'user': {'login': 'author'},
#     'head': {'ref': 'feature-branch'},
#     ...
# }
```

#### `fetch_issue_comments(repo: str, issue_number: int) -> List[Dict]`

Fetch comments on an issue or PR.

```python
comments = fetch_issue_comments("facebook/react", 12345)
# Returns: [{'user': {'login': 'reviewer'}, 'body': 'LGTM', ...}, ...]
```

#### `post_pr_review(repo: str, pr_number: int, body: str, event: str = 'COMMENT') -> Dict`

Post a review comment on a PR.

```python
post_pr_review(
    "facebook/react",
    12345,
    "## Code Review\n\n- ✅ Security: No issues\n- ⚠️  Performance: Consider caching",
    event='COMMENT'  # or 'APPROVE' or 'REQUEST_CHANGES'
)
```

#### `post_pr_line_comment(repo: str, pr_number: int, body: str, commit_id: str, path: str, line: int) -> Dict`

Post a line-specific comment.

```python
post_pr_line_comment(
    "facebook/react",
    12345,
    "This could cause SQL injection. Use parameterized queries.",
    commit_id="abc123",
    path="src/db.py",
    line=42
)
```

### Review Agents

#### Root Agent (Full Review)

```python
from python_codebase_reviewer import root_agent

review = root_agent.run("Review this code: ...")
# Coordinates all specialized reviewers
```

#### Specialized Reviewers

```python
from python_codebase_reviewer.sub_agents import (
    security_reviewer,
    architecture_reviewer,
    code_quality_reviewer,
    performance_reviewer,
    python_expert
)

# Security only
security = security_reviewer.run("Check for vulnerabilities: ...")

# Code quality only
quality = code_quality_reviewer.run("Review code quality: ...")

# Performance only
perf = performance_reviewer.run("Analyze performance: ...")
```

---

## Integration Patterns

### Pattern 1: Webhook Handler

Build a custom webhook receiver:

```python
from flask import Flask, request
import hmac
import hashlib

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def handle_webhook():
    # Verify signature
    signature = request.headers.get('X-Hub-Signature-256')
    if not verify_signature(request.data, signature):
        return 'Invalid signature', 403

    # Parse event
    event = request.headers.get('X-GitHub-Event')
    payload = request.json

    if event == 'pull_request':
        if payload['action'] in ['opened', 'synchronize']:
            # Trigger review
            review_pr_async(
                payload['repository']['full_name'],
                payload['pull_request']['number']
            )

    return 'OK', 200

def verify_signature(payload_body, signature_header):
    secret = os.getenv('WEBHOOK_SECRET')
    hash_object = hmac.new(secret.encode(), payload_body, hashlib.sha256)
    expected = 'sha256=' + hash_object.hexdigest()
    return hmac.compare_digest(expected, signature_header)
```

### Pattern 2: Scheduled Reviews

Review all open PRs periodically:

```python
import schedule
import time

def review_all_open_prs():
    """Review all open PRs in monitored repositories."""
    repos = ['owner/repo1', 'owner/repo2']

    for repo in repos:
        # Fetch open PRs
        prs = fetch_open_prs(repo)

        for pr in prs:
            # Check if already reviewed recently
            if not needs_review(repo, pr['number']):
                continue

            # Run review
            review_pr(repo, pr['number'])

# Schedule daily at 9 AM
schedule.every().day.at("09:00").do(review_all_open_prs)

while True:
    schedule.run_pending()
    time.sleep(60)
```

### Pattern 3: Pre-Merge Gate

Integrate with CI/CD to block merges:

```python
def pr_merge_gate(repo: str, pr_number: int) -> bool:
    """
    Return True if PR is safe to merge.
    Used in CI/CD to block merges with critical issues.
    """
    files = fetch_pr_files(repo, pr_number)

    for file in files:
        if not file['filename'].endswith('.py'):
            continue

        code = fetch_file_content(repo, file['filename'])

        # Quick security check only (fast)
        review = security_reviewer.run(f"Find critical issues: {code}")

        # Block if critical issues found
        if 'CRITICAL' in review.upper():
            post_pr_review(
                repo, pr_number,
                f"🔴 **MERGE BLOCKED**\n\nCritical security issues in `{file['filename']}`:\n\n{review}",
                event='REQUEST_CHANGES'
            )
            return False

    return True
```

### Pattern 4: Interactive CLI

Build an interactive review tool:

```python
import click

@click.group()
def cli():
    """Python Codebase Reviewer CLI"""
    pass

@cli.command()
@click.argument('repo')
@click.argument('pr_number', type=int)
@click.option('--focus', multiple=True, help='Focus areas: security, performance, quality')
@click.option('--post/--no-post', default=False)
def review(repo, pr_number, focus, post):
    """Review a pull request."""
    click.echo(f"Reviewing PR #{pr_number} in {repo}")

    if focus:
        click.echo(f"Focus: {', '.join(focus)}")

    # Run review
    results = run_custom_review(repo, pr_number, focus)

    # Display results
    click.echo(results)

    if post:
        if click.confirm('Post review to GitHub?'):
            post_pr_review(repo, pr_number, results)
            click.echo('✅ Posted!')

if __name__ == '__main__':
    cli()
```

### Pattern 5: Database Integration

Store reviews for analytics:

```python
from sqlalchemy import create_engine, Column, Integer, String, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

Base = declarative_base()

class CodeReview(Base):
    __tablename__ = 'code_reviews'

    id = Column(Integer, primary_key=True)
    repo = Column(String)
    pr_number = Column(Integer)
    timestamp = Column(DateTime, default=datetime.now)
    files_reviewed = Column(Integer)
    critical_issues = Column(Integer)
    high_issues = Column(Integer)
    medium_issues = Column(Integer)
    low_issues = Column(Integer)
    results = Column(JSON)

def review_and_store(repo, pr_number):
    """Review PR and store in database."""
    results = review_pr(repo, pr_number)

    # Count issues by severity
    counts = count_issues_by_severity(results)

    # Store in database
    review = CodeReview(
        repo=repo,
        pr_number=pr_number,
        files_reviewed=len(results),
        critical_issues=counts['critical'],
        high_issues=counts['high'],
        medium_issues=counts['medium'],
        low_issues=counts['low'],
        results=results
    )

    session.add(review)
    session.commit()

def get_analytics():
    """Get review analytics."""
    return session.query(
        CodeReview.repo,
        func.count(CodeReview.id).label('total_reviews'),
        func.sum(CodeReview.critical_issues).label('total_critical'),
        func.avg(CodeReview.files_reviewed).label('avg_files')
    ).group_by(CodeReview.repo).all()
```

---

## Advanced Usage

### Parallel Reviews

Review multiple files concurrently:

```python
from concurrent.futures import ThreadPoolExecutor, as_completed

def review_file(filename, code):
    """Review a single file."""
    return root_agent.run(f"Review {filename}: {code}")

def review_pr_parallel(repo, pr_number, max_workers=4):
    """Review PR with parallel processing."""
    files = fetch_pr_files(repo, pr_number)
    results = []

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all tasks
        future_to_file = {
            executor.submit(
                review_file,
                f['filename'],
                fetch_file_content(repo, f['filename'])
            ): f
            for f in files if f['filename'].endswith('.py')
        }

        # Collect results as they complete
        for future in as_completed(future_to_file):
            file = future_to_file[future]
            try:
                review = future.result()
                results.append({'file': file['filename'], 'review': review})
            except Exception as e:
                results.append({'file': file['filename'], 'error': str(e)})

    return results
```

### Caching

Cache reviews to avoid re-reviewing unchanged code:

```python
import hashlib
import pickle
from pathlib import Path

CACHE_DIR = Path('.review_cache')
CACHE_DIR.mkdir(exist_ok=True)

def get_cache_key(repo, pr_number, filename, content_hash):
    """Generate cache key."""
    return f"{repo.replace('/', '_')}_{pr_number}_{filename}_{content_hash}"

def get_cached_review(cache_key):
    """Get review from cache if exists."""
    cache_file = CACHE_DIR / f"{cache_key}.pkl"
    if cache_file.exists():
        return pickle.loads(cache_file.read_bytes())
    return None

def cache_review(cache_key, review):
    """Save review to cache."""
    cache_file = CACHE_DIR / f"{cache_key}.pkl"
    cache_file.write_bytes(pickle.dumps(review))

def review_with_cache(repo, pr_number):
    """Review with caching."""
    files = fetch_pr_files(repo, pr_number)
    results = []

    for file in files:
        if not file['filename'].endswith('.py'):
            continue

        content = fetch_file_content(repo, file['filename'])
        content_hash = hashlib.sha256(content.encode()).hexdigest()
        cache_key = get_cache_key(repo, pr_number, file['filename'], content_hash)

        # Check cache
        review = get_cached_review(cache_key)

        if review is None:
            # Review and cache
            review = root_agent.run(f"Review: {content}")
            cache_review(cache_key, review)
            print(f"✅ Reviewed {file['filename']}")
        else:
            print(f"📦 Using cached review for {file['filename']}")

        results.append({'file': file['filename'], 'review': review})

    return results
```

### Error Handling

Robust error handling for production:

```python
from tenacity import retry, stop_after_attempt, wait_exponential
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    reraise=True
)
def fetch_with_retry(repo, pr_number):
    """Fetch PR files with retry logic."""
    try:
        return fetch_pr_files(repo, pr_number)
    except GitHubAPIError as e:
        logger.error(f"GitHub API error: {e}")
        raise

def safe_review(repo, pr_number):
    """Review with comprehensive error handling."""
    try:
        # Fetch files with retry
        files = fetch_with_retry(repo, pr_number)

    except Exception as e:
        logger.error(f"Failed to fetch PR: {e}")
        return {'status': 'error', 'message': 'Could not fetch PR'}

    results = []

    for file in files:
        try:
            # Review file
            code = fetch_file_content(repo, file['filename'])
            review = root_agent.run(f"Review: {code}")

            results.append({
                'file': file['filename'],
                'status': 'success',
                'review': review
            })

        except Exception as e:
            logger.error(f"Failed to review {file['filename']}: {e}")
            results.append({
                'file': file['filename'],
                'status': 'error',
                'error': str(e)
            })

    return {'status': 'completed', 'results': results}
```

---

## Comparison with Other Options

| Feature | Direct API (Option 4) | GitHub Actions (Option 1) | GitHub App (Option 2) | GitHub CLI (Option 3) |
|---------|----------------------|---------------------------|------------------------|------------------------|
| **Flexibility** | ✅ Complete control | Limited | Limited | High |
| **Deployment** | Custom | Workflow file | Cloud Run | Local |
| **Automation** | ⚙️ You build it | ✅ Automatic | ✅ Automatic | ❌ Manual |
| **Setup complexity** | High | Low | Medium | Low |
| **Best for** | Custom needs | Teams | Organizations | Individuals |

**Choose Direct API if**:
- ✅ You have unique integration requirements
- ✅ You want full control over the workflow
- ✅ You're building a custom platform
- ✅ You need to integrate with other tools
- ✅ Standard options don't fit your needs

**Choose other options if**:
- ❌ You want quick setup (use Actions or CLI)
- ❌ You want organization-wide deployment (use App)
- ❌ You want automatic PR reviews (use Actions or App)

---

## Examples Summary

1. **`example_simple_review.py`**: Basic PR review with minimal code
2. **`example_agent_with_github_tools.py`**: Autonomous agent with GitHub access
3. **`example_custom_workflow.py`**: Multi-stage reviews with custom logic

---

## Next Steps

### 1. Explore Examples

Run the provided examples to understand different patterns:
```bash
python example_simple_review.py owner/repo 123
python example_custom_workflow.py owner/repo 123 --json results.json
```

### 2. Build Your Integration

Use the patterns above to build your custom solution.

### 3. Add Custom Logic

Extend with your own:
- File filtering rules
- Review stages
- Output formats
- Integration points

### 4. Deploy

Deploy your custom integration:
- As a webhook service
- As a scheduled job
- As a CLI tool
- As part of your platform

---

## Support

- **Documentation**: See `SETUP.md` for detailed setup
- **Examples**: All examples in this directory
- **GitHub Tools**: See `../tools/github_tools.py`
- **Agents**: See `../sub_agents/` for specialized reviewers

---

**Ready to build?** Check out the examples and start coding!
