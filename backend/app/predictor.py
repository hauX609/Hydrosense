"""
Model loading and prediction logic
"""
import json
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, List, Tuple
from catboost import CatBoostClassifier

from .config import settings
from .models import PredictionRequest, PredictionResponse


class FloodPredictor:
    """Manages model loading and predictions"""
    
    def __init__(self):
        self.model = None
        self.feature_names = None
        self.model_loaded = False
        
    def load_model(self) -> bool:
        """Load the CatBoost model and metadata"""
        try:
            # Load model metadata
            with open(settings.MODEL_META_PATH, 'r') as f:
                meta = json.load(f)
                self.feature_names = meta['feature_names']
            
            # Load CatBoost model
            self.model = CatBoostClassifier()
            self.model.load_model(str(settings.MODEL_PATH))
            
            self.model_loaded = True
            print(f"[OK] Model loaded successfully from {settings.MODEL_PATH}")
            print(f"[OK] Features: {', '.join(self.feature_names)}")
            return True
            
        except Exception as e:
            print(f"[ERROR] Failed to load model: {e}")
            self.model_loaded = False
            return False
    
    def _prepare_input(self, request: PredictionRequest) -> pd.DataFrame:
        """Convert request to DataFrame with correct feature order"""
        data = {
            'lat': request.lat,
            'lon': request.lon,
            'date': request.date,
            'elevation': request.elevation,
            'slope': request.slope,
            'landcover': request.landcover,
            'precip_1d': request.precip_1d,
            'precip_3d': request.precip_3d,
            'precip_7d': request.precip_7d,
            'precip_14d': request.precip_14d,
            'dis_last': request.dis_last,
            'dis_trend_3': request.dis_trend_3,
            'dayofyear': request.dayofyear
        }
        
        # Create DataFrame with correct column order
        df = pd.DataFrame([data], columns=self.feature_names)
        
        # Handle any missing or infinite values
        df = df.replace([np.inf, -np.inf], np.nan)
        df = df.fillna(0.0)
        
        return df
    
    def _calculate_risk_level(self, probability: float) -> str:
        """Determine risk level based on probability"""
        if probability < settings.LOW_RISK_THRESHOLD:
            return "Low"
        elif probability < settings.MEDIUM_RISK_THRESHOLD:
            return "Medium"
        else:
            return "High"
    
    def predict(self, request: PredictionRequest) -> PredictionResponse:
        """Generate flood prediction for a single location"""
        if not self.model_loaded:
            raise RuntimeError("Model not loaded. Please check server logs.")
        
        # Prepare input data
        input_df = self._prepare_input(request)
        
        # Get prediction probabilities
        probabilities = self.model.predict_proba(input_df)
        flood_probability = float(probabilities[0][1])  # Probability of class 1 (flood)
        
        # Calculate confidence (distance from 0.5 decision boundary)
        confidence = abs(flood_probability - 0.5) * 2
        
        # Determine risk level
        risk_level = self._calculate_risk_level(flood_probability)
        
        # Binary prediction (threshold 0.5)
        is_flood_predicted = flood_probability >= 0.5
        
        return PredictionResponse(
            flood_probability=flood_probability,
            risk_level=risk_level,
            is_flood_predicted=is_flood_predicted,
            confidence=confidence
        )
    
    def predict_batch(self, requests: List[PredictionRequest]) -> List[PredictionResponse]:
        """Generate predictions for multiple locations"""
        if not self.model_loaded:
            raise RuntimeError("Model not loaded. Please check server logs.")
        
        # Prepare batch input
        batch_data = []
        for req in requests:
            data = {
                 'lat': req.lat,
                'lon': req.lon,
                'date': req.date,
                'elevation': req.elevation,
                'slope': req.slope,
                'landcover': req.landcover,
                'precip_1d': req.precip_1d,
                'precip_3d': req.precip_3d,
                'precip_7d': req.precip_7d,
                'precip_14d': req.precip_14d,
                'dis_last': req.dis_last,
                'dis_trend_3': req.dis_trend_3,
                'dayofyear': req.dayofyear
            }
            batch_data.append(data)
        
        # Create DataFrame
        input_df = pd.DataFrame(batch_data, columns=self.feature_names)
        input_df = input_df.replace([np.inf, -np.inf], np.nan)
        input_df = input_df.fillna(0.0)
        
        # Get predictions
        probabilities = self.model.predict_proba(input_df)
        
        # Create response for each prediction
        responses = []
        for prob in probabilities:
            flood_probability = float(prob[1])
            confidence = abs(flood_probability - 0.5) * 2
            risk_level = self._calculate_risk_level(flood_probability)
            is_flood_predicted = flood_probability >= 0.5
            
            responses.append(PredictionResponse(
                flood_probability=flood_probability,
                risk_level=risk_level,
                is_flood_predicted=is_flood_predicted,
                confidence=confidence
            ))
        
        return responses
    
    def get_model_info(self) -> Dict:
        """Get model metadata"""
        return {
            "model_name": "CatBoost Flood Classifier",
            "model_type": "CatBoost",
            "feature_names": self.feature_names,
            "feature_count": len(self.feature_names) if self.feature_names else 0,
            "version": settings.APP_VERSION
        }


# Global predictor instance
predictor = FloodPredictor()
