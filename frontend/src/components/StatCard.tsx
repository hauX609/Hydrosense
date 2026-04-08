import { TrendingUp, AlertTriangle, CheckCircle, Activity } from 'lucide-react';
import './StatCard.css';

interface StatCardProps {
    icon: 'trending' | 'alert' | 'check' | 'activity';
    label: string;
    value: string | number;
    trend?: string;
    color?: 'blue' | 'red' | 'green' | 'orange';
}

export default function StatCard({ icon, label, value, trend, color = 'blue' }: StatCardProps) {
    const icons = {
        trending: TrendingUp,
        alert: AlertTriangle,
        check: CheckCircle,
        activity: Activity,
    };

    const Icon = icons[icon];

    return (
        <div className={`stat-card glass ${color}`}>
            <div className="stat-icon">
                <Icon size={24} />
            </div>
            <div className="stat-content">
                <p className="stat-label">{label}</p>
                <h3 className="stat-value">{value}</h3>
                {trend && <span className="stat-trend">{trend}</span>}
            </div>
        </div>
    );
}
