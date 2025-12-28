"""
SQLite Storage Layer
Manages structured metadata in SQLite database.
"""

import sqlite3
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime
import json


class SQLiteStore:
    """
    SQLite database interface for image metadata.
    
    Stores:
    - Image paths, file info
    - Model metadata
    - Placeholder columns for future features (v0.2)
    """
    
    def __init__(self, db_path: Union[str, Path]):
        """
        Initialize SQLite connection.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = Path(db_path)
        self.connection = None
        self.connect()
    
    def connect(self) -> None:
        """Open connection to SQLite database"""
        self.connection = sqlite3.connect(str(self.db_path))
        self.connection.row_factory = sqlite3.Row  # Return rows as dictionaries
        
        # Ensure tables exist
        self._ensure_tables()
    
    def _ensure_tables(self) -> None:
        """
        Create tables if they don't exist.
        Schema includes placeholder columns for v0.2 features.
        """
        cursor = self.connection.cursor()
        
        # Images table
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
                
                -- Placeholder columns for v0.2 features
                tags TEXT,              -- JSON array
                ocr_text TEXT,
                face_count INTEGER DEFAULT 0,
                face_data TEXT,         -- JSON array
                mood TEXT,
                scene_type TEXT,
                
                -- Model metadata
                embedding_model TEXT,
                embedding_version TEXT,
                
                -- Search optimization
                last_accessed TIMESTAMP,
                access_count INTEGER DEFAULT 0
            )
        """)
        
        # Indexes
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_filename ON images(filename)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_embedding_model ON images(embedding_model)
        """)
        
        self.connection.commit()
    
    def insert_image(
        self,
        image_id: str,
        file_path: str,
        filename: str,
        file_size: int,
        width: int,
        height: int,
        format: str,
        embedding_model: str,
        **kwargs
    ) -> None:
        """
        Insert new image record.
        
        Args:
            image_id: Unique image identifier
            file_path: Full path to image file
            filename: Image filename
            file_size: File size in bytes
            width: Image width in pixels
            height: Image height in pixels
            format: Image format (JPEG, PNG, etc.)
            embedding_model: Model used for embedding
            **kwargs: Additional fields (tags, ocr_text, etc.)
        """
        cursor = self.connection.cursor()
        
        now = datetime.now()
        
        cursor.execute("""
            INSERT INTO images (
                image_id, file_path, filename, file_size_bytes,
                width, height, format, embedding_model,
                created_at, indexed_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            image_id, file_path, filename, file_size,
            width, height, format, embedding_model,
            now, now
        ))
        
        self.connection.commit()
    
    def get_image(self, image_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve image record by ID.
        
        Args:
            image_id: Image identifier
            
        Returns:
            Image metadata as dictionary, or None if not found
        """
        cursor = self.connection.cursor()
        
        cursor.execute("""
            SELECT * FROM images WHERE image_id = ?
        """, (image_id,))
        
        row = cursor.fetchone()
        
        if row:
            return dict(row)
        return None
    
    def get_all_images(self) -> List[Dict[str, Any]]:
        """
        Get all image records.
        
        Returns:
            List of image metadata dictionaries
        """
        cursor = self.connection.cursor()
        
        cursor.execute("""
            SELECT * FROM images ORDER BY indexed_at DESC
        """)
        
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    
    def update_access(self, image_id: str) -> None:
        """
        Update access timestamp and count for an image.
        
        Args:
            image_id: Image identifier
        """
        cursor = self.connection.cursor()
        
        cursor.execute("""
            UPDATE images
            SET last_accessed = ?,
                access_count = access_count + 1
            WHERE image_id = ?
        """, (datetime.now(), image_id))
        
        self.connection.commit()
    
    def image_exists(self, image_id: str) -> bool:
        """
        Check if image exists in database.
        
        Args:
            image_id: Image identifier
            
        Returns:
            True if exists, False otherwise
        """
        cursor = self.connection.cursor()
        
        cursor.execute("""
            SELECT 1 FROM images WHERE image_id = ? LIMIT 1
        """, (image_id,))
        
        return cursor.fetchone() is not None
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get database statistics.
        
        Returns:
            Statistics dictionary
        """
        cursor = self.connection.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM images")
        total_images = cursor.fetchone()[0]
        
        cursor.execute("SELECT embedding_model, COUNT(*) FROM images GROUP BY embedding_model")
        models = {row[0]: row[1] for row in cursor.fetchall()}
        
        return {
            "total_images": total_images,
            "models": models
        }
    
    def close(self) -> None:
        """Close database connection"""
        if self.connection:
            self.connection.close()
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()


# Add missing import
from typing import Union
