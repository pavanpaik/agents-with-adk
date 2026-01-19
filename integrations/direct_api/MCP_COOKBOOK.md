# MCP Cookbook - Natural Language Code Review

With GitHub MCP tools, you no longer need to manually orchestrate API calls. Just **tell the agent what you want** in natural language, and it figures out which tools to use.

This cookbook shows common code review patterns using the **agent-driven approach**.

---

## 🎯 Philosophy: Tell, Don't Orchestrate

### ❌ Old Way (Manual Orchestration)
```python
# Manual: You orchestrate every step
from python_codebase_reviewer.tools.github_tools import fetch_pr_files, fetch_file_content

files = fetch_pr_files(repo, pr_number)
python_files = [f for f in files if f['filename'].endswith('.py')]
for file in python_files:
    content = fetch_file_content(repo, file['filename'])
    review = root_agent.run(f"Review this code: {content}")
    # ... more manual steps
```

### ✅ New Way (Agent-Driven with MCP)
```python
# Agent-driven: Just describe what you want
from python_codebase_reviewer import root_agent

review = root_agent.run("""
Review all Python files in PR #123 of owner/repo.
Fetch files, analyze them, and provide a comprehensive report.
""")
```

**The agent uses MCP tools autonomously!**

---

## 📚 Common Patterns

### 1. Basic PR Review

**Task:** Review all Python files in a pull request

```python
from python_codebase_reviewer import root_agent

review = root_agent.run("""
Review pull request #456 in microsoft/vscode-python.

1. Use get_pull_request_files to list changed files
2. Filter to Python files only
3. Use get_file_contents to fetch each file
4. Review for security, architecture, code quality, performance
5. Generate a markdown report with severity levels
""")

print(review)
```

---

### 2. Security-Only Review

**Task:** Focus only on security issues

```python
review = root_agent.run("""
Review PR #123 in owner/repo for SECURITY ISSUES ONLY.

Focus on:
- SQL injection vulnerabilities
- XSS attacks
- CSRF vulnerabilities
- Authentication/authorization bugs
- Secrets in code
- Insecure cryptography

Ignore code style, performance, and architecture.
Report only Critical and High severity findings.
""")
```

---

### 3. Compare with Main Branch

**Task:** Show what changed vs main branch

```python
review = root_agent.run("""
Review PR #789 in owner/repo.

For each changed Python file:
1. Fetch the PR version using get_file_contents
2. Fetch the main branch version for comparison
3. Highlight what changed and why it matters
4. Focus on behavioral differences, not style

Generate a side-by-side comparison report.
""")
```

---

### 4. Review Specific Files Only

**Task:** Review only authentication-related files

```python
review = root_agent.run("""
Review PR #321 in owner/repo.

ONLY review files that:
- Contain "auth" in the filename OR
- Import authentication libraries (e.g., django.contrib.auth, flask_login)

Skip all other files.
Focus on authentication security and session management.
""")
```

---

### 5. Auto-Fix and Push

**Task:** Automatically fix common issues and push to PR

```python
result = root_agent.run("""
Review PR #654 in owner/repo.

After reviewing:
1. Identify all PEP 8 violations
2. For simple violations (whitespace, imports, line length):
   - Generate fixed versions
   - Use push_files to update the PR branch
3. For complex issues, create review comments only

Report what was auto-fixed and what needs manual attention.
""")
```

---

### 6. Multi-Stage Review

**Task:** Security first, then code quality

```python
# Stage 1: Security review
security_review = root_agent.run("""
Review PR #111 in owner/repo for SECURITY ONLY.

If any Critical security issues found:
- Use create_issue to create a security advisory
- STOP and report immediately

If no critical issues, proceed with full review.
""")

if "CRITICAL" not in security_review:
    # Stage 2: Full review
    full_review = root_agent.run("""
    Review PR #111 in owner/repo for:
    - Architecture
    - Code quality
    - Performance
    - Python best practices
    """)
```

---

### 7. Review with Context from Issues

**Task:** Consider related GitHub issues

```python
review = root_agent.run("""
Review PR #999 in owner/repo.

This PR claims to fix issue #123.

1. Use get_issue to fetch issue #123
2. Verify the PR actually addresses the issue
3. Check if the fix is complete
4. Review code quality and security
5. Comment on whether the issue is fully resolved

Include issue context in your review.
""")
```

---

### 8. Review with CI/CD Context

**Task:** Check if CI passed before reviewing

```python
review = root_agent.run("""
Review PR #777 in owner/repo.

First, check if CI passed:
1. Use list_workflow_runs to get recent runs
2. If CI failed, note which checks failed
3. If linting failed, skip code style review
4. Focus review on areas CI doesn't cover

Mention CI status in your review summary.
""")
```

---

### 9. Review and Auto-Merge

**Task:** Review, and if clean, auto-merge

```python
result = root_agent.run("""
Review PR #555 in owner/repo.

After reviewing:
- If NO Critical or High issues found AND all CI checks passed:
  * Use create_pull_request_review with event='APPROVE'
  * Use merge_pull_request to merge the PR
  * Use create_issue_comment to thank the contributor

- If issues found:
  * Use create_pull_request_review with event='REQUEST_CHANGES'
  * List all issues that need fixing

Report what action was taken.
""")
```

---

### 10. Review New Contributors

**Task:** Extra helpful review for first-time contributors

```python
review = root_agent.run("""
Review PR #222 in owner/repo.

First, check if this is the author's first PR:
1. Use get_pull_request to get author info
2. Check their contribution history

If first-time contributor:
- Be extra helpful and encouraging
- Explain WHY issues are problems, not just WHAT
- Suggest learning resources
- Thank them for contributing

If experienced contributor:
- Use standard review tone
""")
```

---

### 11. Custom Severity Filtering

**Task:** Only report Medium+ issues

```python
review = root_agent.run("""
Review PR #888 in owner/repo.

Review all aspects, but ONLY REPORT issues that are:
- Medium severity or higher
- Actually affect functionality or security
- Not just style preferences

Ignore:
- Low severity issues
- Nitpicks
- Personal style preferences

Be concise. Focus on what matters.
""")
```

---

### 12. Performance-Focused Review

**Task:** Deep dive into performance

```python
review = root_agent.run("""
Review PR #444 in owner/repo for PERFORMANCE ONLY.

Focus on:
- Algorithm complexity (O(n²) loops, etc.)
- Database query patterns (N+1 queries)
- Memory usage (unnecessary copies, large lists)
- Caching opportunities
- Async/await usage

Use search_code to find similar patterns in the repo.
Suggest specific optimizations with code examples.
""")
```

---

### 13. Dependency Security Review

**Task:** Check for vulnerable dependencies

```python
review = root_agent.run("""
Review PR #333 in owner/repo.

Focus on dependency changes:
1. Look for requirements.txt, setup.py, pyproject.toml changes
2. Use get_code_scanning_alerts to check for known vulnerabilities
3. Check if dependencies are pinned to specific versions
4. Verify dependencies are from trusted sources

Report any security concerns with dependencies.
""")
```

---

### 14. Documentation Review

**Task:** Ensure code is well-documented

```python
review = root_agent.run("""
Review PR #666 in owner/repo for DOCUMENTATION.

Check:
- Are all public functions documented?
- Are docstrings complete (params, returns, raises)?
- Are docstrings following Google/NumPy style?
- Are complex algorithms explained?
- Are there code comments for non-obvious logic?

Generate examples of proper docstrings for undocumented functions.
""")
```

---

### 15. Test Coverage Review

**Task:** Ensure adequate test coverage

```python
review = root_agent.run("""
Review PR #999 in owner/repo for TEST COVERAGE.

1. Identify all new or modified functions
2. Search for corresponding test files using search_code
3. Check if each function has tests
4. Verify tests cover edge cases
5. Report untested functions

Suggest specific test cases that should be added.
""")
```

---

## 🎨 Advanced Patterns

### Custom Output Formats

**JSON output for automation:**
```python
review = root_agent.run("""
Review PR #123 in owner/repo.

Output format: JSON with this structure:
{
  "summary": "...",
  "total_issues": 10,
  "critical": 2,
  "high": 3,
  "medium": 4,
  "low": 1,
  "files": [
    {
      "path": "file.py",
      "issues": [
        {
          "line": 42,
          "severity": "critical",
          "type": "security",
          "message": "...",
          "fix": "..."
        }
      ]
    }
  ]
}
""")

import json
data = json.loads(review)
print(f"Found {data['critical']} critical issues")
```

---

### Parallel Review (Multiple PRs)

```python
import concurrent.futures

def review_pr(pr_number):
    return root_agent.run(f"Review PR #{pr_number} in owner/repo")

# Review multiple PRs in parallel
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
    prs = [123, 456, 789]
    reviews = executor.map(review_pr, prs)

for pr, review in zip(prs, reviews):
    print(f"PR #{pr}:\n{review}\n")
```

---

### Conditional Reviews

```python
# Only review if PR touches critical files
review = root_agent.run("""
Review PR #456 in owner/repo.

First, check if the PR modifies any of these critical files:
- src/auth/*.py
- src/payments/*.py
- config/security.py

If YES: Do a thorough security review
If NO: Do a standard quick review
""")
```

---

## 💡 Pro Tips

### 1. Be Specific
```python
# ❌ Vague
root_agent.run("Review this PR")

# ✅ Specific
root_agent.run("""
Review PR #123 in owner/repo.
Focus on SQL injection vulnerabilities in database queries.
Check files in src/models/ and src/api/.
Report only Critical issues.
""")
```

### 2. Give Context
```python
root_agent.run("""
Review PR #456 in owner/repo.

CONTEXT:
- This is a hotfix for production issue #789
- Security is critical, performance is secondary
- Code must be Python 3.8 compatible (no 3.10+ features)
- This will be deployed to 10M+ users

Review accordingly.
""")
```

### 3. Use Examples
```python
root_agent.run("""
Review PR #789 in owner/repo.

For security issues, format like this example:
🔴 **Critical - SQL Injection** (line 42)
Current code allows SQL injection via user input.
Fix: Use parameterized queries.
Example: cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
""")
```

### 4. Chain Tools
```python
root_agent.run("""
Review PR #123 in owner/repo.

Workflow:
1. Use get_pull_request to check if PR description mentions 'breaking change'
2. If yes, use search_code to find all usages of modified functions
3. Check if migration guide is included in the PR
4. Review code thoroughly
5. Post review with migration warnings if needed
""")
```

---

## 🚀 Integration Examples

### GitHub Actions
```yaml
# .github/workflows/ai-review.yml
- name: AI Code Review
  run: |
    python -c "
    from python_codebase_reviewer import root_agent
    review = root_agent.run('''
    Review PR #${{ github.event.pull_request.number }} in ${{ github.repository }}.
    Post review using create_pull_request_review.
    ''')
    "
```

### Pre-commit Hook
```python
# .git/hooks/pre-commit
from python_codebase_reviewer import root_agent

review = root_agent.run("""
Review my staged Python files.
If any Critical issues, exit with error code 1.
""")
```

### CI/CD Pipeline
```python
# ci/review.py
review = root_agent.run(f"""
Review PR #{os.getenv('PR_NUMBER')} in {os.getenv('REPO')}.

If review finds Critical issues:
  - Post review as PR comment
  - Fail the CI build
Else:
  - Post review
  - Pass CI build
""")
```

---

## 📊 Comparison: Old vs New

| Task | Old (Manual) | New (MCP) |
|------|-------------|-----------|
| **Lines of code** | 50-200 | 5-20 |
| **Complexity** | High (orchestration) | Low (just describe) |
| **Flexibility** | Limited by tools | Unlimited (natural language) |
| **Maintenance** | Update code for changes | Update prompt only |
| **Error handling** | Manual try/catch | Agent handles it |
| **Tool discovery** | Read docs, import | Agent knows all tools |

---

## 🎓 Learning Path

1. **Start Simple:** Use basic PR review pattern
2. **Add Filters:** Focus on specific files or issues
3. **Add Actions:** Auto-fix, post comments, merge
4. **Add Context:** Use CI status, issues, dependencies
5. **Get Creative:** Multi-stage reviews, custom workflows

---

## 🔗 Related Documentation

- [GitHub MCP Tools List](https://github.com/github/github-mcp-server)
- [MEANINGFUL_INTEGRATIONS.md](../../MEANINGFUL_INTEGRATIONS.md)
- [MCP_MIGRATION_SUMMARY.md](../../MCP_MIGRATION_SUMMARY.md)

---

**Remember:** The agent has 51+ GitHub MCP tools. Just tell it what you want, and it figures out how to do it!
