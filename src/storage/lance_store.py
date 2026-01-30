"""
LanceDB Storage - Enhanced for Batch Processing

Handles vector embeddings storage with support for batch operations.

Phase 1 Day 2 - Image Analysis System v0.1
"""

import lancedb
import numpy as np
from pathlib import Path
from typing import Optional, Dict, List


class LanceStore:
    """LanceDB for vector embeddings storage"""
    
    def __init__(self, db_path: str, table_name: str = "image_embeddings"):
        """Initialize LanceDB connection
        
        Args:
            db_path: Path to LanceDB directory
            table_name: Name of the embeddings table
        """
        self.db_path = Path(db_path)
        self.table_name = table_name
        
        # Create directory if it doesn't exist
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Connect to database
        self.db = lancedb.connect(str(self.db_path))
        
        # Try to open existing table
        try:
            self.table = self.db.open_table(table_name)
        except Exception:
            # Table doesn't exist yet - it will be created on first store
            self.table = None
    
    def store_embedding(self, image_id: str, embedding: np.ndarray, metadata: Optional[Dict] = None):
        """Store image embedding
        
        Args:
            image_id: Unique identifier for the image
            embedding: Embedding vector (numpy array)
            metadata: Optional metadata dictionary
        """
        # Ensure embedding is 1D numpy array
        if len(embedding.shape) > 1:
            embedding = embedding.flatten()
        
        # Prepare data
        data = {
            'image_id': image_id,
            'vector': embedding.tolist(),
        }
        
        # Add metadata if provided
        if metadata:
            for key, value in metadata.items():
                if key not in ['image_id', 'vector']:
                    data[key] = value
        
        # Create or append to table
        if self.table is None:
            # Create new table
            self.table = self.db.create_table(
                self.table_name,
                data=[data]
            )
        else:
            # Append to existing table
            # Note: LanceDB's add() doesn't support upsert, so we need to check for duplicates
            # For now, we'll just append (in production, we'd handle duplicates properly)
            self.table.add([data])
    
    def get_embedding(self, image_id: str) -> Optional[np.ndarray]:
        """Retrieve embedding for an image
        
        Args:
            image_id: Unique identifier for the image
            
        Returns:
            Embedding vector as numpy array, or None if not found
        """
        if self.table is None:
            return None
        
        # Search for the image
        results = self.table.search() \
            .where(f"image_id = '{image_id}'") \
            .limit(1) \
            .to_list()
        
        if results:
            return np.array(results[0]['vector'])
        return None
    
    def search_similar(
        self, 
        query_embedding: np.ndarray, 
        top_k: int = 10,
        filter_image_id: Optional[str] = None
    ) -> List[Dict]:
        """Search for similar images
        
        Args:
            query_embedding: Query embedding vector
            top_k: Number of results to return
            filter_image_id: If provided, only return this specific image
            
        Returns:
            List of dictionaries with image_id and similarity score
        """
        if self.table is None:
            return []
        
        # Ensure embedding is 1D
        if query_embedding is not None and len(query_embedding.shape) > 1:
            query_embedding = query_embedding.flatten()
        
        # If filtering by specific ID
        if filter_image_id:
            results = self.table.search() \
                .where(f"image_id = '{filter_image_id}'") \
                .limit(1) \
                .to_list()
        elif query_embedding is not None:
            # Vector similarity search
            results = self.table.search(query_embedding.tolist()) \
                .limit(top_k) \
                .to_list()
        else:
            return []
        
        # Format results
        formatted_results = []
        for result in results:
            formatted_results.append({
                'image_id': result['image_id'],
                'score': result.get('_distance', 0.0),
                'metadata': {k: v for k, v in result.items() 
                           if k not in ['image_id', 'vector', '_distance']}
            })
        
        return formatted_results
    
    def count_embeddings(self) -> int:
        """Count total number of embeddings in database
        
        Returns:
            Number of embeddings
        """
        if self.table is None:
            return 0
        
        # LanceDB doesn't have a direct count method, so we count rows
        try:
            # Get all rows and count them
            # Note: This is not efficient for large datasets, but fine for v0.1
            count = self.table.count_rows()
            return count
        except Exception:
            # Fallback: get all and count
            results = self.table.search().limit(100000).to_list()
            return len(results)
    
    def delete_embedding(self, image_id: str) -> bool:
        """Delete embedding for an image
        
        Args:
            image_id: Unique identifier for the image
            
        Returns:
            True if embedding was deleted, False if not found
        """
        if self.table is None:
            return False
        
        try:
            # LanceDB delete operation
            self.table.delete(f"image_id = '{image_id}'")
            return True
        except Exception:
            return False
    
    def get_all_ids(self) -> List[str]:
        """Get all image IDs in the database
        
        Returns:
            List of image IDs
        """
        if self.table is None:
            return []
        
        # Get all records (just IDs)
        results = self.table.search() \
            .select(['image_id']) \
            .limit(100000) \
            .to_list()
        
        return [r['image_id'] for r in results]
    
    def get_stats(self) -> Dict:
        """Get database statistics
        
        Returns:
            Dictionary with statistics
        """
        if self.table is None:
            return {
                'total_embeddings': 0,
                'embedding_dimension': None,
            }
        
        count = self.count_embeddings()
        
        # Get embedding dimension (sample one embedding)
        dimension = None
        if count > 0:
            sample = self.table.search().limit(1).to_list()
            if sample:
                dimension = len(sample[0]['vector'])
        
        return {
            'total_embeddings': count,
            'embedding_dimension': dimension,
        }
    
    def close(self):
        """Close database connection"""
        # LanceDB handles connection cleanup automatically
        pass
    
    def __del__(self):
        """Destructor"""
        self.close()
