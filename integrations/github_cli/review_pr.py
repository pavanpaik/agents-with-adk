#!/usr/bin/env python3
"""
GitHub CLI integration for Python Codebase Reviewer.

Review pull requests locally using the gh CLI tool.

Usage:
    # Review a specific PR
    python review_pr.py 123

    # Review current branch's PR
    python review_pr.py

    # Review with custom output
    python review_pr.py 123 --output review.md

    # Post review as PR comment
    python review_pr.py 123 --post-comment

Requirements:
    - gh CLI installed: https://cli.github.com/
    - Authenticated: gh auth login
    - google-adk installed: pip install google-adk
    - GOOGLE_API_KEY environment variable set
"""

import os
import sys
import json
import subprocess
import argparse
from pathlib import Path
from typing import List, Dict, Optional, Tuple

# Add parent directory to path to import reviewer
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from python_codebase_reviewer import root_agent
except ImportError as e:
    print(f"❌ Error importing Python Codebase Reviewer: {e}")
    print("   Install: pip install google-adk")
    sys.exit(1)


def run_gh_command(args: List[str]) -> Tuple[str, int]:
    """
    Run a gh CLI command.

    Args:
        args: Command arguments (e.g., ['pr', 'view', '123'])

    Returns:
        Tuple of (output, return_code)
    """
    try:
        result = subprocess.run(
            ['gh'] + args,
            capture_output=True,
            text=True,
            check=False
        )
        return result.stdout, result.returncode
    except FileNotFoundError:
        print("❌ Error: gh CLI not found")
        print("   Install from: https://cli.github.com/")
        sys.exit(1)


def check_gh_auth() -> bool:
    """Check if gh CLI is authenticated."""
    output, code = run_gh_command(['auth', 'status'])
    return code == 0


def get_current_repo() -> str:
    """
    Get current repository name.

    Returns:
        Repository in format "owner/repo"
    """
    output, code = run_gh_command(['repo', 'view', '--json', 'nameWithOwner', '-q', '.nameWithOwner'])
    if code != 0:
        print("❌ Error: Not in a git repository or no remote configured")
        sys.exit(1)
    return output.strip()


def get_pr_info(pr_number: Optional[str] = None) -> Dict:
    """
    Get PR information.

    Args:
        pr_number: PR number (optional, uses current branch if not provided)

    Returns:
        PR information as dictionary
    """
    cmd = ['pr', 'view']
    if pr_number:
        cmd.append(pr_number)

    cmd.extend(['--json', 'number,title,body,headRefName,files,url'])

    output, code = run_gh_command(cmd)

    if code != 0:
        if pr_number:
            print(f"❌ Error: PR #{pr_number} not found")
        else:
            print("❌ Error: No PR found for current branch")
            print("   Usage: python review_pr.py <PR_NUMBER>")
        sys.exit(1)

    return json.loads(output)


def get_file_content(file_path: str, ref: str) -> Optional[str]:
    """
    Get file content from a specific ref.

    Args:
        file_path: Path to file
        ref: Git ref (branch name, commit SHA)

    Returns:
        File content or None if error
    """
    try:
        result = subprocess.run(
            ['git', 'show', f'{ref}:{file_path}'],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout
    except subprocess.CalledProcessError:
        return None


def review_file(file_path: str, code: str, repo: str, pr_number: str) -> Dict:
    """
    Review a single Python file.

    Args:
        file_path: Path to file
        code: File content
        repo: Repository name
        pr_number: PR number

    Returns:
        Review results dictionary
    """
    review_request = f"""
Review this Python file from PR #{pr_number}:

**Repository**: {repo}
**File**: `{file_path}`
**Context**: Changed in pull request

```python
{code}
```

Provide comprehensive review covering:
- Security vulnerabilities (OWASP Top 10)
- Architecture and design (SOLID principles)
- Code quality (PEP 8, Pythonic idioms)
- Performance (algorithm complexity, N+1 queries)
- Python best practices

Focus on actionable findings with severity levels and fixes.
"""

    try:
        print(f"  🤖 Running AI review...")
        response = root_agent.run(review_request)

        return {
            'file': file_path,
            'review': response,
            'status': 'success'
        }

    except Exception as e:
        print(f"  ❌ Error reviewing {file_path}: {e}")
        return {
            'file': file_path,
            'review': f"Error during review: {str(e)}",
            'status': 'error'
        }


def count_findings(review_text: str) -> Dict[str, int]:
    """Count findings by severity."""
    return {
        'critical': review_text.upper().count('CRITICAL'),
        'high': review_text.upper().count('HIGH'),
        'medium': review_text.upper().count('MEDIUM'),
        'low': review_text.upper().count('LOW'),
    }


def format_review_markdown(results: List[Dict], pr_info: Dict, repo: str) -> str:
    """
    Format review results as markdown.

    Args:
        results: List of review results
        pr_info: PR information
        repo: Repository name

    Returns:
        Formatted markdown string
    """
    output = []

    # Header
    output.append("# 🔍 Python Code Review Results\n\n")
    output.append(f"**Repository**: {repo}\n")
    output.append(f"**Pull Request**: #{pr_info['number']} - {pr_info['title']}\n")
    output.append(f"**Branch**: `{pr_info['headRefName']}`\n")
    output.append(f"**Files Reviewed**: {len(results)}\n")
    output.append("\n---\n\n")

    # Count totals
    total_counts = {'critical': 0, 'high': 0, 'medium': 0, 'low': 0}
    for result in results:
        if result['status'] == 'success':
            counts = count_findings(result['review'])
            for severity, count in counts.items():
                total_counts[severity] += count

    # Summary
    output.append("## 📊 Summary\n\n")

    if sum(total_counts.values()) == 0:
        output.append("✅ **No issues found!** All code looks good.\n\n")
    else:
        if total_counts['critical'] > 0:
            output.append(f"- 🔴 **{total_counts['critical']} Critical** - Immediate action required\n")
        if total_counts['high'] > 0:
            output.append(f"- 🟠 **{total_counts['high']} High** - Should fix before merge\n")
        if total_counts['medium'] > 0:
            output.append(f"- 🟡 **{total_counts['medium']} Medium** - Consider fixing\n")
        if total_counts['low'] > 0:
            output.append(f"- 🔵 **{total_counts['low']} Low** - Nice to have\n")
        output.append("\n")

        if total_counts['critical'] > 0:
            output.append("> ⚠️ **Warning**: Critical security issues detected!\n\n")

    output.append("---\n\n")

    # Detailed results
    output.append("## 📁 Detailed Review\n\n")

    for result in results:
        output.append(f"### 📄 `{result['file']}`\n\n")

        if result['status'] == 'error':
            output.append(f"❌ **Error**: {result['review']}\n\n")
        else:
            counts = count_findings(result['review'])
            total = sum(counts.values())

            if total == 0:
                output.append("✅ No issues found.\n\n")
            else:
                # Show severity summary
                severity_parts = []
                if counts['critical'] > 0:
                    severity_parts.append(f"🔴 {counts['critical']} Critical")
                if counts['high'] > 0:
                    severity_parts.append(f"🟠 {counts['high']} High")
                if counts['medium'] > 0:
                    severity_parts.append(f"🟡 {counts['medium']} Medium")
                if counts['low'] > 0:
                    severity_parts.append(f"🔵 {counts['low']} Low")

                output.append(f"**Found {total} issue(s)**: {' | '.join(severity_parts)}\n\n")

                # Add detailed review
                output.append("<details>\n")
                output.append("<summary>Show detailed review</summary>\n\n")
                output.append(result['review'])
                output.append("\n\n</details>\n\n")

        output.append("---\n\n")

    # Footer
    output.append("## 🤖 About\n\n")
    output.append("**Powered by Python Codebase Reviewer**\n\n")
    output.append("AI-powered code review using specialized agents:\n")
    output.append("- 🛡️ Security Reviewer (OWASP Top 10)\n")
    output.append("- 🏗️ Architecture Reviewer (SOLID principles)\n")
    output.append("- ✨ Code Quality Reviewer (PEP standards)\n")
    output.append("- ⚡ Performance Reviewer (optimization)\n")
    output.append("- 🐍 Python Expert (best practices)\n\n")

    output.append(f"**PR Link**: {pr_info['url']}\n")

    return ''.join(output)


def post_pr_comment(pr_number: str, comment: str) -> bool:
    """
    Post a comment on a PR.

    Args:
        pr_number: PR number
        comment: Comment text

    Returns:
        True if successful
    """
    # Save comment to temp file
    temp_file = Path('/tmp/pr_comment.md')
    temp_file.write_text(comment)

    try:
        output, code = run_gh_command([
            'pr', 'comment', pr_number,
            '--body-file', str(temp_file)
        ])

        if code == 0:
            return True
        else:
            print(f"❌ Failed to post comment: {output}")
            return False

    finally:
        temp_file.unlink(missing_ok=True)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Review a GitHub pull request using AI',
        epilog='Examples:\n'
               '  python review_pr.py 123              # Review PR #123\n'
               '  python review_pr.py                  # Review current branch PR\n'
               '  python review_pr.py 123 --post       # Review and post comment\n',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        'pr_number',
        nargs='?',
        help='PR number to review (optional, uses current branch if omitted)'
    )
    parser.add_argument(
        '--output', '-o',
        default='review_results.md',
        help='Output file for review results (default: review_results.md)'
    )
    parser.add_argument(
        '--post', '--post-comment',
        action='store_true',
        dest='post_comment',
        help='Post review as PR comment'
    )
    parser.add_argument(
        '--no-save',
        action='store_true',
        help='Do not save results to file (only print to console)'
    )

    args = parser.parse_args()

    # Print header
    print("\n" + "=" * 60)
    print("Python Codebase Reviewer - GitHub CLI")
    print("=" * 60 + "\n")

    # Check prerequisites
    print("🔍 Checking prerequisites...")

    if not check_gh_auth():
        print("❌ Error: gh CLI not authenticated")
        print("   Run: gh auth login")
        sys.exit(1)
    print("  ✅ gh CLI authenticated")

    if not os.getenv('GOOGLE_API_KEY'):
        print("❌ Error: GOOGLE_API_KEY environment variable not set")
        print("   Get key from: https://aistudio.google.com/app/apikey")
        print("   Set: export GOOGLE_API_KEY=your-key-here")
        sys.exit(1)
    print("  ✅ GOOGLE_API_KEY found")

    # Get repository info
    repo = get_current_repo()
    print(f"  ✅ Repository: {repo}\n")

    # Get PR info
    print(f"📋 Fetching PR information...")
    pr_info = get_pr_info(args.pr_number)

    print(f"  PR #{pr_info['number']}: {pr_info['title']}")
    print(f"  Branch: {pr_info['headRefName']}\n")

    # Filter Python files
    python_files = [
        f for f in pr_info['files']
        if f['path'].endswith('.py') and f['additions'] > 0
    ]

    if not python_files:
        print("ℹ️  No Python files changed in this PR")
        sys.exit(0)

    print(f"📝 Found {len(python_files)} Python file(s) to review:\n")
    for f in python_files:
        print(f"  - {f['path']} (+{f['additions']} -{f['deletions']})")
    print()

    # Review each file
    print("🚀 Starting code review...\n")
    results = []

    for file_info in python_files:
        file_path = file_info['path']
        print(f"📄 Reviewing: {file_path}")

        # Get file content from PR branch
        code = get_file_content(file_path, pr_info['headRefName'])

        if code is None:
            print(f"  ⚠️  Could not read file, skipping")
            results.append({
                'file': file_path,
                'review': 'Error: Could not read file',
                'status': 'error'
            })
            continue

        # Run review
        result = review_file(file_path, code, repo, str(pr_info['number']))
        results.append(result)

        if result['status'] == 'success':
            counts = count_findings(result['review'])
            total = sum(counts.values())
            print(f"  ✅ Found {total} issue(s)")
        else:
            print(f"  ❌ Review failed")

        print()

    # Format results
    print("📝 Formatting results...")
    markdown = format_review_markdown(results, pr_info, repo)

    # Save to file
    if not args.no_save:
        output_path = Path(args.output)
        output_path.write_text(markdown)
        print(f"  ✅ Saved to: {output_path}\n")

    # Post comment if requested
    if args.post_comment:
        print("💬 Posting review as PR comment...")
        if post_pr_comment(str(pr_info['number']), markdown):
            print(f"  ✅ Comment posted on PR #{pr_info['number']}\n")
        else:
            print("  ❌ Failed to post comment\n")

    # Print summary
    total_counts = {'critical': 0, 'high': 0, 'medium': 0, 'low': 0}
    for result in results:
        if result['status'] == 'success':
            counts = count_findings(result['review'])
            for severity, count in counts.items():
                total_counts[severity] += count

    print("=" * 60)
    print("📊 Review Summary")
    print("=" * 60)
    print(f"Files reviewed: {len(results)}")
    print(f"Total issues: {sum(total_counts.values())}")
    if total_counts['critical'] > 0:
        print(f"  🔴 Critical: {total_counts['critical']}")
    if total_counts['high'] > 0:
        print(f"  🟠 High: {total_counts['high']}")
    if total_counts['medium'] > 0:
        print(f"  🟡 Medium: {total_counts['medium']}")
    if total_counts['low'] > 0:
        print(f"  🔵 Low: {total_counts['low']}")
    print("=" * 60 + "\n")

    if total_counts['critical'] > 0:
        print("⚠️  Warning: Critical issues found!")
        sys.exit(1)


if __name__ == '__main__':
    main()
