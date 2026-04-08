import { useState, FormEvent, useEffect } from 'react';
import { MapPin, Mountain, Cloud, Waves, Sparkles, Activity, Map as MapIcon } from 'lucide-react';
import axios from 'axios';
import type { PredictionRequest } from '../types';
import MapSelector from './MapSelector';
import HistoricalChart from './HistoricalChart';
import './PredictionForm.css';

interface PredictionFormProps {
    onSubmit: (data: PredictionRequest) => void;
    isLoading: boolean;
}

export default function PredictionForm({ onSubmit, isLoading }: PredictionFormProps) {
    const [showMap, setShowMap] = useState(false);
    const [isFetchingWeather, setIsFetchingWeather] = useState(false);
    const [formData, setFormData] = useState<PredictionRequest>({
        lat: 23.8103,
        lon: 90.4125,
        date: new Date().getDay(), // Approximate day of year
        elevation: 10.5,
        slope: 0.5,
        landcover: 11,
        precip_1d: 50.0,
        precip_3d: 120.0,
        precip_7d: 200.0,
        precip_14d: 300.0,
        dis_last: 1500.0,
        dis_trend_3: 100.0,
        dayofyear: new Date().getDay(),
    });

    // Load saved data on mount
    useEffect(() => {
        const savedData = localStorage.getItem('prediction-form-data');
        if (savedData) {
            try {
                setFormData(JSON.parse(savedData));
            } catch (e) {
                console.error("Failed to parse saved form data", e);
            }
        }
    }, []);

    // Save data on change
    useEffect(() => {
        localStorage.setItem('prediction-form-data', JSON.stringify(formData));
    }, [formData]);

    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const { name, value } = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: parseFloat(value) || 0
        }));
    };

    const handleLocationSelect = (lat: number, lon: number) => {
        setFormData(prev => ({ ...prev, lat, lon }));
    };

    const fetchLiveData = async () => {
        setIsFetchingWeather(true);
        try {
            const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
            const response = await axios.get(`${API_URL}/weather/live?lat=${formData.lat}&lon=${formData.lon}`);
            const data = response.data;

            setFormData(prev => ({
                ...prev,
                elevation: data.elevation,
                precip_1d: data.precip_1d,
                precip_3d: data.precip_3d,
                precip_7d: data.precip_7d,
                precip_14d: data.precip_14d,
                // Keep existing values for fields not returned by API or use defaults
                slope: data.slope || prev.slope,
                landcover: data.landcover || prev.landcover,
                dis_last: data.dis_last || prev.dis_last,
                dis_trend_3: data.dis_trend_3 || prev.dis_trend_3
            }));
        } catch (error) {
            console.error("Failed to fetch live weather data:", error);
            alert("Failed to fetch live weather data. Please try again.");
        } finally {
            setIsFetchingWeather(false);
        }
    };

    // Handler for date selection from HistoricalChart
    const handleHistoricalDateSelect = (entry: { date: string; precipitation: number; temperature: number }) => {
        // Convert ISO date to day of year
        const dateObj = new Date(entry.date);
        const start = new Date(dateObj.getFullYear(), 0, 0);
        const diff = dateObj.getTime() - start.getTime();
        const oneDay = 1000 * 60 * 60 * 24;
        const dayOfYear = Math.floor(diff / oneDay);

        setFormData(prev => ({
            ...prev,
            precip_1d: entry.precipitation,
            precip_3d: entry.precipitation,
            precip_7d: entry.precipitation,
            precip_14d: entry.precipitation,
            dayofyear: dayOfYear,
            date: dayOfYear
        }));
    };

    const handleSubmit = (e: FormEvent) => {
        e.preventDefault();
        onSubmit(formData);
    };

    const fillSampleData = () => {
        setFormData({
            lat: 24.3636,
            lon: 88.6241,
            date: 210,
            elevation: 8.2,
            slope: 0.3,
            landcover: 11,
            precip_1d: 85.0,
            precip_3d: 180.0,
            precip_7d: 320.0,
            precip_14d: 450.0,
            dis_last: 2200.0,
            dis_trend_3: 250.0,
            dayofyear: 210,
        });
    };

    return (
        <div className="form-container">
            <form className="prediction-form glass" onSubmit={handleSubmit}>
                <div className="form-header">
                    <h2>Enter Location Data</h2>
                    <div className="header-actions">
                        <button type="button" onClick={() => setShowMap(!showMap)} className="icon-btn" title="Toggle Map">
                            <MapIcon size={18} />
                            {showMap ? 'Hide Map' : 'Show Map'}
                        </button>
                        <button type="button" onClick={fillSampleData} className="sample-btn">
                            <Sparkles size={16} />
                            Sample
                        </button>
                    </div>
                </div>

                {showMap && (
                    <MapSelector
                        lat={formData.lat}
                        lon={formData.lon}
                        onLocationSelect={handleLocationSelect}
                    />
                )}

                {/* Location Section */}
                <div className="form-section">
                    <div className="section-header">
                        <MapPin size={20} />
                        <h3>Location</h3>
                    </div>
                    <div className="input-grid">
                        <div className="input-group">
                            <label htmlFor="lat">Latitude</label>
                            <input
                                type="number"
                                id="lat"
                                name="lat"
                                value={formData.lat}
                                onChange={handleChange}
                                step="0.0001"
                                required
                            />
                        </div>
                        <div className="input-group">
                            <label htmlFor="lon">Longitude</label>
                            <input
                                type="number"
                                id="lon"
                                name="lon"
                                value={formData.lon}
                                onChange={handleChange}
                                step="0.0001"
                                required
                            />
                        </div>
                    </div>
                    <button
                        type="button"
                        onClick={fetchLiveData}
                        className="live-data-btn"
                        disabled={isFetchingWeather}
                    >
                        {isFetchingWeather ? (
                            <>Loading...</>
                        ) : (
                            <>
                                <Activity size={16} />
                                Fetch Live Weather & Elevation
                            </>
                        )}
                    </button>
                </div>

                {/* Terrain Section */}
                <div className="form-section">
                    <div className="section-header">
                        <Mountain size={20} />
                        <h3>Terrain</h3>
                    </div>
                    <div className="input-grid">
                        <div className="input-group">
                            <label htmlFor="elevation">Elevation (m)</label>
                            <input
                                type="number"
                                id="elevation"
                                name="elevation"
                                value={formData.elevation}
                                onChange={handleChange}
                                step="0.1"
                                required
                            />
                        </div>
                        <div className="input-group">
                            <label htmlFor="slope">Slope (degrees)</label>
                            <input
                                type="number"
                                id="slope"
                                name="slope"
                                value={formData.slope}
                                onChange={handleChange}
                                step="0.1"
                                required
                            />
                        </div>
                        <div className="input-group">
                            <label htmlFor="landcover">Land Cover</label>
                            <input
                                type="number"
                                id="landcover"
                                name="landcover"
                                value={formData.landcover}
                                onChange={handleChange}
                                required
                            />
                        </div>
                    </div>
                </div>

                {/* Precipitation Section */}
                <div className="form-section">
                    <div className="section-header">
                        <Cloud size={20} />
                        <h3>Precipitation (mm)</h3>
                    </div>
                    <div className="input-grid">
                        <div className="input-group">
                            <label htmlFor="precip_1d">1-Day Total</label>
                            <input
                                type="number"
                                id="precip_1d"
                                name="precip_1d"
                                value={formData.precip_1d}
                                onChange={handleChange}
                                step="0.1"
                                required
                            />
                        </div>
                        <div className="input-group">
                            <label htmlFor="precip_3d">3-Day Total</label>
                            <input
                                type="number"
                                id="precip_3d"
                                name="precip_3d"
                                value={formData.precip_3d}
                                onChange={handleChange}
                                step="0.1"
                                required
                            />
                        </div>
                        <div className="input-group">
                            <label htmlFor="precip_7d">7-Day Total</label>
                            <input
                                type="number"
                                id="precip_7d"
                                name="precip_7d"
                                value={formData.precip_7d}
                                onChange={handleChange}
                                step="0.1"
                                required
                            />
                        </div>
                        <div className="input-group">
                            <label htmlFor="precip_14d">14-Day Total</label>
                            <input
                                type="number"
                                id="precip_14d"
                                name="precip_14d"
                                value={formData.precip_14d}
                                onChange={handleChange}
                                step="0.1"
                                required
                            />
                        </div>
                    </div>
                </div>

                {/* River Data Section */}
                <div className="form-section">
                    <div className="section-header">
                        <Waves size={20} />
                        <h3>River Discharge</h3>
                    </div>
                    <div className="input-grid">
                        <div className="input-group">
                            <label htmlFor="dis_last">Last Discharge</label>
                            <input
                                type="number"
                                id="dis_last"
                                name="dis_last"
                                value={formData.dis_last}
                                onChange={handleChange}
                                step="0.1"
                                required
                            />
                        </div>
                        <div className="input-group">
                            <label htmlFor="dis_trend_3">3-Day Trend</label>
                            <input
                                type="number"
                                id="dis_trend_3"
                                name="dis_trend_3"
                                value={formData.dis_trend_3}
                                onChange={handleChange}
                                step="0.1"
                                required
                            />
                        </div>
                    </div>
                </div>

                <button type="submit" className="submit-btn" disabled={isLoading}>
                    {isLoading ? 'Analyzing...' : 'Predict Flood Risk'}
                </button>
            </form>

            <HistoricalChart lat={formData.lat} lon={formData.lon} onDateSelect={handleHistoricalDateSelect} />
        </div>
    );
}
