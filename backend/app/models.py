"""
Pydantic models for request/response validation
"""
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator
from datetime import datetime


class PredictionRequest(BaseModel):
    """Single location flood prediction request"""
    
    lat: float = Field(..., description="Latitude", ge=-90, le=90)
    lon: float = Field(..., description="Longitude", ge=-180, le=180)
    date: int = Field(..., description="Day of year (1-365)", ge=1, le=365)
    elevation: float = Field(..., description="Elevation in meters")
    slope: float = Field(..., description="Slope in degrees", ge=0)
    landcover: int = Field(..., description="Land cover type code")
    precip_1d: float = Field(..., description="1-day precipitation (mm)", ge=0)
    precip_3d: float = Field(..., description="3-day precipitation (mm)", ge=0)
    precip_7d: float = Field(..., description="7-day precipitation (mm)", ge=0)
    precip_14d: float = Field(..., description="14-day precipitation (mm)", ge=0)
    dis_last: float = Field(..., description="Last river discharge (m³/s)", ge=0)
    dis_trend_3: float = Field(..., description="3-day discharge trend")
    dayofyear: int = Field(..., description="Day of year (1-365)", ge=1, le=365)
    
    class Config:
        json_schema_extra = {
            "example": {
                "lat": 23.8103,
                "lon": 90.4125,
                "date": 180,
                "elevation": 10.5,
                "slope": 0.5,
                "landcover": 11,
                "precip_1d": 50.0,
                "precip_3d": 120.0,
                "precip_7d": 200.0,
                "precip_14d": 300.0,
                "dis_last": 1500.0,
                "dis_trend_3": 100.0,
                "dayofyear": 180
            }
        }


class BatchPredictionRequest(BaseModel):
    """Batch prediction request for multiple locations"""
    
    predictions: List[PredictionRequest] = Field(..., description="List of prediction requests")
    
    @field_validator('predictions')
    @classmethod
    def validate_batch_size(cls, v):
        if len(v) > 1000:
            raise ValueError("Batch size cannot exceed 1000 predictions")
        if len(v) == 0:
            raise ValueError("Batch must contain at least one prediction request")
        return v


class PredictionResponse(BaseModel):
    """Flood prediction response"""
    
    flood_probability: float = Field(..., description="Probability of flooding (0-1)")
    risk_level: str = Field(..., description="Risk level: Low, Medium, or High")
    is_flood_predicted: bool = Field(..., description="Binary flood prediction (threshold 0.5)")
    confidence: float = Field(..., description="Model confidence score (0-1)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "flood_probability": 0.75,
                "risk_level": "High",
                "is_flood_predicted": True,
                "confidence": 0.85
            }
        }


class BatchPredictionResponse(BaseModel):
    """Batch prediction response"""
    
    predictions: List[PredictionResponse] = Field(..., description="List of predictions")
    total_count: int = Field(..., description="Total number of predictions")
    high_risk_count: int = Field(..., description="Number of high-risk predictions")
    
    class Config:
        json_schema_extra = {
            "example": {
                "predictions": [
                    {
                        "flood_probability": 0.75,
                        "risk_level": "High",
                        "is_flood_predicted": True,
                        "confidence": 0.85
                    }
                ],
                "total_count": 1,
                "high_risk_count": 1
            }
        }


class ModelInfoResponse(BaseModel):
    """Model metadata response"""
    
    model_name: str = Field(..., description="Model name")
    model_type: str = Field(..., description="Model type")
    feature_names: List[str] = Field(..., description="List of required features")
    feature_count: int = Field(..., description="Number of features")
    version: str = Field(..., description="API version")
    
    class Config:
        json_schema_extra = {
            "example": {
                "model_name": "CatBoost Flood Classifier",
                "model_type": "CatBoost",
                "feature_names": ["lat", "lon", "date", "elevation", "slope", "landcover", 
                                 "precip_1d", "precip_3d", "precip_7d", "precip_14d", 
                                 "dis_last", "dis_trend_3", "dayofyear"],
                "feature_count": 13,
                "version": "1.0.0"
            }
        }


class HealthResponse(BaseModel):
    """Health check response"""
    
    status: str = Field(..., description="Service status")
    model_loaded: bool = Field(..., description="Whether model is loaded")
    timestamp: str = Field(..., description="Current timestamp")
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "model_loaded": True,
                "timestamp": "2025-11-26T00:00:00Z"
            }
        }


class ErrorResponse(BaseModel):
    """Error response"""
    
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Detailed error information")
    
    class Config:
        json_schema_extra = {
            "example": {
                "error": "ValidationError",
                "message": "Invalid input data",
                "detail": "Field 'lat' must be between -90 and 90"
            }
        }
