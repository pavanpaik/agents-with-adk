#!/bin/bash
#
# Setup Google Cloud secrets for Python Codebase Reviewer GitHub App
#
# This script creates secrets in Google Secret Manager for:
# - GitHub App ID
# - GitHub Webhook Secret
# - GitHub App Private Key
# - Google API Key
#
# Usage:
#   ./setup_secrets.sh

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Setup Secrets for GitHub App${NC}"
echo -e "${GREEN}========================================${NC}"
echo

# Check project
if [ -z "$GOOGLE_CLOUD_PROJECT" ]; then
    echo -e "${YELLOW}Enter your Google Cloud Project ID:${NC}"
    read GOOGLE_CLOUD_PROJECT
    export GOOGLE_CLOUD_PROJECT
fi

echo "Project: $GOOGLE_CLOUD_PROJECT"
echo

# Enable Secret Manager API
echo -e "${YELLOW}Enabling Secret Manager API...${NC}"
gcloud services enable secretmanager.googleapis.com --project=$GOOGLE_CLOUD_PROJECT

echo
echo -e "${YELLOW}Creating secrets...${NC}"
echo

# 1. GitHub App ID
echo "1. GitHub App ID"
echo "   Find this at: https://github.com/settings/apps/[your-app]"
echo "   Enter GitHub App ID:"
read GITHUB_APP_ID

if [ ! -z "$GITHUB_APP_ID" ]; then
    echo -n "$GITHUB_APP_ID" | gcloud secrets create github-app-id \
        --data-file=- \
        --replication-policy=automatic \
        --project=$GOOGLE_CLOUD_PROJECT 2>/dev/null || \
    echo -n "$GITHUB_APP_ID" | gcloud secrets versions add github-app-id \
        --data-file=- \
        --project=$GOOGLE_CLOUD_PROJECT
    echo -e "${GREEN}   ✓ GitHub App ID saved${NC}"
else
    echo "   Skipped"
fi

echo

# 2. GitHub Webhook Secret
echo "2. GitHub Webhook Secret"
echo "   This is a secret string you create for webhook verification"
echo "   Generate a random secret? (Y/n)"
read -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]] || [[ -z $REPLY ]]; then
    WEBHOOK_SECRET=$(openssl rand -hex 32)
    echo "   Generated secret: $WEBHOOK_SECRET"
    echo "   ⚠️  IMPORTANT: Save this secret! You'll need it for GitHub App configuration."
else
    echo "   Enter your webhook secret:"
    read WEBHOOK_SECRET
fi

if [ ! -z "$WEBHOOK_SECRET" ]; then
    echo -n "$WEBHOOK_SECRET" | gcloud secrets create github-webhook-secret \
        --data-file=- \
        --replication-policy=automatic \
        --project=$GOOGLE_CLOUD_PROJECT 2>/dev/null || \
    echo -n "$WEBHOOK_SECRET" | gcloud secrets versions add github-webhook-secret \
        --data-file=- \
        --project=$GOOGLE_CLOUD_PROJECT
    echo -e "${GREEN}   ✓ Webhook secret saved${NC}"
else
    echo "   Skipped"
fi

echo

# 3. GitHub App Private Key
echo "3. GitHub App Private Key"
echo "   Find this at: https://github.com/settings/apps/[your-app]"
echo "   Click 'Generate a private key' and download the .pem file"
echo "   Enter path to private key file (e.g., ~/Downloads/your-app.private-key.pem):"
read PRIVATE_KEY_PATH

if [ ! -z "$PRIVATE_KEY_PATH" ] && [ -f "$PRIVATE_KEY_PATH" ]; then
    gcloud secrets create github-app-private-key \
        --data-file="$PRIVATE_KEY_PATH" \
        --replication-policy=automatic \
        --project=$GOOGLE_CLOUD_PROJECT 2>/dev/null || \
    gcloud secrets versions add github-app-private-key \
        --data-file="$PRIVATE_KEY_PATH" \
        --project=$GOOGLE_CLOUD_PROJECT
    echo -e "${GREEN}   ✓ Private key saved${NC}"
else
    echo "   Skipped or file not found"
fi

echo

# 4. Google API Key
echo "4. Google API Key (for Gemini)"
echo "   Get this from: https://aistudio.google.com/app/apikey"
echo "   Enter your Google API Key:"
read -s GOOGLE_API_KEY
echo

if [ ! -z "$GOOGLE_API_KEY" ]; then
    echo -n "$GOOGLE_API_KEY" | gcloud secrets create google-api-key \
        --data-file=- \
        --replication-policy=automatic \
        --project=$GOOGLE_CLOUD_PROJECT 2>/dev/null || \
    echo -n "$GOOGLE_API_KEY" | gcloud secrets versions add google-api-key \
        --data-file=- \
        --project=$GOOGLE_CLOUD_PROJECT
    echo -e "${GREEN}   ✓ Google API Key saved${NC}"
else
    echo "   Skipped"
fi

echo
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Secrets Setup Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo

echo "Created secrets:"
gcloud secrets list --project=$GOOGLE_CLOUD_PROJECT | grep -E "github-|google-api"

echo
echo -e "${YELLOW}Next steps:${NC}"
echo "1. Run: ./deploy.sh"
echo "2. Configure GitHub App webhook with the Cloud Run URL"
echo "3. Install the GitHub App on your repositories"
echo
