import { Link, useLocation } from 'react-router-dom';
import { Home, Activity, TrendingUp, Shield, Menu, X } from 'lucide-react';
import { useState } from 'react';
import ThemeToggle from './ThemeToggle';
import AlertCenter from './AlertCenter';
import './Navigation.css';

export default function Navigation() {
    const location = useLocation();
    const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

    const navItems = [
        { path: '/', label: 'Home', icon: Home },
        { path: '/dashboard', label: 'Dashboard', icon: Activity },
        { path: '/analytics', label: 'Analytics', icon: TrendingUp },
        { path: '/safety', label: 'Safety', icon: Shield },
    ];

    const isActive = (path: string) => location.pathname === path;

    return (
        <nav className="navigation glass">
            <div className="nav-container">
                <Link to="/" className="nav-logo">
                    <span className="logo-icon">🌊</span>
                    <span className="logo-text">Flood Predict</span>
                </Link>

                {/* Desktop Navigation */}
                <div className="nav-links desktop">
                    {navItems.map((item) => {
                        const Icon = item.icon;
                        return (
                            <Link
                                key={item.path}
                                to={item.path}
                                className={`nav-link ${isActive(item.path) ? 'active' : ''}`}
                            >
                                <Icon size={18} />
                                {item.label}
                            </Link>
                        );
                    })}
                </div>

                {/* Right Section */}
                <div className="nav-actions">
                    <AlertCenter />
                    <ThemeToggle />

                    {/* Mobile Menu Button */}
                    <button
                        className="mobile-menu-btn"
                        onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
                    >
                        {isMobileMenuOpen ? <X size={24} /> : <Menu size={24} />}
                    </button>
                </div>
            </div>

            {/* Mobile Navigation */}
            {isMobileMenuOpen && (
                <div className="nav-links mobile">
                    {navItems.map((item) => {
                        const Icon = item.icon;
                        return (
                            <Link
                                key={item.path}
                                to={item.path}
                                className={`nav-link ${isActive(item.path) ? 'active' : ''}`}
                                onClick={() => setIsMobileMenuOpen(false)}
                            >
                                <Icon size={18} />
                                {item.label}
                            </Link>
                        );
                    })}
                </div>
            )}
        </nav>
    );
}
