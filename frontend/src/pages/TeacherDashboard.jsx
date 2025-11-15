import React, { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { attendanceAPI, teacherAPI } from '../services/api';
import CreateSessionModal from '../components/teacher/CreateSessionModal';
import QRViewer from '../components/teacher/QRViewer';

const TeacherDashboard = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const [sessions, setSessions] = useState([]);
  const [courses, setCourses] = useState([]);
  const [schedules, setSchedules] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [selectedSession, setSelectedSession] = useState(null);
  const [showQRModal, setShowQRModal] = useState(false);

  // Fetch teacher's courses, schedules, and sessions
  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    setLoading(true);
    setError(null);

    try {
      // Fetch courses, schedules, and sessions in parallel
      const [coursesRes, schedulesRes, sessionsRes] = await Promise.all([
        teacherAPI.getCourses(),
        teacherAPI.getSchedules(),
        attendanceAPI.getSessions(),
      ]);

      setCourses(coursesRes.data.results || coursesRes.data);
      setSchedules(schedulesRes.data.results || schedulesRes.data);
      setSessions(sessionsRes.data.results || sessionsRes.data);
    } catch (err) {
      console.error('Failed to fetch data:', err);
      setError(err.message || 'Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const handleCreateSession = () => {
    setShowCreateModal(true);
  };

  const handleSessionCreated = (newSession) => {
    // Add new session to the list
    setSessions((prev) => [newSession, ...prev]);
    // Show QR code for the new session
    setSelectedSession(newSession);
    setShowQRModal(true);
  };

  const handleViewQR = (session) => {
    setSelectedSession(session);
    setShowQRModal(true);
  };

  const formatDateTime = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const getSessionStatus = (session) => {
    const now = new Date();
    const startTime = new Date(session.start_at);
    const endTime = new Date(session.end_at);

    if (now < startTime) return 'upcoming';
    if (now > endTime) return 'expired';
    return 'active';
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'active':
        return 'bg-green-100 text-green-800';
      case 'upcoming':
        return 'bg-blue-100 text-blue-800';
      case 'expired':
        return 'bg-gray-100 text-gray-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  // Separate active and past sessions
  const activeSessions = sessions.filter(
    (session) => getSessionStatus(session) === 'active' || getSessionStatus(session) === 'upcoming'
  );
  const pastSessions = sessions.filter((session) => getSessionStatus(session) === 'expired');

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow">
        <div className="container mx-auto px-4 py-4 flex justify-between items-center">
          <h1 className="text-2xl font-bold text-gray-900">Teacher Dashboard</h1>
          <div className="flex items-center space-x-4">
            <span className="text-gray-700">Welcome, {user?.full_name}</span>
            <button
              onClick={handleLogout}
              className="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700"
            >
              Logout
            </button>
          </div>
        </div>
      </header>

      {/* Main content */}
      <main className="container mx-auto px-4 py-8">
        {/* Create Session Button */}
        <div className="mb-6">
          <button
            onClick={handleCreateSession}
            className="px-6 py-3 bg-blue-600 text-white rounded-md hover:bg-blue-700 font-medium"
          >
            + Create Attendance Session
          </button>
        </div>

        {/* Loading State */}
        {loading && (
          <div className="text-center py-12">
            <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
            <p className="mt-4 text-gray-600">Loading sessions...</p>
          </div>
        )}

        {/* Error State */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-md p-4 mb-6">
            <p className="text-red-600">{error}</p>
            <button
              onClick={fetchData}
              className="mt-2 text-sm text-red-700 underline hover:text-red-800"
            >
              Try again
            </button>
          </div>
        )}

        {/* Sessions List */}
        {!loading && !error && (
          <>
            {/* Active Sessions */}
            {activeSessions.length > 0 && (
              <div className="mb-8">
                <h2 className="text-xl font-bold text-gray-900 mb-4">Active Sessions</h2>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                  {activeSessions.map((session) => (
                    <SessionCard
                      key={session.id}
                      session={session}
                      status={getSessionStatus(session)}
                      statusColor={getStatusColor(getSessionStatus(session))}
                      formatDateTime={formatDateTime}
                      onViewQR={handleViewQR}
                    />
                  ))}
                </div>
              </div>
            )}

            {/* Past Sessions */}
            {pastSessions.length > 0 && (
              <div>
                <h2 className="text-xl font-bold text-gray-900 mb-4">Past Sessions</h2>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                  {pastSessions.map((session) => (
                    <SessionCard
                      key={session.id}
                      session={session}
                      status={getSessionStatus(session)}
                      statusColor={getStatusColor(getSessionStatus(session))}
                      formatDateTime={formatDateTime}
                      onViewQR={handleViewQR}
                    />
                  ))}
                </div>
              </div>
            )}

            {/* Empty State */}
            {sessions.length === 0 && (
              <div className="text-center py-12">
                <p className="text-gray-600 mb-4">No attendance sessions yet</p>
                <button
                  onClick={handleCreateSession}
                  className="px-6 py-3 bg-blue-600 text-white rounded-md hover:bg-blue-700"
                >
                  Create Your First Session
                </button>
              </div>
            )}
          </>
        )}
      </main>

      {/* Create Session Modal */}
      <CreateSessionModal
        isOpen={showCreateModal}
        onClose={() => setShowCreateModal(false)}
        onSuccess={handleSessionCreated}
        courses={courses}
        schedules={schedules}
      />

      {/* QR Viewer Modal */}
      {showQRModal && (
        <div className="fixed inset-0 z-50 overflow-y-auto">
          <div className="flex items-center justify-center min-h-screen px-4">
            <div className="fixed inset-0 bg-black opacity-50" onClick={() => setShowQRModal(false)}></div>
            <div className="relative bg-white rounded-lg max-w-2xl w-full p-6">
              <div className="flex justify-between items-center mb-4">
                <h3 className="text-xl font-bold">Session QR Code</h3>
                <button
                  onClick={() => setShowQRModal(false)}
                  className="text-gray-500 hover:text-gray-700"
                >
                  ✕
                </button>
              </div>
              <QRViewer session={selectedSession} />
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

// Session Card Component
const SessionCard = ({ session, status, statusColor, formatDateTime, onViewQR }) => {
  return (
    <div className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow">
      {/* Course Info */}
      <div className="mb-4">
        <h3 className="text-lg font-bold text-gray-900 mb-1">
          {session.course_code}
        </h3>
        <p className="text-sm text-gray-600">{session.course_title}</p>
      </div>

      {/* Session Details */}
      <div className="space-y-2 text-sm text-gray-600 mb-4">
        <p>
          <span className="font-medium">Start:</span> {formatDateTime(session.start_at)}
        </p>
        <p>
          <span className="font-medium">End:</span> {formatDateTime(session.end_at)}
        </p>
        <p>
          <span className="font-medium">Radius:</span> {session.radius_meters}m
        </p>
      </div>

      {/* Attendance Count */}
      {session.attendance_count !== undefined && (
        <div className="mb-4 p-3 bg-gray-50 rounded-md">
          <p className="text-sm text-gray-600">
            <span className="font-medium text-gray-900">{session.attendance_count}</span> students marked attendance
          </p>
        </div>
      )}

      {/* Status Badge */}
      <div className="mb-4">
        <span className={`inline-block px-3 py-1 rounded-full text-xs font-medium ${statusColor}`}>
          {status.charAt(0).toUpperCase() + status.slice(1)}
        </span>
      </div>

      {/* Actions */}
      <div className="flex space-x-2">
        <button
          onClick={() => onViewQR(session)}
          className="flex-1 px-4 py-2 bg-blue-600 text-white text-sm rounded-md hover:bg-blue-700"
        >
          View QR
        </button>
        <Link
          to={`/teacher/sessions/${session.id}`}
          className="flex-1 px-4 py-2 bg-gray-600 text-white text-sm rounded-md hover:bg-gray-700 text-center"
        >
          Details
        </Link>
      </div>
    </div>
  );
};

export default TeacherDashboard;
