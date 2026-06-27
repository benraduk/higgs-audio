#!/usr/bin/env bash
# Start local Higgs Audio v3 server via SGLang-Omni.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_FILE="$SCRIPT_DIR/.env"

if [[ -f "$ENV_FILE" ]]; then
  # shellcheck disable=SC1090
  source "$ENV_FILE"
fi

MODEL_ID="${MODEL_ID:-bosonai/higgs-audio-v3-tts-4b}"
MODEL_LOCAL_DIR="${MODEL_LOCAL_DIR:-}"
SGLANG_OMNI_DIR="${SGLANG_OMNI_DIR:-$(dirname "$SCRIPT_DIR/../../")/sglang-omni}"
SERVE_PORT="${SERVE_PORT:-8000}"
SERVE_HOST="${SERVE_HOST:-0.0.0.0}"

if [[ -z "$MODEL_LOCAL_DIR" ]]; then
  MODEL_PATH="$MODEL_ID"
else
  MODEL_PATH="$MODEL_LOCAL_DIR"
fi

if [[ ! -d "$SGLANG_OMNI_DIR/.venv" ]]; then
  echo "ERROR: SGLang-Omni venv not found. Run ./scripts/v3/setup_gpu.sh first."
  exit 1
fi

# shellcheck disable=SC1091
source "$SGLANG_OMNI_DIR/.venv/bin/activate"

ALLOWED_MEDIA="${SGLANG_OMNI_DIR}/docs/_static/audio"

echo "Serving $MODEL_PATH on http://${SERVE_HOST}:${SERVE_PORT}"
echo "OpenAI-compatible endpoint: POST /v1/audio/speech"

exec sgl-omni serve \
  --model-path "$MODEL_PATH" \
  --host "$SERVE_HOST" \
  --port "$SERVE_PORT" \
  --allowed-local-media-path "$ALLOWED_MEDIA"
