"""
Base Embedding Model Interface
Defines abstract interface for all embedding models.
This enables plugin architecture - models are swappable.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Union, List
import numpy as np
from PIL import Image


class EmbeddingModel(ABC):
    """
    Abstract base class for all embedding models.
    
    All model implementations must inherit from this and implement:
    - load_model()
    - generate_embedding()
    - generate_text_embedding()
    """
    
    def __init__(self, model_path: Union[str, Path], model_name: str):
        """
        Initialize embedding model.
        
        Args:
            model_path: Path to ONNX model file
            model_name: Name/identifier for this model
        """
        self.model_path = Path(model_path)
        self.model_name = model_name
        self.session = None
        self.embedding_dim = None
        
        if not self.model_path.exists():
            raise FileNotFoundError(f"Model file not found: {self.model_path}")
    
    @abstractmethod
    def load_model(self) -> None:
        """
        Load the ONNX model into memory.
        Must set self.session and self.embedding_dim.
        """
        pass
    
    @abstractmethod
    def generate_embedding(self, image: Union[str, Path, Image.Image]) -> np.ndarray:
        """
        Generate embedding vector for an image.
        
        Args:
            image: Image file path or PIL Image object
            
        Returns:
            Embedding vector as numpy array (shape: [embedding_dim])
        """
        pass
    
    @abstractmethod
    def generate_text_embedding(self, text: str) -> np.ndarray:
        """
        Generate embedding vector for text query.
        
        Args:
            text: Text query string
            
        Returns:
            Embedding vector as numpy array (shape: [embedding_dim])
        """
        pass
    
    def generate_batch_embeddings(self, images: List[Union[str, Path, Image.Image]]) -> np.ndarray:
        """
        Generate embeddings for multiple images.
        
        Default implementation: loop through images.
        Subclasses can override for true batch processing.
        
        Args:
            images: List of image paths or PIL Image objects
            
        Returns:
            Embeddings as numpy array (shape: [num_images, embedding_dim])
        """
        embeddings = []
        for image in images:
            emb = self.generate_embedding(image)
            embeddings.append(emb)
        
        return np.array(embeddings)
    
    def _load_image(self, image: Union[str, Path, Image.Image]) -> Image.Image:
        """
        Load image from path or return PIL Image as-is.
        
        Args:
            image: Image path or PIL Image
            
        Returns:
            PIL Image object
        """
        if isinstance(image, (str, Path)):
            return Image.open(image).convert('RGB')
        elif isinstance(image, Image.Image):
            return image.convert('RGB')
        else:
            raise TypeError(f"Unsupported image type: {type(image)}")
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(model='{self.model_name}', dim={self.embedding_dim})"
