# GitHub Actions Integration - Python Codebase Reviewer

Automated code review for Python pull requests using GitHub Actions CI/CD.

## Overview

This integration automatically reviews Python code in pull requests using AI-powered analysis. When a PR is opened or updated, the workflow:

1. Detects changed Python files
2. Runs comprehensive review (security, architecture, quality, performance)
3. Posts results as a PR comment
4. Optionally blocks merge if critical issues found

**Deployment**: Runs in GitHub Actions (free for public repos, included minutes for private repos)

**Best for**:
- Teams using GitHub for version control
- CI/CD-based workflows
- Automatic review on every PR
- Projects with existing GitHub Actions setup

---

## Quick Start

### 1. Add Workflow to Your Repository

Copy the workflow file to your repository:

```bash
mkdir -p .github/workflows
cp python_codebase_reviewer/github_actions/code-review.yml .github/workflows/
```

### 2. Add Google API Key Secret

1. Get API key: https://aistudio.google.com/app/apikey
2. Go to your repository → Settings → Secrets and variables → Actions
3. Click "New repository secret"
4. Name: `GOOGLE_API_KEY`
5. Value: Your API key
6. Click "Add secret"

### 3. Enable GitHub Actions

1. Go to repository → Settings → Actions → General
2. Under "Workflow permissions":
   - Select "Read and write permissions"
   - Check "Allow GitHub Actions to create and approve pull requests"
3. Save

### 4. Test It!

Create a test PR with a Python file:

```python
# test_security.py
def login(username):
    query = f"SELECT * FROM users WHERE username='{username}'"
    return db.execute(query)
```

Wait ~2 minutes, then check the PR comments for the automated review!

---

## Features

### 🔍 Comprehensive Analysis

Every Python file is reviewed for:
- **Security**: SQL injection, XSS, hardcoded secrets, unsafe deserialization
- **Architecture**: SOLID principles, design patterns, code smells
- **Code Quality**: PEP 8/20/257/484, Pythonic idioms, maintainability
- **Performance**: Algorithm complexity, N+1 queries, memory leaks
- **Best Practices**: Python 3.8-3.12 features, framework patterns

### 🚦 Severity Levels

Findings are categorized by impact:
- 🔴 **CRITICAL**: Security vulnerabilities, data loss risks
- 🟠 **HIGH**: Major bugs, serious design flaws
- 🟡 **MEDIUM**: Code quality issues, minor bugs
- 🔵 **LOW**: Style issues, minor improvements

### ✅ Quality Gates

Optional workflow failure on critical issues:
- Blocks PR merge if critical security issues found
- Configurable thresholds
- Override capability for false positives

### 📊 Rich Reporting

Review comments include:
- Summary dashboard with issue counts
- Detailed findings per file
- Suggested fixes with code examples
- Collapsible sections for long reviews

---

## Configuration

### Basic Configuration

The workflow runs automatically on:
- Pull requests opened/updated
- Only when Python files (`.py`) change
- Excludes test files by default

### Advanced Configuration

Edit `.github/workflows/code-review.yml`:

#### 1. Change Trigger Conditions

Review all file types, not just Python:
```yaml
on:
  pull_request:
    types: [opened, synchronize, reopened]
    # Remove paths filter to review all PRs
```

Review specific branches only:
```yaml
on:
  pull_request:
    branches:
      - main
      - develop
    types: [opened, synchronize, reopened]
```

#### 2. Include/Exclude Files

Customize which files to review:
```yaml
- name: Get changed Python files
  id: changed-files
  uses: tj-actions/changed-files@v40
  with:
    files: |
      **.py
    files_ignore: |
      **/test_*.py
      **/*_test.py
      **/tests/**
      **/migrations/**  # Ignore Django migrations
      **/venv/**
      **/__pycache__/**
```

#### 3. Disable Automatic Failure

Remove the critical issue check step:
```yaml
# Comment out or remove this step:
# - name: Check for critical issues
#   if: steps.changed-files.outputs.any_changed == 'true'
#   run: |
#     if grep -q "CRITICAL" review_results.md; then
#       exit 1
#     fi
```

#### 4. Custom Review Focus

Edit `review_pr.py` line 88 to customize the review prompt:
```python
review_request = f"""
Review this Python file for our company standards:

**Repository**: {repo}
**File**: `{file_path}`

Focus on:
- Django 4.2 best practices
- Our security guidelines: [link]
- Company style guide: PEP 8 + Black
- AWS Lambda optimization (we use serverless)

{code}
"""
```

#### 5. Schedule Reviews

Add a scheduled workflow to review all code periodically:
```yaml
on:
  schedule:
    - cron: '0 0 * * 0'  # Every Sunday at midnight
  workflow_dispatch:  # Manual trigger
```

---

## Usage Examples

### Manual Trigger

Review a specific PR manually:

1. Go to: Actions → Python Code Review → Run workflow
2. Enter PR number
3. Click "Run workflow"

### Review Multiple PRs

Create a batch review script:

```bash
#!/bin/bash
# review_all_open_prs.sh

for pr in $(gh pr list --json number --jq '.[].number'); do
  gh workflow run code-review.yml -f pr_number=$pr
done
```

### Integration with Other Workflows

Trigger after tests pass:

```yaml
name: CI Pipeline
on: [pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: pytest

  code-review:
    needs: test  # Only run after tests pass
    uses: ./.github/workflows/code-review.yml
    secrets: inherit
```

---

## Customization

### Modify Review Script

The review script is at `python_codebase_reviewer/github_actions/review_pr.py`.

**Add custom checks:**
```python
def custom_security_check(code: str) -> List[str]:
    """Check for company-specific security issues."""
    issues = []

    # Example: Ban specific imports
    if 'import pickle' in code:
        issues.append("🔴 CRITICAL: pickle imports are banned (use JSON instead)")

    # Example: Require specific patterns
    if 'def login(' in code and 'audit_log' not in code:
        issues.append("🟠 HIGH: Login functions must include audit logging")

    return issues
```

**Custom output format:**
```python
def format_review_markdown(results: List[Dict], repo: str, pr_number: str) -> str:
    """Add custom branding to review output."""
    output = []
    output.append("# 🏢 Company Code Review\n")
    output.append(f"*Powered by {os.getenv('COMPANY_NAME', 'AI')} Engineering*\n\n")
    # ... rest of formatting
    return ''.join(output)
```

---

## Troubleshooting

### Issue: Workflow not triggering

**Check**:
1. Workflow file is in `.github/workflows/` directory
2. File has `.yml` extension (not `.yaml`)
3. GitHub Actions is enabled (Settings → Actions → General)

**Fix**:
```bash
# Verify workflow file location
ls -la .github/workflows/code-review.yml

# Check workflow syntax
gh workflow view code-review.yml
```

### Issue: Permission denied posting comments

**Error**: `Resource not accessible by integration`

**Fix**:
1. Go to Settings → Actions → General
2. Under "Workflow permissions", select "Read and write permissions"
3. Save and re-run workflow

### Issue: GOOGLE_API_KEY not found

**Error**: `Error: GOOGLE_API_KEY environment variable not set`

**Fix**:
1. Verify secret exists: Settings → Secrets and variables → Actions
2. Secret name must be exactly `GOOGLE_API_KEY` (case-sensitive)
3. Repository secrets are NOT available to forks (security feature)

### Issue: Review takes too long / times out

**Cause**: Large PRs with many files can exceed 5-minute limit

**Fix 1**: Review fewer files at once
```yaml
- name: Get changed Python files
  uses: tj-actions/changed-files@v40
  with:
    files: |
      **.py
    max_files: 10  # Limit to 10 files per review
```

**Fix 2**: Increase timeout
```yaml
jobs:
  review:
    runs-on: ubuntu-latest
    timeout-minutes: 15  # Increase from default 5 minutes
```

**Fix 3**: Run reviews in parallel
```yaml
- name: Review files in parallel
  run: |
    echo "${{ steps.changed-files.outputs.all_changed_files }}" | \
      xargs -n 1 -P 4 python review_pr.py --file
```

### Issue: Too many API calls

**Cause**: GitHub API rate limits (5,000 requests/hour authenticated)

**Fix**: Reviews use the automatically provided `GITHUB_TOKEN`, which has higher limits

Check rate limit status:
```bash
curl -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/rate_limit
```

### Issue: False positives in review

**Fix 1**: Improve review prompt specificity (edit `review_pr.py` line 88)

**Fix 2**: Add ignore patterns
```python
# In review_pr.py, add skip conditions
if 'TODO: AI ignore this' in code:
    print(f"Skipping {file_path}: Marked for ignore")
    continue
```

**Fix 3**: Post-process results
```python
def filter_false_positives(review: str) -> str:
    """Remove known false positives."""
    # Example: Remove specific patterns
    lines = review.split('\n')
    filtered = [
        line for line in lines
        if not ('deprecated in Python 3.13' in line and 'but we use 3.11' in line)
    ]
    return '\n'.join(filtered)
```

---

## Performance & Costs

### Execution Time

- **Small PR** (1-3 files): ~30-60 seconds
- **Medium PR** (4-10 files): ~2-4 minutes
- **Large PR** (10+ files): ~5-10 minutes

### GitHub Actions Minutes

**Free tier**:
- Public repos: Unlimited
- Private repos: 2,000 minutes/month

**Usage per review**:
- ~2-5 minutes per review
- ~400-1,000 reviews/month on free tier

**Optimization**: Only review Python files (already configured)

### Google AI API Costs

**Gemini models** (as of Jan 2025):
- gemini-2.0-flash-exp: FREE during preview
- gemini-2.0-pro-exp: FREE during preview
- After preview: ~$0.01-0.05 per review (estimate)

**Monitoring usage**: https://aistudio.google.com/app/apikey

---

## Security

### Secrets Management

**Good** ✅:
- API keys stored in GitHub Secrets
- Secrets not exposed in logs
- Secrets not accessible to forks

**Bad** ❌:
- Hardcoding API keys in workflow
- Printing secrets in logs
- Committing `.env` files

### Private Repository Code

**Q**: Does my code get sent to Google?

**A**: Yes, code is sent to Google AI API for analysis. This is similar to using GitHub Copilot.

**Mitigation**:
- Review Google AI Terms of Service
- Use only on approved repositories
- Avoid reviewing files with secrets
- Consider self-hosted alternatives (see Option 4)

### Workflow Security

The workflow runs with limited permissions:
```yaml
permissions:
  contents: read        # Read code only
  pull-requests: write  # Post comments only
```

**Not granted**:
- Cannot push code
- Cannot modify secrets
- Cannot access other repositories
- Cannot change repository settings

---

## Comparison with Other Options

| Feature | GitHub Actions (Option 1) | GitHub App (Option 2) | GitHub CLI (Option 3) | Direct API (Option 4) |
|---------|---------------------------|------------------------|------------------------|------------------------|
| **Deployment** | Add workflow file | Cloud Run service | Local scripts | Custom integration |
| **Automation** | ✅ Fully automatic | ✅ Fully automatic | ❌ Manual | ⚙️ Custom |
| **Cost** | Free tier available | ~$5-20/month | Free | Varies |
| **Setup time** | 5 minutes | 30 minutes | 10 minutes | Custom |
| **Scalability** | Medium (2K mins/mo free) | High (auto-scaling) | Low (manual) | Custom |
| **Best for** | Teams with GitHub Actions | Organizations | Individual devs | Custom workflows |

**Choose GitHub Actions if**:
- ✅ You already use GitHub Actions
- ✅ You want automatic PR reviews
- ✅ You have public repos or GitHub Actions minutes available
- ✅ You want minimal setup and maintenance

**Choose GitHub App if**:
- ✅ You need organization-wide deployment
- ✅ You want highest scalability
- ✅ You have budget for Cloud Run hosting
- ✅ You want centralized management

---

## Next Steps

### 1. Customize Review Focus

Edit `review_pr.py` to focus on your tech stack:
- Add framework-specific checks (Django, Flask, FastAPI)
- Include company coding standards
- Add custom security rules

### 2. Add Review Templates

Create `.github/PULL_REQUEST_TEMPLATE.md`:
```markdown
## Changes
<!-- Describe your changes -->

## Review Focus
<!-- Tell the AI what to focus on -->
- [ ] Security review
- [ ] Performance review
- [ ] Architecture review

## AI Review Notes
<!-- The AI will add findings here -->
```

### 3. Integrate with Other Tools

Combine with:
- **pytest**: Run tests before review
- **black**: Auto-format before review
- **mypy**: Type checking before review
- **bandit**: Security scanning alongside review

Example combined workflow:
```yaml
jobs:
  quality-gate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Format with Black
        run: black --check .

      - name: Type check with mypy
        run: mypy .

      - name: Security scan with bandit
        run: bandit -r .

      - name: AI Code Review
        run: python review_pr.py ...
```

### 4. Monitor and Improve

Track review effectiveness:
- Count issues found vs. resolved
- Measure reduction in bugs reaching production
- Collect team feedback
- Tune prompts based on false positives

---

## Support

- **Issues**: [Report bugs](https://github.com/your-org/agents-with-adk/issues)
- **Documentation**: See `SETUP.md` for detailed setup guide
- **Other integration options**: See parent directory README

---

## License

Same license as the parent project (agents-with-adk).

---

**Ready to get started?** Follow the Quick Start above or see `SETUP.md` for detailed instructions.
