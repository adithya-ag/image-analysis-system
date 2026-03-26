# Local-First Image Analysis System

**Version:** v0.1.0 (Embeddings-Only Semantic Search)
**Status:** Phase 1 Complete - Multi-Model Semantic Search
**License:** MIT

## Overview

A local-first image analysis system that enables semantic search over personal photo collections without sending data to external servers. Built for Windows with cross-platform architecture.

### Current Capabilities (v0.1)

- Image ingestion with unique ID generation
- Embedding extraction using 3 vision models (CLIP, MobileCLIP, SigLIP)
- Hybrid storage (SQLite metadata + LanceDB vectors)
- Semantic text-to-image search
- Multi-model comparison and benchmarking tools
- ONNX Runtime inference with optional OpenVINO GPU acceleration

### Roadmap

- **v0.2:** OCR, face detection, mood extraction, CLIP text encoding via ONNX
- **v0.3:** GUI, background processing, incremental updates
- **v1.0:** Production release with Android support

## Architecture

```
CLI / Scripts
      │
┌─────▼─────────────────────────────────┐
│              Core Engine              │
│  ┌────────────┐   ┌────────────────┐  │
│  │ Ingestion  │ → │    Analysis    │  │
│  │  Module    │   │   Plugins      │  │
│  └────────────┘   └───────┬────────┘  │
│                           │           │
│  ┌────────────────────────▼────────┐  │
│  │         Storage Layer           │  │
│  │  SQLite (metadata.db)           │  │
│  │  LanceDB (embeddings.lance)     │  │
│  └────────────────────────┬────────┘  │
└───────────────────────────┼───────────┘
                            │
┌───────────────────────────▼───────────┐
│         Retrieval & Search            │
│  Text Query → Embedding → Cosine      │
│  Similarity → Ranked Results          │
└───────────────────────────────────────┘
```

## Models

| Model | Embedding Dim | Image | Text | Notes |
|-------|--------------|-------|------|-------|
| CLIP ViT-B/32 | 512D | ✅ | ⚠️ PyTorch fallback | ONNX via optimum; text encoding uses PyTorch in search |
| MobileCLIP-S2 | 512D | ✅ | ✅ | Dual ONNX encoders (image + text); lightest option |
| SigLIP-2 Base | 768D | ✅ | ⚠️ Zero vector fallback | Combined ONNX model; text encoding in progress |

Active model is configured in `src/config.py` (`active_model` field).

## Tech Stack

- **Language:** Python 3.11
- **Vision Models:** CLIP ViT-B/32, MobileCLIP-S2, SigLIP-2 Base
- **ML Runtime:** ONNX Runtime + OpenVINO (Intel GPU acceleration)
- **Databases:** SQLite + LanceDB
- **Image Processing:** OpenCV + Pillow

## Quick Start

### Prerequisites

- Windows 11
- Python 3.11.x
- 12-16GB RAM minimum
- Intel integrated GPU (or discrete GPU)

### Installation

```bash
# Clone repository
git clone https://github.com/YOUR_USERNAME/image-analysis-system.git
cd image-analysis-system

# Create virtual environment
py -3.11 -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install PyTorch CPU-only (separate step to avoid CUDA downloads)
pip install torch==2.5.1+cpu --index-url https://download.pytorch.org/whl/cpu

# Download and convert CLIP to ONNX
pip install optimum[onnxruntime] onnx
python scripts/setup_models.py

# Initialize databases
python src/init_databases.py

# Verify setup
python scripts/verify_setup.py
```

## Usage

### Index Images

```bash
# Batch index a folder (uses active_model from config.py)
python run_batch_ingestion.py
```

### Search

```bash
# Run semantic search with sample queries
python test_search.py

# Search a specific query programmatically
python -c "
from src.retrieval.search_engine import SearchEngine
engine = SearchEngine('mobileclip')
engine.search_and_display('beach sunset', top_k=5)
"
```

### Compare Models

```bash
# Compare search quality across all models
python compare_search_quality.py

# Validate ONNX encoder outputs
python test_onnx_encoders.py

# Inspect MobileCLIP ONNX model structure
python inspect_mobileclip_onnx.py
```

### Switch Active Model

```python
# In src/config.py, change:
active_model = "mobileclip"  # Options: "clip", "mobileclip", "siglip"
```

Then re-index images with the new model:

```bash
# 1. Delete existing databases
del databases\metadata.db
rmdir /s databases\embeddings.lance

# 2. Re-initialize
python src\init_databases.py

# 3. Re-run batch processing
python run_batch_ingestion.py
```

## Project Structure

```
image-analysis-system/
├── src/                        # Source code
│   ├── analysis/               # Embedding model plugins
│   │   ├── base.py             # Abstract EmbeddingModel interface
│   │   ├── clip_openai.py      # CLIP ViT-B/32 (ONNX)
│   │   ├── mobileclip.py       # MobileCLIP-S2 (dual ONNX)
│   │   └── siglip.py           # SigLIP-2 Base (ONNX)
│   ├── ingestion/              # Image loading and ID generation
│   │   └── batch_processor.py  # Batch ingestion pipeline
│   ├── storage/                # Database interfaces
│   │   ├── sqlite_store.py     # SQLite metadata store
│   │   └── lance_store.py      # LanceDB vector store
│   ├── retrieval/              # Search module
│   │   └── search_engine.py    # Text-to-image semantic search
│   ├── config.py               # Multi-model configuration
│   └── init_databases.py       # Database schema initialization
├── scripts/                    # Setup and utility scripts
│   ├── setup_models.py         # Download and convert CLIP to ONNX
│   └── verify_setup.py         # Verify installation
├── run_batch_ingestion.py      # CLI: batch index images
├── test_search.py              # Test semantic search queries
├── test_onnx_encoders.py       # Validate ONNX encoder outputs
├── compare_search_quality.py   # Compare search across models
├── inspect_mobileclip_onnx.py  # Inspect ONNX model structure
├── models/                     # ONNX models (gitignored)
├── databases/                  # SQLite + LanceDB files (gitignored)
├── data/                       # Test images (gitignored)
├── tests/                      # Unit tests
└── requirements.txt            # Python dependencies
```

## Development

### Team Workflow

1. Create feature branch: `git checkout -b feature/your-feature`
2. Make changes and commit
3. Push and create Pull Request
4. Team review → merge to `develop`
5. Periodic merges to `main` for releases

### Running Tests

```bash
pytest tests/
python test_onnx_encoders.py
python test_search.py
```

### Code Style

```bash
# Format code
black src/

# Lint
flake8 src/
```

## Performance Targets (v0.1)

| Metric | Target | Status |
|--------|--------|--------|
| Embedding generation | <1s per image | Testing |
| Search latency | <500ms for 10K images | Testing |
| Memory usage | <4GB during indexing | Testing |
| Accuracy (beach sunset) | >80% relevant results | Testing |

## Documentation

- [Setup Instructions](SETUP_INSTRUCTIONS.md) - Detailed installation guide
- [Architecture Document](docs/Strategic_Architecture.md) - High-level design

## Contributing

This project will be open-sourced after initial development phase. Contributions welcome!

### Current Team

- 3 core developers
- Planning public release: Q1 2026

## License

MIT License - See [LICENSE](LICENSE) for details

## Acknowledgments

- CLIP ViT-B/32 by OpenAI
- MobileCLIP by Apple
- SigLIP-2 by Google
- LanceDB vector database
- HuggingFace Transformers & Optimum

## Contact

For questions or collaboration: [Add contact info]
