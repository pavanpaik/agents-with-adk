# GitHub Integration Options

**Reference implementations for integrating Python Codebase Reviewer with GitHub.**

These are **example implementations** that you can copy, customize, and deploy. They are not installed with the core package - instead, they serve as templates and starting points for your own integration.

---

## 📊 Quick Comparison

| Option | Type | Setup | Automation | Best For |
|--------|------|-------|------------|----------|
| **[1. GitHub Actions](#option-1-github-actions)** | CI/CD Workflow | 5 min | ✅ Automatic | Teams with GitHub Actions |
| **[2. GitHub App](#option-2-github-app)** | Cloud Service | 30 min | ✅ Automatic | Organizations |
| **[3. GitHub CLI](#option-3-github-cli)** | Local Scripts | 10 min | ❌ Manual | Individual Developers |
| **[4. Direct API](#option-4-direct-api)** | Custom Code | Varies | ⚙️ Custom | Unique Requirements |

---

## 🎯 Option 1: GitHub Actions

**CI/CD integration for automatic PR reviews**

### What It Is
A GitHub Actions workflow that runs on every pull request, reviews changed Python files, and posts results as PR comments.

### When to Use
- ✅ You already use GitHub Actions for CI/CD
- ✅ You want automatic reviews on every PR
- ✅ You have GitHub Actions minutes available (free for public repos)
- ✅ You want minimal setup and maintenance

### Files Included
```
github_actions/
├── README.md              # Complete documentation
├── SETUP.md               # Step-by-step setup guide
├── code-review.yml        # GitHub Actions workflow
└── review_pr.py           # Review script
```

### Quick Start
```bash
# 1. Copy workflow to your repository
cp github_actions/code-review.yml YOUR_REPO/.github/workflows/

# 2. Add GOOGLE_API_KEY secret in GitHub repo settings

# 3. Create a PR with Python changes - automatic review!
```

### Cost
- Free tier: 2,000 minutes/month for private repos
- Public repos: Unlimited
- Google AI API: Free during preview

**→ Full docs**: [`github_actions/README.md`](github_actions/README.md)

---

## 🏢 Option 2: GitHub App

**Organization-wide deployment as a GitHub App on Cloud Run**

### What It Is
A production-ready GitHub App that receives webhooks from GitHub, reviews PRs automatically, and posts detailed comments. Deployed on Google Cloud Run with auto-scaling.

### When to Use
- ✅ You need organization-wide deployment
- ✅ You want centralized configuration
- ✅ You have budget for Cloud Run (~$5-20/month)
- ✅ You want professional, scalable solution

### Files Included
```
github_app/
├── README.md              # Complete documentation
├── SETUP.md               # Step-by-step deployment guide
├── webhook_handler.py     # Flask app for webhook handling
├── Dockerfile             # Container configuration
├── deploy.sh              # Deployment script
├── setup_secrets.sh       # Secrets setup helper
├── run_local.sh           # Local testing
└── test_webhook.sh        # Webhook testing
```

### Quick Start
```bash
# 1. Create GitHub App (see SETUP.md)
# 2. Deploy to Cloud Run
cd github_app
./deploy.sh

# 3. Install app on your organization
# 4. Automatic reviews on all repositories!
```

### Cost
- Cloud Run: ~$5-20/month (with auto-scaling)
- Google AI API: Free during preview

**→ Full docs**: [`github_app/README.md`](github_app/README.md)

---

## 💻 Option 3: GitHub CLI

**Local development tools for manual, on-demand reviews**

### What It Is
Python scripts that use the `gh` CLI to review PRs locally. Perfect for pre-commit reviews and individual developer workflows.

### When to Use
- ✅ You want manual control over when reviews run
- ✅ You're an individual developer or small team
- ✅ You want to review before committing/pushing
- ✅ You don't need CI/CD infrastructure

### Files Included
```
github_cli/
├── README.md              # Complete documentation
├── SETUP.md               # Quick setup guide
├── review_pr.py           # Review PRs via gh CLI
└── review_files.py        # Review files directly
```

### Quick Start
```bash
# 1. Install gh CLI
brew install gh  # macOS
# or: https://cli.github.com/

# 2. Authenticate
gh auth login

# 3. Review a PR
cd github_cli
python review_pr.py 123

# 4. Review local files
python review_files.py src/main.py
```

### Cost
- Free (just API costs)

**→ Full docs**: [`github_cli/README.md`](github_cli/README.md)

---

## 🔧 Option 4: Direct API

**Custom integrations using the GitHub API directly**

### What It Is
Python examples showing how to use the core package with GitHub API tools to build custom workflows. Maximum flexibility for unique requirements.

### When to Use
- ✅ You have unique integration requirements
- ✅ You want full control over the workflow
- ✅ You're building a custom platform
- ✅ Standard options don't fit your needs

### Files Included
```
direct_api/
├── README.md                           # Complete guide
├── SETUP.md                            # Setup instructions
├── example_simple_review.py            # Basic PR review
├── example_agent_with_github_tools.py  # Autonomous agent
└── example_custom_workflow.py          # Multi-stage review
```

### Quick Start
```python
from python_codebase_reviewer import root_agent
from python_codebase_reviewer.tools.github_tools import fetch_pr_files

# Fetch PR files
files = fetch_pr_files("owner/repo", 123)

# Review
for file in files:
    review = root_agent.run(f"Review: {file['content']}")
    print(review)
```

### Use Cases
- Custom webhook handlers
- Scheduled batch reviews
- Pre-merge gates
- Integration with other tools
- Database storage of reviews

### Cost
- Varies (you control infrastructure)

**→ Full docs**: [`direct_api/README.md`](direct_api/README.md)

---

## 🤔 Which Option Should I Choose?

### Decision Tree

```
Start here
    │
    ├─ Do you need automatic reviews?
    │   ├─ Yes, for entire organization
    │   │   └─→ Option 2: GitHub App
    │   │
    │   └─ Yes, for specific repos
    │       └─→ Option 1: GitHub Actions
    │
    └─ Do you prefer manual control?
        ├─ Yes, local development
        │   └─→ Option 3: GitHub CLI
        │
        └─ Need custom workflow
            └─→ Option 4: Direct API
```

### By Team Size

- **Individual/Freelancer**: Option 3 (GitHub CLI)
- **Small Team (2-5 devs)**: Option 1 (GitHub Actions)
- **Medium Team (5-20 devs)**: Option 1 or 2
- **Organization (20+ devs)**: Option 2 (GitHub App)
- **Enterprise**: Option 2 + Option 4 (custom workflows)

### By Use Case

- **CI/CD automation**: Option 1 (GitHub Actions)
- **Organization-wide**: Option 2 (GitHub App)
- **Pre-commit reviews**: Option 3 (GitHub CLI)
- **Custom platform**: Option 4 (Direct API)
- **Experimentation**: Option 3 or 4

---

## 📚 Complete Decision Guide

See [`INTEGRATION_GUIDE.md`](INTEGRATION_GUIDE.md) for:
- Detailed comparison tables
- Cost analysis
- Performance benchmarks
- Migration paths between options
- Combining multiple options
- FAQ

---

## 🚀 Getting Started

1. **Choose your option** using the decision tree above
2. **Read the README** in that option's directory
3. **Follow the SETUP guide** for step-by-step instructions
4. **Test on a sample repository** before production use
5. **Customize** to fit your team's needs

---

## 💡 Tips

### Combining Options

You can use multiple options together:

- **Actions + CLI**: Auto-review PRs + manual pre-commit reviews
- **App + API**: Organization-wide + custom workflows
- **CLI + API**: Local development + custom scripts

### Starting Small

1. Start with Option 3 (CLI) to understand the system
2. Move to Option 1 (Actions) when ready for automation
3. Upgrade to Option 2 (App) for organization-wide deployment
4. Add Option 4 (API) for custom requirements

### Migration

All options use the same core package, so migrating is easy:
- Keep using the same agents
- Just change how you trigger reviews
- No lock-in to any option

---

## 🤝 Contributing

Have a new integration idea? Contributions are welcome!

1. Create a new directory for your integration
2. Include README.md and SETUP.md
3. Provide working examples
4. Document use cases and benefits
5. Submit a pull request

**Ideas for new integrations**:
- GitLab integration
- Bitbucket integration
- Azure DevOps integration
- Slack bot integration
- VS Code extension
- Pre-commit hooks
- Gerrit integration

---

## 📧 Support

- **Questions**: Open an issue or discussion
- **Bugs**: Report in GitHub Issues
- **Feature requests**: Start a discussion

---

## 📖 Related Documentation

- **[Core Package Documentation](../docs/)**: Agent architecture and API
- **[Testing Guide](../tests/README.md)**: How to run tests
- **[Evaluation Suite](../evals/README.md)**: Agent quality metrics
- **[Examples](../examples/)**: Simple usage examples

---

**Ready to integrate?** Choose your option and get started! 🚀
