"""
Geolocation utilities for distance calculation and location validation.
"""
import math
from typing import Tuple, Optional, Dict


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the great circle distance between two points on Earth using the Haversine formula.
    
    Args:
        lat1: Latitude of first point in decimal degrees
        lon1: Longitude of first point in decimal degrees
        lat2: Latitude of second point in decimal degrees
        lon2: Longitude of second point in decimal degrees
    
    Returns:
        Distance in meters
    
    Handles edge cases:
    - Poles: Works correctly at extreme latitudes
    - Antimeridian crossing: Properly handles longitude wrapping at ±180°
    """
    # Earth's radius in meters
    EARTH_RADIUS = 6371000
    
    # Convert decimal degrees to radians
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)
    
    # Haversine formula
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2) ** 2
    c = 2 * math.asin(math.sqrt(a))
    
    distance = EARTH_RADIUS * c
    
    return distance


def validate_location(
    student_lat: float,
    student_lon: float,
    student_accuracy: float,
    class_lat: float,
    class_lon: float,
    allowed_radius: float
) -> Dict[str, any]:
    """
    Validate if a student's location is within the allowed radius of the class location.
    
    Args:
        student_lat: Student's latitude in decimal degrees
        student_lon: Student's longitude in decimal degrees
        student_accuracy: GPS accuracy in meters
        class_lat: Class location latitude in decimal degrees
        class_lon: Class location longitude in decimal degrees
        allowed_radius: Maximum allowed distance in meters
    
    Returns:
        Dictionary with validation result:
        {
            'valid': bool,
            'distance': float (in meters),
            'reason': str (explanation if invalid)
        }
    """
    # Check for invalid coordinates (0,0 is likely an error)
    if student_lat == 0.0 and student_lon == 0.0:
        return {
            'valid': False,
            'distance': None,
            'reason': 'Invalid coordinates: location is (0,0)'
        }
    
    # Validate coordinate ranges
    if not (-90 <= student_lat <= 90):
        return {
            'valid': False,
            'distance': None,
            'reason': f'Invalid latitude: {student_lat} (must be between -90 and 90)'
        }
    
    if not (-180 <= student_lon <= 180):
        return {
            'valid': False,
            'distance': None,
            'reason': f'Invalid longitude: {student_lon} (must be between -180 and 180)'
        }
    
    # Check location accuracy threshold (reject if accuracy > 100 meters)
    if student_accuracy > 100:
        return {
            'valid': False,
            'distance': None,
            'reason': f'Location accuracy too low: {student_accuracy}m (must be ≤ 100m)'
        }
    
    # Calculate distance using Haversine formula
    distance = haversine_distance(student_lat, student_lon, class_lat, class_lon)
    
    # Compare against allowed radius
    if distance <= allowed_radius:
        return {
            'valid': True,
            'distance': distance,
            'reason': None
        }
    else:
        return {
            'valid': False,
            'distance': distance,
            'reason': f'Distance {distance:.1f}m exceeds allowed radius of {allowed_radius}m'
        }
