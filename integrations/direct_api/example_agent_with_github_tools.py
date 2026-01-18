#!/usr/bin/env python3
"""
Advanced example: Create a custom agent with GitHub tools integrated.

This example shows how to create a custom ADK agent that has GitHub tools
available directly, allowing the agent to fetch and review code autonomously.

Usage:
    export GITHUB_TOKEN=your_github_token
    export GOOGLE_API_KEY=your_google_api_key

    python example_agent_with_github_tools.py
"""

import os
import sys


from google.genai import types as genai_types
from google_adk import Agent, AgentTool
from python_codebase_reviewer import root_agent
from python_codebase_reviewer.tools import github_tools


# Create ADK tool wrappers for GitHub API functions
def create_github_tools():
    """
    Create ADK tools from GitHub API functions.

    This wraps our GitHub API functions so they can be used by ADK agents.
    """

    # Tool 1: Fetch PR files
    fetch_pr_files_tool = AgentTool(
        function=github_tools.fetch_pr_files,
        name="fetch_pr_files",
        description=(
            "Fetch list of files changed in a GitHub pull request. "
            "Returns file information including filename, status (added/modified/deleted), "
            "additions, deletions, and changes."
        ),
        parameter_schema=genai_types.GenerateContentConfig.ToolConfig.FunctionCallingConfig.FunctionDeclarations(
            name="fetch_pr_files",
            description="Fetch files changed in a pull request",
            parameters={
                "type": "OBJECT",
                "properties": {
                    "repo": {
                        "type": "STRING",
                        "description": "Repository in format 'owner/repo' (e.g., 'facebook/react')"
                    },
                    "pr_number": {
                        "type": "INTEGER",
                        "description": "Pull request number"
                    }
                },
                "required": ["repo", "pr_number"]
            }
        )
    )

    # Tool 2: Fetch file content
    fetch_file_content_tool = AgentTool(
        function=github_tools.fetch_file_content,
        name="fetch_file_content",
        description=(
            "Fetch content of a file from a GitHub repository at a specific ref (branch, tag, or commit). "
            "Returns the raw file content as a string."
        ),
        parameter_schema=genai_types.GenerateContentConfig.ToolConfig.FunctionCallingConfig.FunctionDeclarations(
            name="fetch_file_content",
            description="Fetch file content from repository",
            parameters={
                "type": "OBJECT",
                "properties": {
                    "repo": {
                        "type": "STRING",
                        "description": "Repository in format 'owner/repo'"
                    },
                    "path": {
                        "type": "STRING",
                        "description": "File path in repository (e.g., 'src/main.py')"
                    },
                    "ref": {
                        "type": "STRING",
                        "description": "Git ref (branch, tag, or commit SHA). Default: 'main'"
                    }
                },
                "required": ["repo", "path"]
            }
        )
    )

    # Tool 3: Fetch PR info
    fetch_pr_info_tool = AgentTool(
        function=github_tools.fetch_pr_info,
        name="fetch_pr_info",
        description=(
            "Fetch detailed information about a GitHub pull request including title, description, "
            "state, author, reviewers, labels, and more."
        ),
        parameter_schema=genai_types.GenerateContentConfig.ToolConfig.FunctionCallingConfig.FunctionDeclarations(
            name="fetch_pr_info",
            description="Fetch pull request information",
            parameters={
                "type": "OBJECT",
                "properties": {
                    "repo": {
                        "type": "STRING",
                        "description": "Repository in format 'owner/repo'"
                    },
                    "pr_number": {
                        "type": "INTEGER",
                        "description": "Pull request number"
                    }
                },
                "required": ["repo", "pr_number"]
            }
        )
    )

    # Tool 4: Post PR review
    post_pr_review_tool = AgentTool(
        function=github_tools.post_pr_review,
        name="post_pr_review",
        description=(
            "Post a code review comment on a GitHub pull request. "
            "Can post general comments or line-specific comments."
        ),
        parameter_schema=genai_types.GenerateContentConfig.ToolConfig.FunctionCallingConfig.FunctionDeclarations(
            name="post_pr_review",
            description="Post a review comment on a pull request",
            parameters={
                "type": "OBJECT",
                "properties": {
                    "repo": {
                        "type": "STRING",
                        "description": "Repository in format 'owner/repo'"
                    },
                    "pr_number": {
                        "type": "INTEGER",
                        "description": "Pull request number"
                    },
                    "body": {
                        "type": "STRING",
                        "description": "Review comment body (supports markdown)"
                    },
                    "event": {
                        "type": "STRING",
                        "description": "Review event type: COMMENT, APPROVE, or REQUEST_CHANGES. Default: COMMENT"
                    }
                },
                "required": ["repo", "pr_number", "body"]
            }
        )
    )

    return [
        fetch_pr_files_tool,
        fetch_file_content_tool,
        fetch_pr_info_tool,
        post_pr_review_tool
    ]


# Create a custom code review agent with GitHub tools
def create_github_code_reviewer():
    """
    Create an autonomous code review agent with GitHub access.

    This agent can:
    - Fetch PR information from GitHub
    - Retrieve file contents
    - Review code using sub-agents
    - Post results back to GitHub
    """

    github_tools_list = create_github_tools()

    # Wrap the Python Codebase Reviewer as a tool
    review_tool = AgentTool(
        agent=root_agent,
        name="python_code_reviewer",
        description=(
            "Comprehensive Python code review agent with specialized reviewers for "
            "security, architecture, code quality, performance, and Python best practices. "
            "Use this to review Python code and get detailed findings."
        )
    )

    # Create agent with both GitHub tools and review tool
    agent = Agent(
        model="gemini-2.0-flash-exp",
        name="github_code_reviewer",
        description="Autonomous code review agent with GitHub integration",
        instruction="""
You are an autonomous GitHub code review agent.

Your capabilities:
1. Fetch PR information from GitHub (fetch_pr_info)
2. List files changed in a PR (fetch_pr_files)
3. Retrieve file contents (fetch_file_content)
4. Review Python code using specialized reviewers (python_code_reviewer)
5. Post review results to GitHub (post_pr_review)

Workflow:
1. When given a repository and PR number, fetch the PR info
2. List changed files and filter for Python files
3. For each Python file:
   - Fetch the file content
   - Use python_code_reviewer to analyze it
4. Aggregate results into a comprehensive review
5. Optionally post the review as a PR comment

Be thorough but concise. Focus on actionable findings.
""",
        tools=[*github_tools_list, review_tool]
    )

    return agent


def main():
    """Demonstrate the autonomous GitHub code review agent."""

    # Check environment
    if not os.getenv('GITHUB_TOKEN'):
        print("❌ Error: GITHUB_TOKEN environment variable not set")
        sys.exit(1)

    if not os.getenv('GOOGLE_API_KEY'):
        print("❌ Error: GOOGLE_API_KEY environment variable not set")
        sys.exit(1)

    # Create agent
    print("🤖 Creating autonomous code review agent...\n")
    agent = create_github_code_reviewer()

    # Example usage
    print("=" * 60)
    print("Example: Review a PR autonomously")
    print("=" * 60)
    print()

    # The agent can now understand natural language requests
    # and use its tools autonomously to complete the task

    request = """
Please review pull request #123 in the repository 'owner/repo'.

Focus on:
- Security vulnerabilities
- Code quality issues
- Performance problems

After reviewing, provide a summary but DO NOT post to GitHub
(just show me what you would post).
"""

    print("Request to agent:")
    print(request)
    print()

    print("Agent response:")
    print("-" * 60)

    try:
        # The agent will autonomously:
        # 1. Call fetch_pr_info to get PR details
        # 2. Call fetch_pr_files to list changed files
        # 3. Call fetch_file_content for each Python file
        # 4. Call python_code_reviewer to analyze each file
        # 5. Aggregate results and respond

        response = agent.run(request)
        print(response)

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

    print("-" * 60)
    print()

    # Example 2: More complex request
    print("\n" + "=" * 60)
    print("Example 2: Review and post (if you uncomment)")
    print("=" * 60)
    print()

    advanced_request = """
Review PR #123 in 'owner/repo' focusing on:
1. SQL injection vulnerabilities
2. Hardcoded secrets
3. Performance issues in database queries

Then post a review comment with:
- A summary of critical issues at the top
- Detailed findings grouped by severity
- Specific line references where possible
"""

    print("Advanced request:")
    print(advanced_request)
    print()
    print("(To actually post to GitHub, the agent would call post_pr_review)")
    print()


if __name__ == '__main__':
    main()
