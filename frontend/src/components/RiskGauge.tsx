import { useEffect, useState } from 'react';
import './RiskGauge.css';

interface RiskGaugeProps {
    probability: number;
    riskLevel: 'Low' | 'Medium' | 'High';
}

export default function RiskGauge({ probability }: RiskGaugeProps) {
    const [animatedValue, setAnimatedValue] = useState(0);

    useEffect(() => {
        const timer = setTimeout(() => {
            setAnimatedValue(probability);
        }, 100);
        return () => clearTimeout(timer);
    }, [probability]);

    const percentage = Math.round(animatedValue * 100);
    const rotation = (animatedValue * 180) - 90; // -90 to 90 degrees

    const getGaugeColor = () => {
        if (probability < 0.3) return 'var(--risk-low)';
        if (probability < 0.6) return 'var(--risk-medium)';
        return 'var(--risk-high)';
    };

    return (
        <div className="risk-gauge">
            <svg className="gauge-svg" viewBox="0 0 200 120">
                {/* Background arc */}
                <path
                    d="M 20 100 A 80 80 0 0 1 180 100"
                    fill="none"
                    stroke="rgba(255, 255, 255, 0.1)"
                    strokeWidth="20"
                    strokeLinecap="round"
                />

                {/* Colored arc */}
                <path
                    d="M 20 100 A 80 80 0 0 1 180 100"
                    fill="none"
                    stroke={getGaugeColor()}
                    strokeWidth="20"
                    strokeLinecap="round"
                    strokeDasharray={`${animatedValue * 251.2} 251.2`}
                    className="gauge-fill"
                />

                {/* Needle */}
                <g transform={`rotate(${rotation} 100 100)`}>
                    <line
                        x1="100"
                        y1="100"
                        x2="100"
                        y2="40"
                        stroke="white"
                        strokeWidth="3"
                        strokeLinecap="round"
                    />
                    <circle cx="100" cy="100" r="6" fill="white" />
                </g>
            </svg>

            <div className="gauge-value">
                <div className="gauge-percentage">{percentage}%</div>
                <div className="gauge-label">Flood Probability</div>
            </div>
        </div>
    );
}
