"""
FastAPI main application
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, status, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from datetime import datetime
import logging

from .config import settings
from .models import (
    PredictionRequest,
    PredictionResponse,
    BatchPredictionRequest,
    BatchPredictionResponse,
    ModelInfoResponse,
    HealthResponse,
    ErrorResponse
)
from .predictor import predictor
from app.weather import weather_service
from sqlalchemy.orm import Session
from .database import SessionLocal, engine, Base
from . import db_models
import json

# Create database tables
Base.metadata.create_all(bind=engine)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager for the FastAPI app"""
    # Startup
    logger.info("Starting up Bangladesh Flood Prediction API...")
    success = predictor.load_model()
    if success:
        logger.info("✓ Model loaded successfully")
    else:
        logger.error("✗ Failed to load model")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Bangladesh Flood Prediction API...")

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="API for predicting flood risk in Bangladesh using machine learning",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint"""
    return {
        "message": "Bangladesh Flood Prediction API",
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy" if predictor.model_loaded else "unhealthy",
        model_loaded=predictor.model_loaded,
        timestamp=datetime.utcnow().isoformat() + "Z"
    )


@app.get("/model/info", response_model=ModelInfoResponse, tags=["Model"])
async def get_model_info():
    """Get model metadata and feature information"""
    if not predictor.model_loaded:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Model not loaded"
        )
    
    info = predictor.get_model_info()
    return ModelInfoResponse(**info)


@app.post("/predict", response_model=PredictionResponse, tags=["Prediction"])
async def predict_flood(request: PredictionRequest, db: Session = Depends(get_db)):
    """
    Predict flood risk for a single location
    
    Returns flood probability, risk level, and confidence score.
    """
    try:
        if not predictor.model_loaded:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Model not loaded. Please check server logs."
            )
        
        prediction = predictor.predict(request)
        logger.info(f"Prediction made: probability={prediction.flood_probability:.3f}, risk={prediction.risk_level}")
        
        # Save to database
        try:
            db_prediction = db_models.Prediction(
                location=f"{request.lat:.4f}, {request.lon:.4f}",
                lat=request.lat,
                lon=request.lon,
                risk_level=prediction.risk_level,
                flood_probability=prediction.flood_probability,
                input_data=json.dumps(request.model_dump())
            )
            db.add(db_prediction)
            db.commit()
            db.refresh(db_prediction)
        except Exception as e:
            logger.error(f"Failed to save prediction to DB: {e}")
            # Don't fail the request if DB save fails
            
        return prediction
        
    except Exception as e:
        logger.error(f"Prediction error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Prediction failed: {str(e)}"
        )


@app.post("/predict/batch", response_model=BatchPredictionResponse, tags=["Prediction"])
async def predict_flood_batch(request: BatchPredictionRequest):
    """
    Predict flood risk for multiple locations
    
    Accepts up to 1000 prediction requests in a single batch.
    Returns predictions with summary statistics.
    """
    try:
        if not predictor.model_loaded:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Model not loaded. Please check server logs."
            )
        
        predictions = predictor.predict_batch(request.predictions)
        
        # Calculate summary statistics
        total_count = len(predictions)
        high_risk_count = sum(1 for p in predictions if p.risk_level == "High")
        
        logger.info(f"Batch prediction made: {total_count} locations, {high_risk_count} high-risk")
        
        return BatchPredictionResponse(
            predictions=predictions,
            total_count=total_count,
            high_risk_count=high_risk_count
        )
        
    except Exception as e:
        logger.error(f"Batch prediction error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Batch prediction failed: {str(e)}"
        )


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Custom HTTP exception handler"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.__class__.__name__,
            "message": exc.detail,
            "detail": None
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """General exception handler"""
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "InternalServerError",
            "message": "An unexpected error occurred",
            "detail": str(exc) if settings.DEBUG else None
        }
    )


@app.get("/weather/live")
async def get_live_weather(lat: float, lon: float):
    """Get live weather data for auto-filling the form"""
    try:
        return await weather_service.get_live_weather(lat, lon)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/weather/history")
async def get_historical_weather(lat: float, lon: float):
    """Get historical weather trends"""
    try:
        return await weather_service.get_historical_weather(lat, lon)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/history", tags=["History"])
async def get_prediction_history(limit: int = 50, db: Session = Depends(get_db)):
    """Get recent prediction history"""
    predictions = db.query(db_models.Prediction).order_by(db_models.Prediction.timestamp.desc()).limit(limit).all()
    return predictions

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
