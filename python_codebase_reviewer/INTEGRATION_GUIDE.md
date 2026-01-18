# GitHub Integration Guide - Python Codebase Reviewer

Complete guide to integrating Python Codebase Reviewer with GitHub.

---

## Overview

The Python Codebase Reviewer can be integrated with GitHub in four different ways, each optimized for different use cases:

| Option | Name | Best For | Setup Time | Automation |
|--------|------|----------|------------|------------|
| **1** | GitHub Actions | Teams using CI/CD | 5 min | ✅ Automatic |
| **2** | GitHub App | Organizations | 30 min | ✅ Automatic |
| **3** | GitHub CLI | Individual developers | 10 min | ❌ Manual |
| **4** | Direct API | Custom integrations | Varies | ⚙️ Custom |

---

## Quick Decision Guide

### Choose Option 1 (GitHub Actions) if:
- ✅ You already use GitHub Actions for CI/CD
- ✅ You want automatic PR reviews
- ✅ You have public repos or GitHub Actions minutes available
- ✅ You want minimal setup and maintenance
- ✅ You're comfortable with YAML workflows

**Pros**:
- Very quick setup (5 minutes)
- No infrastructure to manage
- Free for public repos
- Familiar to teams already using Actions
- Easy to customize per repository

**Cons**:
- Limited by GitHub Actions minutes (2,000/month free for private repos)
- Less suitable for high-volume organizations
- Each repository needs the workflow file

**→ Go to**: `github_actions/` directory

---

### Choose Option 2 (GitHub App) if:
- ✅ You need organization-wide deployment
- ✅ You want highest scalability
- ✅ You have budget for Cloud Run hosting (~$5-20/month)
- ✅ You want centralized management and configuration
- ✅ You prefer a hosted service model

**Pros**:
- Install once, works across all repositories
- Auto-scales to handle any load
- Professional webhook delivery
- Centralized configuration
- Works for entire GitHub organization

**Cons**:
- Longer setup (30 minutes)
- Requires Google Cloud account
- Monthly hosting costs
- More complex architecture

**→ Go to**: `github_app/` directory

---

### Choose Option 3 (GitHub CLI) if:
- ✅ You want manual, on-demand reviews
- ✅ You're an individual developer or small team
- ✅ You want to review before committing/pushing
- ✅ You don't want to set up CI/CD infrastructure
- ✅ You want full control over when reviews run

**Pros**:
- Complete control over execution
- No infrastructure needed
- Works offline (after fetching code)
- Great for pre-commit reviews
- Fast iteration during development

**Cons**:
- Manual execution required
- Not suitable for team-wide automation
- Each developer sets up independently

**→ Go to**: `github_cli/` directory

---

### Choose Option 4 (Direct API) if:
- ✅ You have unique integration requirements
- ✅ You want full control over the workflow
- ✅ You're building a custom platform
- ✅ You need to integrate with other tools
- ✅ Standard options don't fit your needs

**Pros**:
- Maximum flexibility
- Integrate with any system
- Custom workflow logic
- Combine with other tools easily
- No constraints

**Cons**:
- Requires programming
- You build and maintain everything
- Longer development time
- Need to handle errors, retries, etc.

**→ Go to**: `direct_api/` directory

---

## Detailed Comparison

### Setup & Deployment

| Aspect | Option 1 (Actions) | Option 2 (App) | Option 3 (CLI) | Option 4 (API) |
|--------|-------------------|----------------|----------------|----------------|
| **Setup time** | 5 minutes | 30 minutes | 10 minutes | Varies |
| **Technical difficulty** | Beginner | Intermediate | Beginner | Advanced |
| **Prerequisites** | GitHub repo | Google Cloud account, GitHub org | gh CLI, Python | Python, programming |
| **Infrastructure** | None (GitHub-hosted) | Cloud Run service | Local machine | Custom |
| **Deployment** | Add workflow file | Deploy to Cloud Run | Install CLI + scripts | Build your own |

### Cost & Performance

| Aspect | Option 1 (Actions) | Option 2 (App) | Option 3 (CLI) | Option 4 (API) |
|--------|-------------------|----------------|----------------|----------------|
| **GitHub Actions** | 2,000 min/month free | Not used | Not used | Not used |
| **Cloud hosting** | $0 | ~$5-20/month | $0 | Varies |
| **API costs** | Google AI API | Google AI API | Google AI API | Google AI API |
| **Scalability** | Medium (2K mins) | High (auto-scale) | Low (manual) | Custom |
| **Concurrency** | 20 jobs (default) | Unlimited | 1 | Custom |

**Note**: Google AI API is currently FREE during preview (gemini-2.0 models)

### Automation & Workflow

| Aspect | Option 1 (Actions) | Option 2 (App) | Option 3 (CLI) | Option 4 (API) |
|--------|-------------------|----------------|----------------|----------------|
| **Trigger** | PR events | Webhook events | Manual command | Custom |
| **Automatic reviews** | ✅ Yes | ✅ Yes | ❌ No | ⚙️ Custom |
| **Real-time feedback** | ~2-5 minutes | ~1-3 minutes | Immediate | Custom |
| **Batch reviews** | Via workflow_dispatch | Not ideal | ✅ Easy | ✅ Easy |
| **Scheduled reviews** | ✅ Yes (cron) | Requires custom code | ✅ Easy (cron) | ✅ Easy |

### Features & Flexibility

| Aspect | Option 1 (Actions) | Option 2 (App) | Option 3 (CLI) | Option 4 (API) |
|--------|-------------------|----------------|----------------|----------------|
| **Review PR on open** | ✅ | ✅ | ❌ (manual) | ⚙️ Custom |
| **Review on update** | ✅ | ✅ | ❌ (manual) | ⚙️ Custom |
| **Review specific files** | ✅ (filter) | Limited | ✅ | ✅ |
| **Custom filtering** | YAML config | Python code | Python code | ✅ Full control |
| **Multi-stage review** | Sequential steps | Custom code | Easy | ✅ Full control |
| **Line comments** | Limited | ✅ | ✅ | ✅ |
| **Block merge** | ✅ (status check) | ✅ (review status) | Manual | Custom |

### Management & Maintenance

| Aspect | Option 1 (Actions) | Option 2 (App) | Option 3 (CLI) | Option 4 (API) |
|--------|-------------------|----------------|----------------|----------------|
| **Centralized config** | ❌ Per-repo | ✅ One place | ❌ Per-developer | Custom |
| **Update process** | Edit workflow file | Redeploy service | Update scripts | Custom |
| **Monitoring** | Actions tab | Cloud Run logs | Local | Custom |
| **Error handling** | Workflow retry | Service auto-restart | Manual | Custom |
| **Secrets management** | GitHub Secrets | Google Secret Manager | Environment vars | Custom |

---

## Use Case Examples

### Small Team (2-5 developers)

**Recommendation**: Option 1 (GitHub Actions) or Option 3 (GitHub CLI)

**Rationale**:
- Quick setup, no infrastructure
- Free or low cost
- Simple maintenance
- Each developer can use CLI for pre-commit reviews
- Actions for automated PR reviews

**Setup**:
```bash
# Team lead sets up Actions (5 min)
# Copy workflow file to repository
# Add GOOGLE_API_KEY secret

# Each developer sets up CLI (10 min)
# Install gh CLI
# Export GOOGLE_API_KEY
# Review before pushing
```

---

### Medium Organization (10-50 developers, multiple teams)

**Recommendation**: Option 2 (GitHub App)

**Rationale**:
- Install once, works everywhere
- Centralized configuration
- Professional appearance
- Scales with growth
- Easy to manage

**Setup**:
```bash
# DevOps team deploys App (30 min)
# Create GitHub App
# Deploy to Cloud Run
# Install on organization

# Developers: nothing to do!
# Reviews happen automatically
```

---

### Large Enterprise (100+ developers)

**Recommendation**: Option 2 (GitHub App) + Option 4 (Direct API)

**Rationale**:
- GitHub App for standard PR reviews
- Direct API for custom workflows (e.g., pre-release checks, compliance, etc.)
- Integrate with existing tools (JIRA, Slack, etc.)
- Custom analytics and reporting

**Setup**:
```bash
# Infrastructure team:
# - Deploy GitHub App for PR reviews
# - Build custom integrations with Direct API
# - Integrate with company dashboard
# - Set up monitoring and alerts
```

---

### Open Source Project

**Recommendation**: Option 1 (GitHub Actions)

**Rationale**:
- Free for public repos
- Familiar to contributors
- No infrastructure to manage
- Transparent (workflow in repo)

**Setup**:
```yaml
# .github/workflows/code-review.yml
# Runs on every PR
# Posts review comments
# Contributors see results immediately
```

---

### Individual Developer / Freelancer

**Recommendation**: Option 3 (GitHub CLI)

**Rationale**:
- Full control
- Review before pushing
- No setup on GitHub
- Works offline
- Zero cost

**Setup**:
```bash
# One-time setup (10 min)
gh auth login
export GOOGLE_API_KEY=your_key

# Daily usage
python review_pr.py 123
# or
git diff --staged | xargs python review_files.py
```

---

### Custom Platform / SaaS

**Recommendation**: Option 4 (Direct API)

**Rationale**:
- Integrate into your product
- Custom UX and branding
- Combine with your features
- Full control over workflow

**Example**:
```python
# Your platform's code
def on_pr_created(pr_id):
    # Review using Python Codebase Reviewer
    results = review_pr(pr_id)

    # Store in your database
    db.reviews.insert(results)

    # Notify via your system
    send_notification(pr_id, results)

    # Show in your UI
    return render_review_page(results)
```

---

## Migration Paths

### From Option 3 (CLI) to Option 1 (Actions)

**Why**: Team wants automation

**Steps**:
1. Copy `github_actions/code-review.yml` to `.github/workflows/`
2. Add `GOOGLE_API_KEY` to repository secrets
3. Team continues using CLI for pre-commit reviews
4. Actions runs automatically on PRs

**Time**: 5 minutes

---

### From Option 1 (Actions) to Option 2 (App)

**Why**: Organization-wide deployment needed

**Steps**:
1. Follow `github_app/SETUP.md`
2. Deploy GitHub App to Cloud Run
3. Install App on organization
4. Remove Actions workflows (optional - can keep both)

**Time**: 30 minutes

---

### From Option 2 (App) to Option 4 (API)

**Why**: Need custom workflows

**Steps**:
1. Keep GitHub App running for standard reviews
2. Add custom workflows using `direct_api/` patterns
3. Use same backend agents
4. Custom workflows handle special cases

**Time**: Varies (can co-exist)

---

## Combining Options

You can use multiple options together:

### Option 1 + Option 3
- **Actions**: Automatic PR reviews
- **CLI**: Pre-commit reviews by developers

**Benefit**: Double coverage

### Option 2 + Option 4
- **App**: Standard PR reviews
- **API**: Custom workflows (pre-release checks, compliance scans, etc.)

**Benefit**: Best of both worlds

### Option 1 + Option 2
- **Actions**: For specific high-priority repositories
- **App**: For rest of organization

**Benefit**: Different levels of scrutiny

---

## Getting Started

### Step 1: Choose Your Option

Use the decision guide above.

### Step 2: Follow Setup Guide

Each option has detailed documentation:
- **Option 1**: `github_actions/SETUP.md`
- **Option 2**: `github_app/SETUP.md`
- **Option 3**: `github_cli/SETUP.md`
- **Option 4**: `direct_api/SETUP.md`

### Step 3: Customize (Optional)

All options can be customized:
- Review prompts (focus areas)
- File filters (which files to review)
- Output format (markdown style)
- Severity thresholds (when to block)

### Step 4: Test

All options include test instructions:
- Create test PR with security issues
- Verify review is generated
- Check results meet your needs

### Step 5: Deploy

Production deployment varies by option:
- **Option 1**: Commit workflow file
- **Option 2**: Deploy to Cloud Run
- **Option 3**: Distribute to team
- **Option 4**: Deploy your custom code

---

## Support & Resources

### Documentation
- **Option 1**: `github_actions/README.md`
- **Option 2**: `github_app/README.md`
- **Option 3**: `github_cli/README.md`
- **Option 4**: `direct_api/README.md`

### Examples
- All options include working examples
- Test on public repositories first
- See `eval/` directory for test cases

### Troubleshooting
- Each README has troubleshooting section
- Common issues and solutions
- Debug commands and logs

---

## FAQ

### Q: Can I change options later?

**A**: Yes! See "Migration Paths" above. You can also run multiple options simultaneously.

---

### Q: What if I want to review non-Python code?

**A**: The agents are optimized for Python. For other languages, you can:
1. Modify prompts in `prompt.py` files
2. Create new specialized agents
3. Use general code review prompts

---

### Q: How much does this cost?

**A**: Breakdown:
- **GitHub API**: Free
- **Google AI API**: Currently FREE (gemini-2.0 during preview)
- **Cloud Run** (Option 2 only): ~$5-20/month depending on usage
- **GitHub Actions** (Option 1): 2,000 minutes/month free, then $0.008/minute

**Most users**: $0-5/month during preview

---

### Q: Is my code sent to Google?

**A**: Yes, code is sent to Google AI API for analysis (similar to GitHub Copilot, Tabnine, etc.).

**Mitigation**:
- Review Google AI Terms of Service
- Use only on approved repositories
- Avoid reviewing files with secrets
- Consider self-hosted AI models (requires custom integration)

---

### Q: Can I use a different AI model?

**A**: Yes! The agent system uses Google ADK which supports multiple models:
- `gemini-2.0-pro-exp` (highest quality)
- `gemini-2.0-flash-exp` (fast, default)
- Other Gemini models

Edit `constants.py` to change models.

---

### Q: How accurate are the reviews?

**A**: Based on evaluation suite:
- **Precision**: ~90% (few false positives)
- **Recall**: ~85% (catches most real issues)
- **F1 Score**: ~0.87

See `eval/` directory for details.

---

### Q: Can I customize what gets reviewed?

**A**: Yes! All options support:
- File filtering (by path, pattern, extension)
- Focus areas (security only, performance only, etc.)
- Severity thresholds
- Custom prompts

---

### Q: Does this replace human code review?

**A**: No! This is a tool to augment human review:
- AI catches common issues (security, patterns)
- Humans focus on business logic, architecture
- Best results: AI + human review

---

## Next Steps

1. **Choose your option** using the decision guide above
2. **Read the setup guide** for your chosen option
3. **Test on a sample repository** before production use
4. **Customize** to fit your team's needs
5. **Deploy** and start reviewing!

---

**Questions?** Check the README.md in each option's directory for detailed documentation.

**Ready to get started?** Pick your option and dive in! 🚀
