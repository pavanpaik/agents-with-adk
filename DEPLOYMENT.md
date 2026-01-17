# Deployment Guide

This document provides a quick-start guide for deploying the Development Tutor Agent using GitHub Actions CI/CD.

## 🚀 Quick Start

### Prerequisites
- Google Cloud Project with billing enabled
- GitHub repository (this repo)
- 30 minutes for initial setup

### Setup Steps

#### 1. Create Google Cloud Service Account (5 minutes)

```bash
# Set your project ID
export GCP_PROJECT_ID="your-project-id"

# Create service account
gcloud iam service-accounts create github-actions-deployer \
    --display-name="GitHub Actions Deployer"

# Grant permissions
gcloud projects add-iam-policy-binding $GCP_PROJECT_ID \
    --member="serviceAccount:github-actions-deployer@${GCP_PROJECT_ID}.iam.gserviceaccount.com" \
    --role="roles/run.admin"

gcloud projects add-iam-policy-binding $GCP_PROJECT_ID \
    --member="serviceAccount:github-actions-deployer@${GCP_PROJECT_ID}.iam.gserviceaccount.com" \
    --role="roles/iam.serviceAccountUser"

gcloud projects add-iam-policy-binding $GCP_PROJECT_ID \
    --member="serviceAccount:github-actions-deployer@${GCP_PROJECT_ID}.iam.gserviceaccount.com" \
    --role="roles/storage.admin"

gcloud projects add-iam-policy-binding $GCP_PROJECT_ID \
    --member="serviceAccount:github-actions-deployer@${GCP_PROJECT_ID}.iam.gserviceaccount.com" \
    --role="roles/artifactregistry.admin"

gcloud projects add-iam-policy-binding $GCP_PROJECT_ID \
    --member="serviceAccount:github-actions-deployer@${GCP_PROJECT_ID}.iam.gserviceaccount.com" \
    --role="roles/cloudbuild.builds.editor"

# Create and download key
gcloud iam service-accounts keys create github-actions-key.json \
    --iam-account=github-actions-deployer@${GCP_PROJECT_ID}.iam.gserviceaccount.com
```

#### 2. Enable Required APIs

```bash
gcloud services enable run.googleapis.com \
    cloudbuild.googleapis.com \
    artifactregistry.googleapis.com \
    --project=$GCP_PROJECT_ID
```

#### 3. Configure GitHub Secrets (10 minutes)

Go to: **GitHub Repository → Settings → Secrets and variables → Actions**

Add these secrets:

| Secret Name | Where to Get It |
|-------------|-----------------|
| `GCP_PROJECT_ID` | Your Google Cloud project ID |
| `GCP_SA_KEY` | Copy entire contents of `github-actions-key.json` |
| `GCP_REGION` | `us-central1` (or your preferred region) |
| `GOOGLE_API_KEY` | From Google AI Studio (if using) |
| `GOOGLE_GENAI_USE_VERTEXAI` | `True` (for Vertex AI) or `False` (for AI Studio) |

**Important:** After adding `GCP_SA_KEY` to GitHub, delete the local `github-actions-key.json` file:
```bash
rm github-actions-key.json
```

#### 4. Test Deployment (5 minutes)

**Option A: Deploy to Staging**
```bash
git checkout -b staging
git push origin staging
```

**Option B: Manual Trigger**
1. Go to GitHub → Actions tab
2. Select "Deploy to Staging"
3. Click "Run workflow"
4. Monitor the deployment

#### 5. Deploy to Production

**When ready:**
```bash
git checkout main
git merge staging
git push origin main
```

Or create a release:
```bash
git tag -a v1.0.0 -m "First production release"
git push origin v1.0.0
```

---

## 📋 Deployment Workflows

### Automatic Triggers

| Action | Workflow | Result |
|--------|----------|--------|
| Push to any branch | CI checks | Lint, test, validate |
| Push to `staging` | Deploy to staging | Cloud Run staging environment |
| Push to `main` | Deploy to production | Cloud Run production environment |
| Push tag `v*.*.*` | Deploy + Release | Production + GitHub release |
| Pull Request | CI checks | Quality validation |

### Manual Triggers

Both staging and production deployments can be manually triggered:

1. GitHub → Actions tab
2. Select workflow (Deploy to Staging / Production)
3. Click "Run workflow"
4. Choose branch
5. Click "Run workflow"

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────┐
│           GitHub Repository                  │
│  (Code + GitHub Actions Workflows)          │
└─────────────────┬───────────────────────────┘
                  │
                  │ (git push)
                  ▼
┌─────────────────────────────────────────────┐
│         GitHub Actions Runner                │
│  • Install dependencies                      │
│  • Run tests & linting                       │
│  • Authenticate to Google Cloud              │
│  • Build container image                     │
│  • Deploy to Cloud Run                       │
└─────────────────┬───────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────┐
│         Google Cloud Run                     │
│                                              │
│  Staging:      dev-tutor-staging            │
│  Production:   dev-tutor                     │
│                                              │
│  • Auto-scaling containers                   │
│  • HTTPS endpoints                           │
│  • Integrated logging                        │
└─────────────────────────────────────────────┘
```

---

## 🌲 Branching Strategy

```
main (production)
├── staging (pre-production)
│   └── develop (active development)
│       ├── feature/feature-1
│       ├── feature/feature-2
│       └── bugfix/fix-1
└── hotfix/urgent-fix (emergency production fixes)
```

### Workflow:
1. **Develop features** in `feature/*` branches
2. **Merge to develop** for integration
3. **Merge to staging** for pre-production testing
4. **Merge to main** for production deployment
5. **Tag releases** on main (v1.0.0, v1.1.0, etc.)

---

## 🔍 Monitoring & Logs

### View Deployment Status
- **GitHub:** Actions tab → View workflow runs
- **Summary:** Each workflow generates a detailed summary

### Access Application
- **Staging:** Check workflow output for URL or:
  ```bash
  gcloud run services describe dev-tutor-staging --region=us-central1 --format='value(status.url)'
  ```
- **Production:**
  ```bash
  gcloud run services describe dev-tutor --region=us-central1 --format='value(status.url)'
  ```

### View Logs
```bash
# Stream staging logs
gcloud run services logs tail dev-tutor-staging --region=us-central1

# Stream production logs
gcloud run services logs tail dev-tutor --region=us-central1

# View recent logs
gcloud run services logs read dev-tutor --region=us-central1 --limit=50
```

### Cloud Console
- **Services:** https://console.cloud.google.com/run
- **Logs:** https://console.cloud.google.com/logs
- **Metrics:** Available in each service's details page

---

## 🔄 Common Tasks

### Update Application Code
```bash
# Make changes
vim development_tutor/prompt.py

# Commit and push
git add .
git commit -m "Update agent prompt"
git push origin main  # Auto-deploys to production
```

### Deploy New Feature
```bash
# Create feature branch
git checkout -b feature/new-capability

# Develop and test locally
# ... make changes ...

# Push for CI checks
git push origin feature/new-capability

# Create PR to staging
# After review, merge to staging (auto-deploys to staging)

# Test in staging environment

# Create PR to main
# After approval, merge to main (auto-deploys to production)
```

### Create a Release
```bash
git checkout main
git pull origin main

# Tag the release
git tag -a v1.2.0 -m "Release v1.2.0: Add new features"
git push origin v1.2.0

# This triggers:
# - Production deployment
# - GitHub Release creation with release notes
```

### Rollback Deployment
```bash
# Option 1: Revert to previous Cloud Run revision
gcloud run services update-traffic dev-tutor \
    --to-revisions=PREVIOUS_REVISION=100 \
    --region=us-central1

# Option 2: Deploy previous git commit
git checkout <previous-commit-sha>
git push origin main --force  # Use with caution!

# Option 3: Revert commit and deploy
git revert HEAD
git push origin main
```

---

## 💰 Cost Estimates

### Cloud Run Pricing (as of 2026)
- **Free Tier:** 2M requests, 360,000 GB-seconds compute, 1GB egress per month
- **Paid:** ~$0.40 per million requests, ~$0.00002400 per GB-second

### Estimated Monthly Costs
- **Light usage** (< 10k requests/month): **$0** (within free tier)
- **Moderate usage** (100k requests/month): **$5-15**
- **Heavy usage** (1M requests/month): **$40-60**

### GitHub Actions
- **Public repositories:** Unlimited minutes (free)
- **Private repositories:** 2,000 minutes/month (free tier)
- Each deployment: ~5 minutes
- **Monthly:** ~300 deployments free (very generous)

---

## 🔒 Security Checklist

- [ ] Service account key stored only in GitHub Secrets
- [ ] Local `github-actions-key.json` deleted
- [ ] Branch protection enabled on `main`
- [ ] Required reviews for production PRs
- [ ] GitHub environments configured (staging/production)
- [ ] Production environment requires approval
- [ ] Secrets audit trail reviewed
- [ ] Service account permissions follow least privilege
- [ ] Regular security scans enabled (CI workflow)
- [ ] Dependency updates monitored

---

## 🐛 Troubleshooting

### "Permission Denied" Error
**Issue:** Deployment fails with authentication error

**Fix:**
1. Verify service account has all required roles
2. Check `GCP_SA_KEY` secret is properly formatted (entire JSON)
3. Ensure Google Cloud APIs are enabled

### "Build Failed" Error
**Issue:** Container image build fails

**Fix:**
1. Check `requirements.txt` for syntax errors
2. Verify all dependencies are available
3. Review build logs in GitHub Actions

### Deployment Succeeds but App Doesn't Work
**Issue:** Service deployed but returns errors

**Fix:**
1. Check Cloud Run logs: `gcloud run services logs read dev-tutor`
2. Verify environment variables in GitHub Secrets
3. Test locally: `adk web`
4. Check agent code for runtime errors

### Workflow Not Triggering
**Issue:** Push doesn't trigger expected workflow

**Fix:**
1. Check branch name matches workflow trigger conditions
2. Verify workflows are enabled in Settings → Actions
3. Check for YAML syntax errors
4. Review Actions tab for failed workflow runs

---

## 📚 Additional Documentation

- **Detailed CI/CD Setup:** See `.github/workflows/README.md`
- **Project Overview:** See main `README.md`
- **ADK Documentation:** https://google.github.io/adk-docs/
- **Cloud Run Documentation:** https://cloud.google.com/run/docs

---

## ✅ Post-Setup Checklist

After completing setup, verify:

- [ ] All GitHub secrets configured
- [ ] Service account created with correct permissions
- [ ] Google Cloud APIs enabled
- [ ] CI workflow runs successfully on test push
- [ ] Staging deployment completes successfully
- [ ] Staging application accessible and functional
- [ ] Production deployment completes successfully
- [ ] Production application accessible and functional
- [ ] Team members have access to GitHub repository
- [ ] Documentation shared with team
- [ ] Monitoring and alerting configured (optional)
- [ ] Backup/rollback strategy documented

---

## 🎯 Next Steps

1. **Set up branch protection** on `main` branch
2. **Configure monitoring** and alerts in Google Cloud
3. **Set up staging environment** for safe testing
4. **Create deployment runbook** for team reference
5. **Schedule regular security audits** of service account permissions
6. **Consider** Workload Identity Federation for enhanced security

---

**Need Help?**

- Review `.github/workflows/README.md` for detailed documentation
- Check GitHub Actions logs for specific error messages
- Review Cloud Run logs for application issues
- Consult ADK documentation for agent-specific problems

**Happy Deploying! 🚀**
