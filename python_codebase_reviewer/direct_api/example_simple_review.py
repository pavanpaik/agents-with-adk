#!/usr/bin/env python3
"""
Simple example: Review a PR using GitHub API tools directly.

This example shows the most basic usage of the Python Codebase Reviewer
with GitHub API integration - no GitHub Actions, no GitHub App, no CLI needed.

Usage:
    export GITHUB_TOKEN=your_github_token
    export GOOGLE_API_KEY=your_google_api_key

    python example_simple_review.py owner/repo 123
"""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from python_codebase_reviewer import root_agent
from python_codebase_reviewer.tools.github_tools import (
    fetch_pr_files,
    fetch_file_content,
    post_pr_review,
    GitHubAPIError
)


def review_pr(repo: str, pr_number: int, post_comment: bool = False):
    """
    Review a pull request and optionally post results.

    Args:
        repo: Repository in format "owner/repo"
        pr_number: Pull request number
        post_comment: If True, post review as PR comment
    """
    print(f"\n{'=' * 60}")
    print(f"Reviewing PR #{pr_number} in {repo}")
    print(f"{'=' * 60}\n")

    # Step 1: Fetch PR files
    print("📋 Fetching PR files...")
    try:
        files = fetch_pr_files(repo, pr_number)
        print(f"   Found {len(files)} file(s) changed\n")
    except GitHubAPIError as e:
        print(f"❌ Error fetching PR: {e}")
        sys.exit(1)

    # Step 2: Filter Python files
    python_files = [f for f in files if f['filename'].endswith('.py')]

    if not python_files:
        print("ℹ️  No Python files in this PR")
        return

    print(f"📝 Found {len(python_files)} Python file(s):\n")
    for f in python_files:
        print(f"   - {f['filename']} (+{f['additions']} -{f['deletions']})")
    print()

    # Step 3: Review each file
    reviews = []

    for file_info in python_files:
        filename = file_info['filename']
        print(f"📄 Reviewing: {filename}")

        # Fetch file content
        try:
            # Use the blob URL to get content
            code = fetch_file_content(
                repo,
                filename,
                ref=file_info.get('sha') or 'HEAD'
            )
        except GitHubAPIError as e:
            print(f"   ⚠️  Could not fetch content: {e}")
            continue

        # Run review
        review_request = f"""
Review this Python file from PR #{pr_number}:

**Repository**: {repo}
**File**: `{filename}`
**Changes**: +{file_info['additions']} -{file_info['deletions']} lines

```python
{code}
```

Provide comprehensive review covering:
- Security vulnerabilities (OWASP Top 10)
- Architecture and design issues
- Code quality and PEP standards
- Performance issues
- Python best practices

Focus on actionable findings.
"""

        try:
            print("   🤖 Running AI review...")
            response = root_agent.run(review_request)
            reviews.append({
                'file': filename,
                'review': response
            })
            print("   ✅ Review complete\n")

        except Exception as e:
            print(f"   ❌ Error: {e}\n")
            continue

    # Step 4: Format results
    print("📝 Formatting results...\n")

    review_body = format_review(repo, pr_number, reviews)

    # Step 5: Output or post
    if post_comment:
        print("💬 Posting review as PR comment...")
        try:
            post_pr_review(repo, pr_number, review_body)
            print("   ✅ Comment posted!\n")
        except GitHubAPIError as e:
            print(f"   ❌ Failed to post: {e}\n")
            print("Review content:")
            print(review_body)
    else:
        print("Review complete! Here's the result:\n")
        print(review_body)


def format_review(repo: str, pr_number: int, reviews: list) -> str:
    """Format review results as markdown."""
    lines = []

    lines.append("# 🔍 Python Code Review Results\n")
    lines.append(f"**Repository**: {repo}\n")
    lines.append(f"**Pull Request**: #{pr_number}\n")
    lines.append(f"**Files Reviewed**: {len(reviews)}\n")
    lines.append("\n---\n\n")

    lines.append("## 📁 Files Reviewed\n\n")

    for review in reviews:
        lines.append(f"### 📄 `{review['file']}`\n\n")
        lines.append(review['review'])
        lines.append("\n\n---\n\n")

    lines.append("*Powered by Python Codebase Reviewer*\n")

    return ''.join(lines)


def main():
    """Main entry point."""
    if len(sys.argv) < 3:
        print("Usage: python example_simple_review.py owner/repo PR_NUMBER [--post]")
        print("\nExample:")
        print("  python example_simple_review.py facebook/react 12345")
        print("  python example_simple_review.py facebook/react 12345 --post")
        sys.exit(1)

    # Check environment variables
    if not os.getenv('GITHUB_TOKEN'):
        print("❌ Error: GITHUB_TOKEN environment variable not set")
        print("   Get token from: https://github.com/settings/tokens")
        sys.exit(1)

    if not os.getenv('GOOGLE_API_KEY'):
        print("❌ Error: GOOGLE_API_KEY environment variable not set")
        print("   Get key from: https://aistudio.google.com/app/apikey")
        sys.exit(1)

    repo = sys.argv[1]
    pr_number = int(sys.argv[2])
    post_comment = '--post' in sys.argv

    review_pr(repo, pr_number, post_comment)


if __name__ == '__main__':
    main()
