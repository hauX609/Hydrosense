import ComparisonTool from './ComparisonTool';
import './Analytics.css';

export default function Analytics() {
    return (
        <div className="analytics-page">
            <div className="analytics-header">
                <h1>📈 Advanced Analytics</h1>
                <p>Deep dive into flood risk patterns and comparisons</p>
            </div>

            <ComparisonTool />

            <div className="analytics-info glass">
                <h3>💡 Analytics Features</h3>
                <ul>
                    <li>Compare flood risk across multiple locations simultaneously</li>
                    <li>Analyze patterns and trends in prediction data</li>
                    <li>Make informed decisions based on comparative analysis</li>
                    <li>Export comparison results for reporting</li>
                </ul>
            </div>
        </div>
    );
}
