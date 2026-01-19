#!/usr/bin/env python3
"""
Simple example: Review a PR using GitHub MCP tools.

This example shows the most basic usage of the Python Codebase Reviewer
with GitHub MCP integration - the agent autonomously fetches files and analyzes them.

Usage:
    export GITHUB_TOKEN=your_github_token
    export GOOGLE_API_KEY=your_google_api_key

    python example_simple_review.py owner/repo 123
"""

import os
import sys

from python_codebase_reviewer import root_agent


def review_pr(repo: str, pr_number: int):
    """
    Review a pull request using agent with MCP tools.

    The agent will autonomously:
    - Fetch changed files using get_pull_request_files MCP tool
    - Fetch file contents using get_file_contents MCP tool
    - Analyze the code with specialized reviewers
    - Generate a comprehensive review

    Args:
        repo: Repository in format "owner/repo"
        pr_number: Pull request number
    """
    print(f"\n{'=' * 60}")
    print(f"Reviewing PR #{pr_number} in {repo}")
    print(f"{'=' * 60}\n")

    print("🤖 Delegating to AI agent with GitHub MCP tools...")
    print("   The agent will autonomously fetch and review files.\n")

    review_request = f"""
Review pull request #{pr_number} in repository {repo}.

**Your task:**
1. Use `get_pull_request_files` MCP tool to list all changed files in the PR
2. Filter to Python files only (*.py)
3. For each Python file, use `get_file_contents` to fetch the file content
4. Analyze each file using your specialized reviewer agents
5. Generate a comprehensive review report

**Review focus areas:**
- Security vulnerabilities (OWASP Top 10)
- Architecture and design (SOLID principles)
- Code quality (PEP standards, Pythonic idioms)
- Performance issues (complexity, N+1 queries)
- Python best practices

**Output format:**
Provide a detailed markdown report with:
- Executive summary with severity counts
- File-by-file breakdown
- Specific issues with line numbers
- Suggested fixes
- Severity indicators (🔴 Critical, 🟠 High, 🟡 Medium, 🔵 Low)
"""

    try:
        print("⏳ Review in progress...\n")
        review = root_agent.run(review_request)

        print("=" * 60)
        print("REVIEW RESULTS")
        print("=" * 60)
        print(review)
        print("\n" + "=" * 60)

        return review

    except Exception as e:
        print(f"❌ Error during review: {e}")
        sys.exit(1)


def main():
    """Main entry point."""
    if len(sys.argv) < 3:
        print("Usage: python example_simple_review.py <repo> <pr_number>")
        print("Example: python example_simple_review.py microsoft/vscode 123")
        sys.exit(1)

    repo = sys.argv[1]
    pr_number = int(sys.argv[2])

    # Verify environment variables
    if not os.getenv('GOOGLE_API_KEY'):
        print("❌ Error: GOOGLE_API_KEY environment variable not set")
        sys.exit(1)

    if not os.getenv('GITHUB_TOKEN'):
        print("❌ Error: GITHUB_TOKEN environment variable not set")
        sys.exit(1)

    # Run review
    review_pr(repo, pr_number)


if __name__ == '__main__':
    main()
