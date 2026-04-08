import { useEffect } from 'react';
import { MapContainer, TileLayer, Marker, useMapEvents } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';

// Fix for default marker icon
delete (L.Icon.Default.prototype as any)._getIconUrl;
L.Icon.Default.mergeOptions({
    iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
    iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
    shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
});

interface MapSelectorProps {
    lat: number;
    lon: number;
    onLocationSelect: (lat: number, lon: number) => void;
}

function LocationMarker({ lat, lon, onLocationSelect }: MapSelectorProps) {
    const map = useMapEvents({
        click(e) {
            onLocationSelect(e.latlng.lat, e.latlng.lng);
        },
    });

    useEffect(() => {
        map.flyTo([lat, lon], map.getZoom());
    }, [lat, lon, map]);

    return <Marker position={[lat, lon]} />;
}

export default function MapSelector({ lat, lon, onLocationSelect }: MapSelectorProps) {
    return (
        <div className="map-container glass">
            <MapContainer
                center={[lat, lon]}
                zoom={7}
                style={{ height: '400px', width: '100%', borderRadius: '1rem' }}
            >
                <TileLayer
                    attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                    url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                />
                <LocationMarker lat={lat} lon={lon} onLocationSelect={onLocationSelect} />
            </MapContainer>
            <div className="map-hint">
                Click anywhere on the map to update location
            </div>
        </div>
    );
}
