import { useEffect, useState } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, LineChart, Line, Legend } from 'recharts';
import StatCard from './StatCard';
import type { StatisticsData, PredictionHistoryEntry } from '../types';
import './Dashboard.css';

export default function Dashboard() {
    const [stats, setStats] = useState<StatisticsData>({
        totalPredictions: 0,
        highRiskCount: 0,
        mediumRiskCount: 0,
        lowRiskCount: 0,
        averageRisk: 0,
        recentPredictions: [],
    });

    useEffect(() => {
        // Load statistics from localStorage
        const history = localStorage.getItem('prediction-history');
        if (history) {
            const predictions: PredictionHistoryEntry[] = JSON.parse(history);

            const highRisk = predictions.filter(p => p.response.risk_level === 'High').length;
            const mediumRisk = predictions.filter(p => p.response.risk_level === 'Medium').length;
            const lowRisk = predictions.filter(p => p.response.risk_level === 'Low').length;

            const avgRisk = predictions.length > 0
                ? predictions.reduce((sum, p) => sum + p.response.flood_probability, 0) / predictions.length
                : 0;

            setStats({
                totalPredictions: predictions.length,
                highRiskCount: highRisk,
                mediumRiskCount: mediumRisk,
                lowRiskCount: lowRisk,
                averageRisk: avgRisk,
                recentPredictions: predictions.slice(-10).reverse(),
            });
        }
    }, []);

    // Prepare chart data
    const riskDistribution = [
        { name: 'Low Risk', value: stats.lowRiskCount, fill: '#10B981' },
        { name: 'Medium Risk', value: stats.mediumRiskCount, fill: '#F59E0B' },
        { name: 'High Risk', value: stats.highRiskCount, fill: '#EF4444' },
    ];

    const trendData = stats.recentPredictions.map((pred, idx) => ({
        name: `#${stats.recentPredictions.length - idx}`,
        probability: (pred.response.flood_probability * 100).toFixed(1),
        confidence: (pred.response.confidence * 100).toFixed(1),
    })).reverse();

    return (
        <div className="dashboard">
            <div className="dashboard-header">
                <h1>📊 Flood Prediction Dashboard</h1>
                <p>Overview of flood risk analysis and predictions</p>
            </div>

            {/* Statistics Cards */}
            <div className="stats-grid">
                <StatCard
                    icon="activity"
                    label="Total Predictions"
                    value={stats.totalPredictions}
                    color="blue"
                />
                <StatCard
                    icon="alert"
                    label="High Risk Areas"
                    value={stats.highRiskCount}
                    color="red"
                />
                <StatCard
                    icon="trending"
                    label="Medium Risk"
                    value={stats.mediumRiskCount}
                    color="orange"
                />
                <StatCard
                    icon="check"
                    label="Low Risk"
                    value={stats.lowRiskCount}
                    color="green"
                />
            </div>

            {/* Charts Section */}
            {stats.totalPredictions > 0 && (
                <div className="charts-section">
                    <div className="chart-card glass">
                        <h3>Risk Level Distribution</h3>
                        <ResponsiveContainer width="100%" height={300}>
                            <BarChart data={riskDistribution}>
                                <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
                                <XAxis dataKey="name" stroke="var(--text-secondary)" />
                                <YAxis stroke="var(--text-secondary)" />
                                <Tooltip
                                    contentStyle={{
                                        background: 'var(--surface)',
                                        border: '1px solid var(--border)',
                                        borderRadius: 'var(--radius-sm)',
                                        color: 'var(--text-primary)'
                                    }}
                                />
                                <Bar dataKey="value" fill="var(--primary-blue)" radius={[8, 8, 0, 0]} />
                            </BarChart>
                        </ResponsiveContainer>
                    </div>

                    <div className="chart-card glass">
                        <h3>Recent Prediction Trends</h3>
                        <ResponsiveContainer width="100%" height={300}>
                            <LineChart data={trendData}>
                                <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
                                <XAxis dataKey="name" stroke="var(--text-secondary)" />
                                <YAxis stroke="var(--text-secondary)" />
                                <Tooltip
                                    contentStyle={{
                                        background: 'var(--surface)',
                                        border: '1px solid var(--border)',
                                        borderRadius: 'var(--radius-sm)',
                                        color: 'var(--text-primary)'
                                    }}
                                />
                                <Legend />
                                <Line
                                    type="monotone"
                                    dataKey="probability"
                                    stroke="var(--primary-blue)"
                                    strokeWidth={2}
                                    name="Flood Probability (%)"
                                />
                                <Line
                                    type="monotone"
                                    dataKey="confidence"
                                    stroke="var(--accent-teal)"
                                    strokeWidth={2}
                                    name="Confidence (%)"
                                />
                            </LineChart>
                        </ResponsiveContainer>
                    </div>
                </div>
            )}

            {/* Recent Predictions List */}
            {stats.recentPredictions.length > 0 && (
                <div className="recent-predictions glass">
                    <h3>Recent Predictions</h3>
                    <div className="predictions-list">
                        {stats.recentPredictions.map((pred) => (
                            <div key={pred.id} className="prediction-item">
                                <div className="prediction-info">
                                    <span className="prediction-location">📍 {pred.location}</span>
                                    <span className="prediction-time">
                                        {new Date(pred.timestamp).toLocaleString()}
                                    </span>
                                </div>
                                <div className="prediction-result">
                                    <span className={`risk-badge ${pred.response.risk_level.toLowerCase()}`}>
                                        {pred.response.risk_level} Risk
                                    </span>
                                    <span className="probability">
                                        {(pred.response.flood_probability * 100).toFixed(1)}%
                                    </span>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {stats.totalPredictions === 0 && (
                <div className="empty-state glass">
                    <h3>No Predictions Yet</h3>
                    <p>Start making predictions to see your dashboard statistics and trends.</p>
                </div>
            )}
        </div>
    );
}
