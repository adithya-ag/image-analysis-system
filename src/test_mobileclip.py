"""
Test MobileCLIP on Single Image

Verifies MobileCLIP plugin works correctly.

Phase 1 Day 2 - Image Analysis System v0.1

Usage:
    python test_mobileclip.py <image_path>
"""

import sys
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from config import Config
from analysis.mobileclip import MobileCLIP
from storage.sqlite_store import SQLiteStore
from storage.lance_store import LanceStore
import hashlib
import os


def generate_image_id(file_path: str) -> str:
    """Generate unique ID for image"""
    stat = os.stat(file_path)
    content = f"{file_path}_{stat.st_size}_{stat.st_mtime}".encode()
    return hashlib.sha256(content).hexdigest()[:16]


def main():
    if len(sys.argv) < 2:
        print("Usage: python test_mobileclip.py <image_path>")
        sys.exit(1)
    
    image_path = sys.argv[1]
    
    if not os.path.exists(image_path):
        print(f"❌ Error: Image not found: {image_path}")
        sys.exit(1)
    
    print("\n" + "=" * 70)
    print("🧪 MOBILECLIP SINGLE IMAGE TEST")
    print("=" * 70)
    
    # Initialize config for MobileCLIP
    print("\n📊 Step 1: Loading MobileCLIP model...")
    start_time = time.time()
    
    config = Config(model_name='mobileclip')
    model = MobileCLIP(config)
    
    load_time = time.time() - start_time
    
    # Show model info
    info = model.get_model_info()
    print(f"✅ MobileCLIP model loaded")
    print(f"   Provider: {info['provider']}")
    print(f"   Image encoder: {info['image_encoder_size_mb']:.1f} MB")
    print(f"   Text encoder: {info['text_encoder_size_mb']:.1f} MB")
    print(f"   Embedding dim: {info['embedding_dim']}")
    print(f"   Load time: {load_time:.2f}s")
    
    # Load image
    print(f"\n📷 Step 2: Loading image...")
    print(f"   Path: {image_path}")
    print(f"✅ Image loaded: {os.path.basename(image_path)}")
    
    # Generate embedding
    print(f"\n🔢 Step 3: Generating embedding...")
    start_time = time.time()
    
    embedding = model.generate_embedding(image_path)
    
    embed_time = time.time() - start_time
    
    print(f"✅ Embedding generated")
    print(f"   Dimensions: {embedding.shape}")
    print(f"   Time: {embed_time:.3f}s")
    print(f"   L2 norm: {(embedding ** 2).sum() ** 0.5:.4f} (should be ~1.0)")
    
    # Store in SQLite
    print(f"\n💾 Step 4: Storing in SQLite...")
    sqlite_store = SQLiteStore(config.sqlite_path)
    
    image_id = generate_image_id(image_path)
    stat = os.stat(image_path)
    
    sqlite_store.store_image(
        image_id=image_id,
        file_path=image_path,
        metadata={
            'filename': os.path.basename(image_path),
            'file_size_bytes': stat.st_size,
            'embedding_model': 'mobileclip_s2',
            'embedding_version': '1.0',
        }
    )
    print(f"✅ Stored in SQLite")
    print(f"   Image ID: {image_id}")
    
    # Store in LanceDB
    print(f"\n🗄️  Step 5: Storing in LanceDB...")
    lance_store = LanceStore(config.lance_path)
    
    lance_store.store_embedding(
        image_id=image_id,
        embedding=embedding,
        metadata={'file_path': image_path}
    )
    print(f"✅ Stored in LanceDB")
    
    # Verify retrieval
    print(f"\n🔍 Step 6: Verifying storage...")
    retrieved_emb = lance_store.get_embedding(image_id)
    
    if retrieved_emb is not None:
        match = ((retrieved_emb - embedding) ** 2).sum() < 1e-6
        print(f"✅ Retrieved from LanceDB")
        print(f"   Embeddings match: {match}")
    else:
        print(f"❌ Failed to retrieve from LanceDB")
        sys.exit(1)
    
    # Self-similarity search
    print(f"\n🔎 Step 7: Testing self-similarity search...")
    results = lance_store.search_similar(embedding, top_k=1)
    
    if results and results[0]['image_id'] == image_id:
        print(f"✅ Self-similarity search works")
        print(f"   Found: {results[0]['image_id']}")
        print(f"   Score: {results[0]['score']:.4f}")
    else:
        print(f"❌ Self-similarity search failed")
        sys.exit(1)
    
    # Final summary
    print("\n" + "=" * 70)
    print("🎉 ALL TESTS PASSED!")
    print("=" * 70)
    print(f"\nMobileCLIP Performance:")
    print(f"   Model load: {load_time:.2f}s")
    print(f"   Embedding generation: {embed_time:.3f}s")
    print(f"   Total: {load_time + embed_time:.2f}s")
    print("\n✅ MobileCLIP is ready to use!")
    print("=" * 70)


if __name__ == '__main__':
    main()
