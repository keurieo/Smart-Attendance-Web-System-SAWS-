import React, { useState, useEffect } from 'react';
import Modal from '../shared/Modal';
import { useGeolocation } from '../../hooks/useGeolocation';
import { attendanceAPI } from '../../services/api';

/**
 * Modal component for creating attendance sessions
 * Captures teacher location and validates form inputs
 */
const CreateSessionModal = ({ isOpen, onClose, onSuccess, courses, schedules }) => {
  const { location, error: locationError, loading: locationLoading, getCurrentLocation } = useGeolocation();
  
  const [formData, setFormData] = useState({
    course_id: '',
    schedule_id: '',
    start_at: '',
    end_at: '',
    radius_meters: 50,
  });
  
  const [errors, setErrors] = useState({});
  const [submitting, setSubmitting] = useState(false);
  const [locationCaptured, setLocationCaptured] = useState(false);

  // Trigger geolocation capture when modal opens
  useEffect(() => {
    if (isOpen && !locationCaptured) {
      getCurrentLocation()
        .then(() => setLocationCaptured(true))
        .catch((err) => {
          console.error('Failed to get location:', err);
        });
    }
  }, [isOpen, locationCaptured, getCurrentLocation]);

  // Reset form when modal closes
  useEffect(() => {
    if (!isOpen) {
      setFormData({
        course_id: '',
        schedule_id: '',
        start_at: '',
        end_at: '',
        radius_meters: 50,
      });
      setErrors({});
      setLocationCaptured(false);
    }
  }, [isOpen]);

  // Filter schedules based on selected course
  const filteredSchedules = schedules?.filter(
    (schedule) => schedule.course_id === parseInt(formData.course_id)
  ) || [];

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
    // Clear error for this field
    if (errors[name]) {
      setErrors((prev) => ({ ...prev, [name]: null }));
    }
  };

  const validateForm = () => {
    const newErrors = {};

    if (!formData.course_id) {
      newErrors.course_id = 'Please select a course';
    }

    if (!formData.start_at) {
      newErrors.start_at = 'Start time is required';
    }

    if (!formData.end_at) {
      newErrors.end_at = 'End time is required';
    }

    // Validate start_at is before end_at
    if (formData.start_at && formData.end_at) {
      const startDate = new Date(formData.start_at);
      const endDate = new Date(formData.end_at);
      if (startDate >= endDate) {
        newErrors.end_at = 'End time must be after start time';
      }
    }

    // Validate radius is in range (10-500 meters)
    const radius = parseInt(formData.radius_meters);
    if (isNaN(radius) || radius < 10 || radius > 500) {
      newErrors.radius_meters = 'Radius must be between 10 and 500 meters';
    }

    if (!location) {
      newErrors.location = 'Location is required. Please enable location access.';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!validateForm()) {
      return;
    }

    setSubmitting(true);

    try {
      // Prepare request data with teacher location
      const requestData = {
        course_id: parseInt(formData.course_id),
        schedule_id: formData.schedule_id ? parseInt(formData.schedule_id) : null,
        start_at: formData.start_at,
        end_at: formData.end_at,
        radius_meters: parseInt(formData.radius_meters),
        latitude: location.latitude,
        longitude: location.longitude,
      };

      const response = await attendanceAPI.createSession(requestData);
      
      // Call success callback with session data
      if (onSuccess) {
        onSuccess(response.data);
      }
      
      // Close modal
      onClose();
    } catch (error) {
      console.error('Failed to create session:', error);
      setErrors({
        submit: error.message || 'Failed to create session. Please try again.',
      });
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Create Attendance Session">
      <form onSubmit={handleSubmit} className="space-y-4">
        {/* Location Status */}
        <div className="bg-gray-50 p-3 rounded-md">
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium text-gray-700">Location Status:</span>
            {locationLoading && (
              <span className="text-sm text-blue-600">Capturing location...</span>
            )}
            {location && (
              <span className="text-sm text-green-600">
                ✓ Captured (Accuracy: {location.accuracy?.toFixed(0)}m)
              </span>
            )}
            {locationError && (
              <span className="text-sm text-red-600">✗ {locationError}</span>
            )}
          </div>
          {errors.location && (
            <p className="text-sm text-red-600 mt-1">{errors.location}</p>
          )}
        </div>

        {/* Course Selection */}
        <div>
          <label htmlFor="course_id" className="block text-sm font-medium text-gray-700 mb-1">
            Course *
          </label>
          <select
            id="course_id"
            name="course_id"
            value={formData.course_id}
            onChange={handleChange}
            className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 ${
              errors.course_id ? 'border-red-500' : 'border-gray-300'
            }`}
            disabled={submitting}
          >
            <option value="">Select a course</option>
            {courses?.map((course) => (
              <option key={course.id} value={course.id}>
                {course.code} - {course.title}
              </option>
            ))}
          </select>
          {errors.course_id && (
            <p className="text-sm text-red-600 mt-1">{errors.course_id}</p>
          )}
        </div>

        {/* Schedule Selection (Optional) */}
        {filteredSchedules.length > 0 && (
          <div>
            <label htmlFor="schedule_id" className="block text-sm font-medium text-gray-700 mb-1">
              Schedule (Optional)
            </label>
            <select
              id="schedule_id"
              name="schedule_id"
              value={formData.schedule_id}
              onChange={handleChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              disabled={submitting}
            >
              <option value="">No schedule</option>
              {filteredSchedules.map((schedule) => (
                <option key={schedule.id} value={schedule.id}>
                  {['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'][schedule.weekday]} - {schedule.start_time} ({schedule.duration_minutes}min)
                </option>
              ))}
            </select>
          </div>
        )}

        {/* Start Time */}
        <div>
          <label htmlFor="start_at" className="block text-sm font-medium text-gray-700 mb-1">
            Start Time *
          </label>
          <input
            type="datetime-local"
            id="start_at"
            name="start_at"
            value={formData.start_at}
            onChange={handleChange}
            className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 ${
              errors.start_at ? 'border-red-500' : 'border-gray-300'
            }`}
            disabled={submitting}
          />
          {errors.start_at && (
            <p className="text-sm text-red-600 mt-1">{errors.start_at}</p>
          )}
        </div>

        {/* End Time */}
        <div>
          <label htmlFor="end_at" className="block text-sm font-medium text-gray-700 mb-1">
            End Time *
          </label>
          <input
            type="datetime-local"
            id="end_at"
            name="end_at"
            value={formData.end_at}
            onChange={handleChange}
            className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 ${
              errors.end_at ? 'border-red-500' : 'border-gray-300'
            }`}
            disabled={submitting}
          />
          {errors.end_at && (
            <p className="text-sm text-red-600 mt-1">{errors.end_at}</p>
          )}
        </div>

        {/* Radius */}
        <div>
          <label htmlFor="radius_meters" className="block text-sm font-medium text-gray-700 mb-1">
            Radius (meters) *
          </label>
          <input
            type="number"
            id="radius_meters"
            name="radius_meters"
            value={formData.radius_meters}
            onChange={handleChange}
            min="10"
            max="500"
            className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 ${
              errors.radius_meters ? 'border-red-500' : 'border-gray-300'
            }`}
            disabled={submitting}
          />
          <p className="text-xs text-gray-500 mt-1">Range: 10-500 meters</p>
          {errors.radius_meters && (
            <p className="text-sm text-red-600 mt-1">{errors.radius_meters}</p>
          )}
        </div>

        {/* Submit Error */}
        {errors.submit && (
          <div className="bg-red-50 border border-red-200 rounded-md p-3">
            <p className="text-sm text-red-600">{errors.submit}</p>
          </div>
        )}

        {/* Action Buttons */}
        <div className="flex justify-end space-x-3 pt-4">
          <button
            type="button"
            onClick={onClose}
            className="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50"
            disabled={submitting}
          >
            Cancel
          </button>
          <button
            type="submit"
            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
            disabled={submitting || !location}
          >
            {submitting ? 'Creating...' : 'Create Session'}
          </button>
        </div>
      </form>
    </Modal>
  );
};

export default CreateSessionModal;
