"""
Machine Learning based attack detector
Uses Random Forest classifier trained on URL features
"""
import os
import pickle
import logging
from typing import Tuple, Dict, Any
from pathlib import Path
import numpy as np

logger = logging.getLogger(__name__)

class MLDetector:
    """ML-based URL attack detector"""
    
    def __init__(self, model_path: str = None):
        """Initialize ML detector"""
        if model_path is None:
            model_path = Path(__file__).parent.parent / 'models' / 'rf_classifier.pkl'
        
        self.model_path = Path(model_path)
        self.model = None
        self.label_encoder = None
        self.feature_names = None
    
    def load_model(self):
        """Load trained model from disk"""
        if not self.model_path.exists():
            raise FileNotFoundError(f"Model not found at {self.model_path}. Please train the model first.")
        
        try:
            with open(self.model_path, 'rb') as f:
                model_data = pickle.load(f)
            
            self.model = model_data['model']
            self.label_encoder = model_data['label_encoder']
            self.feature_names = model_data['feature_names']
            
            logger.info(f"Model loaded successfully from {self.model_path}")
            logger.info(f"Supports {len(self.label_encoder.classes_)} attack types")
        
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            raise
    
    def predict(self, features: Dict[str, Any]) -> Tuple[str, float]:
        """
        Predict attack type from features
        
        Args:
            features: Dictionary of extracted features
        
        Returns:
            (attack_type, confidence)
        """
        if self.model is None:
            raise RuntimeError("Model not loaded. Call load_model() first.")
        
        # Convert features dict to array in correct order
        feature_vector = []
        for fname in self.feature_names:
            feature_vector.append(features.get(fname, 0))
        
        feature_array = np.array(feature_vector).reshape(1, -1)
        
        # Get prediction and probability
        prediction = self.model.predict(feature_array)[0]
        probabilities = self.model.predict_proba(feature_array)[0]
        
        # Decode label
        attack_type = self.label_encoder.inverse_transform([prediction])[0]
        confidence = float(np.max(probabilities))
        
        return attack_type, confidence
    
    def is_loaded(self) -> bool:
        """Check if model is loaded"""
        return self.model is not None
