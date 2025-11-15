import React, { useState } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { adminAPI } from '../../services/api';
import Modal from '../shared/Modal';

const AttendanceOverride = ({ isOpen, onClose, attendanceRecord, onSuccess }) => {
  const queryClient = useQueryClient();
  const [formData, setFormData] = useState({
    status: attendanceRecord?.status || 'present',
    reason: '',
  });

  // Override attendance mutation
  const overrideMutation = useMutation({
    mutationFn: ({ recordId, data }) => adminAPI.overrideAttendance(recordId, data),
    onSuccess: () => {
      queryClient.invalidateQueries(['attendance']);
      if (onSuccess) onSuccess();
      onClose();
      setFormData({ status: 'present', reason: '' });
    },
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    
    // Validate reason is provided
    if (!formData.reason.trim()) {
      return;
    }

    overrideMutation.mutate({
      recordId: attendanceRecord.id,
      data: formData,
    });
  };

  // Reset form when modal opens with new record
  React.useEffect(() => {
    if (isOpen && attendanceRecord) {
      setFormData({
        status: attendanceRecord.status,
        reason: '',
      });
    }
  }, [isOpen, attendanceRecord]);

  if (!attendanceRecord) return null;

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Override Attendance Record">
      <div className="space-y-4">
        {/* Current Record Details */}
        <div className="bg-gray-50 p-4 rounded-md space-y-2">
          <h4 className="text-sm font-medium text-gray-700">Current Record Details</h4>
          <div className="text-sm text-gray-600 space-y-1">
            <p>
              <span className="font-medium">Student:</span> {attendanceRecord.student_name}
            </p>
            <p>
              <span className="font-medium">Course:</span> {attendanceRecord.course_code} - {attendanceRecord.course_title}
            </p>
            <p>
              <span className="font-medium">Session Date:</span>{' '}
              {new Date(attendanceRecord.marked_at).toLocaleString()}
            </p>
            <p>
              <span className="font-medium">Current Status:</span>{' '}
              <span
                className={`px-2 py-1 rounded text-xs font-semibold ${
                  attendanceRecord.status === 'present'
                    ? 'bg-green-100 text-green-800'
                    : attendanceRecord.status === 'absent'
                    ? 'bg-red-100 text-red-800'
                    : attendanceRecord.status === 'rejected'
                    ? 'bg-yellow-100 text-yellow-800'
                    : 'bg-gray-100 text-gray-800'
                }`}
              >
                {attendanceRecord.status}
              </span>
            </p>
            {attendanceRecord.distance_meters && (
              <p>
                <span className="font-medium">Distance:</span> {attendanceRecord.distance_meters.toFixed(2)}m
              </p>
            )}
            {attendanceRecord.reason && (
              <p>
                <span className="font-medium">Previous Reason:</span> {attendanceRecord.reason}
              </p>
            )}
          </div>
        </div>

        {/* Override Form */}
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              New Status *
            </label>
            <select
              required
              value={formData.status}
              onChange={(e) => setFormData({ ...formData, status: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="present">Present</option>
              <option value="absent">Absent</option>
              <option value="rejected">Rejected</option>
              <option value="pending">Pending</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Reason for Override *
            </label>
            <textarea
              required
              value={formData.reason}
              onChange={(e) => setFormData({ ...formData, reason: e.target.value })}
              placeholder="Provide a detailed reason for this override..."
              rows={4}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            {formData.reason.trim() === '' && (
              <p className="mt-1 text-sm text-red-600">Reason is required</p>
            )}
          </div>

          {overrideMutation.isError && (
            <div className="text-red-600 text-sm">
              {overrideMutation.error?.message || 'Failed to override attendance record'}
            </div>
          )}

          <div className="flex justify-end space-x-2">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={overrideMutation.isPending || !formData.reason.trim()}
              className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
            >
              {overrideMutation.isPending ? 'Overriding...' : 'Override Attendance'}
            </button>
          </div>
        </form>
      </div>
    </Modal>
  );
};

export default AttendanceOverride;
