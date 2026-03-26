# Project Structure - Image Analysis System

**Complete directory listing with exact case-sensitive names**
Generated: 2026-02-01

## Root Directory
```
image-analysis-system/
├── .claude/
│   └── settings.local.json
├── data/
│   ├── ori_test_images/          # Original test images (100 images)
│   │   ├── test_0001.jpg ... test_0100.jpg
│   │   └── test_images_metadata.json
│   └── test_images/              # User test images
│       └── IMG_*.jpg, IMG*.jpg   # Various test photos
├── databases/                    # Generated - SQLite & LanceDB storage
├── docs/                         # Documentation directory
├── logs/                         # Log files directory
├── models/                       # Generated - ONNX model files
├── outputs/                      # Output directory
├── scripts/
│   ├── fix_clip_export.py
│   ├── fix_clip_export_v2.py
│   ├── prepare_test_data.py
│   └── verify_setup.py
├── src/
│   ├── analysis/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── clip_openai.py
│   │   ├── mobileclip.py
│   │   └── siglip.py
│   ├── ingestion/
│   │   ├── __init__.py
│   │   └── batch_processor.py
│   ├── retrieval/
│   │   ├── __init__.py
│   │   └── search_engine.py
│   ├── storage/
│   │   ├── __init__.py
│   │   ├── lance_store.py
│   │   └── sqlite_store.py
│   ├── __init__.py
│   ├── config.py
│   ├── IMPLEMENTATION_INSTRUCTIONS.md
│   ├── INSTRUCTIONS_Phase1Day2.md
│   ├── INSTRUCTIONS_SiglipSetup.md
│   ├── INSTRUCTIONSMobileClip.md
│   ├── run_batch_ingestion.py
│   ├── test_mobileclip.py
│   ├── test_siglip.py
│   ├── test_single_image.py
│   └── verify_batch.py
├── tests/                        # Unit tests directory
├── venv/                         # Generated - Python virtual environment
├── CLAUDE.md                     # Claude Code instructions
├── compare_search_quality.py
├── GITHUB_WORKFLOW.md
├── MOBILECLIP_SETUP.md
├── PROJECT_STRUCTURE.md          # This file
├── QUICK_REFERENCE_MOBILECLIP.md
├── QUICKSTART.md
├── QUICKSTART-Search.md
├── README.md
├── README-Search.md
├── requirements.txt
├── requirements_search.txt
├── run_batch_ingestion.py
├── SETUP_INSTRUCTIONS.md
└── test_search.py
```

---

## Key Module Classes (Case-Sensitive Reference)

### Storage Module (`src/storage/`)
| File | Class Name | Import Statement |
|------|-----------|------------------|
| `sqlite_store.py` | `SQLiteStore` | `from storage.sqlite_store import SQLiteStore` |
| `lance_store.py` | `LanceStore` | `from storage.lance_store import LanceStore` |

### Analysis Module (`src/analysis/`)
| File | Class Name | Import Statement |
|------|-----------|------------------|
| `base.py` | `EmbeddingModel` | `from analysis.base import EmbeddingModel` |
| `clip_openai.py` | `CLIPOpenAI` | `from analysis.clip_openai import CLIPOpenAI` |
| `mobileclip.py` | `MobileCLIP` | `from analysis.mobileclip import MobileCLIP` |
| `siglip.py` | `SigLIP` | `from analysis.siglip import SigLIP` |

### Retrieval Module (`src/retrieval/`)
| File | Class Name | Import Statement |
|------|-----------|------------------|
| `search_engine.py` | `SearchEngine` | `from retrieval.search_engine import SearchEngine` |

### Ingestion Module (`src/ingestion/`)
| File | Class Name | Import Statement |
|------|-----------|------------------|
| `batch_processor.py` | `BatchProcessor` | `from ingestion.batch_processor import BatchProcessor` |

---

## Important Notes

1. **Class Names vs File Names**:
   - File: `sqlite_store.py` → Class: `SQLiteStore` (NOT `SQLiteImageStore`)
   - File: `lance_store.py` → Class: `LanceStore` (NOT `LanceImageStore`)

2. **Python Module Structure**:
   - All module folders contain `__init__.py`
   - Import paths use dot notation: `from module.file import Class`

3. **Case Sensitivity**:
   - Python files: lowercase with underscores (`snake_case`)
   - Class names: PascalCase (`ClassName`)
   - Module imports: Match exact file/folder names

4. **Generated Directories** (not in version control):
   - `databases/` - Contains `.db` and `.lance` files
   - `models/` - Contains ONNX model files
   - `venv/` - Python virtual environment
   - `__pycache__/` - Python bytecode cache

---

## Common Import Errors to Avoid

❌ **WRONG**:
```python
from storage.sqlite_store import SQLiteImageStore  # Class doesn't exist
from storage.lance_store import LanceImageStore    # Class doesn't exist
from analysis.clip_openai import CLIPEmbedding     # Class doesn't exist
```

✅ **CORRECT**:
```python
from storage.sqlite_store import SQLiteStore
from storage.lance_store import LanceStore
from analysis.clip_openai import CLIPOpenAI
```

---

## Verification Checklist

When adding new imports:
- [ ] Check file name matches exactly (case-sensitive)
- [ ] Check class name matches the definition in the file
- [ ] Verify `__init__.py` exports if importing from module
- [ ] Use relative imports within same package or absolute from `src/`
- [ ] Test import in Python REPL before committing
- [ ] Reference this document for exact class names

---

## Quick Import Test

To verify imports work correctly:
```bash
# From project root
python -c "from src.storage.sqlite_store import SQLiteStore; print('✅ SQLiteStore OK')"
python -c "from src.storage.lance_store import LanceStore; print('✅ LanceStore OK')"
python -c "from src.retrieval.search_engine import SearchEngine; print('✅ SearchEngine OK')"
```

---

*This document should be updated when new files/classes are added to prevent naming conflicts.*
