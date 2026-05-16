#!/usr/bin/env bash
# deploy.sh — Build and deploy TRACE.ai to Google Cloud Run
# Usage: ./deploy.sh [--skip-build]
#
# Prerequisites:
#   gcloud auth login (already done as animeshraj958@gmail.com)
#   gcloud config set project agrowise-192e3
#
# The google_service_key.json is NEVER baked into the image.
# Cloud Run receives credentials via a mounted secret (see notes at bottom).

set -euo pipefail

PROJECT_ID="agrowise-192e3"
REGION="us-central1"
SERVICE_NAME="trace-ai"
IMAGE="gcr.io/${PROJECT_ID}/${SERVICE_NAME}:latest"
SKIP_BUILD="${1:-}"

# ── Colour helpers ──────────────────────────────────────────────────────────
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'
info()  { echo -e "${GREEN}[INFO]${NC}  $*"; }
warn()  { echo -e "${YELLOW}[WARN]${NC}  $*"; }
error() { echo -e "${RED}[ERROR]${NC} $*" >&2; exit 1; }

# ── 1. Check gcloud auth ────────────────────────────────────────────────────
info "Checking gcloud authentication..."
ACTIVE_ACCOUNT=$(gcloud auth list --filter="status:ACTIVE" --format="value(account)" 2>/dev/null | head -n1)
if [[ -z "$ACTIVE_ACCOUNT" ]]; then
    error "No active gcloud account found. Run: gcloud auth login"
fi
info "Authenticated as: ${ACTIVE_ACCOUNT}"

CURRENT_PROJECT=$(gcloud config get-value project 2>/dev/null)
if [[ "$CURRENT_PROJECT" != "$PROJECT_ID" ]]; then
    warn "Active project is '${CURRENT_PROJECT}', switching to '${PROJECT_ID}'..."
    gcloud config set project "$PROJECT_ID"
fi

# ── 2. Enable required APIs ─────────────────────────────────────────────────
info "Enabling required GCP APIs (this is idempotent)..."
gcloud services enable \
    run.googleapis.com \
    cloudbuild.googleapis.com \
    containerregistry.googleapis.com \
    secretmanager.googleapis.com \
    --project="$PROJECT_ID"

# ── 3. Configure Docker auth for GCR ────────────────────────────────────────
info "Configuring Docker to authenticate with gcr.io..."
gcloud auth configure-docker gcr.io --quiet

# ── 4. Build and push the Docker image ──────────────────────────────────────
if [[ "$SKIP_BUILD" == "--skip-build" ]]; then
    warn "Skipping Docker build (--skip-build passed). Using existing image: ${IMAGE}"
else
    info "Building Docker image: ${IMAGE}"
    info "  Note: Rust compilation will make this ~10-15 min on first build."
    docker build -t "$IMAGE" .

    info "Pushing image to Container Registry..."
    docker push "$IMAGE"
fi

# ── 5. (Optional) Upload service account key as a Secret Manager secret ─────
# Uncomment this block if you want Cloud Run to access google_service_key.json
# via Secret Manager rather than embedding it. The Dockerfile does NOT include it.
#
# SECRET_NAME="trace-ai-service-account"
# if ! gcloud secrets describe "$SECRET_NAME" --project="$PROJECT_ID" &>/dev/null; then
#     info "Creating Secret Manager secret: ${SECRET_NAME}..."
#     gcloud secrets create "$SECRET_NAME" \
#         --replication-policy="automatic" \
#         --project="$PROJECT_ID"
# fi
# info "Uploading google_service_key.json to Secret Manager..."
# gcloud secrets versions add "$SECRET_NAME" \
#     --data-file="google_service_key.json" \
#     --project="$PROJECT_ID"

# ── 6. Deploy to Cloud Run ───────────────────────────────────────────────────
info "Deploying ${SERVICE_NAME} to Cloud Run (${REGION})..."
gcloud run deploy "$SERVICE_NAME" \
    --image="$IMAGE" \
    --platform=managed \
    --region="$REGION" \
    --allow-unauthenticated \
    --memory=2Gi \
    --cpu=2 \
    --timeout=300 \
    --set-env-vars="PYTHONUNBUFFERED=1" \
    --project="$PROJECT_ID"

# ── 7. Print deployed URL ────────────────────────────────────────────────────
SERVICE_URL=$(gcloud run services describe "$SERVICE_NAME" \
    --platform=managed \
    --region="$REGION" \
    --project="$PROJECT_ID" \
    --format="value(status.url)")

echo ""
info "Deployment complete."
echo -e "  ${GREEN}Service URL:${NC} ${SERVICE_URL}"
echo -e "  ${GREEN}Health check:${NC} ${SERVICE_URL}/health"
echo ""
echo "To stream logs:"
echo "  gcloud run services logs read ${SERVICE_NAME} --region=${REGION} --project=${PROJECT_ID}"
echo ""
echo "IMPORTANT: google_service_key.json was NOT deployed with the image."
echo "If the app needs Google Cloud APIs at runtime, mount the secret via:"
echo "  gcloud run services update ${SERVICE_NAME} \\"
echo "    --update-secrets=/secrets/service_account.json=${SECRET_NAME}:latest \\"
echo "    --update-env-vars=GOOGLE_APPLICATION_CREDENTIALS=/secrets/service_account.json \\"
echo "    --region=${REGION} --project=${PROJECT_ID}"
