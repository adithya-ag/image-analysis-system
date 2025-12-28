# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Local-first image analysis system enabling semantic search over personal photo collections without external servers. Currently in Phase 1 development (v0.1.0 - Embeddings-Only Semantic Search).

## Common Commands

```bash
# Environment setup (requires Python 3.11)
py -3.11 -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install PyTorch CPU-only (separate step to avoid CUDA downloads)
pip install torch==2.5.1+cpu --index-url https://download.pytorch.org/whl/cpu

# Model setup (downloads and converts CLIP to ONNX)
pip install optimum[onnxruntime] onnx
python scripts/setup_models.py

# Or manual model conversion
cd models
optimum-cli export onnx --model openai/clip-vit-base-patch32 --task feature-extraction clip_vit_b32/

# Database initialization
python src/init_databases.py

# Verification
python scripts/verify_setup.py

# Testing and linting
pytest tests/
black src/
flake8 src/
```

## Architecture

```
CLI/GUI → Core Engine → Storage Layer → Retrieval
              │
    ┌─────────┴─────────┐
    │                   │
Ingestion          Analysis
(Image loading)    (Embedding extraction via ONNX models)
    │                   │
    └─────────┬─────────┘
              │
    Storage Layer
    ├── SQLite (metadata.db) - image metadata, search history
    └── LanceDB (embeddings.lance) - 512-dim vectors
```

### Module Structure

- `src/ingestion/` - Image loading, format validation, ID generation
- `src/analysis/` - Embedding extraction using CLIP ViT-B/32
- `src/storage/` - Database interfaces for SQLite and LanceDB
- `src/retrieval/` - Text-to-vector search, result ranking

### Models

**v0.1 (Current):**
- **CLIP ViT-B/32** - OpenAI's vision-language model for text-image embeddings (512-dim)

**Deferred to v0.2** (pending optimum export support):
- SmolVLM-500M - Idefics3 architecture not supported by optimum
- MobileCLIP-S2 - Requires custom export handling

The model outputs 512-dimensional embeddings and runs via ONNX Runtime with optional OpenVINO acceleration.

## Key Dependencies

- `transformers>=4.57.3` - Required for CLIP model loading
- `tokenizers>=0.22.1` - Fast tokenization backend
- `torch==2.5.1+cpu` - PyTorch CPU-only for model export
- `onnxruntime` + `openvino` - ML inference
- `lancedb` - Vector database
- `optimum[onnxruntime]` - Model conversion tools

## Git Workflow

Uses Git Flow: `main` (protected) ← `develop` ← `feature/*` branches

Commit message format:
```
<type>: <description>
# Types: feat, fix, docs, refactor, test, chore
```

## Database Schema

SQLite `images` table stores: image_id, file_path, dimensions, format, embedding_model, and placeholders for future v0.2 features (OCR, face detection, mood).

LanceDB stores: image_id, 512-dim float32 embedding vector, model_name, timestamp.
