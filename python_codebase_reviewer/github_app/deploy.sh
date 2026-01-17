#!/bin/bash
#
# Deploy Python Codebase Reviewer GitHub App to Google Cloud Run
#
# Usage:
#   ./deploy.sh
#
# Required environment variables:
#   GOOGLE_CLOUD_PROJECT - Google Cloud project ID
#   GOOGLE_CLOUD_REGION - Region for deployment (default: us-central1)
#
# Required secrets in Google Secret Manager:
#   - github-app-id
#   - github-webhook-secret
#   - github-app-private-key
#   - google-api-key

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Python Codebase Reviewer GitHub App${NC}"
echo -e "${GREEN}Deployment to Cloud Run${NC}"
echo -e "${GREEN}========================================${NC}"
echo

# Check required environment variables
if [ -z "$GOOGLE_CLOUD_PROJECT" ]; then
    echo -e "${RED}Error: GOOGLE_CLOUD_PROJECT not set${NC}"
    echo "Set it with: export GOOGLE_CLOUD_PROJECT=your-project-id"
    exit 1
fi

REGION=${GOOGLE_CLOUD_REGION:-us-central1}
SERVICE_NAME=${SERVICE_NAME:-python-code-reviewer}

echo -e "${YELLOW}Configuration:${NC}"
echo "  Project: $GOOGLE_CLOUD_PROJECT"
echo "  Region: $REGION"
echo "  Service: $SERVICE_NAME"
echo

# Confirm deployment
read -p "Deploy to Cloud Run? (y/N) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Deployment cancelled"
    exit 0
fi

echo
echo -e "${YELLOW}Step 1: Enabling required APIs...${NC}"
gcloud services enable \
    run.googleapis.com \
    secretmanager.googleapis.com \
    cloudbuild.googleapis.com \
    --project=$GOOGLE_CLOUD_PROJECT

echo
echo -e "${YELLOW}Step 2: Building container image...${NC}"
gcloud builds submit \
    --tag gcr.io/$GOOGLE_CLOUD_PROJECT/$SERVICE_NAME \
    --project=$GOOGLE_CLOUD_PROJECT \
    .

echo
echo -e "${YELLOW}Step 3: Deploying to Cloud Run...${NC}"
gcloud run deploy $SERVICE_NAME \
    --image gcr.io/$GOOGLE_CLOUD_PROJECT/$SERVICE_NAME \
    --platform managed \
    --region $REGION \
    --allow-unauthenticated \
    --set-env-vars PORT=8080 \
    --set-secrets GITHUB_APP_ID=github-app-id:latest,GITHUB_WEBHOOK_SECRET=github-webhook-secret:latest,GITHUB_PRIVATE_KEY=github-app-private-key:latest,GOOGLE_API_KEY=google-api-key:latest \
    --memory 1Gi \
    --cpu 1 \
    --timeout 300 \
    --max-instances 10 \
    --project=$GOOGLE_CLOUD_PROJECT

echo
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Deployment Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo

# Get service URL
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME \
    --platform managed \
    --region $REGION \
    --project=$GOOGLE_CLOUD_PROJECT \
    --format='value(status.url)')

echo -e "${GREEN}Service URL: $SERVICE_URL${NC}"
echo
echo -e "${YELLOW}Next steps:${NC}"
echo "1. Test the service:"
echo "   curl $SERVICE_URL/health"
echo
echo "2. Configure GitHub App webhook URL:"
echo "   Webhook URL: $SERVICE_URL/webhook"
echo
echo "3. Install the GitHub App on your repositories"
echo

echo -e "${YELLOW}To view logs:${NC}"
echo "  gcloud run services logs read $SERVICE_NAME --region $REGION --project $GOOGLE_CLOUD_PROJECT"
echo
