import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { useState } from 'react';
import { ThemeProvider } from './context/ThemeContext';
import Navigation from './components/Navigation';
import Dashboard from './components/Dashboard';
import Analytics from './components/Analytics';
import SafetyTips from './components/SafetyTips';
import PredictionForm from './components/PredictionForm';
import ResultCard from './components/ResultCard';
import LoadingSpinner from './components/LoadingSpinner';
import { predictFlood, ApiError } from './services/api';
import type { PredictionRequest, PredictionResponse, PredictionHistoryEntry, Alert } from './types';
import './App.css';

function PredictionPage() {
    const [result, setResult] = useState<PredictionResponse | null>(null);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [lastRequest, setLastRequest] = useState<PredictionRequest | null>(null);

    const handlePrediction = async (data: PredictionRequest) => {
        setIsLoading(true);
        setError(null);

        try {
            const prediction = await predictFlood(data);
            setResult(prediction);
            setLastRequest(data);

            // Save to prediction history
            const historyEntry: PredictionHistoryEntry = {
                id: Date.now().toString(),
                timestamp: new Date().toISOString(),
                location: `${data.lat.toFixed(4)}, ${data.lon.toFixed(4)}`,
                lat: data.lat,
                lon: data.lon,
                request: data,
                response: prediction,
            };

            const history = localStorage.getItem('prediction-history');
            const historyArray: PredictionHistoryEntry[] = history ? JSON.parse(history) : [];
            historyArray.push(historyEntry);
            localStorage.setItem('prediction-history', JSON.stringify(historyArray));

            // Create alert if high risk
            if (prediction.risk_level === 'High' || prediction.risk_level === 'Medium') {
                const alert: Alert = {
                    id: Date.now().toString(),
                    timestamp: new Date().toISOString(),
                    location: `${data.lat.toFixed(4)}, ${data.lon.toFixed(4)}`,
                    lat: data.lat,
                    lon: data.lon,
                    riskLevel: prediction.risk_level,
                    probability: prediction.flood_probability,
                    message: `${prediction.risk_level} flood risk detected with ${(prediction.flood_probability * 100).toFixed(1)}% probability`,
                    isRead: false,
                };

                const alerts = localStorage.getItem('flood-alerts');
                const alertsArray: Alert[] = alerts ? JSON.parse(alerts) : [];
                alertsArray.unshift(alert);
                localStorage.setItem('flood-alerts', JSON.stringify(alertsArray));
            }
        } catch (err) {
            if (err instanceof ApiError) {
                setError(`Prediction failed: ${err.message}`);
            } else {
                setError('An unexpected error occurred. Please check if the backend is running.');
            }
            console.error('Prediction error:', err);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <main className="main-content container">
            <div className="content-grid">
                <div className="form-column">
                    <PredictionForm onSubmit={handlePrediction} isLoading={isLoading} />
                </div>

                <div className="result-column">
                    {error && (
                        <div className="error-card glass fade-in">
                            <h3>⚠️ Error</h3>
                            <p>{error}</p>
                            <p className="error-hint">
                                Make sure the backend server is running on http://localhost:8000
                            </p>
                        </div>
                    )}

                    {result && !error && lastRequest && (
                        <ResultCard result={result} request={lastRequest} />
                    )}

                    {!result && !error && (
                        <div className="placeholder-card glass">
                            <div className="placeholder-content">
                                <svg className="placeholder-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                                    <path d="M12 2.69l5.66 5.66a8 8 0 1 1-11.31 0z" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                                </svg>
                                <h3>Ready to Predict</h3>
                                <p>Fill in the location data and click "Predict Flood Risk" to get started.</p>
                            </div>
                        </div>
                    )}
                </div>
            </div>

            {isLoading && <LoadingSpinner />}
        </main>
    );
}

function App() {
    return (
        <ThemeProvider>
            <Router>
                <div className="app">
                    <Navigation />

                    <Routes>
                        <Route path="/" element={<PredictionPage />} />
                        <Route path="/dashboard" element={<Dashboard />} />
                        <Route path="/analytics" element={<Analytics />} />
                        <Route path="/safety" element={<SafetyTips />} />
                    </Routes>
                </div>
            </Router>
        </ThemeProvider>
    );
}

export default App;
