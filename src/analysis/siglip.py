"""
SigLIP Model Plugin

SigLIP-2 Base - Improved CLIP variant with better training.
Provides both image and text encoding for semantic search.

Phase 1 Day 2 - Image Analysis System v0.1
"""

import numpy as np
import onnxruntime as ort
from PIL import Image
from pathlib import Path
from typing import Union

from analysis.base import EmbeddingModel


class SigLIP(EmbeddingModel):
    """SigLIP-2 Base model for image and text embeddings"""
    
    def __init__(self, model_path: Union[str, Path], model_name: str):
        """Initialize SigLIP model
        
        Args:
            model_path: Path to ONNX model file
            model_name: Name identifier for this model
        """
        super().__init__(model_path, model_name)
        
        # Image preprocessing settings (224x224)
        self.image_size = 224
        self.mean = np.array([0.5, 0.5, 0.5], dtype=np.float32)
        self.std = np.array([0.5, 0.5, 0.5], dtype=np.float32)
        
        # Load model
        self.load_model()
    
    def load_model(self) -> None:
        """Load the ONNX model into memory"""
        self.session = ort.InferenceSession(
            str(self.model_path),
            providers=['CPUExecutionProvider']
        )
        
        # Set embedding dimension
        self.embedding_dim = 768  # SigLIP base uses 768D
        
        # Get input/output names
        self.inputs = {inp.name: inp for inp in self.session.get_inputs()}
        self.outputs = {out.name: out for out in self.session.get_outputs()}
    
    def preprocess_image(self, image_path: Union[str, Path]) -> np.ndarray:
        """Preprocess image for SigLIP
        
        Args:
            image_path: Path to image file
            
        Returns:
            Preprocessed image tensor
        """
        # Load and resize image
        image = Image.open(image_path).convert('RGB')
        image = image.resize((self.image_size, self.image_size), Image.BICUBIC)
        
        # Convert to numpy array and normalize to [0, 1]
        image_array = np.array(image, dtype=np.float32) / 255.0
        
        # Normalize with mean and std
        image_array = (image_array - self.mean) / self.std
        
        # Change from HWC to CHW format
        image_array = np.transpose(image_array, (2, 0, 1))
        
        # Add batch dimension
        image_array = np.expand_dims(image_array, axis=0)
        
        return image_array
    
    def generate_embedding(self, image: Union[str, Path, Image.Image]) -> np.ndarray:
        """Generate embedding for an image
        
        Args:
            image: Image file path or PIL Image object
            
        Returns:
            Image embedding as numpy array (768D)
        """
        # Preprocess image
        if isinstance(image, (str, Path)):
            image_tensor = self.preprocess_image(image)
        else:
            # If PIL Image, save temporarily and process
            import tempfile
            with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as f:
                image.save(f.name)
                image_tensor = self.preprocess_image(f.name)
        
        # Prepare inputs (SigLIP combined model expects both pixel_values and input_ids)
        # Provide dummy text input for image-only inference
        dummy_text = np.array([[0] * 64], dtype=np.int64)  # Dummy token sequence

        # Run inference with both inputs
        outputs = self.session.run(
            None,  # Get all outputs
            {
                'pixel_values': image_tensor,
                'input_ids': dummy_text
            }
        )

        # Get image embedding (4th output: 'image_embeds')
        embedding = outputs[3][0]  # Output index 3 is image_embeds, remove batch dimension
        
        # L2 normalize
        embedding = embedding / np.linalg.norm(embedding)
        
        return embedding
    
    def generate_text_embedding(self, text: str) -> np.ndarray:
        """Generate embedding for text query
        
        Args:
            text: Text query string
            
        Returns:
            Text embedding as numpy array (768D)
        """
        # Simple tokenization (placeholder - actual implementation would use proper tokenizer)
        # For now, create dummy text embedding
        # Note: Proper implementation requires tokenizer
        
        tokens = self._simple_tokenize(text)
        
        # Find text input name (usually second input)
        input_names = list(self.inputs.keys())
        text_input_name = input_names[1] if len(input_names) > 1 else input_names[0]
        
        # Run inference
        try:
            outputs = self.session.run(
                None,
                {text_input_name: tokens}
            )
            
            # Get text embedding (usually second output)
            embedding = outputs[1][0] if len(outputs) > 1 else outputs[0][0]
            
            # L2 normalize
            embedding = embedding / np.linalg.norm(embedding)
            
        except Exception as e:
            # Fallback: return zero vector if text encoding fails
            print(f"Warning: Text encoding not fully implemented - {e}")
            embedding = np.zeros(self.embedding_dim, dtype=np.float32)
        
        return embedding
    
    def _simple_tokenize(self, text: str, max_length: int = 64) -> np.ndarray:
        """Simple tokenization for text
        
        Args:
            text: Input text
            max_length: Maximum sequence length
            
        Returns:
            Token IDs as numpy array
        """
        # Simple character-level encoding
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
        model_size_mb = self.model_path.stat().st_size / (1024**2)
        
        return {
            'name': self.model_name,
            'type': 'SigLIP-2 Base',
            'model_size_mb': model_size_mb,
            'embedding_dim': self.embedding_dim,
            'image_size': self.image_size,
            'provider': self.session.get_providers()[0],
        }
