# Complete Setup Guide - Python Codebase Reviewer GitHub App

This guide will walk you through setting up the GitHub App from scratch to production deployment.

**Time required**: ~30 minutes
**Difficulty**: Intermediate

---

## Prerequisites

### Required
- ✅ Google Cloud account with billing enabled
- ✅ GitHub organization (or personal account)
- ✅ `gcloud` CLI installed: https://cloud.google.com/sdk/docs/install
- ✅ Git installed

### Recommended
- GitHub organization admin access (for org-wide installation)
- Basic knowledge of Docker and Cloud Run
- Familiarity with GitHub Apps

---

## Step-by-Step Setup

### Part 1: Create Google Cloud Project (5 minutes)

1. **Create a new project**:
   ```bash
   # Set project ID (must be globally unique)
   export GOOGLE_CLOUD_PROJECT="python-reviewer-$(date +%s)"

   # Create project
   gcloud projects create $GOOGLE_CLOUD_PROJECT \
       --name="Python Code Reviewer"

   # Set as active project
   gcloud config set project $GOOGLE_CLOUD_PROJECT
   ```

2. **Enable billing**:
   - Go to: https://console.cloud.google.com/billing
   - Link your billing account to the project

3. **Verify project**:
   ```bash
   gcloud config get-value project
   # Should output your project ID
   ```

---

### Part 2: Get Google AI API Key (2 minutes)

1. Go to: https://aistudio.google.com/app/apikey

2. Click "Create API key"

3. Copy the API key and save it securely

---

### Part 3: Create GitHub App (10 minutes)

#### Option A: Quick Create with Manifest (Recommended)

1. Edit `github-app-manifest.json`:
   ```json
   {
     "name": "Python Codebase Reviewer - [Your Org]",
     "url": "https://github.com/your-org/agents-with-adk",
     "hook_attributes": {
       "url": "https://PLACEHOLDER.com/webhook"
     }
   }
   ```

2. Go to:
   - Personal: https://github.com/settings/apps/new
   - Organization: https://github.com/organizations/[your-org]/settings/apps/new

3. Paste the manifest JSON and click "Create GitHub App from manifest"

4. **Save these values**:
   - App ID
   - Click "Generate a private key" → Download `.pem` file
   - Webhook secret (you'll set this next)

#### Option B: Manual Creation

1. Go to:
   - Personal: https://github.com/settings/apps/new
   - Organization: https://github.com/organizations/[org]/settings/apps/new

2. Fill in:
   - **Name**: `Python Codebase Reviewer - [Your Org]`
   - **Homepage URL**: Your repo URL
   - **Webhook URL**: `https://PLACEHOLDER.com/webhook` (will update later)
   - **Webhook secret**: Click "Generate" and save it

3. **Permissions** - Repository permissions:
   - Contents: `Read`
   - Pull requests: `Read and write`
   - Issues: `Read and write`

4. **Subscribe to events**:
   - [x] Pull request

5. **Where can this app be installed?**
   - Choose based on your needs

6. Click "Create GitHub App"

7. **Generate private key**:
   - In your new app settings
   - Scroll down to "Private keys"
   - Click "Generate a private key"
   - Download the `.pem` file

8. **Note your App ID** (shown at top of app settings page)

---

### Part 4: Deploy to Google Cloud (10 minutes)

1. **Clone repository and navigate to GitHub App directory**:
   ```bash
   cd python_codebase_reviewer/github_app
   ```

2. **Set up secrets**:
   ```bash
   chmod +x setup_secrets.sh
   ./setup_secrets.sh
   ```

   You'll be prompted for:
   - **Google Cloud Project ID**: Enter your project ID
   - **GitHub App ID**: From Part 3
   - **GitHub Webhook Secret**: From Part 3 (or generate new one)
   - **Private key path**: Path to the `.pem` file you downloaded
   - **Google API Key**: From Part 2

   Example:
   ```
   Enter your Google Cloud Project ID:
   > python-reviewer-1234567890

   1. GitHub App ID
      Enter GitHub App ID:
   > 123456

   2. GitHub Webhook Secret
      Generate a random secret? (Y/n)
   > Y
      Generated secret: a1b2c3d4e5f6...
      ⚠️  IMPORTANT: Save this! You'll need it for GitHub.

   3. GitHub App Private Key
      Enter path to private key file:
   > ~/Downloads/python-reviewer.2024-01-01.private-key.pem

   4. Google API Key
      Enter your Google API Key:
   > AIzaSy...
   ```

3. **Deploy to Cloud Run**:
   ```bash
   chmod +x deploy.sh
   ./deploy.sh
   ```

   This will:
   - Enable required APIs
   - Build Docker container
   - Deploy to Cloud Run
   - Output your service URL

   Example output:
   ```
   ========================================
   Deployment Complete!
   ========================================

   Service URL: https://python-code-reviewer-xyz123-uc.a.run.app

   Next steps:
   1. Test the service:
      curl https://python-code-reviewer-xyz123-uc.a.run.app/health
   ...
   ```

4. **Save your service URL**:
   ```bash
   export SERVICE_URL="<your-service-url-from-output>"
   ```

---

### Part 5: Configure GitHub App Webhook (3 minutes)

1. Go back to your GitHub App settings:
   - Personal: https://github.com/settings/apps/[your-app-name]
   - Organization: https://github.com/organizations/[org]/settings/apps/[your-app-name]

2. **Update Webhook URL**:
   - Find "Webhook URL" field
   - Replace with: `[YOUR-SERVICE-URL]/webhook`
   - Example: `https://python-code-reviewer-xyz123-uc.a.run.app/webhook`

3. **Update Webhook secret** (if you generated a new one):
   - Paste the secret from Step 4 setup

4. **Check "Active"** checkbox

5. Click "Save changes"

---

### Part 6: Install the GitHub App (2 minutes)

1. In your GitHub App settings, click "Install App" in left sidebar

2. Select your organization/account

3. Choose installation option:
   - **All repositories** (recommended for org-wide use)
   - **Only select repositories** (choose specific repos)

4. Click "Install"

---

### Part 7: Test the Setup (5 minutes)

#### Test 1: Health Check

```bash
curl $SERVICE_URL/health
```

Expected output:
```json
{"status":"healthy","service":"python-codebase-reviewer","version":"1.0.0"}
```

#### Test 2: Create Test PR

1. In one of your repositories, create a file with a vulnerability:

   ```python
   # test_security.py
   def login(username, password):
       query = f"SELECT * FROM users WHERE username='{username}'"
       return db.execute(query)
   ```

2. Commit and push to a branch

3. Open a Pull Request

4. Wait ~30 seconds

5. Check for a review comment from your GitHub App!

Expected comment:
```markdown
# 🔍 Python Code Review Results

**Repository**: your-org/your-repo
**Pull Request**: #1

## 📊 Summary
- 🔴 1 Critical - Immediate action required

⚠️ Warning: Critical security issues detected!

## 📁 Detailed Review

### 📄 `test_security.py`

**Found 1 issue(s)** 🔴 1 Critical

[Detailed review with SQL injection vulnerability...]
```

#### Test 3: Check Logs

```bash
gcloud run services logs read python-code-reviewer \
    --region us-central1 \
    --project $GOOGLE_CLOUD_PROJECT \
    --limit 20
```

Look for:
```
✅ Successfully reviewed PR #1
```

---

## Verification Checklist

- [ ] Google Cloud project created and billing enabled
- [ ] Google AI API key obtained
- [ ] GitHub App created with correct permissions
- [ ] Private key downloaded
- [ ] Secrets stored in Google Secret Manager
- [ ] Cloud Run service deployed successfully
- [ ] GitHub App webhook URL configured
- [ ] GitHub App installed on repository/organization
- [ ] Test PR triggers automatic review
- [ ] Review comment posted successfully

---

## Troubleshooting

### Issue: Deploy fails with "Permission denied"

**Solution**: Enable required APIs manually:
```bash
gcloud services enable run.googleapis.com \
    secretmanager.googleapis.com \
    cloudbuild.googleapis.com \
    --project=$GOOGLE_CLOUD_PROJECT
```

### Issue: Webhook not triggering

**Check**:
1. Webhook deliveries in GitHub App settings → Advanced
2. Look for failed deliveries
3. Check response codes

**Debug**:
```bash
# View recent webhook attempts
# In GitHub App settings → Advanced → Recent Deliveries
# Click on a delivery to see request/response

# Check Cloud Run logs
gcloud run services logs read python-code-reviewer --limit 50
```

### Issue: Review not posting

**Possible causes**:
1. GitHub App needs re-authentication
2. Missing permissions (check PR write permission)
3. API rate limits

**Fix**:
```bash
# Check logs for errors
gcloud run services logs read python-code-reviewer --limit 100 | grep ERROR

# Verify permissions in GitHub App settings
```

### Issue: Out of memory

**Fix**: Increase memory:
```bash
gcloud run services update python-code-reviewer \
    --memory 2Gi \
    --region us-central1 \
    --project $GOOGLE_CLOUD_PROJECT
```

---

## Next Steps

### Customize Reviews

Edit `webhook_handler.py` line 280 to customize review prompts:

```python
review_request = f"""
Review this Python file...

Focus on:
- Our company's security standards
- Framework: Django 4.2
- Style guide: PEP 8 + Black
"""
```

### Monitor Usage

View metrics:
```bash
# Open Cloud Console metrics
echo "https://console.cloud.google.com/run/detail/us-central1/python-code-reviewer/metrics?project=$GOOGLE_CLOUD_PROJECT"
```

### Scale Configuration

For high volume:
```bash
gcloud run services update python-code-reviewer \
    --memory 2Gi \
    --cpu 2 \
    --max-instances 50 \
    --region us-central1 \
    --project $GOOGLE_CLOUD_PROJECT
```

---

## Support

- **Issues**: https://github.com/your-org/agents-with-adk/issues
- **Discussions**: https://github.com/your-org/agents-with-adk/discussions
- **Documentation**: See `README.md` in this directory

---

## Clean Up (if you want to remove everything)

```bash
# Uninstall from GitHub
# Go to: https://github.com/settings/installations
# Configure → Uninstall

# Delete Cloud Run service
gcloud run services delete python-code-reviewer \
    --region us-central1 \
    --project $GOOGLE_CLOUD_PROJECT

# Delete container images
gcloud container images delete \
    gcr.io/$GOOGLE_CLOUD_PROJECT/python-code-reviewer \
    --quiet

# Delete secrets
for secret in github-app-id github-webhook-secret github-app-private-key google-api-key; do
    gcloud secrets delete $secret --project=$GOOGLE_CLOUD_PROJECT --quiet
done

# Optionally delete project
gcloud projects delete $GOOGLE_CLOUD_PROJECT
```

---

You're all set! 🎉

Your GitHub App will now automatically review Python code in pull requests across your organization.
