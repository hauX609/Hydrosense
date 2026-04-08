import './LoadingSpinner.css';

export default function LoadingSpinner() {
    return (
        <div className="loading-overlay">
            <div className="spinner-container">
                <div className="spinner"></div>
                <p className="loading-text">Analyzing flood risk...</p>
            </div>
        </div>
    );
}
