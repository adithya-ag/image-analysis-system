"""
SQLite Storage - Enhanced for Batch Processing

Handles metadata storage with support for batch operations.

Phase 1 Day 2 - Image Analysis System v0.1
"""

import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, List, Any


class SQLiteStore:
    """SQLite database for image metadata storage"""
    
    def __init__(self, db_path: str):
        """Initialize SQLite connection
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Connect to database
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row  # Access columns by name
        
        # Ensure table exists (should already exist from init_databases.py)
        self._verify_schema()
    
    def _verify_schema(self):
        """Verify that the images table exists with correct schema"""
        cursor = self.conn.cursor()
        
        # Check if table exists
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='images'
        """)
        
        if not cursor.fetchone():
            raise RuntimeError(
                "Images table not found! "
                "Run 'python src/init_databases.py' first to create schema."
            )
    
    def store_image(self, image_id: str, file_path: str, metadata: Dict[str, Any]):
        """Store image metadata
        
        Args:
            image_id: Unique identifier for the image
            file_path: Full path to the image file
            metadata: Dictionary with image metadata
        """
        cursor = self.conn.cursor()
        
        # Prepare data
        now = datetime.now()
        
        cursor.execute("""
            INSERT OR REPLACE INTO images (
                image_id, file_path, filename, file_size_bytes,
                width, height, format, created_at, indexed_at,
                embedding_model, embedding_version,
                access_count
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            image_id,
            file_path,
            metadata.get('filename'),
            metadata.get('file_size_bytes'),
            metadata.get('width'),
            metadata.get('height'),
            metadata.get('format'),
            metadata.get('created_at'),
            now,
            metadata.get('embedding_model'),
            metadata.get('embedding_version'),
            0  # Initial access count
        ))
        
        self.conn.commit()
    
    def get_image(self, image_id: str) -> Optional[Dict]:
        """Retrieve image metadata by ID
        
        Args:
            image_id: Unique identifier for the image
            
        Returns:
            Dictionary with image metadata, or None if not found
        """
        cursor = self.conn.cursor()
        
        cursor.execute("""
            SELECT * FROM images WHERE image_id = ?
        """, (image_id,))
        
        row = cursor.fetchone()
        if row:
            return dict(row)
        return None
    
    def image_exists(self, image_id: str) -> bool:
        """Check if image exists in database
        
        Args:
            image_id: Unique identifier for the image
            
        Returns:
            True if image exists, False otherwise
        """
        cursor = self.conn.cursor()
        
        cursor.execute("""
            SELECT 1 FROM images WHERE image_id = ? LIMIT 1
        """, (image_id,))
        
        return cursor.fetchone() is not None
    
    def count_images(self) -> int:
        """Count total number of images in database
        
        Returns:
            Number of images
        """
        cursor = self.conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM images")
        
        return cursor.fetchone()[0]
    
    def get_all_images(self, limit: Optional[int] = None, offset: int = 0) -> List[Dict]:
        """Get all images from database
        
        Args:
            limit: Maximum number of images to return (None = all)
            offset: Number of images to skip
            
        Returns:
            List of dictionaries with image metadata
        """
        cursor = self.conn.cursor()
        
        if limit is not None:
            cursor.execute("""
                SELECT * FROM images 
                ORDER BY indexed_at DESC
                LIMIT ? OFFSET ?
            """, (limit, offset))
        else:
            cursor.execute("""
                SELECT * FROM images 
                ORDER BY indexed_at DESC
            """)
        
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    
    def update_access_stats(self, image_id: str):
        """Update access statistics for an image
        
        Args:
            image_id: Unique identifier for the image
        """
        cursor = self.conn.cursor()
        now = datetime.now()
        
        cursor.execute("""
            UPDATE images 
            SET last_accessed = ?, 
                access_count = access_count + 1
            WHERE image_id = ?
        """, (now, image_id))
        
        self.conn.commit()
    
    def delete_image(self, image_id: str) -> bool:
        """Delete image metadata
        
        Args:
            image_id: Unique identifier for the image
            
        Returns:
            True if image was deleted, False if not found
        """
        cursor = self.conn.cursor()
        
        cursor.execute("""
            DELETE FROM images WHERE image_id = ?
        """, (image_id,))
        
        deleted = cursor.rowcount > 0
        self.conn.commit()
        
        return deleted
    
    def search_by_filename(self, filename_pattern: str) -> List[Dict]:
        """Search images by filename pattern
        
        Args:
            filename_pattern: SQL LIKE pattern (e.g., 'beach%.jpg')
            
        Returns:
            List of matching images
        """
        cursor = self.conn.cursor()
        
        cursor.execute("""
            SELECT * FROM images 
            WHERE filename LIKE ?
            ORDER BY indexed_at DESC
        """, (filename_pattern,))
        
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    
    def get_stats(self) -> Dict:
        """Get database statistics
        
        Returns:
            Dictionary with statistics
        """
        cursor = self.conn.cursor()
        
        # Total images
        cursor.execute("SELECT COUNT(*) FROM images")
        total_images = cursor.fetchone()[0]
        
        # Total size
        cursor.execute("SELECT SUM(file_size_bytes) FROM images")
        total_bytes = cursor.fetchone()[0] or 0
        
        # Average dimensions
        cursor.execute("""
            SELECT AVG(width), AVG(height) 
            FROM images 
            WHERE width IS NOT NULL AND height IS NOT NULL
        """)
        avg_width, avg_height = cursor.fetchone()
        
        # Format distribution
        cursor.execute("""
            SELECT format, COUNT(*) as count 
            FROM images 
            GROUP BY format
        """)
        formats = {row[0]: row[1] for row in cursor.fetchall()}
        
        return {
            'total_images': total_images,
            'total_size_bytes': total_bytes,
            'total_size_mb': total_bytes / (1024 * 1024),
            'avg_width': avg_width,
            'avg_height': avg_height,
            'formats': formats,
        }
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
    
    def __del__(self):
        """Destructor - ensure connection is closed"""
        self.close()
