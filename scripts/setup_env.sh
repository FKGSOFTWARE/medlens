#!/usr/bin/env bash
# MedLens Environment Setup
# Validates Python, CUDA, installs dependencies, checks VRAM

set -euo pipefail

echo "=== MedLens Environment Setup ==="

# Check Python version
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
PYTHON_MAJOR=$(echo "$PYTHON_VERSION" | cut -d. -f1)
PYTHON_MINOR=$(echo "$PYTHON_VERSION" | cut -d. -f2)

echo "[1/5] Python version: $PYTHON_VERSION"
if [ "$PYTHON_MAJOR" -lt 3 ] || [ "$PYTHON_MINOR" -lt 10 ]; then
    echo "ERROR: Python 3.10+ required, found $PYTHON_VERSION"
    exit 1
fi
echo "  ✓ Python OK"

# Check CUDA
echo "[2/5] Checking CUDA..."
if command -v nvidia-smi &> /dev/null; then
    CUDA_VERSION=$(nvidia-smi | grep "CUDA Version" | awk '{print $9}')
    echo "  CUDA Version: $CUDA_VERSION"
    GPU_NAME=$(nvidia-smi --query-gpu=name --format=csv,noheader | head -1)
    GPU_VRAM=$(nvidia-smi --query-gpu=memory.total --format=csv,noheader | head -1)
    echo "  GPU: $GPU_NAME ($GPU_VRAM)"
    echo "  ✓ CUDA OK"
else
    echo "  ⚠ nvidia-smi not found. CUDA may not be available."
    echo "  MedLens requires a CUDA-capable GPU with ≥12GB VRAM."
fi

# Check VRAM
echo "[3/5] Checking VRAM..."
if command -v nvidia-smi &> /dev/null; then
    VRAM_MB=$(nvidia-smi --query-gpu=memory.total --format=csv,noheader,nounits | head -1 | tr -d ' ')
    VRAM_GB=$((VRAM_MB / 1024))
    echo "  Available VRAM: ${VRAM_GB}GB"
    if [ "$VRAM_GB" -lt 12 ]; then
        echo "  ⚠ WARNING: ${VRAM_GB}GB VRAM detected. MedGemma 4B quantized needs ≥12GB."
    else
        echo "  ✓ VRAM OK"
    fi
fi

# Install Python dependencies
echo "[4/5] Installing Python dependencies..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    echo "  ✓ Dependencies installed"
else
    echo "  ERROR: requirements.txt not found. Run from project root."
    exit 1
fi

# Verify key imports
echo "[5/5] Verifying imports..."
python3 -c "
import torch
print(f'  PyTorch: {torch.__version__}')
print(f'  CUDA available: {torch.cuda.is_available()}')
if torch.cuda.is_available():
    print(f'  CUDA device: {torch.cuda.get_device_name(0)}')
import transformers
print(f'  Transformers: {transformers.__version__}')
import streamlit
print(f'  Streamlit: {streamlit.__version__}')
print('  ✓ All imports OK')
"

echo ""
echo "=== Setup Complete ==="
echo "Next: Run 'bash scripts/download_model.sh' to download MedGemma"
