"""
Search Engine for Image Analysis System

Provides semantic search across indexed images using text queries.
Supports CLIP, MobileCLIP, and SigLIP models.
"""

import numpy as np
from pathlib import Path
from typing import List, Tuple, Dict, Optional
import sys

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from storage.sqlite_store import SQLiteStore
from storage.lance_store import LanceStore


class SearchEngine:
    """
    Semantic search engine for images.
    
    Converts text queries to embeddings and finds similar images
    in the vector database using cosine similarity.
    """
    
    def __init__(self, model_name: str = 'clip', db_path: str = 'databases'):
        """
        Initialize search engine.
        
        Args:
            model_name: Which model to use ('clip', 'mobileclip', 'siglip')
            db_path: Path to database directory
        """
        self.model_name = model_name.lower()
        self.db_path = Path(db_path)
        
        # Initialize stores
        self.metadata_store = SQLiteStore(str(self.db_path / 'metadata.db'))
        self.vector_store = LanceStore(
            str(self.db_path / f'embeddings_{self.model_name}.lance')
        )
        
        # Load text encoder
        self._load_text_encoder()
        
        print(f"✅ SearchEngine initialized with {self.model_name} model")
    
    def _load_text_encoder(self):
        """Load the appropriate text encoder for the model."""
        from transformers import CLIPProcessor, CLIPModel
        from transformers import AutoProcessor, AutoModel
        import torch

        self.device = 'cpu'  # CPU for now, GPU support in future

        if self.model_name == 'clip':
            # OpenAI CLIP - PyTorch (ONNX text export pending)
            model_id = "openai/clip-vit-base-patch32"
            self.processor = CLIPProcessor.from_pretrained(model_id)
            self.model = CLIPModel.from_pretrained(model_id).to(self.device)
            self.model.eval()
            self.embedding_dim = 512
            print(f"  Text encoder loaded: {model_id} (PyTorch)")

        elif self.model_name == 'mobileclip':
            # MobileCLIP - Use ONNX text encoder for alignment with image embeddings
            from config import Config
            from analysis.mobileclip import MobileCLIP

            config = Config(model_name='mobileclip')
            self.model = MobileCLIP(config)  # ONNX model with text encoder
            self.embedding_dim = 512
            print(f"  Text encoder loaded: MobileCLIP ONNX (aligned with image encoder)")

        elif self.model_name == 'siglip':
            # SigLIP - PyTorch (ONNX text export pending)
            model_id = "google/siglip-base-patch16-224"
            self.processor = AutoProcessor.from_pretrained(model_id)
            self.model = AutoModel.from_pretrained(model_id).to(self.device)
            self.model.eval()
            self.embedding_dim = 768
            print(f"  Text encoder loaded: {model_id} (PyTorch)")

        else:
            raise ValueError(f"Unknown model: {self.model_name}")
    
    def encode_text(self, text: str) -> np.ndarray:
        """
        Convert text query to embedding vector.

        Args:
            text: Search query text

        Returns:
            Embedding vector (512D or 768D depending on model)
        """
        if self.model_name == 'mobileclip':
            # MobileCLIP - Use ONNX text encoder
            embedding = self.model.generate_text_embedding(text)
            return embedding

        # For CLIP and SigLIP, use PyTorch (temporary until ONNX text export)
        import torch

        with torch.no_grad():
            if self.model_name == 'clip':
                # CLIP encoding
                inputs = self.processor(text=[text], return_tensors="pt", padding=True)
                inputs = {k: v.to(self.device) for k, v in inputs.items()}
                text_features = self.model.get_text_features(**inputs)

            elif self.model_name == 'siglip':
                # SigLIP encoding
                inputs = self.processor(text=[text], return_tensors="pt", padding=True)
                inputs = {k: v.to(self.device) for k, v in inputs.items()}
                outputs = self.model.get_text_features(**inputs)
                text_features = outputs

            # Normalize to unit length (important for cosine similarity)
            text_features = text_features / text_features.norm(dim=-1, keepdim=True)

            # Convert to numpy
            embedding = text_features.cpu().numpy()[0]

            return embedding
    
    def search(
        self, 
        query: str, 
        top_k: int = 10,
        score_threshold: Optional[float] = None
    ) -> List[Dict]:
        """
        Search for images matching the text query.
        
        Args:
            query: Text search query (e.g., "beach sunset")
            top_k: Number of results to return
            score_threshold: Optional minimum similarity score (0-1)
            
        Returns:
            List of dicts with keys: image_id, file_path, score, metadata
        """
        # Step 1: Encode query text to embedding
        print(f"Encoding query: '{query}'")
        query_embedding = self.encode_text(query)
        
        # Step 2: Search vector database for similar embeddings
        print(f"Searching {self.model_name} database...")
        search_results = self.vector_store.search_similar(
            query_embedding,
            top_k=top_k
        )
        
        # Step 3: Fetch metadata for each result
        results = []
        for result in search_results:
            image_id = result['image_id']
            score = float(result['score'])
            
            # Apply score threshold if specified
            if score_threshold is not None and score < score_threshold:
                continue
            
            # Get image metadata from SQLite
            metadata = self.metadata_store.get_image(image_id)
            
            if metadata:
                results.append({
                    'image_id': image_id,
                    'file_path': metadata['file_path'],
                    'score': score,
                    'metadata': metadata
                })
        
        return results
    
    def search_and_display(
        self, 
        query: str, 
        top_k: int = 10,
        verbose: bool = True
    ) -> List[Dict]:
        """
        Search and display results in a readable format.
        
        Args:
            query: Text search query
            top_k: Number of results to return
            verbose: Whether to print results
            
        Returns:
            List of search results
        """
        results = self.search(query, top_k=top_k)
        
        if verbose:
            print(f"\n{'='*60}")
            print(f"SEARCH RESULTS for: '{query}'")
            print(f"Model: {self.model_name}")
            print(f"Found {len(results)} results")
            print(f"{'='*60}\n")
            
            for i, result in enumerate(results, 1):
                print(f"{i}. Score: {result['score']:.4f}")
                print(f"   Path: {result['file_path']}")
                print(f"   ID: {result['image_id']}")
                print()
        
        return results


def main():
    """Example usage of SearchEngine."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Search images by text query')
    parser.add_argument('query', type=str, help='Search query text')
    parser.add_argument('--model', type=str, default='clip', 
                       choices=['clip', 'mobileclip', 'siglip'],
                       help='Which model to use')
    parser.add_argument('--top-k', type=int, default=10,
                       help='Number of results to return')
    parser.add_argument('--db-path', type=str, default='databases',
                       help='Path to database directory')
    
    args = parser.parse_args()
    
    # Initialize search engine
    engine = SearchEngine(model_name=args.model, db_path=args.db_path)
    
    # Perform search
    results = engine.search_and_display(args.query, top_k=args.top_k)
    
    print(f"✅ Search complete: {len(results)} results found")


if __name__ == '__main__':
    main()
