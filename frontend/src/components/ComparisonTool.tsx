import { useState } from 'react';
import { Plus, X, TrendingUp } from 'lucide-react';
import { predictFlood } from '../services/api';
import type { ComparisonLocation, PredictionRequest } from '../types';
import './ComparisonTool.css';

export default function ComparisonTool() {
    const [locations, setLocations] = useState<ComparisonLocation[]>([]);
    const [isLoading, setIsLoading] = useState(false);

    const addLocation = () => {
        if (locations.length >= 3) {
            alert('Maximum 3 locations can be compared');
            return;
        }

        const newLocation: ComparisonLocation = {
            id: Date.now().toString(),
            nickname: `Location ${locations.length + 1}`,
            lat: 23.8103,
            lon: 90.4125,
            precip_1d: 50,
            precip_3d: 120,
            precip_7d: 200,
            precip_14d: 300,
        };

        setLocations([...locations, newLocation]);
    };

    const removeLocation = (id: string) => {
        setLocations(locations.filter(loc => loc.id !== id));
    };

    const updateLocation = (id: string, field: keyof ComparisonLocation, value: any) => {
        setLocations(locations.map(loc =>
            loc.id === id ? { ...loc, [field]: value } : loc
        ));
    };

    const runComparison = async () => {
        setIsLoading(true);

        const updatedLocations = await Promise.all(
            locations.map(async (loc) => {
                try {
                    const request: PredictionRequest = {
                        lat: loc.lat,
                        lon: loc.lon,
                        date: new Date().getDay(),
                        elevation: 10,
                        slope: 0.5,
                        landcover: 11,
                        precip_1d: loc.precip_1d || 50,
                        precip_3d: loc.precip_3d || 120,
                        precip_7d: loc.precip_7d || 200,
                        precip_14d: loc.precip_14d || 300,
                        dis_last: 1500,
                        dis_trend_3: 100,
                        dayofyear: new Date().getDay(),
                    };

                    const prediction = await predictFlood(request);
                    return { ...loc, prediction };
                } catch (error) {
                    console.error(`Failed to predict for ${loc.nickname}:`, error);
                    return loc;
                }
            })
        );

        setLocations(updatedLocations);
        setIsLoading(false);
    };

    return (
        <div className="comparison-tool">
            <div className="comparison-header">
                <h2>📍 Location Comparison</h2>
                <p>Compare flood risk across multiple locations</p>
            </div>

            <div className="comparison-actions">
                <button
                    onClick={addLocation}
                    className="add-location-btn"
                    disabled={locations.length >= 3}
                >
                    <Plus size={18} />
                    Add Location
                </button>
                {locations.length > 0 && (
                    <button
                        onClick={runComparison}
                        className="compare-btn"
                        disabled={isLoading}
                    >
                        <TrendingUp size={18} />
                        {isLoading ? 'Analyzing...' : 'Compare All'}
                    </button>
                )}
            </div>

            <div className="comparison-grid">
                {locations.map((loc) => (
                    <div key={loc.id} className="comparison-card glass">
                        <button
                            className="remove-btn"
                            onClick={() => removeLocation(loc.id)}
                        >
                            <X size={16} />
                        </button>

                        <div className="location-inputs">
                            <div className="input-group">
                                <label>Nickname</label>
                                <input
                                    type="text"
                                    value={loc.nickname}
                                    onChange={(e) => updateLocation(loc.id, 'nickname', e.target.value)}
                                    placeholder="Location name"
                                />
                            </div>

                            <div className="input-row">
                                <div className="input-group">
                                    <label>Latitude</label>
                                    <input
                                        type="number"
                                        value={loc.lat}
                                        onChange={(e) => updateLocation(loc.id, 'lat', parseFloat(e.target.value))}
                                        step="0.0001"
                                    />
                                </div>

                                <div className="input-group">
                                    <label>Longitude</label>
                                    <input
                                        type="number"
                                        value={loc.lon}
                                        onChange={(e) => updateLocation(loc.id, 'lon', parseFloat(e.target.value))}
                                        step="0.0001"
                                    />
                                </div>
                            </div>

                            <div className="precipitation-inputs">
                                <h4>Precipitation (mm)</h4>
                                <div className="input-grid-small">
                                    <div className="input-group">
                                        <label>1-Day</label>
                                        <input
                                            type="number"
                                            value={loc.precip_1d || 0}
                                            onChange={(e) => updateLocation(loc.id, 'precip_1d', parseFloat(e.target.value))}
                                            placeholder="0"
                                        />
                                    </div>
                                    <div className="input-group">
                                        <label>3-Day</label>
                                        <input
                                            type="number"
                                            value={loc.precip_3d || 0}
                                            onChange={(e) => updateLocation(loc.id, 'precip_3d', parseFloat(e.target.value))}
                                            placeholder="0"
                                        />
                                    </div>
                                    <div className="input-group">
                                        <label>7-Day</label>
                                        <input
                                            type="number"
                                            value={loc.precip_7d || 0}
                                            onChange={(e) => updateLocation(loc.id, 'precip_7d', parseFloat(e.target.value))}
                                            placeholder="0"
                                        />
                                    </div>
                                    <div className="input-group">
                                        <label>14-Day</label>
                                        <input
                                            type="number"
                                            value={loc.precip_14d || 0}
                                            onChange={(e) => updateLocation(loc.id, 'precip_14d', parseFloat(e.target.value))}
                                            placeholder="0"
                                        />
                                    </div>
                                </div>
                            </div>
                        </div>

                        {loc.prediction && (
                            <div className="prediction-result">
                                <div className={`risk-level ${loc.prediction.risk_level.toLowerCase()}`}>
                                    {loc.prediction.risk_level} Risk
                                </div>
                                <div className="probability-display">
                                    <span className="probability-value">
                                        {(loc.prediction.flood_probability * 100).toFixed(1)}%
                                    </span>
                                    <span className="probability-label">Flood Probability</span>
                                </div>
                                <div className="confidence-display">
                                    Confidence: {(loc.prediction.confidence * 100).toFixed(1)}%
                                </div>
                            </div>
                        )}
                    </div>
                ))}
            </div>

            {locations.length === 0 && (
                <div className="empty-comparison glass">
                    <p>Click "Add Location" to start comparing flood risks</p>
                </div>
            )}
        </div>
    );
}
