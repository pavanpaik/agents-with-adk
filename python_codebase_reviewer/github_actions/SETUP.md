# Complete Setup Guide - GitHub Actions Integration

Step-by-step guide to set up automated code review using GitHub Actions.

**Time required**: ~5-10 minutes
**Difficulty**: Beginner

---

## Prerequisites

- ✅ GitHub repository (public or private)
- ✅ Repository admin access (to add secrets and enable workflows)
- ✅ Google AI API key (free at https://aistudio.google.com/app/apikey)

---

## Setup Steps

### Step 1: Get Google AI API Key (2 minutes)

1. **Go to Google AI Studio**:
   - Visit: https://aistudio.google.com/app/apikey

2. **Create API key**:
   - Click "Create API key"
   - Select or create a Google Cloud project
   - Copy the API key (starts with `AIza...`)

3. **Save securely**:
   - You'll need this in Step 3
   - ⚠️ Never commit this key to your repository

---

### Step 2: Add Workflow to Repository (3 minutes)

**Option A: Copy from this repository**

If you have this repository checked out:

```bash
# Navigate to your project repository
cd /path/to/your-project

# Create workflows directory
mkdir -p .github/workflows

# Copy workflow file
cp /path/to/agents-with-adk/python_codebase_reviewer/github_actions/code-review.yml \
   .github/workflows/

# Copy review script (optional - workflow can download it)
mkdir -p scripts
cp /path/to/agents-with-adk/python_codebase_reviewer/github_actions/review_pr.py \
   scripts/
```

**Option B: Create manually**

1. In your repository, create: `.github/workflows/code-review.yml`

2. Copy content from:
   ```
   python_codebase_reviewer/github_actions/code-review.yml
   ```

3. Optionally create: `scripts/review_pr.py` (or let workflow download it)

**Option C: Use GitHub web interface**

1. Go to your repository on GitHub
2. Click "Actions" tab
3. Click "New workflow"
4. Click "set up a workflow yourself"
5. Name it: `code-review.yml`
6. Paste content from `code-review.yml`
7. Commit directly to main branch

---

### Step 3: Add API Key as Secret (2 minutes)

1. **Go to repository settings**:
   - Navigate to your repository on GitHub
   - Click "Settings" tab
   - Click "Secrets and variables" → "Actions" in left sidebar

2. **Add secret**:
   - Click "New repository secret"
   - Name: `GOOGLE_API_KEY` (exact spelling, case-sensitive)
   - Value: Paste your API key from Step 1
   - Click "Add secret"

3. **Verify**:
   - You should see `GOOGLE_API_KEY` in the secrets list
   - The value will be hidden (shows as `***`)

---

### Step 4: Enable Workflow Permissions (1 minute)

1. **Go to Actions settings**:
   - Settings → Actions → General

2. **Set workflow permissions**:
   - Scroll to "Workflow permissions"
   - Select "Read and write permissions"
   - Check "Allow GitHub Actions to create and approve pull requests"
   - Click "Save"

**Why?**: This allows the workflow to post review comments on PRs.

---

### Step 5: Test the Setup (5 minutes)

#### Test 1: Create a Test Branch

```bash
# Create a new branch
git checkout -b test-ai-review

# Create a Python file with a security issue
cat > test_security.py << 'EOF'
def login(username, password):
    """Login function with SQL injection vulnerability."""
    query = f"SELECT * FROM users WHERE username='{username}'"
    return database.execute(query)

def save_data(data):
    """Unsafe pickle deserialization."""
    import pickle
    return pickle.loads(data)

# Hardcoded secret
API_KEY = "sk_live_1234567890abcdef"
EOF

# Commit and push
git add test_security.py
git commit -m "Add test file for AI review"
git push -u origin test-ai-review
```

#### Test 2: Create Pull Request

1. **On GitHub**:
   - Go to your repository
   - Click "Pull requests" → "New pull request"
   - Base: `main`, Compare: `test-ai-review`
   - Click "Create pull request"
   - Add title: "Test AI Code Review"
   - Click "Create pull request"

2. **Monitor workflow**:
   - Click "Actions" tab
   - You should see "Python Code Review" workflow running
   - Click on it to see progress

#### Test 3: Check Results

After ~2-3 minutes:

1. **Check PR comments**:
   - Go back to your Pull Request
   - Scroll to comments section
   - You should see a detailed review comment

2. **Expected review**:
   ```markdown
   # 🔍 Python Code Review Results

   **Repository**: your-org/your-repo
   **Pull Request**: #1

   ## 📊 Summary
   - 🔴 3 Critical issues (immediate action required)

   > ⚠️ Warning: Critical security issues detected!

   ## 📁 Detailed Review by File

   ### `test_security.py`

   **Found 3 issue(s)**

   1. 🔴 CRITICAL: SQL Injection vulnerability
   2. 🔴 CRITICAL: Unsafe pickle deserialization
   3. 🔴 CRITICAL: Hardcoded secret in code
   ```

3. **Check workflow artifacts**:
   - Actions → Latest workflow run → "code-review-results" artifact
   - Download to see full review markdown

#### Test 4: Verify Workflow Failure (Optional)

Since the test file has CRITICAL issues, the workflow should fail:

1. **Check status**:
   - Go to PR → "Checks" tab
   - "Python Code Review" should show ❌ Failed

2. **Why?**: The workflow is configured to fail on critical issues (prevents merging)

3. **Disable if needed**: See README.md → Configuration → "Disable Automatic Failure"

---

### Step 6: Customize (Optional)

#### Customize Review Focus

Edit `review_pr.py` or create a custom version:

```python
review_request = f"""
Review this Python file from PR #{pr_number}:

**Repository**: {repo}
**File**: `{file_path}`

**Our Tech Stack**:
- Framework: Django 4.2
- Python: 3.11
- Database: PostgreSQL
- Deployment: AWS Lambda

**Review Focus**:
1. Security (OWASP Top 10 for Python)
2. Django best practices (ORM, views, middleware)
3. AWS Lambda optimization (cold starts, memory)
4. PEP 8 + Black formatting
5. Type hints (PEP 484)

**Company Standards**:
- All database queries must use ORM (no raw SQL)
- All secrets must use environment variables
- All functions must have type hints
- All public functions must have docstrings

```python
{code}
```

Provide actionable findings with severity and fixes.
"""
```

#### Exclude Files from Review

Edit `.github/workflows/code-review.yml`:

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
      **/migrations/**       # ← Django migrations
      **/settings.py         # ← Django settings (usually reviewed manually)
      **/manage.py           # ← Django management script
      **/venv/**
      **/__pycache__/**
```

#### Review Only Specific Branches

Edit `.github/workflows/code-review.yml`:

```yaml
on:
  pull_request:
    branches:
      - main           # Only PRs targeting main
      - develop        # and develop branches
    types: [opened, synchronize, reopened]
    paths:
      - '**.py'
```

---

## Verification Checklist

After setup, verify:

- [ ] `.github/workflows/code-review.yml` exists in repository
- [ ] `GOOGLE_API_KEY` secret is added
- [ ] Workflow permissions set to "Read and write"
- [ ] Test PR triggered the workflow
- [ ] Review comment was posted on PR
- [ ] Workflow status shows in PR "Checks" tab
- [ ] Critical issues cause workflow failure (if desired)

---

## Troubleshooting

### Issue: Workflow doesn't run

**Symptoms**: No workflow appears in Actions tab after creating PR

**Checks**:
1. Is the workflow file in `.github/workflows/` directory?
2. Does the file have `.yml` extension (not `.yaml`)?
3. Did you push the workflow file to the repository?
4. Does the PR modify Python files (`.py`)?

**Debug**:
```bash
# Check workflow file exists
ls -la .github/workflows/code-review.yml

# Validate YAML syntax
cat .github/workflows/code-review.yml | python -m yaml

# Check git status
git status
git log --oneline -1  # Should show workflow commit
```

**Fix**:
```bash
# If file is missing or not committed
git add .github/workflows/code-review.yml
git commit -m "Add AI code review workflow"
git push
```

---

### Issue: "Resource not accessible by integration"

**Symptoms**: Workflow runs but fails when posting comment

**Error in logs**:
```
Error: Resource not accessible by integration
```

**Cause**: Workflow doesn't have permission to post PR comments

**Fix**:
1. Go to: Settings → Actions → General
2. Scroll to "Workflow permissions"
3. Select "Read and write permissions"
4. Check "Allow GitHub Actions to create and approve pull requests"
5. Click "Save"
6. Re-run the failed workflow

---

### Issue: "GOOGLE_API_KEY environment variable not set"

**Symptoms**: Workflow fails with API key error

**Error in logs**:
```
❌ Error: GOOGLE_API_KEY environment variable not set
```

**Checks**:
1. Is the secret named exactly `GOOGLE_API_KEY` (case-sensitive)?
2. Is the secret added to the correct repository?
3. Are you testing from a forked repository?

**Fix**:
1. Go to: Settings → Secrets and variables → Actions
2. Check if `GOOGLE_API_KEY` exists
3. If missing, click "New repository secret" and add it
4. If it exists, delete and recreate (value might be wrong)

**Note**: Repository secrets are NOT available to forked PRs for security reasons.

---

### Issue: Workflow times out

**Symptoms**: Workflow runs for 5+ minutes and times out

**Cause**: Large PR with many files

**Fix 1**: Increase timeout
```yaml
jobs:
  review:
    runs-on: ubuntu-latest
    timeout-minutes: 15  # Increase from default
```

**Fix 2**: Limit files reviewed
```yaml
- name: Get changed Python files
  uses: tj-actions/changed-files@v40
  with:
    files: |
      **.py
    max_files: 10  # Only review first 10 files
```

**Fix 3**: Split large PRs into smaller ones (recommended)

---

### Issue: No review comment appears

**Symptoms**: Workflow completes successfully but no comment on PR

**Checks**:
1. Look at workflow logs: Actions → Latest run → "Post review results" step
2. Check if `review_results.md` was created: Check artifacts
3. Check workflow permissions (see "Resource not accessible" above)

**Debug**:
```yaml
# Add debug step before posting comment
- name: Debug review results
  run: |
    echo "Review results file:"
    ls -la review_results.md || echo "File not found"
    cat review_results.md || echo "Cannot read file"
```

**Fix**: Usually a permissions issue (see "Resource not accessible" above)

---

### Issue: Too many false positives

**Symptoms**: Review flags correct code as issues

**Fix 1**: Improve review prompt
Edit `review_pr.py` line 88 to be more specific about your context:
```python
review_request = f"""
Review this Python file. We use:
- Python 3.11 (not 3.13, so don't flag newer deprecations)
- Django 4.2 (not latest, don't suggest 5.0 features)
- Type hints are optional (don't require them everywhere)

{code}
"""
```

**Fix 2**: Add ignore markers
```python
# In your code, add special comments
# AI-REVIEW-IGNORE: This is intentional for performance
unsafe_but_intentional_code()
```

Then in `review_pr.py`:
```python
# Skip files with ignore marker
if '# AI-REVIEW-IGNORE' in code:
    continue
```

**Fix 3**: Post-process results
```python
def filter_known_false_positives(review: str) -> str:
    """Remove patterns we know are false positives."""
    # Example: Remove specific warnings
    lines = [
        line for line in review.split('\n')
        if not any(fp in line for fp in [
            'deprecated in Python 3.13',  # We use 3.11
            'use async/await',  # Not needed for our use case
        ])
    ]
    return '\n'.join(lines)
```

---

### Issue: Review quality is poor

**Symptoms**: Reviews are too generic or miss important issues

**Fix 1**: Use better model (if available)
```python
# In python_codebase_reviewer/constants.py
ORCHESTRATOR_MODEL = "gemini-2.0-pro-exp"  # Instead of flash
```

**Fix 2**: Provide more context in prompt
```python
review_request = f"""
Review this {repo} file from PR #{pr_number}.

**Project Context**:
This is a Django REST API for e-commerce. We handle:
- Payment processing (PCI compliance required)
- User authentication (GDPR compliance)
- High traffic (100k+ requests/day)

**Critical Areas**:
- Security: No SQL injection, XSS, or secret leaks
- Performance: Optimize DB queries (we have N+1 issues)
- Scale: This runs on 10 servers behind load balancer

{code}
"""
```

**Fix 3**: Add domain-specific checks
```python
def check_ecommerce_patterns(code: str) -> List[str]:
    """Check e-commerce specific patterns."""
    issues = []

    if 'stripe.api_key =' in code and 'os.environ' not in code:
        issues.append("🔴 CRITICAL: Stripe API key must use environment variable")

    if 'models.ForeignKey' in code and 'on_delete' not in code:
        issues.append("🟠 HIGH: Missing on_delete in ForeignKey (Django requirement)")

    return issues
```

---

## Advanced Usage

### Run on Schedule

Review all code weekly:

```yaml
on:
  schedule:
    - cron: '0 0 * * 0'  # Every Sunday at midnight UTC

  workflow_dispatch:
    inputs:
      files:
        description: 'Files to review (space-separated)'
        required: false
        default: '**/*.py'
```

### Review Specific Commit

```yaml
workflow_dispatch:
  inputs:
    commit_sha:
      description: 'Commit SHA to review'
      required: true

jobs:
  review:
    steps:
      - uses: actions/checkout@v4
        with:
          ref: ${{ github.event.inputs.commit_sha }}
```

### Parallel Review of Large PRs

```yaml
- name: Split files and review in parallel
  run: |
    # Split files into batches of 5
    echo "${{ steps.changed-files.outputs.all_changed_files }}" | \
      xargs -n 5 | \
      xargs -P 3 -I {} python review_pr.py --files "{}" --pr-number $PR_NUMBER --repo $REPO_NAME
```

### Integration with Branch Protection

Require review to pass before merging:

1. Settings → Branches → Add rule
2. Branch name pattern: `main`
3. Check "Require status checks to pass"
4. Search for: "review"
5. Check "Python Code Review"
6. Save

Now PRs with critical issues cannot be merged!

---

## Monitoring

### View Workflow Runs

```bash
# List recent workflow runs
gh run list --workflow=code-review.yml

# View specific run
gh run view <run-id>

# View logs
gh run view <run-id> --log
```

### Check API Usage

Google AI Studio: https://aistudio.google.com/app/apikey

Monitor:
- Requests per day
- Quota usage
- Rate limits

### Workflow Analytics

Repository → Insights → Actions:
- Success rate
- Average duration
- Failure reasons

---

## Next Steps

### 1. Customize for Your Stack

Add framework-specific checks:
- Django: Model validations, migration safety
- Flask: Blueprint structure, error handling
- FastAPI: Dependency injection, async patterns

### 2. Integrate with Other Tools

Combine with:
- `pytest` for test coverage
- `black` for code formatting
- `mypy` for type checking
- `bandit` for security scanning

### 3. Scale to Organization

Once proven, deploy to:
- All repositories (create organization-wide workflow)
- Different teams (customize prompts per team)
- Different languages (extend beyond Python)

### 4. Try Other Integration Options

- **Option 2 (GitHub App)**: For organization-wide deployment
- **Option 3 (GitHub CLI)**: For local development
- **Option 4 (Direct API)**: For custom integrations

See parent directory README for comparison.

---

## Support

- **Documentation**: `README.md` in this directory
- **Issues**: Report at https://github.com/your-org/agents-with-adk/issues
- **Integration options**: See `../README.md`

---

**Setup complete!** 🎉

Your repository now has automated AI code review on every pull request.
