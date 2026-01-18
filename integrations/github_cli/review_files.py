#!/usr/bin/env python3
"""
Review specific Python files directly (without PR context).

Useful for:
- Pre-commit reviews
- Local development
- Reviewing uncommitted changes

Usage:
    # Review specific files
    python review_files.py src/main.py src/utils.py

    # Review all Python files in directory
    python review_files.py src/**/*.py

    # Review git staged files
    git diff --cached --name-only --diff-filter=ACM | grep '.py$' | xargs python review_files.py

    # Save output to file
    python review_files.py src/main.py --output review.md
"""

import os
import sys
import argparse
from pathlib import Path
from typing import List, Dict

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from python_codebase_reviewer import root_agent
except ImportError as e:
    print(f"❌ Error importing Python Codebase Reviewer: {e}")
    print("   Install: pip install google-adk")
    sys.exit(1)


def review_file(file_path: Path) -> Dict:
    """
    Review a single Python file.

    Args:
        file_path: Path to file

    Returns:
        Review result dictionary
    """
    try:
        code = file_path.read_text()
    except Exception as e:
        return {
            'file': str(file_path),
            'review': f"Error reading file: {e}",
            'status': 'error'
        }

    review_request = f"""
Review this Python file:

**File**: `{file_path}`
**Size**: {len(code)} characters

```python
{code}
```

Provide comprehensive review covering:
- Security vulnerabilities (OWASP Top 10)
- Architecture and design (SOLID principles)
- Code quality (PEP 8, Pythonic idioms)
- Performance (algorithm complexity, N+1 queries)
- Python best practices

Focus on actionable findings with severity levels and code fixes.
"""

    try:
        print(f"  🤖 Running AI review...")
        response = root_agent.run(review_request)

        return {
            'file': str(file_path),
            'review': response,
            'status': 'success'
        }

    except Exception as e:
        return {
            'file': str(file_path),
            'review': f"Error during review: {e}",
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


def format_markdown(results: List[Dict]) -> str:
    """Format review results as markdown."""
    output = []

    # Header
    output.append("# 🔍 Python Code Review Results\n\n")
    output.append(f"**Files Reviewed**: {len(results)}\n")
    output.append("\n---\n\n")

    # Summary
    total_counts = {'critical': 0, 'high': 0, 'medium': 0, 'low': 0}
    for result in results:
        if result['status'] == 'success':
            counts = count_findings(result['review'])
            for severity, count in counts.items():
                total_counts[severity] += count

    output.append("## 📊 Summary\n\n")

    if sum(total_counts.values()) == 0:
        output.append("✅ **No issues found!** All code looks good.\n\n")
    else:
        if total_counts['critical'] > 0:
            output.append(f"- 🔴 **{total_counts['critical']} Critical**\n")
        if total_counts['high'] > 0:
            output.append(f"- 🟠 **{total_counts['high']} High**\n")
        if total_counts['medium'] > 0:
            output.append(f"- 🟡 **{total_counts['medium']} Medium**\n")
        if total_counts['low'] > 0:
            output.append(f"- 🔵 **{total_counts['low']} Low**\n")
        output.append("\n")

        if total_counts['critical'] > 0:
            output.append("> ⚠️ **Warning**: Critical issues detected!\n\n")

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
                output.append(f"**Found {total} issue(s)**\n\n")
                output.append(result['review'])
                output.append("\n\n")

        output.append("---\n\n")

    # Footer
    output.append("## 🤖 Powered by Python Codebase Reviewer\n")

    return ''.join(output)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Review Python files using AI',
        epilog='Examples:\n'
               '  python review_files.py src/main.py\n'
               '  python review_files.py src/*.py\n'
               '  git diff --cached --name-only | grep .py | xargs python review_files.py\n',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        'files',
        nargs='+',
        help='Python files to review'
    )
    parser.add_argument(
        '--output', '-o',
        help='Output file for results (default: print to console)'
    )

    args = parser.parse_args()

    # Check prerequisites
    if not os.getenv('GOOGLE_API_KEY'):
        print("❌ Error: GOOGLE_API_KEY environment variable not set")
        print("   Get key from: https://aistudio.google.com/app/apikey")
        sys.exit(1)

    # Convert to Path objects and filter Python files
    file_paths = [Path(f) for f in args.files if f.endswith('.py')]

    if not file_paths:
        print("ℹ️  No Python files to review")
        sys.exit(0)

    # Print header
    print("\n" + "=" * 60)
    print("Python Codebase Reviewer")
    print("=" * 60 + "\n")
    print(f"Files to review: {len(file_paths)}\n")

    # Review files
    results = []
    for file_path in file_paths:
        print(f"📄 Reviewing: {file_path}")

        if not file_path.exists():
            print(f"  ⚠️  File not found, skipping")
            results.append({
                'file': str(file_path),
                'review': 'Error: File not found',
                'status': 'error'
            })
            continue

        result = review_file(file_path)
        results.append(result)

        if result['status'] == 'success':
            counts = count_findings(result['review'])
            total = sum(counts.values())
            print(f"  ✅ Found {total} issue(s)")
        else:
            print(f"  ❌ Review failed")

        print()

    # Format results
    markdown = format_markdown(results)

    # Output
    if args.output:
        output_path = Path(args.output)
        output_path.write_text(markdown)
        print(f"✅ Results saved to: {output_path}\n")
    else:
        print("\n" + "=" * 60)
        print("REVIEW RESULTS")
        print("=" * 60 + "\n")
        print(markdown)

    # Exit with error if critical issues found
    total_critical = sum(
        count_findings(r['review'])['critical']
        for r in results if r['status'] == 'success'
    )

    if total_critical > 0:
        sys.exit(1)


if __name__ == '__main__':
    main()
