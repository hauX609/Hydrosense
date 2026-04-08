# Bangladesh Flood Predictor - Frontend

Beautiful, modern React + TypeScript frontend for AI-powered flood risk prediction.

## 🎨 Features

- **Stunning UI**: Glassmorphism design with vibrant gradients
- **Real-time Predictions**: Instant flood risk assessment
- **Interactive Visualizations**: Animated risk gauge and color-coded results
- **Responsive Design**: Works perfectly on all devices
- **Type-Safe**: Full TypeScript implementation
- **Error Handling**: Graceful error states and user feedback

## 🚀 Quick Start

### Prerequisites

- Node.js 16+ and npm
- Backend API running on `http://localhost:8000`

### Installation

```bash
# Install dependencies
npm install

# Start development server
npm run dev
```

The app will be available at `http://localhost:5174`

## 📁 Project Structure

```
src/
├── components/
│   ├── Header.tsx           # App header with branding
│   ├── PredictionForm.tsx   # Input form for all 13 features
│   ├── ResultCard.tsx       # Prediction results display
│   ├── RiskGauge.tsx        # Animated SVG risk gauge
│   └── LoadingSpinner.tsx   # Loading animation
├── services/
│   └── api.ts               # Backend API integration
├── types/
│   └── index.ts             # TypeScript type definitions
├── App.tsx                  # Main application component
├── App.css                  # App-level styles
├── index.css                # Global styles and design system
└── main.tsx                 # Application entry point
```

## 🎯 Usage

1. **Fill in Location Data**: Enter all 13 required features:
   - Location: Latitude, Longitude, Date, Day of Year
   - Terrain: Elevation, Slope, Land Cover
   - Precipitation: 1-day, 3-day, 7-day, 14-day totals
   - River: Last discharge, 3-day trend

2. **Quick Fill**: Click "Fill Sample Data" for pre-populated values

3. **Predict**: Click "Predict Flood Risk" to get results

4. **View Results**: See flood probability, risk level, and confidence score

## 🎨 Design System

### Colors

- **Primary**: `#0EA5E9` (Sky Blue)
- **Accent**: `#14B8A6` (Teal)
- **Risk Low**: `#10B981` (Green)
- **Risk Medium**: `#F59E0B` (Amber)
- **Risk High**: `#EF4444` (Red)

### Typography

- **Font**: Inter (Google Fonts)
- **Weights**: 400 (regular), 500 (medium), 600 (semibold), 700 (bold)

### Effects

- Glassmorphism with `backdrop-filter: blur(10px)`
- Smooth transitions (300ms ease-in-out)
- Gradient overlays and shadows
- Animated risk indicators

## 🔌 API Integration

The frontend connects to the FastAPI backend at `http://localhost:8000`.

### Endpoints Used

- `POST /predict` - Get flood prediction
- `GET /model/info` - Fetch model metadata
- `GET /health` - Check backend status

### Changing API URL

Edit `src/services/api.ts`:

```typescript
const API_BASE_URL = 'https://your-backend-url.com';
```

## 📱 Responsive Design

- **Desktop**: Two-column layout (form | results)
- **Tablet**: Single column, optimized spacing
- **Mobile**: Compact layout, touch-friendly inputs

## 🛠️ Development

### Build for Production

```bash
npm run build
```

Output will be in the `dist/` directory.

### Preview Production Build

```bash
npm run preview
```

### Lint Code

```bash
npm run lint
```

## 🚀 Deployment

### Vercel (Recommended)

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel
```

### Netlify

1. Connect your GitHub repository
2. Build command: `npm run build`
3. Publish directory: `dist`

### Environment Variables

For production, set:

```
VITE_API_URL=https://your-backend-api.com
```

Then update `api.ts` to use `import.meta.env.VITE_API_URL`.

## 🎯 Key Components

### PredictionForm

- Organized into 4 sections (Location, Terrain, Precipitation, River)
- Real-time validation
- Sample data quick-fill
- Disabled state during loading

### ResultCard

- Dynamic risk level badge
- Color-coded indicators
- Animated entrance
- Detailed metrics display

### RiskGauge

- SVG-based circular gauge
- Animated fill and needle
- Color transitions based on risk level

## 🐛 Troubleshooting

### Backend Connection Error

**Error**: "An unexpected error occurred. Please check if the backend is running."

**Solution**: Ensure the FastAPI backend is running on `http://localhost:8000`. Start it with:

```bash
cd ../backend
uvicorn app.main:app --reload
```

### Port Already in Use

If port 5174 is in use, Vite will automatically try another port. Check the terminal output for the actual URL.

### CORS Errors

The backend is pre-configured to accept requests from `localhost:5173` and `localhost:5174`. If you're using a different port, update the backend's CORS settings in `backend/app/config.py`.

## 📦 Dependencies

- **react** ^18.3.1 - UI library
- **react-dom** ^18.3.1 - React DOM renderer
- **typescript** ^5.6.2 - Type safety
- **vite** ^7.2.4 - Build tool
- **lucide-react** ^0.469.0 - Icon library

## 🎨 Customization

### Change Theme Colors

Edit `src/index.css` CSS variables:

```css
:root {
  --primary-blue: #0EA5E9;
  --accent-teal: #14B8A6;
  /* ... */
}
```

### Modify Risk Thresholds

Update thresholds in `src/components/RiskGauge.tsx`:

```typescript
if (probability < 0.3) return 'Low';
if (probability < 0.6) return 'Medium';
return 'High';
```

## 📄 License

Part of the Bangladesh Flood Prediction System.

## 🤝 Support

For issues or questions, check the browser console for detailed error messages.
