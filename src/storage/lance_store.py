"""
LanceDB Storage Layer
Manages vector embeddings in LanceDB for similarity search.
"""

from pathlib import Path
from typing import Union, List, Tuple
import numpy as np
import lancedb
from datetime import datetime


class LanceDBStore:
    """
    LanceDB interface for vector embeddings.
    
    Stores:
    - Image embeddings (512-dim vectors)
    - Model metadata
    - Timestamp information
    """
    
    def __init__(self, db_path: Union[str, Path], table_name: str = "embeddings"):
        """
        Initialize LanceDB connection.
        
        Args:
            db_path: Path to LanceDB database directory
            table_name: Name of embeddings table (default: embeddings)
        """
        self.db_path = Path(db_path)
        self.table_name = table_name
        self.db = None
        self.table = None
        
        self.connect()
    
    def connect(self) -> None:
        """Open connection to LanceDB"""
        self.db = lancedb.connect(str(self.db_path))
        
        # Check if table exists
        if self.table_name in self.db.table_names():
            self.table = self.db.open_table(self.table_name)
        else:
            self.table = None  # Will be created on first insert
    
    def insert_embedding(
        self,
        image_id: str,
        embedding: np.ndarray,
        model_name: str
    ) -> None:
        """
        Insert or update embedding for an image.
        
        Args:
            image_id: Unique image identifier
            embedding: Embedding vector (512-dim)
            model_name: Name of model that generated embedding
        """
        # Prepare data
        data = [{
            "image_id": image_id,
            "vector": embedding.tolist(),  # LanceDB expects list
            "model_name": model_name,
            "timestamp": datetime.now().isoformat()
        }]
        
        # Create table if doesn't exist
        if self.table is None:
            self.table = self.db.create_table(self.table_name, data=data)
        else:
            # Add to existing table
            self.table.add(data)
    
    def insert_batch_embeddings(
        self,
        image_ids: List[str],
        embeddings: np.ndarray,
        model_name: str
    ) -> None:
        """
        Insert multiple embeddings at once.
        
        Args:
            image_ids: List of image identifiers
            embeddings: Array of embeddings (shape: [n, 512])
            model_name: Name of model that generated embeddings
        """
        # Prepare batch data
        timestamp = datetime.now().isoformat()
        data = [
            {
                "image_id": image_id,
                "vector": embedding.tolist(),
                "model_name": model_name,
                "timestamp": timestamp
            }
            for image_id, embedding in zip(image_ids, embeddings)
        ]
        
        # Create or add to table
        if self.table is None:
            self.table = self.db.create_table(self.table_name, data=data)
        else:
            self.table.add(data)
    
    def search(
        self,
        query_embedding: np.ndarray,
        limit: int = 10
    ) -> List[Tuple[str, float]]:
        """
        Search for similar images using vector similarity.
        
        Args:
            query_embedding: Query embedding vector (512-dim)
            limit: Maximum number of results to return
            
        Returns:
            List of (image_id, similarity_score) tuples, sorted by similarity
        """
        if self.table is None:
            return []
        
        # Perform vector search
        results = self.table.search(query_embedding.tolist()).limit(limit).to_list()
        
        # Extract image_id and distance (convert to similarity)
        # LanceDB returns L2 distance - convert to similarity score
        matches = []
        for result in results:
            image_id = result["image_id"]
            distance = result["_distance"]
            
            # Convert L2 distance to similarity score (0-1 range)
            # Lower distance = higher similarity
            similarity = 1.0 / (1.0 + distance)
            
            matches.append((image_id, similarity))
        
        return matches
    
    def get_embedding(self, image_id: str) -> np.ndarray:
        """
        Retrieve embedding for a specific image.
        
        Args:
            image_id: Image identifier
            
        Returns:
            Embedding vector, or None if not found
        """
        if self.table is None:
            return None
        
        # Query by image_id
        results = self.table.search().where(f"image_id = '{image_id}'").limit(1).to_list()
        
        if results:
            return np.array(results[0]["vector"])
        return None
    
    def delete_embedding(self, image_id: str) -> None:
        """
        Delete embedding for an image.
        
        Args:
            image_id: Image identifier
        """
        if self.table is None:
            return
        
        # LanceDB delete operation
        self.table.delete(f"image_id = '{image_id}'")
    
    def get_stats(self) -> dict:
        """
        Get database statistics.
        
        Returns:
            Statistics dictionary
        """
        if self.table is None:
            return {"total_embeddings": 0}
        
        count = self.table.count_rows()
        
        return {
            "total_embeddings": count,
            "table_name": self.table_name
        }
    
    def close(self) -> None:
        """Close database connection"""
        # LanceDB doesn't require explicit close
        pass
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()
