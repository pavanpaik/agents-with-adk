#!/usr/bin/env python3
"""
GitHub Actions script to review PR using Python Codebase Reviewer.

This script is designed to run in GitHub Actions CI/CD pipeline.

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
    from python_codebase_reviewer.tools.github_tools import (
        fetch_file_content,
        fetch_pr_info,
        GitHubAPIError
    )
except ImportError as e:
    print(f"Error importing Python Codebase Reviewer: {e}")
    print("Make sure the package is installed:")
    print("  pip install -e /path/to/agents-with-adk")
    print("  Or: pip install python-codebase-reviewer")
    sys.exit(1)


def get_file_content_from_github(repo: str, file_path: str) -> str:
    """
    Fetch file content from GitHub.

    Args:
        repo: Repository in format "owner/repo"
        file_path: Path to file in repository

    Returns:
        File content as string
    """
    try:
        # Try to read from local checkout first (faster)
        if Path(file_path).exists():
            return Path(file_path).read_text()
    except Exception:
        pass

    # Fallback to GitHub API
    try:
        # Get PR branch from environment or use HEAD
        ref = os.getenv('GITHUB_HEAD_REF', 'HEAD')
        return fetch_file_content(repo, file_path, ref)
    except GitHubAPIError as e:
        return f"# Error fetching file: {e}"


def review_files(repo: str, file_paths: List[str], pr_number: str) -> List[Dict]:
    """
    Review changed Python files.

    Args:
        repo: Repository in format "owner/repo"
        file_paths: List of file paths to review
        pr_number: Pull request number

    Returns:
        List of review results per file
    """
    results = []

    for file_path in file_paths:
        print(f"📝 Reviewing: {file_path}")

        # Get file content
        code = get_file_content_from_github(repo, file_path)

        if code.startswith("# Error"):
            print(f"⚠️  Skipping {file_path}: {code}")
            continue

        # Run review
        review_request = f"""
Review this Python file from PR #{pr_number}:

**Repository**: {repo}
**File**: `{file_path}`
**Context**: This file was changed in a pull request

```python
{code}
```

Provide a comprehensive review covering:
- Security vulnerabilities (OWASP Top 10)
- Architecture and design issues (SOLID principles)
- Code quality (PEP standards, Pythonic idioms)
- Performance issues (algorithm complexity, N+1 queries)
- Python best practices

Focus on actionable findings with severity levels and code fixes.
"""

        try:
            print(f"  🤖 Running AI review...")
            response = root_agent.run(review_request)

            results.append({
                'file': file_path,
                'review': response,
                'status': 'success'
            })
            print(f"  ✅ Review complete for {file_path}")

        except Exception as e:
            print(f"  ❌ Error reviewing {file_path}: {e}")
            results.append({
                'file': file_path,
                'review': f"Error during review: {str(e)}",
                'status': 'error'
            })

    return results


def count_findings_by_severity(review_text: str) -> Dict[str, int]:
    """
    Count findings by severity in review text.

    Args:
        review_text: Review text to analyze

    Returns:
        Dictionary with counts by severity
    """
    # Simple counting - could be made more sophisticated
    return {
        'critical': review_text.upper().count('CRITICAL'),
        'high': review_text.upper().count('HIGH'),
        'medium': review_text.upper().count('MEDIUM'),
        'low': review_text.upper().count('LOW'),
    }


def format_review_markdown(results: List[Dict], repo: str, pr_number: str) -> str:
    """
    Format review results as GitHub-flavored markdown.

    Args:
        results: List of review results
        repo: Repository name
        pr_number: Pull request number

    Returns:
        Formatted markdown string
    """
    output = []

    # Header
    output.append("# 🔍 Python Code Review Results\n")
    output.append(f"**Repository**: {repo}\n")
    output.append(f"**Pull Request**: #{pr_number}\n")
    output.append(f"**Files Reviewed**: {len(results)}\n")
    output.append("\n---\n\n")

    # Count total findings by severity
    total_counts = {
        'critical': 0,
        'high': 0,
        'medium': 0,
        'low': 0
    }

    for result in results:
        if result['status'] == 'success':
            counts = count_findings_by_severity(result['review'])
            for severity, count in counts.items():
                total_counts[severity] += count

    # Summary
    output.append("## 📊 Summary\n\n")

    if sum(total_counts.values()) == 0:
        output.append("✅ **No issues found!** All code looks good.\n\n")
    else:
        if total_counts['critical'] > 0:
            output.append(f"- 🔴 **{total_counts['critical']} Critical** issues (immediate action required)\n")
        if total_counts['high'] > 0:
            output.append(f"- 🟠 **{total_counts['high']} High** priority issues\n")
        if total_counts['medium'] > 0:
            output.append(f"- 🟡 **{total_counts['medium']} Medium** priority issues\n")
        if total_counts['low'] > 0:
            output.append(f"- 🔵 **{total_counts['low']} Low** priority issues\n")
        output.append("\n")

        # Add warning if critical issues found
        if total_counts['critical'] > 0:
            output.append("> ⚠️ **Warning**: Critical security issues detected. Please review and fix before merging.\n\n")

    output.append("---\n\n")

    # Detailed results per file
    output.append("## 📁 Detailed Review by File\n\n")

    for result in results:
        output.append(f"### `{result['file']}`\n\n")

        if result['status'] == 'error':
            output.append(f"❌ **Error**: {result['review']}\n\n")
        else:
            # Add collapsible section for long reviews
            counts = count_findings_by_severity(result['review'])
            total = sum(counts.values())

            if total == 0:
                output.append("✅ No issues found in this file.\n\n")
            else:
                output.append(f"**Found {total} issue(s)**\n\n")
                output.append("<details>\n")
                output.append("<summary>Click to view detailed review</summary>\n\n")
                output.append(result['review'])
                output.append("\n\n</details>\n\n")

        output.append("---\n\n")

    # Footer
    output.append("## 🤖 Powered by Python Codebase Reviewer\n\n")
    output.append("*AI-powered code review using specialized agents for security, architecture, ")
    output.append("code quality, performance, and Python best practices.*\n")

    return ''.join(output)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Review Python files in a GitHub PR using AI'
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
    print(f"Files to review: {len(files)}\n")

    # Verify environment variables
    if not os.getenv('GOOGLE_API_KEY'):
        print("❌ Error: GOOGLE_API_KEY environment variable not set")
        sys.exit(1)

    if not os.getenv('GITHUB_TOKEN'):
        print("⚠️  Warning: GITHUB_TOKEN not set, GitHub API calls may fail")

    # Run reviews
    print("🚀 Starting code review...\n")
    results = review_files(args.repo, files, args.pr_number)

    # Format as markdown
    print("\n📝 Formatting results...")
    markdown = format_review_markdown(results, args.repo, args.pr_number)

    # Save results
    output_file = Path('review_results.md')
    output_file.write_text(markdown)

    print(f"\n✅ Review complete! Results saved to {output_file}")

    # Print summary
    total_critical = sum(
        count_findings_by_severity(r['review'])['critical']
        for r in results if r['status'] == 'success'
    )

    if total_critical > 0:
        print(f"\n⚠️  Warning: {total_critical} CRITICAL issues found!")
        print("Review results will be posted as a PR comment.")

    print(f"\n{'=' * 60}\n")


if __name__ == '__main__':
    main()
