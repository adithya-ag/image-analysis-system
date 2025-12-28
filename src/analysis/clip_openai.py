"""
OpenAI CLIP ViT-B/32 Implementation
Concrete implementation of EmbeddingModel for CLIP.
"""

from pathlib import Path
from typing import Union
import numpy as np
from PIL import Image
import onnxruntime as ort
from transformers import CLIPProcessor

from .base import EmbeddingModel


class CLIPOpenAI(EmbeddingModel):
    """
    OpenAI CLIP ViT-B/32 model implementation.
    
    Uses ONNX Runtime for inference with OpenVINO optimization.
    Supports both image and text embeddings.
    """
    
    def __init__(self, model_path: Union[str, Path], model_name: str = "clip_vit_b32"):
        """
        Initialize CLIP model.
        
        Args:
            model_path: Path to CLIP ONNX model file
            model_name: Model identifier (default: clip_vit_b32)
        """
        super().__init__(model_path, model_name)
        
        # CLIP-specific settings
        self.embedding_dim = 512
        self.image_size = 224
        
        # Load processor (for preprocessing)
        self.processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
        
        # Load model
        self.load_model()
    
    def load_model(self) -> None:
        """
        Load CLIP ONNX model with ONNX Runtime.
        Uses OpenVINO execution provider if available, else CPU.
        """
        # Configure execution providers (try OpenVINO, fallback to CPU)
        providers = []
        
        # Try OpenVINO (Intel GPU acceleration)
        if ort.get_available_providers().__contains__('OpenVINOExecutionProvider'):
            providers.append('OpenVINOExecutionProvider')
        
        # Fallback to CPU
        providers.append('CPUExecutionProvider')
        
        # Create inference session
        sess_options = ort.SessionOptions()
        sess_options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
        
        self.session = ort.InferenceSession(
            str(self.model_path),
            sess_options=sess_options,
            providers=providers
        )
        
        # Get actual provider used
        self.active_provider = self.session.get_providers()[0]
        
        print(f"✅ CLIP model loaded: {self.model_name}")
        print(f"   Provider: {self.active_provider}")
        print(f"   Embedding dim: {self.embedding_dim}")
    
    def generate_embedding(self, image: Union[str, Path, Image.Image]) -> np.ndarray:
        """
        Generate embedding for an image.
        
        Args:
            image: Image path or PIL Image
            
        Returns:
            512-dimensional embedding vector
        """
        # Load image
        pil_image = self._load_image(image)
        
        # Preprocess image
        inputs = self.processor(
            images=pil_image,
            return_tensors="np",
            padding=True
        )
        
        # Run inference
        pixel_values = inputs['pixel_values'].astype(np.float32)
        
        # ONNX model expects input named 'pixel_values'
        ort_inputs = {'pixel_values': pixel_values}
        
        # Get embeddings
        outputs = self.session.run(None, ort_inputs)
        embedding = outputs[0][0]  # First output, first batch item
        
        # Normalize embedding (L2 normalization for cosine similarity)
        embedding = embedding / np.linalg.norm(embedding)
        
        return embedding
    
    def generate_text_embedding(self, text: str) -> np.ndarray:
        """
        Generate embedding for text query.
        
        Args:
            text: Text query string
            
        Returns:
            512-dimensional embedding vector
        """
        # Preprocess text
        inputs = self.processor(
            text=text,
            return_tensors="np",
            padding=True,
            truncation=True
        )
        
        # Run inference (text encoder)
        input_ids = inputs['input_ids'].astype(np.int64)
        attention_mask = inputs['attention_mask'].astype(np.int64)
        
        ort_inputs = {
            'input_ids': input_ids,
            'attention_mask': attention_mask
        }
        
        # Note: This assumes the ONNX model has text inputs
        # If using vision-only ONNX export, we need to handle differently
        # For now, we'll use the image encoder and encode text as pseudo-image
        
        # Workaround: For CLIP vision-only ONNX model,
        # we need to use the processor to get text features via PyTorch
        # then match the embedding space
        
        # This is a known limitation - ONNX export of CLIP often only includes vision encoder
        # For v0.1, we'll document this and potentially use PyTorch for text encoding
        
        raise NotImplementedError(
            "Text embedding via ONNX not supported in this export. "
            "Use PyTorch CLIP for text queries or export full model. "
            "This will be addressed in v0.2."
        )
    
    def generate_batch_embeddings(self, images: list) -> np.ndarray:
        """
        Generate embeddings for batch of images.
        
        Args:
            images: List of image paths or PIL Images
            
        Returns:
            Array of embeddings (shape: [num_images, 512])
        """
        # Load all images
        pil_images = [self._load_image(img) for img in images]
        
        # Batch preprocess
        inputs = self.processor(
            images=pil_images,
            return_tensors="np",
            padding=True
        )
        
        pixel_values = inputs['pixel_values'].astype(np.float32)
        ort_inputs = {'pixel_values': pixel_values}
        
        # Batch inference
        outputs = self.session.run(None, ort_inputs)
        embeddings = outputs[0]  # Shape: [batch_size, 512]
        
        # Normalize each embedding
        norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
        embeddings = embeddings / norms
        
        return embeddings


# Factory function for easy instantiation
def create_clip_model(model_path: Union[str, Path]) -> CLIPOpenAI:
    """
    Factory function to create CLIP model instance.
    
    Args:
        model_path: Path to CLIP ONNX model
        
    Returns:
        Initialized CLIPOpenAI instance
    """
    return CLIPOpenAI(model_path)
