import React, { useState, useEffect } from 'react';
import { MapContainer, TileLayer, Marker, useMapEvents } from 'react-leaflet';
import L from 'leaflet';

// Fix for default marker icons in Leaflet when using Webpack/Vite
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
});

function LocationMarker({ position, setPosition }) {
  useMapEvents({
    click(e) {
      setPosition(e.latlng);
    },
  });

  return position === null ? null : (
    <Marker position={position} />
  );
}

export function MapPicker({ value, onChange }) {
  // Default to a central city location, or the provided value
  const defaultCenter = { lat: 40.7128, lng: -74.0060 }; // Example: New York. Adjust as needed.
  const [position, setPosition] = useState(
    value?.lat && value?.lng ? { lat: value.lat, lng: value.lng } : null
  );

  useEffect(() => {
    if (position) {
      onChange(position);
    }
  }, [position, onChange]);

  return (
    <div className="h-64 w-full rounded-md border border-border overflow-hidden relative z-0">
      <MapContainer 
        center={position || defaultCenter} 
        zoom={13} 
        scrollWheelZoom={true} 
        style={{ height: '100%', width: '100%', zIndex: 0 }}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        <LocationMarker position={position} setPosition={setPosition} />
      </MapContainer>
      {!position && (
        <div className="absolute top-2 left-1/2 transform -translate-x-1/2 bg-white px-3 py-1 rounded-full shadow-sm border border-border text-xs text-text-secondary z-[1000] pointer-events-none">
          Click on the map to drop a pin
        </div>
      )}
    </div>
  );
}
