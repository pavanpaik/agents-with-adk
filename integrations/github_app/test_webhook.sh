#!/bin/bash
#
# Test GitHub App webhook locally
#
# Usage:
#   ./test_webhook.sh [local|remote]
#
# Examples:
#   ./test_webhook.sh local   # Test local server at localhost:8080
#   ./test_webhook.sh remote  # Test deployed Cloud Run service
#

MODE=${1:-local}

if [ "$MODE" == "local" ]; then
    WEBHOOK_URL="http://localhost:8080/webhook"
elif [ "$MODE" == "remote" ]; then
    # Get Cloud Run service URL
    WEBHOOK_URL=$(gcloud run services describe python-code-reviewer \
        --region us-central1 \
        --format='value(status.url)')/webhook
else
    echo "Usage: $0 [local|remote]"
    exit 1
fi

echo "Testing webhook at: $WEBHOOK_URL"
echo

# Test 1: Ping event
echo "Test 1: Ping event"
curl -X POST "$WEBHOOK_URL" \
    -H "Content-Type: application/json" \
    -H "X-GitHub-Event: ping" \
    -H "X-Hub-Signature-256: sha256=$(echo -n '{"hook_id":123}' | openssl dgst -sha256 -hmac "${GITHUB_WEBHOOK_SECRET:-test}" | cut -d' ' -f2)" \
    -d '{"hook_id":123}'
echo
echo

# Test 2: Pull Request event (mock)
echo "Test 2: Mock Pull Request event"
cat << 'EOF' > /tmp/pr_payload.json
{
  "action": "opened",
  "pull_request": {
    "number": 123,
    "title": "Test PR"
  },
  "repository": {
    "full_name": "test/repo"
  },
  "installation": {
    "id": 12345
  }
}
EOF

curl -X POST "$WEBHOOK_URL" \
    -H "Content-Type: application/json" \
    -H "X-GitHub-Event: pull_request" \
    -H "X-Hub-Signature-256: sha256=$(cat /tmp/pr_payload.json | openssl dgst -sha256 -hmac "${GITHUB_WEBHOOK_SECRET:-test}" | cut -d' ' -f2)" \
    -d @/tmp/pr_payload.json
echo
echo

rm /tmp/pr_payload.json

# Test 3: Health check
echo "Test 3: Health check"
curl "${WEBHOOK_URL/\/webhook/\/health}"
echo
echo

echo "Tests complete!"
