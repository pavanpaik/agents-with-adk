#!/usr/bin/env python3
"""
GitHub Actions script to review PR using Python Codebase Reviewer with MCP tools.

This script uses the GitHub MCP server to interact with GitHub APIs,
allowing the AI agent to autonomously fetch files and post reviews.

Usage:
    python review_pr.py --files "file1.py file2.py" --pr-number 123 --repo owner/repo

Environment Variables Required:
    GOOGLE_API_KEY: Google AI API key for running the reviewer
    GITHUB_TOKEN: GitHub token (automatically provided by GitHub Actions)
"""
import os
import sys
import argparse
from pathlib import Path
from typing import List, Dict

try:
    from python_codebase_reviewer import root_agent
except ImportError as e:
    print(f"Error importing Python Codebase Reviewer: {e}")
    print("Make sure the package is installed:")
    print("  pip install -e /path/to/agents-with-adk")
    print("  Or: pip install python-codebase-reviewer")
    sys.exit(1)


def review_pr_with_mcp(repo: str, file_paths: List[str], pr_number: str) -> str:
    """
    Review pull request using agent with GitHub MCP tools.

    The agent will autonomously:
    1. Use get_file_contents to fetch each file from GitHub
    2. Analyze the code with specialized reviewers
    3. Generate a comprehensive review

    Args:
        repo: Repository in format "owner/repo"
        file_paths: List of Python files to review
        pr_number: Pull request number

    Returns:
        Formatted markdown review
    """
    print(f"🤖 Asking agent to review {len(file_paths)} Python files...")

    # Create a comprehensive review request for the agent
    # The agent has access to GitHub MCP tools and can fetch files itself
    review_request = f"""
You are reviewing pull request #{pr_number} in repository {repo}.

**Files to review ({len(file_paths)} Python files):**
{chr(10).join(f"- `{f}`" for f in file_paths)}

**Your task:**
1. For each file, use the `get_file_contents` MCP tool to fetch the current file content from the repository
   - Repository: {repo}
   - Reference: Use the PR's head branch (or 'main' if unavailable)
   - Path: Each file path listed above

2. Analyze each file using your specialized reviewer agents:
   - Security vulnerabilities (OWASP Top 10, SQL injection, XSS, secrets)
   - Architecture issues (SOLID principles, design patterns, anti-patterns)
   - Code quality (PEP 8/20/257/484, Pythonic idioms, maintainability)
   - Performance issues (algorithm complexity, N+1 queries, caching)
   - Python best practices (modern features, frameworks, standard library)

3. Generate a comprehensive review in GitHub-flavored Markdown format with:
   - Executive summary with severity counts (Critical/High/Medium/Low)
   - File-by-file breakdown with specific issues
   - Code examples and suggested fixes
   - Severity indicators (🔴 Critical, 🟠 High, 🟡 Medium, 🔵 Low)

**Important:**
- Use get_file_contents for EACH file separately (don't assume you have the content)
- If a file cannot be fetched, note it and continue with other files
- Be specific with line numbers and code snippets
- Provide actionable recommendations
- Focus on security-critical issues first

Begin your review now.
"""

    try:
        response = root_agent.run(review_request)
        return response
    except Exception as e:
        error_msg = f"""# ❌ Code Review Error

**Repository**: {repo}
**Pull Request**: #{pr_number}

**Error**: {str(e)}

The AI agent encountered an error while reviewing the code.
Please check the logs and try again.
"""
        print(f"❌ Error during review: {e}")
        return error_msg


def count_findings_by_severity(review_text: str) -> Dict[str, int]:
    """
    Count findings by severity in review text.

    Args:
        review_text: Review text to analyze

    Returns:
        Dictionary with counts by severity
    """
    # Simple counting based on severity indicators
    return {
        'critical': review_text.upper().count('CRITICAL') + review_text.count('🔴'),
        'high': review_text.upper().count('HIGH') + review_text.count('🟠'),
        'medium': review_text.upper().count('MEDIUM') + review_text.count('🟡'),
        'low': review_text.upper().count('LOW') + review_text.count('🔵'),
    }


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Review Python files in a GitHub PR using AI with MCP tools'
    )
    parser.add_argument(
        '--files',
        required=True,
        help='Space-separated list of Python files to review'
    )
    parser.add_argument(
        '--pr-number',
        required=True,
        help='Pull request number'
    )
    parser.add_argument(
        '--repo',
        required=True,
        help='Repository in format "owner/repo"'
    )

    args = parser.parse_args()

    # Parse file list
    files = [f.strip() for f in args.files.split() if f.strip().endswith('.py')]

    if not files:
        print("ℹ️  No Python files to review")
        # Create empty results file
        Path('review_results.md').write_text(
            "# 🔍 Python Code Review Results\n\n"
            "✅ No Python files were changed in this PR.\n"
        )
        sys.exit(0)

    print(f"\n{'=' * 60}")
    print(f"Python Code Review - PR #{args.pr_number}")
    print(f"{'=' * 60}\n")
    print(f"Repository: {args.repo}")
    print(f"Files to review: {len(files)}")
    print(f"Mode: Agent-driven with GitHub MCP tools\n")

    # Verify environment variables
    if not os.getenv('GOOGLE_API_KEY'):
        print("❌ Error: GOOGLE_API_KEY environment variable not set")
        sys.exit(1)

    if not os.getenv('GITHUB_TOKEN'):
        print("⚠️  Warning: GITHUB_TOKEN not set, GitHub API calls may fail")

    # Run review - agent will use MCP tools to fetch files
    print("🚀 Starting AI-powered code review with MCP tools...\n")
    markdown_review = review_pr_with_mcp(args.repo, files, args.pr_number)

    # Save results
    output_file = Path('review_results.md')
    output_file.write_text(markdown_review)

    print(f"\n✅ Review complete! Results saved to {output_file}")

    # Print summary
    counts = count_findings_by_severity(markdown_review)
    total_critical = counts['critical']

    if total_critical > 0:
        print(f"\n⚠️  Warning: {total_critical} CRITICAL issues found!")
        print("Review results will be posted as a PR comment.")
    elif sum(counts.values()) == 0:
        print("\n✅ No issues found! Code looks good.")
    else:
        total = sum(counts.values())
        print(f"\n📊 Found {total} issues (High: {counts['high']}, "
              f"Medium: {counts['medium']}, Low: {counts['low']})")

    print(f"\n{'=' * 60}\n")


if __name__ == '__main__':
    main()
