import { Droplets } from 'lucide-react';
import './Header.css';

export default function Header() {
    return (
        <header className="header">
            <div className="container">
                <div className="header-content">
                    <div className="logo">
                        <Droplets className="logo-icon" size={32} />
                        <div>
                            <h1 className="logo-title">Bangladesh Flood Predictor</h1>
                            <p className="logo-subtitle">AI-Powered Risk Assessment</p>
                        </div>
                    </div>
                </div>
            </div>
        </header>
    );
}
