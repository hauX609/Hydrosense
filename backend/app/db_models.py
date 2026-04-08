from sqlalchemy import Column, Integer, String, Float, DateTime, Text
from datetime import datetime
from .database import Base

class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    location = Column(String, index=True)
    lat = Column(Float)
    lon = Column(Float)
    risk_level = Column(String)
    flood_probability = Column(Float)
    input_data = Column(Text) # Storing JSON as string
