import { useState, useEffect } from 'react';
import { MapPin, Trash2, ExternalLink } from 'lucide-react';
import type { SavedLocation } from '../types';
import './SavedLocations.css';

interface SavedLocationsProps {
    onLoadLocation?: (lat: number, lon: number) => void;
}

export default function SavedLocations({ onLoadLocation }: SavedLocationsProps) {
    const [locations, setLocations] = useState<SavedLocation[]>([]);

    useEffect(() => {
        const saved = localStorage.getItem('saved-locations');
        if (saved) {
            setLocations(JSON.parse(saved));
        }
    }, []);

    const deleteLocation = (id: string) => {
        const updated = locations.filter(loc => loc.id !== id);
        setLocations(updated);
        localStorage.setItem('saved-locations', JSON.stringify(updated));
    };

    const loadLocation = (lat: number, lon: number) => {
        if (onLoadLocation) {
            onLoadLocation(lat, lon);
        }
    };

    return (
        <div className="saved-locations">
            <h3>
                <MapPin size={20} />
                Saved Locations
            </h3>

            {locations.length === 0 ? (
                <div className="empty-locations">
                    <p>No saved locations yet. Save locations from the prediction form.</p>
                </div>
            ) : (
                <div className="locations-list">
                    {locations.map((loc) => (
                        <div key={loc.id} className="location-item glass">
                            <div className="location-info">
                                <h4>{loc.nickname}</h4>
                                <p>
                                    {loc.lat.toFixed(4)}, {loc.lon.toFixed(4)}
                                </p>
                                <span className="location-date">
                                    Saved: {new Date(loc.addedAt).toLocaleDateString()}
                                </span>
                            </div>

                            <div className="location-actions">
                                <button
                                    onClick={() => loadLocation(loc.lat, loc.lon)}
                                    className="load-btn"
                                    title="Load this location"
                                >
                                    <ExternalLink size={16} />
                                </button>
                                <button
                                    onClick={() => deleteLocation(loc.id)}
                                    className="delete-btn"
                                    title="Delete this location"
                                >
                                    <Trash2 size={16} />
                                </button>
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
}
