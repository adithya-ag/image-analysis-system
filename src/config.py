"""
Configuration Management - Multi-Model Support

Handles model selection and paths for CLIP and MobileCLIP.

Phase 1 Day 2 - Image Analysis System v0.1
"""

from pathlib import Path
import os


class Config:
    """Configuration for image analysis system"""
    
    def __init__(self, model_name: str = 'clip'):
        """Initialize configuration
        
        Args:
            model_name: Name of model to use ('clip' or 'mobileclip')
        """
        # Project paths
        self.project_root = Path(__file__).parent.parent
        self.model_dir = self.project_root / 'models'
        self.data_dir = self.project_root / 'data'
        self.database_dir = self.project_root / 'databases'
        
        # Model selection
        self.model_name = model_name
        self._setup_model_config(model_name)
        
        # Database paths (model-specific for LanceDB)
        self.sqlite_path = self.database_dir / 'metadata.db'
        self.lance_path = self.database_dir / f'embeddings_{model_name}.lance'
    
    def _setup_model_config(self, model_name: str):
        """Setup model-specific configuration
        
        Args:
            model_name: Name of model ('clip' or 'mobileclip')
        """
        if model_name == 'clip':
            self.model_class = 'CLIPOpenAI'
            self.model_path = self.model_dir / 'clip_vit_b32' / 'model.onnx'
            self.embedding_dim = 512
            
        elif model_name == 'mobileclip':
            self.model_class = 'MobileCLIP'
            self.model_path = self.model_dir / 'mobileclip_s2'
            self.embedding_dim = 512
            
        else:
            raise ValueError(f"Unknown model: {model_name}. Use 'clip' or 'mobileclip'")
        
        # Verify model exists
        if model_name == 'clip' and not self.model_path.exists():
            raise FileNotFoundError(f"CLIP model not found: {self.model_path}")
        elif model_name == 'mobileclip':
            img_encoder = self.model_path / 'mobileclip_image_encoder.onnx'
            if not img_encoder.exists():
                raise FileNotFoundError(f"MobileCLIP not found: {img_encoder}")
    
    def get_model_instance(self):
        """Get instance of the configured model
        
        Returns:
            Instantiated model object
        """
        if self.model_class == 'CLIPOpenAI':
            from analysis.clip_openai import CLIPOpenAI
            return CLIPOpenAI(self)
        elif self.model_class == 'MobileCLIP':
            from analysis.mobileclip import MobileCLIP
            return MobileCLIP(self)
        else:
            raise ValueError(f"Unknown model class: {self.model_class}")
    
    def list_available_models(self) -> list:
        """List all available models
        
        Returns:
            List of tuples (model_name, status, path)
        """
        models = []
        
        # Check CLIP
        clip_path = self.model_dir / 'clip_vit_b32' / 'model.onnx'
        models.append(('clip', clip_path.exists(), clip_path))
        
        # Check MobileCLIP
        mobileclip_path = self.model_dir / 'mobileclip_s2' / 'mobileclip_image_encoder.onnx'
        models.append(('mobileclip', mobileclip_path.exists(), mobileclip_path))
        
        return models
    
    def __repr__(self):
        return f"Config(model={self.model_name}, embedding_dim={self.embedding_dim})"
