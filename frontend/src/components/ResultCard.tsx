import { CheckCircle, AlertTriangle, AlertCircle, TrendingUp } from 'lucide-react';
import RiskGauge from './RiskGauge';
import ExportPDF from './ExportPDF';
import type { PredictionResponse, PredictionRequest } from '../types';
import './ResultCard.css';

interface ResultCardProps {
    result: PredictionResponse;
    request: PredictionRequest;
}

export default function ResultCard({ result, request }: ResultCardProps) {
    const getRiskColor = () => {
        switch (result.risk_level) {
            case 'Low': return 'var(--risk-low)';
            case 'Medium': return 'var(--risk-medium)';
            case 'High': return 'var(--risk-high)';
            default: return 'var(--text-secondary)';
        }
    };

    const getRiskIcon = () => {
        switch (result.risk_level) {
            case 'Low': return <CheckCircle size={24} />;
            case 'Medium': return <AlertCircle size={24} />;
            case 'High': return <AlertTriangle size={24} />;
            default: return null;
        }
    };

    const getRiskGradient = () => {
        switch (result.risk_level) {
            case 'Low': return 'var(--gradient-risk-low)';
            case 'Medium': return 'var(--gradient-risk-medium)';
            case 'High': return 'var(--gradient-risk-high)';
            default: return 'var(--gradient-surface)';
        }
    };

    return (
        <div className="result-card glass fade-in">
            <div className="result-header">
                <h2>Prediction Results</h2>
            </div>

            <div className="risk-badge" style={{ background: getRiskGradient(), color: 'white' }}>
                <div className="risk-badge-content">
                    {getRiskIcon()}
                    <div>
                        <div className="risk-level">{result.risk_level} Risk</div>
                        <div className="risk-subtitle">
                            {result.is_flood_predicted ? 'Flood Predicted' : 'No Flood Predicted'}
                        </div>
                    </div>
                </div>
            </div>

            <RiskGauge probability={result.flood_probability} riskLevel={result.risk_level} />

            <div className="metrics-grid">
                <div className="metric-card">
                    <div className="metric-label">Flood Probability</div>
                    <div className="metric-value" style={{ color: getRiskColor() }}>
                        {(result.flood_probability * 100).toFixed(1)}%
                    </div>
                </div>

                <div className="metric-card">
                    <div className="metric-label">
                        <TrendingUp size={16} />
                        Model Confidence
                    </div>
                    <div className="metric-value">
                        {(result.confidence * 100).toFixed(1)}%
                    </div>
                </div>
            </div>

            <div className="prediction-status">
                <div className="status-indicator" style={{ background: getRiskColor() }}></div>
                <p>
                    {result.is_flood_predicted
                        ? 'High likelihood of flooding detected. Take necessary precautions.'
                        : 'Low likelihood of flooding. Continue monitoring conditions.'}
                </p>
            </div>

            <ExportPDF
                prediction={result}
                request={request}
                location={`${request.lat.toFixed(4)}, ${request.lon.toFixed(4)}`}
            />
        </div>
    );
}
