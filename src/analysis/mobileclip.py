"""
MobileCLIP Model Plugin

Lightweight CLIP variant optimized for mobile/edge devices.
Provides both image and text encoding for semantic search.

Phase 1 Day 2 - Image Analysis System v0.1
"""

import numpy as np
import onnxruntime as ort
from PIL import Image
from pathlib import Path
from typing import Union
import json

from analysis.base import EmbeddingModel


class MobileCLIP(EmbeddingModel):
    """MobileCLIP-S2 model for image and text embeddings"""
    
    def __init__(self, config):
        """Initialize MobileCLIP model

        Args:
            config: Configuration object with model paths
        """
        self.config = config
        self.model_name = config.model_name

        # Model paths
        model_dir = config.model_dir / 'mobileclip_s2'
        self.image_encoder_path = model_dir / 'mobileclip_image_encoder.onnx'
        self.text_encoder_path = model_dir / 'mobileclip_text_encoder.onnx'
        self.metadata_path = model_dir / 'mobileclip_metadata.json'

        # Verify files exist
        if not self.image_encoder_path.exists():
            raise FileNotFoundError(f"Image encoder not found: {self.image_encoder_path}")
        if not self.text_encoder_path.exists():
            raise FileNotFoundError(f"Text encoder not found: {self.text_encoder_path}")

        # Load metadata
        if self.metadata_path.exists():
            with open(self.metadata_path, 'r') as f:
                self.metadata = json.load(f)
        else:
            self.metadata = {}

        # Set embedding dimension
        self.embedding_dim = 512

        # Image preprocessing settings (MobileCLIP uses 224x224)
        self.image_size = 224
        self.mean = np.array([0.485, 0.456, 0.406], dtype=np.float32)
        self.std = np.array([0.229, 0.224, 0.225], dtype=np.float32)

        # Initialize session variables
        self.image_session = None
        self.text_session = None
        self.image_input_name = None
        self.image_output_name = None
        self.text_input_name = None
        self.text_output_name = None

        # Load CLIP tokenizer for text encoding (MobileCLIP is CLIP-compatible)
        from transformers import CLIPTokenizer
        self.tokenizer = CLIPTokenizer.from_pretrained("openai/clip-vit-base-patch32")

        # Load models
        self.load_model()

    def load_model(self) -> None:
        """Load ONNX models for MobileCLIP

        Loads both image and text encoder models and sets up
        input/output names for inference.
        """
        # Load image encoder
        self.image_session = ort.InferenceSession(
            str(self.image_encoder_path),
            providers=['CPUExecutionProvider']
        )

        # Load text encoder
        self.text_session = ort.InferenceSession(
            str(self.text_encoder_path),
            providers=['CPUExecutionProvider']
        )

        # Get input/output names for image encoder
        self.image_input_name = self.image_session.get_inputs()[0].name
        self.image_output_name = self.image_session.get_outputs()[0].name

        # Get input/output names for text encoder
        self.text_input_name = self.text_session.get_inputs()[0].name
        self.text_output_name = self.text_session.get_outputs()[0].name

    def preprocess_image(self, image_path: Union[str, Path]) -> np.ndarray:
        """Preprocess image for MobileCLIP
        
        Args:
            image_path: Path to image file
            
        Returns:
            Preprocessed image tensor
        """
        # Load and resize image
        image = Image.open(image_path).convert('RGB')
        image = image.resize((self.image_size, self.image_size), Image.BICUBIC)
        
        # Convert to numpy array and normalize
        image_array = np.array(image, dtype=np.float32) / 255.0
        
        # Normalize with ImageNet stats
        image_array = (image_array - self.mean) / self.std
        
        # Change from HWC to CHW format
        image_array = np.transpose(image_array, (2, 0, 1))
        
        # Add batch dimension
        image_array = np.expand_dims(image_array, axis=0)
        
        return image_array
    
    def generate_embedding(self, image_path: Union[str, Path]) -> np.ndarray:
        """Generate embedding for an image
        
        Args:
            image_path: Path to image file
            
        Returns:
            Image embedding as numpy array (512D)
        """
        # Preprocess image
        image_tensor = self.preprocess_image(image_path)
        
        # Run inference
        outputs = self.image_session.run(
            [self.image_output_name],
            {self.image_input_name: image_tensor}
        )
        
        # Get embedding and normalize
        embedding = outputs[0][0]  # Remove batch dimension
        embedding = embedding / np.linalg.norm(embedding)  # L2 normalize
        
        return embedding
    
    def generate_text_embedding(self, text: str) -> np.ndarray:
        """Generate embedding for text query

        Args:
            text: Text query string

        Returns:
            Text embedding as numpy array (512D)
        """
        # Tokenize using CLIP tokenizer (MobileCLIP is CLIP-compatible)
        tokens = self.tokenizer(
            text,
            padding="max_length",
            max_length=77,
            truncation=True,
            return_tensors="np"
        )

        # Get input_ids as int64
        input_ids = tokens['input_ids'].astype(np.int64)

        # Run inference
        outputs = self.text_session.run(
            [self.text_output_name],
            {self.text_input_name: input_ids}
        )

        # Get embedding and normalize
        embedding = outputs[0][0]  # Remove batch dimension
        embedding = embedding / np.linalg.norm(embedding)  # L2 normalize

        return embedding
    
    def _simple_tokenize(self, text: str, max_length: int = 77) -> np.ndarray:
        """Simple tokenization for text
        
        Args:
            text: Input text
            max_length: Maximum sequence length
            
        Returns:
            Token IDs as numpy array
        """
        # This is a placeholder - actual tokenization would use the 
        # nlp_textual_tokenizer.txt.gz file
        # For now, we'll use a simple character-level encoding
        
        # Convert to lowercase and get character codes
        text = text.lower()
        tokens = [ord(c) % 256 for c in text[:max_length]]
        
        # Pad to max_length
        tokens = tokens + [0] * (max_length - len(tokens))
        
        # Convert to numpy array with shape (1, max_length)
        tokens = np.array([tokens], dtype=np.int64)
        
        return tokens
    
    def get_model_info(self) -> dict:
        """Get model information
        
        Returns:
            Dictionary with model metadata
        """
        return {
            'name': self.model_name,
            'type': 'MobileCLIP-S2',
            'image_encoder_size_mb': self.image_encoder_path.stat().st_size / (1024**2),
            'text_encoder_size_mb': self.text_encoder_path.stat().st_size / (1024**2),
            'embedding_dim': 512,
            'image_size': self.image_size,
            'provider': self.image_session.get_providers()[0],
        }
