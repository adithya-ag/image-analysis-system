"""
Configuration Management
Centralizes all project settings and paths.
"""

from pathlib import Path
import json
from typing import Dict, Any

# Project root directory
PROJECT_ROOT = Path(__file__).parent.parent

# Directory paths
MODELS_DIR = PROJECT_ROOT / "models"
DATABASES_DIR = PROJECT_ROOT / "databases"
DATA_DIR = PROJECT_ROOT / "data"
LOGS_DIR = PROJECT_ROOT / "logs"

# Database paths
SQLITE_DB_PATH = DATABASES_DIR / "metadata.db"
LANCEDB_PATH = DATABASES_DIR / "embeddings.lance"

# Model configuration
MODEL_CONFIG_PATH = MODELS_DIR / "model_config.json"


class Config:
    """
    Application configuration.
    Loads settings from model_config.json and provides defaults.
    """
    
    def __init__(self):
        self.project_root = PROJECT_ROOT
        self.models_dir = MODELS_DIR
        self.databases_dir = DATABASES_DIR
        self.data_dir = DATA_DIR
        self.logs_dir = LOGS_DIR
        
        # Load model configuration
        self.model_config = self._load_model_config()
        
        # Set primary model
        self.primary_model = self.model_config.get("primary_model", "clip_vit_b32")
        
        # Embedding settings
        self.embedding_dim = 512  # CLIP standard
        self.batch_size = 10  # Process 10 images at a time
        
        # Performance settings
        self.use_gpu = True  # Try GPU first, fallback to CPU
        self.num_threads = 4
        
    def _load_model_config(self) -> Dict[str, Any]:
        """Load model configuration from JSON file"""
        if MODEL_CONFIG_PATH.exists():
            with open(MODEL_CONFIG_PATH, 'r') as f:
                return json.load(f)
        else:
            # Default configuration
            return {
                "primary_model": "clip_vit_b32",
                "models": {
                    "clip_vit_b32": {
                        "name": "CLIP-ViT-B/32",
                        "path": str(MODELS_DIR / "clip_vit_b32" / "model.onnx"),
                        "embedding_dim": 512,
                        "type": "vision-language"
                    }
                }
            }
    
    def get_model_path(self, model_name: str = None) -> Path:
        """
        Get path to ONNX model file.
        
        Args:
            model_name: Name of model (default: primary model)
            
        Returns:
            Path to ONNX model file
        """
        if model_name is None:
            model_name = self.primary_model
        
        model_info = self.model_config["models"].get(model_name)
        if not model_info:
            raise ValueError(f"Model '{model_name}' not found in configuration")
        
        return Path(model_info["path"])
    
    def get_model_info(self, model_name: str = None) -> Dict[str, Any]:
        """Get model metadata"""
        if model_name is None:
            model_name = self.primary_model
        
        return self.model_config["models"].get(model_name, {})


# Global configuration instance
config = Config()
