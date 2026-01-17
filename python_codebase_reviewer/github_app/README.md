# Python Codebase Reviewer - GitHub App

Production-ready GitHub App for automated Python code reviews across your organization.

## Architecture

```
┌─────────────┐
│   GitHub    │
│             │
│  PR opened  │───┐
└─────────────┘   │
                  │ Webhook
                  ▼
         ┌────────────────┐
         │  Cloud Run     │
         │  Flask App     │
         └───────┬────────┘
                 │
                 ├─ Verify webhook signature
                 ├─ Get installation token
                 ├─ Fetch PR files
                 ├─ Run code review
                 │  └─ Python Codebase Reviewer
                 │     ├─ Security Reviewer
                 │     ├─ Architecture Reviewer
                 │     ├─ Code Quality Reviewer
                 │     ├─ Performance Reviewer
                 │     └─ Python Expert
                 └─ Post review comment
                    │
                    ▼
         ┌─────────────┐
         │   GitHub    │
         │             │
         │  PR Comment │
         └─────────────┘
```

## Features

✅ **Organization-Wide**: Install once, works on all repositories
✅ **Automatic Reviews**: Triggers on PR open, sync, and reopen
✅ **Comprehensive Analysis**: 5 specialized reviewer agents
✅ **Production-Ready**: Cloud Run deployment with auto-scaling
✅ **Secure**: Webhook signature verification, Secret Manager integration
✅ **Detailed Reports**: GitHub-flavored Markdown with collapsible sections

---

## Quick Start (3 Steps)

### Prerequisites

- Google Cloud account with billing enabled
- GitHub organization admin access (or repository admin)
- `gcloud` CLI installed and configured

### Step 1: Create GitHub App

1. Go to https://github.com/settings/apps (for personal) or https://github.com/organizations/[org]/settings/apps

2. Click "New GitHub App"

3. Fill in:
   - **GitHub App name**: `Python Codebase Reviewer` (or your choice)
   - **Homepage URL**: `https://github.com/your-org/python-codebase-reviewer`
   - **Webhook URL**: `https://placeholder.com` (will update after deployment)
   - **Webhook secret**: Click "Generate" and save this value

4. **Permissions** - Set these repository permissions:
   - Contents: Read
   - Pull requests: Read & Write
   - Issues: Read & Write (for comments)

5. **Subscribe to events**:
   - [x] Pull request

6. **Where can this GitHub App be installed?**
   - Select "Only on this account" or "Any account"

7. Click "Create GitHub App"

8. **Generate Private Key**:
   - Click "Generate a private key"
   - Download the `.pem` file (you'll need this)

9. **Note your App ID** (shown at top of page)

### Step 2: Deploy to Google Cloud

```bash
# 1. Clone repository
cd python_codebase_reviewer/github_app

# 2. Set up Google Cloud project
export GOOGLE_CLOUD_PROJECT="your-project-id"
export GOOGLE_CLOUD_REGION="us-central1"

# 3. Authenticate
gcloud auth login
gcloud config set project $GOOGLE_CLOUD_PROJECT

# 4. Set up secrets
chmod +x setup_secrets.sh
./setup_secrets.sh

# You'll be prompted for:
# - GitHub App ID (from step 1)
# - GitHub Webhook Secret (from step 1)
# - Path to private key .pem file (from step 1)
# - Google API Key (from https://aistudio.google.com/app/apikey)

# 5. Deploy to Cloud Run
chmod +x deploy.sh
./deploy.sh

# Note the service URL printed at the end!
```

### Step 3: Configure GitHub App Webhook

1. Go back to your GitHub App settings:
   https://github.com/settings/apps/[your-app]

2. Update **Webhook URL** with your Cloud Run URL:
   ```
   https://[your-service-url].run.app/webhook
   ```

3. Save changes

4. **Install the app**:
   - Click "Install App" in left sidebar
   - Select your organization/account
   - Choose "All repositories" or select specific ones
   - Click "Install"

---

## Testing

### 1. Test the Service

```bash
# Get your service URL
SERVICE_URL=$(gcloud run services describe python-code-reviewer \
    --region us-central1 \
    --format='value(status.url)')

# Health check
curl $SERVICE_URL/health

# Should return: {"status":"healthy",...}
```

### 2. Test with a Pull Request

1. Create a test PR with Python code containing an issue:

```python
# test.py - SQL Injection vulnerability
def login(username, password):
    query = f"SELECT * FROM users WHERE username='{username}' AND password='{password}'"
    return db.execute(query)
```

2. Open the PR

3. Watch for the review comment!

Expected output:
```markdown
# 🔍 Python Code Review Results

## 📊 Summary
- 🔴 1 Critical - Immediate action required

⚠️ Warning: Critical security issues detected!

## 📁 Detailed Review

### 📄 `test.py`

**Found 1 issue(s)** 🔴 1 Critical

[Detailed review with SQL injection vulnerability and fix]
```

---

## Configuration

### Environment Variables

Set via Google Secret Manager (already configured if you followed setup):

| Secret | Description | Where to Get |
|--------|-------------|--------------|
| `github-app-id` | GitHub App ID | GitHub App settings |
| `github-webhook-secret` | Webhook secret | Generated during setup |
| `github-app-private-key` | Private key (.pem file) | Generated in GitHub App settings |
| `google-api-key` | Google AI API key | https://aistudio.google.com/app/apikey |

### Cloud Run Configuration

Configured in `deploy.sh`:
- **Memory**: 1Gi (can increase for large PRs)
- **CPU**: 1 vCPU
- **Timeout**: 300 seconds (5 minutes)
- **Max instances**: 10 (auto-scales based on load)
- **Concurrency**: 8 requests per instance

### Customize Review Behavior

Edit `webhook_handler.py` to customize:

```python
# Line 280: Customize review request
review_request = f"""
Review this Python file...

Focus on:
- Security (your custom standards)
- Your company's style guide
- Specific frameworks you use
"""
```

---

## Monitoring & Logs

### View Logs

```bash
# Stream logs
gcloud run services logs tail python-code-reviewer \
    --region us-central1 \
    --project $GOOGLE_CLOUD_PROJECT

# View recent logs
gcloud run services logs read python-code-reviewer \
    --region us-central1 \
    --project $GOOGLE_CLOUD_PROJECT \
    --limit 50
```

### Key Log Messages

```
✅ Successfully reviewed PR #123
❌ Error processing webhook: <error message>
🔍 Processing PR #456: Add authentication
📝 Found 3 Python files to review
💬 Posting review comment...
```

### Metrics

View in Cloud Console:
- https://console.cloud.google.com/run/detail/[region]/python-code-reviewer/metrics

Monitor:
- Request count
- Request latency
- Error rate
- Container CPU/memory usage

---

## Troubleshooting

### Webhook Not Triggering

1. Check webhook deliveries in GitHub:
   - Go to GitHub App settings → Advanced → Recent Deliveries
   - Look for failed deliveries
   - Check response codes

2. Verify webhook URL is correct:
   ```bash
   echo $SERVICE_URL/webhook
   ```

3. Test webhook endpoint:
   ```bash
   curl -X POST $SERVICE_URL/webhook \
       -H "X-GitHub-Event: ping" \
       -d '{"hook_id":123}'
   ```

### Reviews Not Posting

Check logs for errors:
```bash
gcloud run services logs read python-code-reviewer --limit 100 | grep "ERROR"
```

Common issues:
- **GitHub token expired**: App needs to be re-installed
- **Missing permissions**: Check GitHub App permissions
- **API rate limits**: Add delays between requests

### Out of Memory

Increase memory allocation:
```bash
gcloud run services update python-code-reviewer \
    --memory 2Gi \
    --region us-central1
```

### Timeouts on Large PRs

Increase timeout:
```bash
gcloud run services update python-code-reviewer \
    --timeout 600 \
    --region us-central1
```

Or add PR size check in webhook_handler.py:
```python
if len(python_files) > 10:
    post_pr_comment(repo, pr_number,
        "⚠️ PR too large for automatic review. "
        "Please split into smaller PRs.")
    return
```

---

## Updating the App

### Update Code

```bash
# 1. Make changes to webhook_handler.py

# 2. Redeploy
./deploy.sh
```

### Update Secrets

```bash
# Update a specific secret
echo "new-value" | gcloud secrets versions add github-app-id \
    --data-file=- \
    --project=$GOOGLE_CLOUD_PROJECT

# Or rerun setup
./setup_secrets.sh
```

---

## Cost Estimate

### Google Cloud Run

Free tier (per month):
- 2 million requests
- 360,000 GB-seconds memory
- 180,000 vCPU-seconds

For typical usage:
- 100 PRs/day × 30 days = 3,000 requests
- ~10 seconds per review = 30,000 seconds
- **Cost**: ~$0-5/month (well within free tier)

### Google AI API (Gemini)

Pricing (as of 2024):
- Gemini 2.0 Flash: $0.10 per 1M input tokens
- Typical review: ~5,000 tokens
- 100 reviews/day: 500K tokens = $0.05/day
- **Cost**: ~$1.50/month

**Total estimated cost**: $1.50-6.50/month for typical usage

---

## Security Best Practices

✅ **Implemented**:
- Webhook signature verification (HMAC SHA-256)
- Secrets stored in Google Secret Manager
- Non-root container user
- HTTPS-only communication
- Minimal container image
- No credentials in code

🔒 **Recommendations**:
- Rotate webhook secret periodically
- Monitor for unusual webhook activity
- Limit GitHub App permissions to minimum required
- Use VPC if handling sensitive code
- Enable Cloud Armor for DDoS protection

---

## Uninstalling

### 1. Remove from GitHub

- Go to: https://github.com/settings/installations
- Click "Configure" on Python Codebase Reviewer
- Click "Uninstall"

### 2. Delete from Google Cloud

```bash
# Delete Cloud Run service
gcloud run services delete python-code-reviewer \
    --region us-central1 \
    --project $GOOGLE_CLOUD_PROJECT

# Delete container images
gcloud container images delete \
    gcr.io/$GOOGLE_CLOUD_PROJECT/python-code-reviewer \
    --project $GOOGLE_CLOUD_PROJECT

# Delete secrets (optional)
gcloud secrets delete github-app-id --project $GOOGLE_CLOUD_PROJECT
gcloud secrets delete github-webhook-secret --project $GOOGLE_CLOUD_PROJECT
gcloud secrets delete github-app-private-key --project $GOOGLE_CLOUD_PROJECT
gcloud secrets delete google-api-key --project $GOOGLE_CLOUD_PROJECT
```

---

## Support & Contributing

### Issues

Report issues at: https://github.com/your-org/agents-with-adk/issues

### Contributing

PRs welcome! See main repo README for contribution guidelines.

### Questions

- GitHub Discussions: https://github.com/your-org/agents-with-adk/discussions
- Email: your-email@example.com

---

## License

See main repository LICENSE file.

---

## Acknowledgments

Built with:
- [Google Agent Development Kit (ADK)](https://github.com/GoogleCloudPlatform/adk)
- [Google Gemini](https://deepmind.google/technologies/gemini/)
- [Google Cloud Run](https://cloud.google.com/run)
- [Flask](https://flask.palletsprojects.com/)
