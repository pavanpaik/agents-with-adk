# Migration to GitHub MCP Tools

This project has been migrated from custom GitHub API tools to the official **GitHub MCP (Model Context Protocol) server**.

## What Changed?

### Before (Custom Tools)
- 550 lines of custom `github_tools.py`
- Manual HTTP requests with retry logic
- 7 custom GitHub operations
- Scripts manually orchestrated file fetching

### After (GitHub MCP)
- GitHub's official MCP server with 51+ tools
- Standardized MCP protocol
- Agent autonomously uses MCP tools
- Simpler, more maintainable code

## Updated Files

### ✅ Core Agent
- **`src/python_codebase_reviewer/agent.py`**: Now includes `github_mcp_toolset`

### ✅ Updated Integration Scripts
- **`integrations/github_actions/review_pr.py`**: Agent-driven with MCP
- **`integrations/direct_api/example_simple_review.py`**: MCP-based simple example

### ⚠️ Legacy Scripts (Need Manual Update)
The following scripts still use old custom tools and need updating:
- `integrations/direct_api/example_agent_with_github_tools.py`
- `integrations/direct_api/example_custom_workflow.py`
- `integrations/github_app/webhook_handler.py`
- `integrations/github_cli/review_pr.py`

**To update these scripts:**
1. Remove imports of custom `github_tools`
2. Instead of calling GitHub functions directly, ask the agent to use MCP tools
3. See `example_simple_review.py` for reference

## How MCP Works

Instead of this (old way):
```python
from python_codebase_reviewer.tools.github_tools import fetch_pr_files, fetch_file_content

# Manual orchestration
files = fetch_pr_files(repo, pr_number)
for file in files:
    content = fetch_file_content(repo, file['filename'])
    review = root_agent.run(f"Review: {content}")
```

Do this (new way):
```python
from python_codebase_reviewer import root_agent

# Agent uses MCP tools autonomously
review = root_agent.run(f"""
Review PR #{pr_number} in {repo}.
Use get_pull_request_files to list files.
Use get_file_contents to fetch each file.
Analyze and provide a comprehensive review.
""")
```

## Available GitHub MCP Tools

The agent now has access to 51+ GitHub tools including:

**Pull Requests:**
- `get_pull_request_files` - List files changed in a PR
- `get_pull_request` - Get PR details
- `get_pull_request_diff` - Get full diff
- `create_pull_request_review` - Post a review
- `create_issue_comment` - Post a comment

**Files & Content:**
- `get_file_contents` - Fetch file content
- `search_code` - Search repository code
- `push_files` - Push changes to a branch

**Actions & Security:**
- `list_workflow_runs` - List GitHub Actions runs
- `get_code_scanning_alerts` - Get security alerts
- `list_secret_scanning_alerts` - List secret alerts

**And 40+ more...**

## Environment Variables

No changes needed:
- `GITHUB_TOKEN` - Still used (passed to MCP server as `GITHUB_PERSONAL_ACCESS_TOKEN`)
- `GOOGLE_API_KEY` - Still required for Gemini models

## Dependencies

Updated in `pyproject.toml`:
```toml
dependencies = [
    "google-adk[mcp]>=1.0.0",  # Was: google-adk>=0.1.0
    "mcp>=1.0.0",              # New MCP SDK
    # Removed: "requests>=2.31.0"
]
```

Install MCP server:
```bash
npm install -g @modelcontextprotocol/server-github
```

## Testing

Test that MCP integration works:
```bash
export GITHUB_TOKEN=ghp_xxx
export GOOGLE_API_KEY=AIza_xxx

python integrations/direct_api/example_simple_review.py owner/repo 123
```

## Benefits

1. **Less code**: 316 lines → 110 lines (65% reduction in review_pr.py)
2. **More features**: 7 tools → 51+ tools
3. **Maintained by GitHub**: Automatic updates and bug fixes
4. **Standardized**: Industry-standard MCP protocol
5. **Autonomous agents**: Agent decides which tools to use

## Rollback (If Needed)

Custom tools are preserved in git history. To rollback:
```bash
git checkout <commit-before-mcp> -- src/python_codebase_reviewer/tools/github_tools.py
```

However, you'll need to also revert:
- `agent.py` (remove MCP toolset)
- `pyproject.toml` (revert dependencies)
- All integration scripts

## Questions?

See the main README or check:
- [GitHub MCP Server Docs](https://github.com/github/github-mcp-server)
- [Google ADK MCP Integration](https://google.github.io/adk-docs/mcp/)
