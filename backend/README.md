# Bangladesh Flood Prediction API - Backend

FastAPI backend for serving flood predictions using a trained CatBoost machine learning model.

## Features

- 🚀 **Fast & Efficient**: Built with FastAPI for high performance
- 🤖 **ML-Powered**: Uses CatBoost classifier for accurate flood predictions
- 🔒 **Type-Safe**: Pydantic models for request/response validation
- 🌐 **CORS-Enabled**: Ready for frontend integration
- 📊 **Batch Predictions**: Support for multiple location predictions
- 📝 **Auto-Documentation**: Interactive API docs with Swagger UI

## Quick Start

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Installation

1. **Navigate to the backend directory**:
   ```bash
   cd backend
   ```

2. **Create a virtual environment** (recommended):
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment** (optional):
   ```bash
   cp .env.example .env
   # Edit .env to customize settings
   ```

### Running the Server

**Development mode** (with auto-reload):
```bash
uvicorn app.main:app --reload
```

**Production mode**:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

The API will be available at: `http://localhost:8000`

## API Documentation

Once the server is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API Endpoints

### Health Check
```http
GET /health
```
Returns server health status and model loading state.

### Model Information
```http
GET /model/info
```
Returns model metadata and required features.

### Single Prediction
```http
POST /predict
Content-Type: application/json

{
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
```

**Response**:
```json
{
  "flood_probability": 0.75,
  "risk_level": "High",
  "is_flood_predicted": true,
  "confidence": 0.85
}
```

### Batch Prediction
```http
POST /predict/batch
Content-Type: application/json

{
  "predictions": [
    { /* prediction request 1 */ },
    { /* prediction request 2 */ }
  ]
}
```

**Response**:
```json
{
  "predictions": [ /* array of prediction responses */ ],
  "total_count": 2,
  "high_risk_count": 1
}
```

## Input Features

The model requires the following 13 features:

| Feature | Type | Description | Range/Units |
|---------|------|-------------|-------------|
| `lat` | float | Latitude | -90 to 90 |
| `lon` | float | Longitude | -180 to 180 |
| `date` | int | Day of year | 1-365 |
| `elevation` | float | Elevation | meters |
| `slope` | float | Terrain slope | degrees (≥0) |
| `landcover` | int | Land cover type code | integer |
| `precip_1d` | float | 1-day precipitation | mm (≥0) |
| `precip_3d` | float | 3-day precipitation | mm (≥0) |
| `precip_7d` | float | 7-day precipitation | mm (≥0) |
| `precip_14d` | float | 14-day precipitation | mm (≥0) |
| `dis_last` | float | Last river discharge | m³/s (≥0) |
| `dis_trend_3` | float | 3-day discharge trend | m³/s |
| `dayofyear` | int | Day of year | 1-365 |

## Risk Levels

Predictions are classified into three risk levels:

- **Low Risk**: Probability < 0.3
- **Medium Risk**: Probability 0.3 - 0.6
- **High Risk**: Probability > 0.6

## Frontend Integration

### CORS Configuration

The backend is pre-configured to accept requests from common frontend development ports:
- http://localhost:3000 (React default)
- http://localhost:5173 (Vite default)
- http://localhost:8080 (Vue default)

To add more origins, edit `CORS_ORIGINS` in `.env` or `app/config.py`.

### Example Frontend Request

**JavaScript/TypeScript**:
```javascript
const response = await fetch('http://localhost:8000/predict', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    lat: 23.8103,
    lon: 90.4125,
    date: 180,
    elevation: 10.5,
    slope: 0.5,
    landcover: 11,
    precip_1d: 50.0,
    precip_3d: 120.0,
    precip_7d: 200.0,
    precip_14d: 300.0,
    dis_last: 1500.0,
    dis_trend_3: 100.0,
    dayofyear: 180
  })
});

const prediction = await response.json();
console.log(prediction);
```

## Project Structure

```
backend/
├── app/
│   ├── __init__.py          # Package initialization
│   ├── main.py              # FastAPI application
│   ├── models.py            # Pydantic models
│   ├── predictor.py         # ML model logic
│   └── config.py            # Configuration
├── models/
│   ├── catboost_multi.cbm   # Trained model
│   └── model_meta.json      # Model metadata
├── requirements.txt         # Dependencies
├── .env.example            # Environment template
└── README.md               # This file
```

## Deployment

### Using Docker (Recommended)

Create a `Dockerfile`:
```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build and run:
```bash
docker build -t flood-api .
docker run -p 8000:8000 flood-api
```

### Using Cloud Platforms

The backend can be deployed to:
- **Render**: Connect GitHub repo and deploy
- **Railway**: One-click deployment
- **Heroku**: Use Procfile with uvicorn
- **AWS/GCP/Azure**: Deploy as container or serverless function

## Troubleshooting

### Model Not Loading
- Ensure `models/catboost_multi.cbm` and `models/model_meta.json` exist
- Check file permissions
- Review server logs for detailed error messages

### CORS Errors
- Add your frontend URL to `CORS_ORIGINS` in config
- Ensure the backend is running before making requests

### Port Already in Use
- Change the port in `.env` or use: `uvicorn app.main:app --port 8001`

## Development

### Running Tests
```bash
pytest tests/
```

### Code Formatting
```bash
black app/
```

### Type Checking
```bash
mypy app/
```

## License

This project is part of the Bangladesh Flood Prediction system.

## Support

For issues or questions, please check the API documentation at `/docs` or review the server logs.
