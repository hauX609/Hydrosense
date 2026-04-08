import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import { useEffect, useState } from 'react';
import axios from 'axios';
import './HistoricalChart.css';

interface HistoricalChartProps {
    lat: number;
    lon: number;
    /**
     * Callback when a date is selected. Provides the full data entry for that date.
     */
    onDateSelect?: (entry: { date: string; precipitation: number; temperature: number }) => void;
}

interface ChartData {
    rawDate: string; // original ISO date string from API
    displayDate: string; // formatted for UI
    precipitation: number;
    temperature: number;
}

export default function HistoricalChart({ lat, lon, onDateSelect }: HistoricalChartProps) {
    const [data, setData] = useState<ChartData[]>([]);
    const [loading, setLoading] = useState(false);
    const [selectedDate, setSelectedDate] = useState<string>('');

    useEffect(() => {
        const fetchData = async () => {
            setLoading(true);
            try {
                const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
                const response = await axios.get(`${API_URL}/weather/history?lat=${lat}&lon=${lon}`);
                const { dates, precipitation, temperature } = response.data;

                const chartData = dates.map((date: string, i: number) => ({
                    rawDate: date,
                    displayDate: new Date(date).toLocaleDateString(undefined, { month: 'short', day: 'numeric' }),
                    precipitation: precipitation[i],
                    temperature: temperature[i]
                }));

                setData(chartData);
            } catch (error) {
                console.error('Failed to fetch historical data:', error);
            } finally {
                setLoading(false);
            }
        };
        fetchData();
    }, [lat, lon]);

    const handleDateChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const iso = e.target.value; // YYYY-MM-DD
        setSelectedDate(iso);
        if (onDateSelect) {
            const entry = data.find(d => d.rawDate.slice(0, 10) === iso);
            if (entry) {
                onDateSelect({
                    date: entry.rawDate,
                    precipitation: entry.precipitation,
                    temperature: entry.temperature
                });
            }
        }
    };

    if (loading) {
        return <div className="chart-loading">Loading historical data...</div>;
    }

    return (
        <div className="historical-chart glass">
            <h3>30-Day Weather Trends</h3>
            <div className="date-picker">
                <label htmlFor="historical-date">Select Date:</label>
                <input
                    type="date"
                    id="historical-date"
                    value={selectedDate}
                    onChange={handleDateChange}
                />
            </div>
            <div className="chart-container">
                <ResponsiveContainer width="100%" height={300}>
                    <LineChart data={data.map(d => ({ date: d.displayDate, precipitation: d.precipitation, temperature: d.temperature }))}>
                        <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                        <XAxis dataKey="date" stroke="var(--text-secondary)" fontSize={12} />
                        <YAxis yAxisId="left" stroke="var(--primary-blue)" fontSize={12} />
                        <YAxis yAxisId="right" orientation="right" stroke="var(--risk-medium)" fontSize={12} />
                        <Tooltip
                            contentStyle={{ backgroundColor: 'var(--surface)', border: '1px solid var(--border)' }}
                            labelStyle={{ color: 'var(--text-primary)' }}
                        />
                        <Legend />
                        <Line
                            yAxisId="left"
                            type="monotone"
                            dataKey="precipitation"
                            name="Precipitation (mm)"
                            stroke="var(--primary-blue)"
                            strokeWidth={2}
                            dot={false}
                        />
                        <Line
                            yAxisId="right"
                            type="monotone"
                            dataKey="temperature"
                            name="Max Temp (°C)"
                            stroke="var(--risk-medium)"
                            strokeWidth={2}
                            dot={false}
                        />
                    </LineChart>
                </ResponsiveContainer>
            </div>
        </div>
    );
}
