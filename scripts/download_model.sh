#!/usr/bin/env bash
# Download MedGemma 4B model from HuggingFace
# Requires HuggingFace authentication and model access approval

set -euo pipefail

MODEL_ID="google/medgemma-4b-it"
CACHE_DIR="${HF_HOME:-$HOME/.cache/huggingface}"

echo "=== MedGemma Model Download ==="
echo "Model: $MODEL_ID"
echo "Cache: $CACHE_DIR"
echo ""

# Check HuggingFace auth
echo "[1/3] Checking HuggingFace authentication..."
if ! python3 -c "from huggingface_hub import HfApi; HfApi().whoami()" 2>/dev/null; then
    echo "  Not logged in. Running huggingface-cli login..."
    echo "  You need a HuggingFace account with access to $MODEL_ID"
    echo "  Request access at: https://huggingface.co/$MODEL_ID"
    echo ""
    huggingface-cli login
fi
echo "  ✓ Authenticated"

# Download model
echo "[2/3] Downloading model (this may take a while)..."
python3 -c "
from transformers import AutoProcessor, AutoModelForCausalLM

print('  Downloading processor...')
processor = AutoProcessor.from_pretrained('$MODEL_ID', trust_remote_code=True)
print('  ✓ Processor downloaded')

print('  Downloading model weights...')
# Download only — don't load into GPU memory
from huggingface_hub import snapshot_download
snapshot_download('$MODEL_ID', ignore_patterns=['*.gguf'])
print('  ✓ Model downloaded')
"

# Verify
echo "[3/3] Verifying download..."
python3 -c "
from transformers import AutoProcessor
processor = AutoProcessor.from_pretrained('$MODEL_ID', trust_remote_code=True)
print('  ✓ Model files verified')
"

echo ""
echo "=== Download Complete ==="
echo "Model cached at: $CACHE_DIR"
echo "Run the app with: streamlit run src/medlens/app.py"
