import React from 'react';
import { MapContainer, TileLayer, Marker, Circle, Popup } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

// Fix for default marker icons in Leaflet with webpack
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: require('leaflet/dist/images/marker-icon-2x.png'),
  iconUrl: require('leaflet/dist/images/marker-icon.png'),
  shadowUrl: require('leaflet/dist/images/marker-shadow.png'),
});

// Custom icons for teacher and student
const teacherIcon = new L.Icon({
  iconUrl: 'data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNSIgaGVpZ2h0PSI0MSIgdmlld0JveD0iMCAwIDI1IDQxIj48cGF0aCBmaWxsPSIjMzQ3MkQ3IiBkPSJNMTIuNSAwQzUuNiAwIDAgNS42IDAgMTIuNWMwIDEuNCAwLjIgMi43IDAuNyAzLjlsOS4xIDE5LjFjMC41IDEuMSAxLjYgMS44IDIuOCAxLjhzMi4zLTAuNyAyLjgtMS44bDkuMS0xOS4xYzAuNC0xLjIgMC43LTIuNSAwLjctMy45QzI1IDUuNiAxOS40IDAgMTIuNSAweiIvPjxjaXJjbGUgZmlsbD0iI0ZGRiIgY3g9IjEyLjUiIGN5PSIxMi41IiByPSI3Ii8+PC9zdmc+',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
});

const studentIcon = new L.Icon({
  iconUrl: 'data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNSIgaGVpZ2h0PSI0MSIgdmlld0JveD0iMCAwIDI1IDQxIj48cGF0aCBmaWxsPSIjMTBCOTgxIiBkPSJNMTIuNSAwQzUuNiAwIDAgNS42IDAgMTIuNWMwIDEuNCAwLjIgMi43IDAuNyAzLjlsOS4xIDE5LjFjMC41IDEuMSAxLjYgMS44IDIuOCAxLjhzMi4zLTAuNyAyLjgtMS44bDkuMS0xOS4xYzAuNC0xLjIgMC43LTIuNSAwLjctMy45QzI1IDUuNiAxOS40IDAgMTIuNSAweiIvPjxjaXJjbGUgZmlsbD0iI0ZGRiIgY3g9IjEyLjUiIGN5PSIxMi41IiByPSI3Ii8+PC9zdmc+',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
});

const MapPreview = ({
  teacherLocation,
  studentLocation = null,
  radius = 50,
  height = '400px',
  zoom = 16,
}) => {
  // Validate teacher location
  if (!teacherLocation || !teacherLocation.latitude || !teacherLocation.longitude) {
    return (
      <div
        className="flex items-center justify-center bg-gray-100 rounded-lg"
        style={{ height }}
      >
        <p className="text-gray-500">Location data not available</p>
      </div>
    );
  }

  const teacherPos = [teacherLocation.latitude, teacherLocation.longitude];
  const studentPos = studentLocation
    ? [studentLocation.latitude, studentLocation.longitude]
    : null;

  // Calculate center point (between teacher and student if both exist)
  const center = studentPos
    ? [
        (teacherPos[0] + studentPos[0]) / 2,
        (teacherPos[1] + studentPos[1]) / 2,
      ]
    : teacherPos;

  // Calculate appropriate zoom level if student location exists
  const calculateZoom = () => {
    if (!studentPos) return zoom;

    const distance = Math.sqrt(
      Math.pow(teacherPos[0] - studentPos[0], 2) +
        Math.pow(teacherPos[1] - studentPos[1], 2)
    );

    // Adjust zoom based on distance
    if (distance > 0.01) return 14;
    if (distance > 0.005) return 15;
    return zoom;
  };

  return (
    <div className="rounded-lg overflow-hidden shadow-md" style={{ height }}>
      <MapContainer
        center={center}
        zoom={calculateZoom()}
        style={{ height: '100%', width: '100%' }}
        scrollWheelZoom={false}
      >
        {/* Using CartoDB Positron tiles - cleaner, faster, and more reliable than OSM */}
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>'
          url="https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png"
          subdomains="abcd"
          maxZoom={20}
        />

        {/* Teacher marker and radius circle */}
        <Marker position={teacherPos} icon={teacherIcon}>
          <Popup>
            <div className="text-sm">
              <strong>Teacher Location</strong>
              <br />
              Lat: {teacherLocation.latitude.toFixed(6)}
              <br />
              Lon: {teacherLocation.longitude.toFixed(6)}
            </div>
          </Popup>
        </Marker>

        {/* Radius circle */}
        <Circle
          center={teacherPos}
          radius={radius}
          pathOptions={{
            color: '#3B82F6',
            fillColor: '#3B82F6',
            fillOpacity: 0.2,
            weight: 2,
          }}
        >
          <Popup>
            <div className="text-sm">
              <strong>Allowed Radius</strong>
              <br />
              {radius} meters
            </div>
          </Popup>
        </Circle>

        {/* Student marker (if provided) */}
        {studentPos && (
          <Marker position={studentPos} icon={studentIcon}>
            <Popup>
              <div className="text-sm">
                <strong>Student Location</strong>
                <br />
                Lat: {studentLocation.latitude.toFixed(6)}
                <br />
                Lon: {studentLocation.longitude.toFixed(6)}
              </div>
            </Popup>
          </Marker>
        )}
      </MapContainer>

      {/* Legend */}
      <div className="bg-white px-4 py-2 border-t">
        <div className="flex items-center space-x-4 text-sm">
          <div className="flex items-center">
            <div className="w-3 h-3 bg-blue-600 rounded-full mr-2"></div>
            <span>Teacher</span>
          </div>
          {studentPos && (
            <div className="flex items-center">
              <div className="w-3 h-3 bg-green-600 rounded-full mr-2"></div>
              <span>Student</span>
            </div>
          )}
          <div className="flex items-center">
            <div className="w-3 h-3 border-2 border-blue-600 rounded-full mr-2"></div>
            <span>Radius: {radius}m</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default MapPreview;
