import { useState, useEffect } from 'react';
import { Bell, X } from 'lucide-react';
import type { Alert } from '../types';
import './AlertCenter.css';

export default function AlertCenter() {
    const [alerts, setAlerts] = useState<Alert[]>([]);
    const [isOpen, setIsOpen] = useState(false);
    const [filter, setFilter] = useState<'all' | 'High' | 'Medium' | 'Low'>('all');

    useEffect(() => {
        // Load alerts from localStorage
        const savedAlerts = localStorage.getItem('flood-alerts');
        if (savedAlerts) {
            setAlerts(JSON.parse(savedAlerts));
        }
    }, []);

    const unreadCount = alerts.filter(a => !a.isRead).length;

    const filteredAlerts = filter === 'all'
        ? alerts
        : alerts.filter(a => a.riskLevel === filter);

    const markAsRead = (id: string) => {
        const updated = alerts.map(a =>
            a.id === id ? { ...a, isRead: true } : a
        );
        setAlerts(updated);
        localStorage.setItem('flood-alerts', JSON.stringify(updated));
    };

    const markAllAsRead = () => {
        const updated = alerts.map(a => ({ ...a, isRead: true }));
        setAlerts(updated);
        localStorage.setItem('flood-alerts', JSON.stringify(updated));
    };

    const deleteAlert = (id: string) => {
        const updated = alerts.filter(a => a.id !== id);
        setAlerts(updated);
        localStorage.setItem('flood-alerts', JSON.stringify(updated));
    };

    return (
        <div className="alert-center">
            <button
                className="alert-button"
                onClick={() => setIsOpen(!isOpen)}
                aria-label="Notifications"
            >
                <Bell size={20} />
                {unreadCount > 0 && (
                    <span className="alert-badge">{unreadCount}</span>
                )}
            </button>

            {isOpen && (
                <div className="alert-dropdown glass">
                    <div className="alert-header">
                        <h3>Notifications</h3>
                        <div className="alert-actions">
                            {unreadCount > 0 && (
                                <button onClick={markAllAsRead} className="mark-read-btn">
                                    Mark all read
                                </button>
                            )}
                            <button onClick={() => setIsOpen(false)} className="close-btn">
                                <X size={18} />
                            </button>
                        </div>
                    </div>

                    <div className="alert-filters">
                        <button
                            className={filter === 'all' ? 'active' : ''}
                            onClick={() => setFilter('all')}
                        >
                            All
                        </button>
                        <button
                            className={filter === 'High' ? 'active' : ''}
                            onClick={() => setFilter('High')}
                        >
                            High
                        </button>
                        <button
                            className={filter === 'Medium' ? 'active' : ''}
                            onClick={() => setFilter('Medium')}
                        >
                            Medium
                        </button>
                        <button
                            className={filter === 'Low' ? 'active' : ''}
                            onClick={() => setFilter('Low')}
                        >
                            Low
                        </button>
                    </div>

                    <div className="alert-list">
                        {filteredAlerts.length === 0 ? (
                            <div className="empty-alerts">
                                <p>No notifications</p>
                            </div>
                        ) : (
                            filteredAlerts.map(alert => (
                                <div
                                    key={alert.id}
                                    className={`alert-item ${alert.isRead ? 'read' : 'unread'} ${alert.riskLevel.toLowerCase()}`}
                                    onClick={() => !alert.isRead && markAsRead(alert.id)}
                                >
                                    <div className="alert-content">
                                        <div className="alert-title">
                                            <span className={`risk-indicator ${alert.riskLevel.toLowerCase()}`}>
                                                {alert.riskLevel}
                                            </span>
                                            <span className="alert-location">{alert.location}</span>
                                        </div>
                                        <p className="alert-message">{alert.message}</p>
                                        <span className="alert-time">
                                            {new Date(alert.timestamp).toLocaleString()}
                                        </span>
                                    </div>
                                    <button
                                        className="delete-alert-btn"
                                        onClick={(e) => {
                                            e.stopPropagation();
                                            deleteAlert(alert.id);
                                        }}
                                    >
                                        <X size={16} />
                                    </button>
                                </div>
                            ))
                        )}
                    </div>
                </div>
            )}
        </div>
    );
}
