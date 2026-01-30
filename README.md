# 🖼️ Local-First Image Analysis System

**Version:** v0.1.0 (Embeddings-Only Semantic Search)  
**Status:** 🚧 In Development - Phase 1  
**License:** MIT  

## Overview

A local-first image analysis system that enables semantic search over personal photo collections without sending data to external servers. Built for Windows with cross-platform architecture.

### Current Capabilities (v0.1)

- ✅ Image ingestion with unique ID generation
- ✅ Embedding extraction using vision models (SmolVLM-500M, MobileCLIP-S2)
- ✅ Hybrid storage (SQLite metadata + LanceDB vectors)
- ✅ Semantic search via text queries
- ✅ CLI interface

### Roadmap

- **v0.2:** OCR, face detection, mood extraction
- **v0.3:** GUI, background processing, incremental updates
- **v1.0:** Production release with Android support

## Architecture

```
┌─────────────────┐
│   CLI/GUI       │
└────────┬────────┘
         │
┌────────▼────────────────────────────┐
│         Core Engine                 │
│  ┌──────────┐  ┌──────────────┐    │
│  │ Ingestion│  │   Analysis   │    │
│  │  Module  │→ │   Plugins    │    │
│  └──────────┘  └──────┬───────┘    │
│                       │             │
│  ┌────────────────────▼───────────┐ │
│  │      Storage Layer             │ │
│  │  SQLite (metadata)             │ │
│  │  LanceDB (vectors)             │ │
│  └────────────────────┬───────────┘ │
└────────────────────────┼────────────┘
                         │
┌────────────────────────▼───────────┐
│      Retrieval & Search            │
│  Text Query → Vector Search        │
│  → Ranked Results                  │
└────────────────────────────────────┘
```
# To switch models: Just change 'active_model' in config.py
# Then re-run: python run_batch_ingestion.py

# 1. Delete both databases
del databases\metadata.db
rmdir /s databases\embeddings.lance

# 2. Re-initialize databases
python src\init_databases.py

# 3. Re-run batch processing
python run_batch_ingestion.py

# 4. Verify (should show 100/100 match)
python src\verify_batch.py

## Tech Stack

- **Language:** Python 3.11
- **Vision Models:** SmolVLM-500M (primary), MobileCLIP-S2 (benchmark)
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
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Download models
python scripts/setup_models.py

# Initialize databases
python src/init_databases.py
```

**Detailed setup instructions:** See [SETUP_INSTRUCTIONS.md](SETUP_INSTRUCTIONS.md)

## Usage

### Index Images

```bash
# Index a folder of images
python src/ingest.py --folder "C:\Photos\Vacation2024"
```

### Search

```bash
# Search with text query
python src/search.py --query "beach sunset"

# Results:
# 1. IMG_5432.jpg (score: 0.87)
# 2. IMG_5433.jpg (score: 0.85)
# 3. IMG_5401.jpg (score: 0.82)
```

### Benchmark Models

```bash
# Compare SmolVLM vs MobileCLIP performance
python src/benchmark.py --folder "C:\Photos\TestSet"
```

## Project Structure

```
image-analysis-system/
├── src/                    # Source code
│   ├── ingestion/         # Image ingestion module
│   ├── analysis/          # Embedding extraction plugins
│   ├── storage/           # Database interfaces
│   └── retrieval/         # Search module
├── scripts/               # Setup and utility scripts
├── models/                # ONNX models (gitignored)
├── databases/             # SQLite + LanceDB files (gitignored)
├── data/                  # Test images (gitignored)
├── tests/                 # Unit tests
├── docs/                  # Documentation
└── requirements.txt       # Python dependencies
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
| Embedding generation | <1s per image | 🚧 Testing |
| Search latency | <500ms for 10K images | 🚧 Testing |
| Memory usage | <4GB during indexing | 🚧 Testing |
| Accuracy (beach sunset) | >80% relevant results | 🚧 Testing |

## Documentation

- [Setup Instructions](SETUP_INSTRUCTIONS.md) - Detailed installation guide
- [Architecture Document](docs/Strategic_Architecture.md) - High-level design
- [API Reference](docs/API.md) - Module interfaces (coming soon)

## Contributing

This project will be open-sourced after initial development phase. Contributions welcome!

### Current Team

- 3 core developers
- Planning public release: Q1 2026

## License

MIT License - See [LICENSE](LICENSE) for details

## Acknowledgments

- SmolVLM-500M by HuggingFace
- MobileCLIP by Apple
- LanceDB vector database

## Contact

For questions or collaboration: [Add contact info]

---

**Status:** 🚧 Phase 1 in progress - Foundation & Core Pipeline (Days 1-4/7)
