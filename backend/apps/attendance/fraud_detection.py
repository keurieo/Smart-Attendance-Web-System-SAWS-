"""
Fraud detection utilities for attendance marking.

This module provides functions to detect and flag suspicious attendance
submissions that may indicate fraudulent behavior.
"""

from django.db.models import Count, Q
from django.contrib.gis.measure import D
from django.contrib.gis.geos import Point
from .models import AttendanceRecord


def detect_identical_coordinates(session, student_location, threshold=5):
    """
    Detect if more than a threshold number of students submitted identical
    coordinates for the same session.
    
    This helps identify cases where students may be sharing location data
    or using spoofed coordinates.
    
    Args:
        session: AttendanceSession instance
        student_location: Point object with student's coordinates
        threshold: Maximum number of students allowed at identical location (default: 5)
        
    Returns:
        tuple: (is_suspicious, count_at_location)
    """
    # Query attendance records for this session with identical coordinates
    # Use a very small distance threshold (1 meter) to detect identical coords
    identical_count = AttendanceRecord.objects.filter(
        session=session,
        student_location__distance_lte=(student_location, D(m=1))
    ).count()
    
    # Check if count exceeds threshold
    is_suspicious = identical_count >= threshold
    
    return is_suspicious, identical_count


def detect_time_delta_anomaly(device_timestamp, server_timestamp, threshold_seconds=300):
    """
    Detect if the time difference between device timestamp and server timestamp
    exceeds a threshold.
    
    Large time deltas may indicate:
    - Device clock manipulation
    - Replay attacks
    - Network issues (less likely with modern infrastructure)
    
    Args:
        device_timestamp: datetime object from device
        server_timestamp: datetime object from server
        threshold_seconds: Maximum allowed time difference (default: 300 seconds = 5 minutes)
        
    Returns:
        tuple: (is_suspicious, time_delta_seconds)
    """
    if device_timestamp is None:
        # No device timestamp provided, cannot check
        return False, None
    
    # Calculate absolute time difference in seconds
    time_delta = abs((device_timestamp - server_timestamp).total_seconds())
    
    # Check if delta exceeds threshold
    is_suspicious = time_delta > threshold_seconds
    
    return is_suspicious, time_delta


def check_fraud_indicators(session, student_location, device_timestamp=None, server_timestamp=None):
    """
    Run all fraud detection checks and return results.
    
    This is the main entry point for fraud detection that should be called
    during attendance marking.
    
    Args:
        session: AttendanceSession instance
        student_location: Point object with student's coordinates
        device_timestamp: Optional datetime from device
        server_timestamp: Optional datetime from server (defaults to current time)
        
    Returns:
        dict: {
            'should_flag': bool,
            'reasons': list of str,
            'details': dict with detection details
        }
    """
    should_flag = False
    reasons = []
    details = {}
    
    # Check for identical coordinates
    coords_suspicious, coords_count = detect_identical_coordinates(
        session, 
        student_location
    )
    
    if coords_suspicious:
        should_flag = True
        reasons.append('identical_coordinates')
        details['identical_coordinates_count'] = coords_count
    
    # Check for time delta anomaly if timestamps provided
    if device_timestamp and server_timestamp:
        time_suspicious, time_delta = detect_time_delta_anomaly(
            device_timestamp,
            server_timestamp
        )
        
        if time_suspicious:
            should_flag = True
            reasons.append('time_delta_anomaly')
            details['time_delta_seconds'] = time_delta
    
    return {
        'should_flag': should_flag,
        'reasons': reasons,
        'details': details
    }


def flag_attendance_for_review(attendance_record, fraud_reasons, fraud_details):
    """
    Flag an attendance record for admin review due to fraud indicators.
    
    Args:
        attendance_record: AttendanceRecord instance
        fraud_reasons: List of fraud detection reasons
        fraud_details: Dict with fraud detection details
    """
    # Set the flagged_for_review field
    attendance_record.flagged_for_review = True
    
    # Append fraud information to the reason field
    fraud_info = f"Flagged for review: {', '.join(fraud_reasons)}"
    if attendance_record.reason:
        attendance_record.reason += f" | {fraud_info}"
    else:
        attendance_record.reason = fraud_info
    
    # Add details to reason if available
    if fraud_details:
        detail_str = "; ".join([f"{k}={v}" for k, v in fraud_details.items()])
        attendance_record.reason += f" ({detail_str})"
    
    attendance_record.save(update_fields=['flagged_for_review', 'reason'])
