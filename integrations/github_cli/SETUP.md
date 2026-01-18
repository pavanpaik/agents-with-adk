# Quick Setup Guide - GitHub CLI Integration

Get started reviewing PRs with GitHub CLI in 10 minutes.

---

## Step 1: Install GitHub CLI (2 minutes)

**macOS**:
```bash
brew install gh
```

**Linux (Ubuntu/Debian)**:
```bash
sudo apt install gh
```

**Linux (Fedora/CentOS/RHEL)**:
```bash
sudo dnf install gh
```

**Windows**:
```bash
winget install GitHub.cli
```

**Or download**: https://cli.github.com/

**Verify**:
```bash
gh --version
# Should show: gh version 2.x.x
```

---

## Step 2: Authenticate (2 minutes)

```bash
# Login to GitHub
gh auth login
```

Follow the prompts:
1. Choose: **GitHub.com**
2. Choose: **HTTPS**
3. Choose: **Login with a web browser**
4. Copy the code shown
5. Press Enter to open browser
6. Paste code and authorize

**Verify**:
```bash
gh auth status
# Should show: ✓ Logged in to github.com as your-username
```

---

## Step 3: Install Python Dependencies (1 minute)

```bash
pip install google-adk requests
```

---

## Step 4: Get Google AI API Key (2 minutes)

1. **Visit**: https://aistudio.google.com/app/apikey

2. **Create key**:
   - Click "Create API key"
   - Select or create a Google Cloud project
   - Copy the API key (starts with `AIza...`)

3. **Set environment variable**:

   **Linux/macOS**:
   ```bash
   export GOOGLE_API_KEY="your-api-key-here"

   # Make permanent (add to ~/.bashrc or ~/.zshrc)
   echo 'export GOOGLE_API_KEY="your-api-key-here"' >> ~/.bashrc
   source ~/.bashrc
   ```

   **Windows (PowerShell)**:
   ```powershell
   $env:GOOGLE_API_KEY="your-api-key-here"

   # Make permanent
   [System.Environment]::SetEnvironmentVariable('GOOGLE_API_KEY', 'your-api-key-here', 'User')
   ```

---

## Step 5: Test It! (3 minutes)

### Option A: Review an existing PR

```bash
# Clone this repository
cd /path/to/agents-with-adk

# Navigate to GitHub CLI scripts
cd python_codebase_reviewer/github_cli

# Review a PR (replace 123 with actual PR number)
python review_pr.py 123
```

### Option B: Create a test PR

```bash
# Navigate to your repository
cd /path/to/your-repo

# Create test file with security issue
cat > test_security.py << 'EOF'
def login(username):
    query = f"SELECT * FROM users WHERE username='{username}'"
    return db.execute(query)
EOF

# Commit and push
git checkout -b test-ai-review
git add test_security.py
git commit -m "Add test file"
git push -u origin test-ai-review

# Create PR
gh pr create --title "Test AI Review" --body "Testing AI code review"

# Review it
cd /path/to/agents-with-adk/python_codebase_reviewer/github_cli
python review_pr.py  # Uses current branch
```

**Expected output**:
```
============================================================
Python Codebase Reviewer - GitHub CLI
============================================================

🔍 Checking prerequisites...
  ✅ gh CLI authenticated
  ✅ GOOGLE_API_KEY found
  ✅ Repository: your-org/your-repo

📋 Fetching PR information...
  PR #123: Test AI Review
  Branch: test-ai-review

📝 Found 1 Python file(s) to review:
  - test_security.py (+5 -0)

🚀 Starting code review...

📄 Reviewing: test_security.py
  🤖 Running AI review...
  ✅ Found 1 issue(s)

📝 Formatting results...
  ✅ Saved to: review_results.md

============================================================
📊 Review Summary
============================================================
Files reviewed: 1
Total issues: 1
  🔴 Critical: 1
============================================================

⚠️  Warning: Critical issues found!
```

**Check results**:
```bash
cat review_results.md
```

---

## Common Usage

### Review a PR and post comment

```bash
python review_pr.py 123 --post
```

### Review current branch PR

```bash
python review_pr.py
```

### Review specific files

```bash
python review_files.py src/main.py src/utils.py
```

### Review staged changes

```bash
git diff --cached --name-only | grep '.py$' | xargs python review_files.py
```

---

## Make It Easier

### Add to PATH

**Linux/macOS**:
```bash
# Add alias to ~/.bashrc or ~/.zshrc
echo 'alias review-pr="python /path/to/agents-with-adk/python_codebase_reviewer/github_cli/review_pr.py"' >> ~/.bashrc
echo 'alias review-files="python /path/to/agents-with-adk/python_codebase_reviewer/github_cli/review_files.py"' >> ~/.bashrc
source ~/.bashrc
```

**Now use anywhere**:
```bash
review-pr 123
review-files src/main.py
```

### Create Git Alias

```bash
git config --global alias.review-pr '!f() { python /path/to/review_pr.py "$@"; }; f'
```

**Usage**:
```bash
git review-pr 123
```

---

## Troubleshooting

### "gh: command not found"

**Fix**: Install GitHub CLI (Step 1)

### "gh: not authenticated"

**Fix**: Run `gh auth login` (Step 2)

### "GOOGLE_API_KEY environment variable not set"

**Fix**:
```bash
export GOOGLE_API_KEY="your-key-here"
```

Make sure to add to your shell config file to persist.

### "No PR found for current branch"

**Fix**: Either:
- Specify PR number: `python review_pr.py 123`
- Or create PR first: `gh pr create`

### "Error importing Python Codebase Reviewer"

**Fix**: Install dependencies
```bash
pip install google-adk requests
```

### "Could not read file"

**Fix**: Make sure you're in a git repository and files exist
```bash
git status  # Check repo status
git ls-tree -r HEAD  # List files
```

---

## Next Steps

### 1. Customize Review Focus

Edit `review_pr.py` or `review_files.py` to focus on your tech stack.

See **README.md → Customization** section.

### 2. Automate Your Workflow

Set up pre-commit hooks or daily review scripts.

See **README.md → Usage Examples** section.

### 3. Integrate with Your Editor

Add review commands to VS Code, Vim, or your favorite editor.

See **README.md → Advanced Usage** section.

### 4. Try Other Integration Options

- **Option 1 (GitHub Actions)**: Automatic PR reviews
- **Option 2 (GitHub App)**: Organization-wide deployment
- **Option 4 (Direct API)**: Custom integrations

---

## Verification Checklist

- [ ] GitHub CLI installed (`gh --version` works)
- [ ] Authenticated to GitHub (`gh auth status` shows logged in)
- [ ] Python dependencies installed (`pip list | grep google-adk`)
- [ ] GOOGLE_API_KEY set (`echo $GOOGLE_API_KEY` shows key)
- [ ] Test review completed successfully
- [ ] `review_results.md` file created with findings

---

**Setup complete!** 🎉

You can now review PRs and Python files locally using GitHub CLI.

**Quick reference**:
```bash
# Review a PR
python review_pr.py 123

# Review and post comment
python review_pr.py 123 --post

# Review specific files
python review_files.py src/main.py
```

For detailed usage and advanced features, see **README.md**.
