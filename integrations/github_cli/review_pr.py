#!/usr/bin/env python3
"""
Simplified GitHub CLI integration for Python Codebase Reviewer.

With MCP tools, the agent autonomously handles all GitHub operations.
This is just a thin wrapper that provides context and displays results.

Usage:
    python review_pr.py 123              # Review PR #123
    python review_pr.py                  # Review current branch PR
    python review_pr.py 123 --post       # Review and post comment

Requirements:
    - gh CLI installed: https://cli.github.com/
    - Authenticated: gh auth login
    - GOOGLE_API_KEY environment variable set
    - GITHUB_TOKEN environment variable set
"""

import os
import sys
import json
import subprocess
import argparse
from pathlib import Path

try:
    from python_codebase_reviewer import root_agent
except ImportError as e:
    print(f"❌ Error importing Python Codebase Reviewer: {e}")
    print("   Install: pip install -e /path/to/agents-with-adk")
    sys.exit(1)


def get_current_repo() -> str:
    """Get current repository using gh CLI."""
    try:
        result = subprocess.run(
            ['gh', 'repo', 'view', '--json', 'nameWithOwner', '-q', '.nameWithOwner'],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Error: gh CLI not found or not in a repository")
        print("   Install gh from: https://cli.github.com/")
        sys.exit(1)


def get_current_pr() -> str:
    """Get PR number for current branch."""
    try:
        result = subprocess.run(
            ['gh', 'pr', 'view', '--json', 'number', '-q', '.number'],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        print("❌ Error: No PR found for current branch")
        print("   Usage: python review_pr.py <PR_NUMBER>")
        sys.exit(1)


def main():
    """Main entry point - now just a thin wrapper around the agent."""
    parser = argparse.ArgumentParser(
        description='Review a GitHub pull request using AI with MCP tools',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        'pr_number',
        nargs='?',
        help='PR number (optional, uses current branch if omitted)'
    )
    parser.add_argument(
        '--output', '-o',
        default='review_results.md',
        help='Save results to file (default: review_results.md)'
    )
    parser.add_argument(
        '--post',
        action='store_true',
        help='Post review as PR comment using MCP tools'
    )

    args = parser.parse_args()

    print("\n" + "=" * 60)
    print("Python Codebase Reviewer - GitHub CLI (MCP)")
    print("=" * 60 + "\n")

    # Check prerequisites
    if not os.getenv('GOOGLE_API_KEY'):
        print("❌ Error: GOOGLE_API_KEY not set")
        sys.exit(1)

    if not os.getenv('GITHUB_TOKEN'):
        print("⚠️  Warning: GITHUB_TOKEN not set")
        print("   The agent may not be able to post comments")

    # Get repository and PR info
    repo = get_current_repo()
    pr_number = args.pr_number or get_current_pr()

    print(f"📋 Repository: {repo}")
    print(f"📋 PR Number: #{pr_number}\n")

    # The agent now does EVERYTHING autonomously via MCP tools!
    print("🤖 Delegating to AI agent with GitHub MCP tools...")
    print("   The agent will autonomously:")
    print("   - Fetch PR files using get_pull_request_files")
    print("   - Fetch file contents using get_file_contents")
    print("   - Review code with specialized agents")
    if args.post:
        print("   - Post review using create_pull_request_review")
    print()

    # Build task for agent
    task = f"""
Review pull request #{pr_number} in repository {repo}.

**Your task:**
1. Use `get_pull_request_files` to list all changed files
2. Filter to Python files only (*.py)
3. Use `get_file_contents` to fetch each Python file
4. Review each file using your specialized reviewer agents
5. Generate a comprehensive markdown review report

**Review focus:**
- Security vulnerabilities (OWASP Top 10)
- Architecture issues (SOLID principles)
- Code quality (PEP 8, Pythonic idioms)
- Performance issues (complexity, N+1 queries)
- Python best practices

**Output format:**
Generate a detailed markdown report with:
- Executive summary with severity counts (Critical/High/Medium/Low)
- File-by-file breakdown with specific issues
- Line numbers and code snippets
- Suggested fixes
- Severity indicators (🔴 Critical, 🟠 High, 🟡 Medium, 🔵 Low)
"""

    if args.post:
        task += """
**After completing the review:**
Use `create_pull_request_review` or `create_issue_comment` to post your
findings as a comment on the pull request.
"""

    try:
        print("⏳ Review in progress...\n")
        review = root_agent.run(task)

        print("=" * 60)
        print("REVIEW RESULTS")
        print("=" * 60)
        print(review)
        print("\n" + "=" * 60)

        # Save to file if requested
        if args.output:
            output_path = Path(args.output)
            output_path.write_text(review)
            print(f"\n✅ Saved to: {output_path}")

        # Check for critical issues
        if "🔴" in review or "CRITICAL" in review.upper():
            print("\n⚠️  Warning: Critical issues found!")
            sys.exit(1)

    except Exception as e:
        print(f"\n❌ Error during review: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
