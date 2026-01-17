# CI/CD Pipeline Documentation

This directory contains GitHub Actions workflows for automated testing and deployment of the Development Tutor Agent.

## 📋 Workflows Overview

### 1. Continuous Integration (`ci.yml`)
**Trigger:** Every push to any branch, all pull requests

**Purpose:** Automated quality checks and validation

**Jobs:**
- **Code Quality Checks**: Black formatting, isort imports, flake8 linting
- **Security Scan**: Dependency vulnerabilities (safety), code security (bandit)
- **Tests**: Run pytest suite with coverage reporting
- **ADK Validation**: Verify agent structure and Python syntax

**Duration:** ~3-5 minutes

---

### 2. Deploy to Staging (`deploy-staging.yml`)
**Trigger:** Push to `staging` or `develop` branches, or manual dispatch

**Purpose:** Deploy to staging environment for testing

**Jobs:**
- Install dependencies and authenticate to GCP
- Deploy to Cloud Run staging service
- Run smoke tests
- Generate deployment summary

**Service:** `dev-tutor-staging`

**Duration:** ~5-8 minutes

---

### 3. Deploy to Production (`deploy-production.yml`)
**Trigger:** Push to `main` branch, version tags (`v*.*.*`), or manual dispatch

**Purpose:** Deploy to production environment

**Jobs:**
- Pre-deployment validation
- Deploy to Cloud Run production service
- Run smoke tests
- Create deployment record
- Generate GitHub release (for version tags)

**Service:** `dev-tutor`

**Duration:** ~5-8 minutes

---

## 🔧 Setup Instructions

### Step 1: Google Cloud Setup

#### 1.1 Create Service Account

```bash
# Set your project ID
export GCP_PROJECT_ID="your-project-id"

# Create service account
gcloud iam service-accounts create github-actions-deployer \
    --display-name="GitHub Actions Deployer" \
    --project=$GCP_PROJECT_ID
```

#### 1.2 Grant Permissions

```bash
# Cloud Run Admin
gcloud projects add-iam-policy-binding $GCP_PROJECT_ID \
    --member="serviceAccount:github-actions-deployer@${GCP_PROJECT_ID}.iam.gserviceaccount.com" \
    --role="roles/run.admin"

# Service Account User
gcloud projects add-iam-policy-binding $GCP_PROJECT_ID \
    --member="serviceAccount:github-actions-deployer@${GCP_PROJECT_ID}.iam.gserviceaccount.com" \
    --role="roles/iam.serviceAccountUser"

# Storage Admin (for Cloud Run artifacts)
gcloud projects add-iam-policy-binding $GCP_PROJECT_ID \
    --member="serviceAccount:github-actions-deployer@${GCP_PROJECT_ID}.iam.gserviceaccount.com" \
    --role="roles/storage.admin"

# Artifact Registry Admin (for Docker images)
gcloud projects add-iam-policy-binding $GCP_PROJECT_ID \
    --member="serviceAccount:github-actions-deployer@${GCP_PROJECT_ID}.iam.gserviceaccount.com" \
    --role="roles/artifactregistry.admin"

# Cloud Build Editor (for building containers)
gcloud projects add-iam-policy-binding $GCP_PROJECT_ID \
    --member="serviceAccount:github-actions-deployer@${GCP_PROJECT_ID}.iam.gserviceaccount.com" \
    --role="roles/cloudbuild.builds.editor"
```

#### 1.3 Create Service Account Key

```bash
# Generate key file
gcloud iam service-accounts keys create github-actions-key.json \
    --iam-account=github-actions-deployer@${GCP_PROJECT_ID}.iam.gserviceaccount.com

# Display the key (copy this for GitHub Secrets)
cat github-actions-key.json

# IMPORTANT: Delete this file after adding to GitHub Secrets
# Do NOT commit this file to your repository
```

---

### Step 2: GitHub Secrets Configuration

Go to your repository: **Settings → Secrets and variables → Actions → New repository secret**

Add the following secrets:

| Secret Name | Value | Description |
|-------------|-------|-------------|
| `GCP_PROJECT_ID` | `your-project-id` | Your Google Cloud project ID |
| `GCP_SA_KEY` | `<contents of github-actions-key.json>` | Service account JSON key (entire file content) |
| `GCP_REGION` | `us-central1` | Cloud Run deployment region |
| `GOOGLE_API_KEY` | `your-gemini-api-key` | Google AI API key (if using AI Studio) |
| `GOOGLE_GENAI_USE_VERTEXAI` | `True` or `False` | Whether to use Vertex AI or AI Studio |
| `TUTOR_MODEL` | `learnlm-1.5-pro-experimental` | (Optional) Override default tutor model |
| `BASE_MODEL` | `gemini-2.0-flash-thinking-exp-01-21` | (Optional) Override default base model |

**To add a secret:**

1. Click "New repository secret"
2. Enter the name (e.g., `GCP_PROJECT_ID`)
3. Paste the value
4. Click "Add secret"

---

### Step 3: GitHub Environments (Optional but Recommended)

Create deployment environments for better control:

1. Go to **Settings → Environments**
2. Create two environments:
   - `staging`
   - `production`

3. For `production` environment, add protection rules:
   - ✅ Required reviewers (select team members)
   - ✅ Wait timer (e.g., 5 minutes)
   - ✅ Deployment branches: `main` and tags only

---

### Step 4: Enable Google Cloud APIs

```bash
# Enable required APIs
gcloud services enable run.googleapis.com \
    cloudbuild.googleapis.com \
    artifactregistry.googleapis.com \
    --project=$GCP_PROJECT_ID
```

---

### Step 5: Test the Workflows

#### Option A: Manual Trigger (Recommended for First Test)

1. Go to **Actions** tab in GitHub
2. Select "Deploy to Staging" workflow
3. Click "Run workflow"
4. Select branch: `staging` or `develop`
5. Click "Run workflow"

#### Option B: Git Push

```bash
# Create and push to staging branch
git checkout -b staging
git push origin staging

# This will trigger the staging deployment workflow
```

---

## 🚦 Workflow Triggers Summary

| Branch/Action | CI | Staging Deploy | Production Deploy |
|---------------|:--:|:--------------:|:-----------------:|
| Push to any branch | ✅ | ❌ | ❌ |
| Push to `staging` | ✅ | ✅ | ❌ |
| Push to `develop` | ✅ | ✅ | ❌ |
| Push to `main` | ✅ | ❌ | ✅ |
| Tag `v*.*.*` | ✅ | ❌ | ✅ |
| Pull Request | ✅ | ❌ | ❌ |
| Manual dispatch | ❌ | ✅ | ✅ |

---

## 📊 Monitoring Deployments

### View Workflow Runs
- GitHub: **Actions** tab → Select workflow → View run details

### View Deployment Logs
```bash
# Staging
gcloud run services logs read dev-tutor-staging \
    --region=us-central1 \
    --project=$GCP_PROJECT_ID

# Production
gcloud run services logs read dev-tutor \
    --region=us-central1 \
    --project=$GCP_PROJECT_ID
```

### Check Service Status
```bash
# List all services
gcloud run services list --project=$GCP_PROJECT_ID

# Get specific service details
gcloud run services describe dev-tutor \
    --region=us-central1 \
    --project=$GCP_PROJECT_ID
```

---

## 🔄 Common Workflows

### Deploying a Feature

```bash
# 1. Create feature branch
git checkout -b feature/my-new-feature

# 2. Make changes and commit
git add .
git commit -m "Add new feature"

# 3. Push to trigger CI
git push origin feature/my-new-feature

# 4. Create PR to staging for testing
# (Merge to staging triggers staging deployment)

# 5. After testing, merge to main
# (Triggers production deployment)
```

### Creating a Release

```bash
# 1. Ensure main branch is ready
git checkout main
git pull origin main

# 2. Create and push version tag
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin v1.0.0

# This triggers:
# - Production deployment
# - GitHub release creation
```

### Rolling Back

```bash
# Option 1: Revert to previous Cloud Run revision
gcloud run services update-traffic dev-tutor \
    --to-revisions=dev-tutor-00001-abc=100 \
    --region=us-central1 \
    --project=$GCP_PROJECT_ID

# Option 2: Redeploy previous commit
git checkout <previous-commit-sha>
git tag -f v1.0.1
git push origin v1.0.1 --force
```

---

## 🐛 Troubleshooting

### Deployment Fails: Authentication Error

**Issue:** `Permission denied` or `Unauthorized`

**Solution:**
1. Verify service account has correct permissions
2. Check `GCP_SA_KEY` secret is correctly formatted (entire JSON)
3. Ensure APIs are enabled in GCP

### Deployment Fails: Image Build Error

**Issue:** Docker build fails or image push fails

**Solution:**
1. Check `requirements.txt` is valid
2. Verify Artifact Registry is enabled
3. Check service account has `artifactregistry.admin` role

### Smoke Test Fails

**Issue:** Service deployed but health check returns non-200

**Solution:**
1. Check Cloud Run logs for application errors
2. Verify environment variables are correctly set
3. Check if service is still starting up (increase wait time)

### Workflow Not Triggering

**Issue:** Push to branch doesn't trigger workflow

**Solution:**
1. Check workflow trigger conditions match your branch
2. Verify workflows are enabled in Settings → Actions
3. Check for YAML syntax errors in workflow files

---

## 📚 Additional Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Google Cloud Run Documentation](https://cloud.google.com/run/docs)
- [ADK Documentation](https://google.github.io/adk-docs/)
- [Workload Identity Federation (Alternative to SA Key)](https://cloud.google.com/iam/docs/workload-identity-federation)

---

## 🔒 Security Best Practices

1. **Never commit service account keys** to the repository
2. **Rotate service account keys** every 90 days
3. **Use least privilege** - only grant necessary permissions
4. **Enable branch protection** on `main` branch
5. **Require PR reviews** before merging to production
6. **Use GitHub environment protection rules** for production
7. **Consider Workload Identity Federation** instead of SA keys for enhanced security
8. **Regularly audit** GitHub Actions logs and GCP IAM policies

---

## 💡 Tips & Best Practices

1. **Test in staging first** before deploying to production
2. **Use semantic versioning** for release tags (v1.0.0, v1.1.0, etc.)
3. **Write descriptive commit messages** - they appear in deployment summaries
4. **Monitor Cloud Run metrics** to understand usage and costs
5. **Set up Cloud Run alerts** for errors and high latency
6. **Use separate environments** (staging/production) with different service names
7. **Keep workflows DRY** - consider creating reusable workflow templates
8. **Document environment variables** so team members know what's required

---

## 📞 Support

If you encounter issues:

1. Check the troubleshooting section above
2. Review GitHub Actions logs in the Actions tab
3. Check Cloud Run logs in GCP Console
4. Review ADK documentation for agent-specific issues

---

**Last Updated:** 2026-01-17
