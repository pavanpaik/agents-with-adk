#!/usr/bin/env python3
"""
Custom workflow example: Build your own review pipeline.

This example shows how to create custom review workflows using the
GitHub API tools and Python Codebase Reviewer.

Use cases:
- Custom filtering logic (only review certain files/patterns)
- Multi-stage reviews (security first, then code quality)
- Integration with other tools (linters, formatters, etc.)
- Custom output formats (JSON, CSV, database, etc.)

Usage:
    export GITHUB_TOKEN=your_github_token
    export GOOGLE_API_KEY=your_google_api_key

    python example_custom_workflow.py owner/repo 123
"""

import os
import sys
import json
from typing import List, Dict, Optional


from python_codebase_reviewer import root_agent
from python_codebase_reviewer.sub_agents import (
    security_reviewer,
    code_quality_reviewer,
    performance_reviewer
)
from python_codebase_reviewer.tools.github_tools import (
    fetch_pr_files,
    fetch_pr_info,
    fetch_file_content,
    post_pr_review,
    GitHubAPIError
)


class CustomReviewWorkflow:
    """
    Custom review workflow with advanced features.

    Features:
    - File filtering by patterns
    - Multi-stage reviews
    - Severity-based routing
    - Custom output formats
    - Integration hooks
    """

    def __init__(self, repo: str, pr_number: int):
        self.repo = repo
        self.pr_number = pr_number
        self.results = []

    def should_review_file(self, filename: str) -> bool:
        """
        Custom logic to determine if a file should be reviewed.

        Override this method to implement your own filtering.
        """
        # Example: Only review Python files in src/ directory
        if not filename.endswith('.py'):
            return False

        # Skip test files
        if 'test_' in filename or filename.startswith('tests/'):
            return False

        # Skip migrations
        if 'migrations/' in filename:
            return False

        # Skip generated files
        if filename.endswith('_pb2.py'):  # Protocol buffers
            return False

        # Only review certain directories
        allowed_dirs = ['src/', 'app/', 'lib/']
        if not any(filename.startswith(d) for d in allowed_dirs):
            return False

        return True

    def run_multi_stage_review(self, filename: str, code: str) -> Dict:
        """
        Run review in multiple stages with different focus.

        Stage 1: Security (critical - must pass)
        Stage 2: Code Quality (important)
        Stage 3: Performance (optional)
        """
        result = {
            'file': filename,
            'stages': {}
        }

        print(f"   Stage 1: Security review...")
        security_prompt = f"""
Review this Python file ONLY for security vulnerabilities:

**File**: {filename}

```python
{code}
```

Focus exclusively on:
- SQL injection
- XSS vulnerabilities
- Hardcoded secrets/credentials
- Unsafe deserialization
- Command injection
- Path traversal

Only report CRITICAL security issues. Ignore code quality.
"""
        try:
            security_result = security_reviewer.run(security_prompt)
            result['stages']['security'] = {
                'status': 'completed',
                'findings': security_result
            }

            # If critical security issues found, stop here
            if 'CRITICAL' in security_result.upper():
                result['stages']['security']['block_merge'] = True
                print(f"   ⚠️  Critical security issues found - stopping review")
                return result

        except Exception as e:
            result['stages']['security'] = {
                'status': 'error',
                'error': str(e)
            }
            return result

        print(f"   Stage 2: Code quality review...")
        quality_prompt = f"""
Review this Python file for code quality:

**File**: {filename}

```python
{code}
```

Focus on:
- PEP 8 compliance
- Code readability
- Maintainability
- Best practices
"""
        try:
            quality_result = code_quality_reviewer.run(quality_prompt)
            result['stages']['code_quality'] = {
                'status': 'completed',
                'findings': quality_result
            }
        except Exception as e:
            result['stages']['code_quality'] = {
                'status': 'error',
                'error': str(e)
            }

        print(f"   Stage 3: Performance review...")
        performance_prompt = f"""
Review this Python file for performance:

**File**: {filename}

```python
{code}
```

Focus on:
- Algorithm complexity
- Database query optimization
- Memory usage
- Caching opportunities
"""
        try:
            performance_result = performance_reviewer.run(performance_prompt)
            result['stages']['performance'] = {
                'status': 'completed',
                'findings': performance_result
            }
        except Exception as e:
            result['stages']['performance'] = {
                'status': 'error',
                'error': str(e)
            }

        return result

    def run(self) -> List[Dict]:
        """Execute the custom review workflow."""

        print(f"\n{'=' * 60}")
        print(f"Custom Review Workflow")
        print(f"Repository: {self.repo}")
        print(f"PR: #{self.pr_number}")
        print(f"{'=' * 60}\n")

        # Fetch PR info
        print("📋 Fetching PR information...")
        try:
            pr_info = fetch_pr_info(self.repo, self.pr_number)
            print(f"   Title: {pr_info['title']}")
            print(f"   Author: {pr_info['user']['login']}")
            print(f"   State: {pr_info['state']}\n")
        except GitHubAPIError as e:
            print(f"❌ Error: {e}")
            return []

        # Fetch files
        print("📁 Fetching changed files...")
        try:
            files = fetch_pr_files(self.repo, self.pr_number)
            print(f"   Total files changed: {len(files)}\n")
        except GitHubAPIError as e:
            print(f"❌ Error: {e}")
            return []

        # Filter files
        print("🔍 Filtering files for review...")
        files_to_review = [
            f for f in files
            if self.should_review_file(f['filename'])
        ]
        print(f"   Files to review: {len(files_to_review)}")
        print(f"   Files skipped: {len(files) - len(files_to_review)}\n")

        if not files_to_review:
            print("ℹ️  No files match review criteria")
            return []

        # Review each file
        print("🚀 Starting multi-stage review...\n")

        for file_info in files_to_review:
            filename = file_info['filename']
            print(f"📄 {filename}")

            # Fetch content
            try:
                code = fetch_file_content(
                    self.repo,
                    filename,
                    ref=pr_info['head']['ref']
                )
            except GitHubAPIError as e:
                print(f"   ❌ Error fetching file: {e}\n")
                self.results.append({
                    'file': filename,
                    'status': 'error',
                    'error': str(e)
                })
                continue

            # Run multi-stage review
            result = self.run_multi_stage_review(filename, code)
            result['status'] = 'completed'
            self.results.append(result)

            print(f"   ✅ Review complete\n")

        return self.results

    def to_json(self, output_file: Optional[str] = None) -> str:
        """Export results as JSON."""
        data = {
            'repo': self.repo,
            'pr_number': self.pr_number,
            'files_reviewed': len(self.results),
            'results': self.results
        }

        json_str = json.dumps(data, indent=2)

        if output_file:
            Path(output_file).write_text(json_str)

        return json_str

    def to_markdown(self) -> str:
        """Export results as markdown report."""
        lines = []

        lines.append(f"# Code Review Report\n\n")
        lines.append(f"**Repository**: {self.repo}\n")
        lines.append(f"**PR**: #{self.pr_number}\n")
        lines.append(f"**Files Reviewed**: {len(self.results)}\n\n")

        lines.append("---\n\n")

        # Summary
        critical_count = 0
        for result in self.results:
            if result.get('status') == 'completed':
                for stage_name, stage_data in result.get('stages', {}).items():
                    if stage_data.get('block_merge'):
                        critical_count += 1

        if critical_count > 0:
            lines.append(f"## ⚠️ Critical Issues Found\n\n")
            lines.append(f"**{critical_count} file(s)** have critical security issues that must be fixed before merge.\n\n")

        lines.append("## Files Reviewed\n\n")

        for result in self.results:
            filename = result['file']
            lines.append(f"### 📄 `{filename}`\n\n")

            if result.get('status') == 'error':
                lines.append(f"❌ **Error**: {result.get('error')}\n\n")
                continue

            stages = result.get('stages', {})

            for stage_name, stage_data in stages.items():
                lines.append(f"#### {stage_name.replace('_', ' ').title()}\n\n")

                if stage_data.get('status') == 'error':
                    lines.append(f"❌ Error: {stage_data.get('error')}\n\n")
                else:
                    if stage_data.get('block_merge'):
                        lines.append("> 🔴 **CRITICAL** - Merge blocked\n\n")

                    lines.append(stage_data.get('findings', ''))
                    lines.append("\n\n")

            lines.append("---\n\n")

        return ''.join(lines)

    def post_to_github(self, as_markdown: bool = True):
        """Post review results to GitHub PR."""
        if as_markdown:
            body = self.to_markdown()
        else:
            body = f"```json\n{self.to_json()}\n```"

        try:
            post_pr_review(self.repo, self.pr_number, body)
            print("✅ Review posted to GitHub")
        except GitHubAPIError as e:
            print(f"❌ Failed to post review: {e}")


def main():
    """Main entry point."""

    if len(sys.argv) < 3:
        print("Usage: python example_custom_workflow.py owner/repo PR_NUMBER [--post] [--json output.json]")
        print("\nExamples:")
        print("  python example_custom_workflow.py facebook/react 12345")
        print("  python example_custom_workflow.py facebook/react 12345 --post")
        print("  python example_custom_workflow.py facebook/react 12345 --json results.json")
        sys.exit(1)

    # Check environment
    if not os.getenv('GITHUB_TOKEN'):
        print("❌ Error: GITHUB_TOKEN not set")
        sys.exit(1)

    if not os.getenv('GOOGLE_API_KEY'):
        print("❌ Error: GOOGLE_API_KEY not set")
        sys.exit(1)

    # Parse arguments
    repo = sys.argv[1]
    pr_number = int(sys.argv[2])
    post_to_github = '--post' in sys.argv
    json_output = None

    if '--json' in sys.argv:
        json_idx = sys.argv.index('--json')
        if json_idx + 1 < len(sys.argv):
            json_output = sys.argv[json_idx + 1]

    # Run workflow
    workflow = CustomReviewWorkflow(repo, pr_number)
    results = workflow.run()

    # Output results
    print("\n" + "=" * 60)
    print("Review Complete")
    print("=" * 60 + "\n")

    print(f"Files reviewed: {len(results)}\n")

    # Export as JSON if requested
    if json_output:
        workflow.to_json(json_output)
        print(f"📄 JSON results saved to: {json_output}\n")

    # Show markdown report
    print("📝 Markdown Report:")
    print("-" * 60)
    print(workflow.to_markdown())
    print("-" * 60)
    print()

    # Post to GitHub if requested
    if post_to_github:
        print("💬 Posting to GitHub...")
        workflow.post_to_github()


if __name__ == '__main__':
    main()
