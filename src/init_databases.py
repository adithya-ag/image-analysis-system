"""
Database Initialization Script
Creates and initializes SQLite (metadata) and LanceDB (vectors) databases.

Usage:
    python src/init_databases.py
"""

import sys
import sqlite3
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


class DatabaseInitializer:
    def __init__(self):
        self.db_dir = PROJECT_ROOT / "databases"
        self.db_dir.mkdir(exist_ok=True)
        
        self.sqlite_path = self.db_dir / "metadata.db"
        self.lance_path = self.db_dir / "embeddings.lance"
    
    def init_sqlite(self):
        """Initialize SQLite database with schema"""
        print("[*] Initializing SQLite database...")
        
        conn = sqlite3.connect(self.sqlite_path)
        cursor = conn.cursor()
        
        # Create images table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS images (
                image_id TEXT PRIMARY KEY,
                file_path TEXT NOT NULL,
                filename TEXT NOT NULL,
                file_size_bytes INTEGER,
                width INTEGER,
                height INTEGER,
                format TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                indexed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                
                -- Placeholder columns for future features (v0.2+)
                tags TEXT,              -- JSON array of tags
                ocr_text TEXT,          -- Extracted text from image
                face_count INTEGER DEFAULT 0,
                face_data TEXT,         -- JSON array of face bounding boxes
                mood TEXT,              -- Mood/emotion analysis
                scene_type TEXT,        -- Indoor/outdoor/etc
                
                -- Model-specific metadata
                embedding_model TEXT,
                embedding_version TEXT,
                
                -- Search optimization
                last_accessed TIMESTAMP,
                access_count INTEGER DEFAULT 0
            )
        """)
        
        # Create indexes for common queries
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_filename ON images(filename)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_created_at ON images(created_at)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_embedding_model ON images(embedding_model)
        """)
        
        # Create search history table (optional)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS search_history (
                search_id INTEGER PRIMARY KEY AUTOINCREMENT,
                query TEXT NOT NULL,
                search_type TEXT,  -- 'text', 'image', etc.
                results_count INTEGER,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                execution_time_ms REAL
            )
        """)
        
        # Create model benchmark table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS model_benchmarks (
                benchmark_id INTEGER PRIMARY KEY AUTOINCREMENT,
                model_name TEXT NOT NULL,
                image_id TEXT,
                processing_time_ms REAL,
                memory_mb REAL,
                embedding_dimension INTEGER,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                
                FOREIGN KEY (image_id) REFERENCES images(image_id)
            )
        """)
        
        conn.commit()
        conn.close()
        
        print(f"[OK] SQLite database created: {self.sqlite_path}")
        print(f"     Tables: images, search_history, model_benchmarks")
    
    def init_lancedb(self):
        """Initialize LanceDB for vector storage"""
        print("\n[*] Initializing LanceDB...")

        try:
            import lancedb
            import pyarrow as pa

            # Create LanceDB connection
            db = lancedb.connect(str(self.lance_path))

            # Define schema for embeddings table
            schema = pa.schema([
                pa.field("image_id", pa.string()),
                pa.field("embedding", pa.list_(pa.float32(), 512)),  # 512-dim vector
                pa.field("model_name", pa.string()),
                pa.field("timestamp", pa.timestamp('ms')),
            ])

            # Create table if it doesn't exist
            # Note: LanceDB creates table on first insert, so this is a placeholder
            print(f"[OK] LanceDB initialized: {self.lance_path}")
            print(f"     Schema: image_id, embedding[512], model_name, timestamp")

        except ImportError:
            print("[WARN] LanceDB not installed. Install with: pip install lancedb pyarrow")
            print("       Creating directory placeholder...")
            self.lance_path.mkdir(exist_ok=True)
            print(f"[OK] LanceDB directory created: {self.lance_path}")
    
    def verify_databases(self):
        """Verify databases are created and accessible"""
        print("\n[*] Verifying databases...")

        # Check SQLite
        if self.sqlite_path.exists():
            conn = sqlite3.connect(self.sqlite_path)
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            conn.close()

            print(f"[OK] SQLite verified: {len(tables)} tables")
            for table in tables:
                print(f"     - {table[0]}")
        else:
            print("[FAIL] SQLite database not found")

        # Check LanceDB
        if self.lance_path.exists():
            print(f"[OK] LanceDB directory verified")
        else:
            print("[FAIL] LanceDB directory not found")
    
    def run(self):
        """Run complete initialization"""
        print("=" * 60)
        print("DATABASE INITIALIZATION")
        print("=" * 60)
        print()

        try:
            self.init_sqlite()
            self.init_lancedb()
            self.verify_databases()

            print("\n" + "=" * 60)
            print("[OK] DATABASE INITIALIZATION COMPLETE")
            print("=" * 60)
            print(f"Database directory: {self.db_dir}")
            print(f"SQLite: {self.sqlite_path}")
            print(f"LanceDB: {self.lance_path}")
            print("=" * 60)

            return 0

        except Exception as e:
            print(f"\n[FAIL] Error during initialization: {e}")
            import traceback
            traceback.print_exc()
            return 1


def main():
    initializer = DatabaseInitializer()
    return initializer.run()


if __name__ == "__main__":
    exit(main())
