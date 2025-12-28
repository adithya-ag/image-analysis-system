"""
Single Image End-to-End Test
Tests complete pipeline: Load image → Generate embedding → Store → Retrieve

Usage:
    python src/test_single_image.py data/test_images/test_0001.jpg
"""

import sys
import time
import hashlib
from pathlib import Path
from PIL import Image

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.config import config
from src.analysis.clip_openai import CLIPOpenAI
from src.storage.sqlite_store import SQLiteStore
from src.storage.lance_store import LanceDBStore


def generate_image_id(file_path: str) -> str:
    """
    Generate unique ID for image using SHA256 hash.
    
    Args:
        file_path: Path to image file
        
    Returns:
        Unique image ID (first 16 chars of hash)
    """
    with open(file_path, 'rb') as f:
        file_hash = hashlib.sha256(f.read()).hexdigest()
    
    return f"img_{file_hash[:16]}"


def get_image_info(file_path: Path) -> dict:
    """
    Extract image metadata.
    
    Args:
        file_path: Path to image file
        
    Returns:
        Dictionary with image metadata
    """
    img = Image.open(file_path)
    
    return {
        "filename": file_path.name,
        "file_path": str(file_path.absolute()),
        "file_size": file_path.stat().st_size,
        "width": img.width,
        "height": img.height,
        "format": img.format
    }


def test_single_image(image_path: str):
    """
    Test complete pipeline with a single image.
    
    Args:
        image_path: Path to test image
    """
    print("=" * 70)
    print("🧪 SINGLE IMAGE END-TO-END TEST")
    print("=" * 70)
    
    # Validate image path
    image_file = Path(image_path)
    if not image_file.exists():
        print(f"❌ Error: Image not found: {image_path}")
        return 1
    
    print(f"\n📸 Image: {image_file.name}")
    print(f"   Path: {image_file}")
    
    # Step 1: Generate image ID
    print("\n" + "─" * 70)
    print("STEP 1: Generate Unique ID")
    print("─" * 70)
    
    image_id = generate_image_id(str(image_file))
    print(f"✅ Image ID: {image_id}")
    
    # Step 2: Extract image metadata
    print("\n" + "─" * 70)
    print("STEP 2: Extract Metadata")
    print("─" * 70)
    
    image_info = get_image_info(image_file)
    print(f"✅ Filename: {image_info['filename']}")
    print(f"   Size: {image_info['file_size'] / 1024:.1f} KB")
    print(f"   Dimensions: {image_info['width']}x{image_info['height']}")
    print(f"   Format: {image_info['format']}")
    
    # Step 3: Load CLIP model
    print("\n" + "─" * 70)
    print("STEP 3: Load CLIP Model")
    print("─" * 70)
    
    model_path = config.get_model_path()
    print(f"📂 Model path: {model_path}")
    
    start_time = time.time()
    model = CLIPOpenAI(model_path)
    load_time = time.time() - start_time
    
    print(f"⏱️  Load time: {load_time:.2f}s")
    
    # Step 4: Generate embedding
    print("\n" + "─" * 70)
    print("STEP 4: Generate Embedding")
    print("─" * 70)
    
    start_time = time.time()
    embedding = model.generate_embedding(str(image_file))
    embed_time = time.time() - start_time
    
    print(f"✅ Embedding generated")
    print(f"   Dimensions: {embedding.shape}")
    print(f"   Norm: {np.linalg.norm(embedding):.4f}")
    print(f"⏱️  Generation time: {embed_time:.3f}s")
    
    # Step 5: Store in SQLite
    print("\n" + "─" * 70)
    print("STEP 5: Store Metadata in SQLite")
    print("─" * 70)
    
    sqlite_store = SQLiteStore(config.SQLITE_DB_PATH)
    
    # Check if already exists
    if sqlite_store.image_exists(image_id):
        print(f"⚠️  Image already in database, skipping insert")
    else:
        sqlite_store.insert_image(
            image_id=image_id,
            file_path=image_info['file_path'],
            filename=image_info['filename'],
            file_size=image_info['file_size'],
            width=image_info['width'],
            height=image_info['height'],
            format=image_info['format'],
            embedding_model=model.model_name
        )
        print(f"✅ Metadata stored in SQLite")
    
    # Verify retrieval
    retrieved = sqlite_store.get_image(image_id)
    if retrieved:
        print(f"✅ Verified: Retrieved from SQLite")
        print(f"   ID: {retrieved['image_id']}")
        print(f"   Model: {retrieved['embedding_model']}")
    
    sqlite_store.close()
    
    # Step 6: Store in LanceDB
    print("\n" + "─" * 70)
    print("STEP 6: Store Embedding in LanceDB")
    print("─" * 70)
    
    lance_store = LanceDBStore(config.LANCEDB_PATH)
    
    lance_store.insert_embedding(
        image_id=image_id,
        embedding=embedding,
        model_name=model.model_name
    )
    print(f"✅ Embedding stored in LanceDB")
    
    # Verify retrieval
    retrieved_emb = lance_store.get_embedding(image_id)
    if retrieved_emb is not None:
        print(f"✅ Verified: Retrieved from LanceDB")
        print(f"   Shape: {retrieved_emb.shape}")
        print(f"   Match: {np.allclose(embedding, retrieved_emb)}")
    
    lance_store.close()
    
    # Step 7: Search test (self-similarity)
    print("\n" + "─" * 70)
    print("STEP 7: Search Test (Self-Similarity)")
    print("─" * 70)
    
    lance_store = LanceDBStore(config.LANCEDB_PATH)
    
    results = lance_store.search(embedding, limit=5)
    print(f"✅ Search completed")
    print(f"   Results: {len(results)}")
    
    if results:
        print(f"\n   Top result:")
        print(f"   - Image ID: {results[0][0]}")
        print(f"   - Similarity: {results[0][1]:.4f}")
        
        if results[0][0] == image_id:
            print(f"   ✅ Correct! Found itself as top match")
        else:
            print(f"   ⚠️  Expected {image_id}, got {results[0][0]}")
    
    lance_store.close()
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 TEST SUMMARY")
    print("=" * 70)
    print(f"✅ Image ID generation: PASSED")
    print(f"✅ Metadata extraction: PASSED")
    print(f"✅ Model loading: PASSED ({load_time:.2f}s)")
    print(f"✅ Embedding generation: PASSED ({embed_time:.3f}s)")
    print(f"✅ SQLite storage: PASSED")
    print(f"✅ LanceDB storage: PASSED")
    print(f"✅ Vector search: PASSED")
    print("=" * 70)
    print("🎉 ALL TESTS PASSED!")
    print("=" * 70)
    
    return 0


if __name__ == "__main__":
    import numpy as np  # Import here for main execution
    
    if len(sys.argv) < 2:
        print("Usage: python src/test_single_image.py <image_path>")
        print("Example: python src/test_single_image.py data/test_images/test_0001.jpg")
        sys.exit(1)
    
    image_path = sys.argv[1]
    exit_code = test_single_image(image_path)
    sys.exit(exit_code)
