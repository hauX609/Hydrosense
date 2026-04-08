# 🌊 Bangladesh Flood Predictor

An AI-powered flood risk prediction system for Bangladesh using machine learning and real-time weather data.

![Project Demo](https://img.shields.io/badge/Status-Production%20Ready-brightgreen)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109.0-009688?logo=fastapi)
![React](https://img.shields.io/badge/React-19.2.0-61DAFB?logo=react)
![TypeScript](https://img.shields.io/badge/TypeScript-5.9.3-3178C6?logo=typescript)
![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python)

## 📋 Overview

The Bangladesh Flood Predictor is a comprehensive web application that combines machine learning, real-time weather data, and interactive visualizations to predict flood risks for any location in Bangladesh. The system uses a trained CatBoost model and integrates with the Open-Meteo API to provide accurate, data-driven flood risk assessments.

## ✨ Features

### 🗺️ Interactive Map
- Click-to-select location on OpenStreetMap
- Real-time coordinate updates
- Visual marker for selected location

### 🌤️ Live Weather Data
- Fetches current weather conditions from Open-Meteo API
- Automatic form population with:
  - Elevation data
  - 1, 3, 7, and 14-day precipitation totals
- One-click data retrieval

### 📊 Historical Weather Trends
- 30-day weather visualization
- Dual-axis chart showing:
  - Precipitation (mm)
  - Maximum temperature (°C)
- Interactive date picker for historical analysis
- Automatic form population from selected dates

### 🤖 AI-Powered Predictions
- CatBoost machine learning model
- Three-tier risk classification (Low/Medium/High)
- Confidence scoring
- Visual risk gauge with color coding

### 🎨 Modern UI/UX
- Glassmorphism design
- Smooth animations and transitions
- Responsive layout
- Accessible controls
- Dark theme optimized

## 🏗️ Architecture

```
Bangladesh_Flood_Project/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── main.py         # FastAPI application
│   │   ├── models.py       # Pydantic models
│   │   ├── predictor.py    # ML model logic
│   │   ├── weather.py      # Weather service
│   │   └── config.py       # Configuration
│   ├── models/
│   │   ├── catboost_multi.cbm  # Trained model
│   │   └── model_meta.json     # Model metadata
│   └── requirements.txt
│
└── frontend/               # React frontend
    ├── src/
    │   ├── components/     # React components
    │   ├── types/         # TypeScript types
    │   └── main.tsx       # Entry point
    ├── package.json
    └── vite.config.ts
```

## 🚀 Getting Started

### Prerequisites

- **Python**: 3.10 or higher
- **Node.js**: 18.0 or higher
- **npm**: 9.0 or higher

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. Start the FastAPI server:
```bash
uvicorn app.main:app --reload
```

The backend will be available at `http://localhost:8000`

**API Documentation**: 
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install Node dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm run dev
```

The frontend will be available at `http://localhost:5174`

## 📡 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/predict` | POST | Get flood risk prediction |
| `/weather/live` | GET | Fetch live weather data |
| `/weather/history` | GET | Get 30-day historical data |
| `/health` | GET | Health check |
| `/model/info` | GET | Model metadata |

### Example Request

```bash
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{
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
  }'
```

### Example Response

```json
{
  "flood_probability": 0.2157,
  "risk_level": "Low",
  "is_flood_predicted": false,
  "confidence": 0.5687
}
```

## 🛠️ Technology Stack

### Backend
- **FastAPI**: Modern, fast web framework
- **CatBoost**: Gradient boosting ML library
- **HTTPX**: Async HTTP client
- **Pydantic**: Data validation
- **Uvicorn**: ASGI server

### Frontend
- **React 19**: UI library
- **TypeScript**: Type-safe JavaScript
- **Vite**: Build tool
- **React Leaflet**: Interactive maps
- **Recharts**: Data visualization
- **Axios**: HTTP client
- **Lucide React**: Icon library

### External APIs
- **Open-Meteo**: Weather data API

## 📊 Model Information

The flood prediction model is a CatBoost classifier trained on historical flood data from Bangladesh.

**Input Features** (13):
- Geographic: `lat`, `lon`, `date`, `dayofyear`
- Terrain: `elevation`, `slope`, `landcover`
- Precipitation: `precip_1d`, `precip_3d`, `precip_7d`, `precip_14d`
- River discharge: `dis_last`, `dis_trend_3`

**Output**:
- Flood probability (0-1)
- Risk level (Low/Medium/High)
- Binary prediction (flood/no flood)
- Confidence score

## 🎯 Usage Workflow

1. **Select Location**: Use the interactive map or enter coordinates manually
2. **Fetch Live Data**: Click "Fetch Live Weather & Elevation" to get current conditions
3. **View Historical Trends**: Scroll down to see 30-day weather patterns
4. **Select Historical Date** (Optional): Choose a specific date to analyze past scenarios
5. **Predict**: Click "Predict Flood Risk" to get AI-powered risk assessment
6. **Review Results**: View risk level, probability, and confidence scores

## 🔧 Configuration

### Backend Configuration

Edit `backend/app/config.py` to customize:
- CORS origins
- Risk thresholds
- Model paths
- Server settings

### Frontend Configuration

Edit `frontend/vite.config.ts` for:
- Development server port
- Build optimizations
- Dependency pre-bundling

## 🚢 Deployment

### Backend Deployment (Render)

1. Push code to GitHub
2. Create new Web Service on Render
3. Connect repository
4. Set build command: `pip install -r requirements.txt`
5. Set start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### Frontend Deployment (Vercel/Netlify)

1. Push code to GitHub
2. Connect repository to Vercel/Netlify
3. Set build command: `npm run build`
4. Set publish directory: `dist`

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License.

## 👥 Authors

- **Your Name** - Initial work

## 🙏 Acknowledgments

- Open-Meteo for providing free weather data API
- CatBoost team for the excellent ML library
- React and FastAPI communities

## 📧 Contact

For questions or support, please open an issue on GitHub.

---

**Made with ❤️ for Bangladesh**
