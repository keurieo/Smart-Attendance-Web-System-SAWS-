import React, { useState, useEffect } from 'react';
import { QRCodeSVG } from 'qrcode.react';

/**
 * Component for displaying QR code and 6-digit code for attendance sessions
 * Shows session details, countdown timer, and copy functionality
 */
const QRViewer = ({ session }) => {
  const [timeRemaining, setTimeRemaining] = useState(null);
  const [copied, setCopied] = useState(false);

  // Calculate time remaining until session ends
  useEffect(() => {
    if (!session?.end_at) return;

    const calculateTimeRemaining = () => {
      const now = new Date();
      const endTime = new Date(session.end_at);
      const diff = endTime - now;

      if (diff <= 0) {
        setTimeRemaining({ expired: true });
        return;
      }

      const hours = Math.floor(diff / (1000 * 60 * 60));
      const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
      const seconds = Math.floor((diff % (1000 * 60)) / 1000);

      setTimeRemaining({ hours, minutes, seconds, expired: false });
    };

    // Calculate immediately
    calculateTimeRemaining();

    // Update every second
    const interval = setInterval(calculateTimeRemaining, 1000);

    return () => clearInterval(interval);
  }, [session?.end_at]);

  const handleCopyCode = () => {
    if (session?.code6) {
      navigator.clipboard.writeText(session.code6).then(() => {
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
      });
    }
  };

  if (!session) {
    return (
      <div className="text-center text-gray-500 py-8">
        No session data available
      </div>
    );
  }

  const formatDateTime = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      {/* Session Details */}
      <div className="mb-6">
        <h3 className="text-xl font-bold text-gray-900 mb-2">
          {session.course_code} - {session.course_title}
        </h3>
        <div className="space-y-1 text-sm text-gray-600">
          <p>
            <span className="font-medium">Start:</span> {formatDateTime(session.start_at)}
          </p>
          <p>
            <span className="font-medium">End:</span> {formatDateTime(session.end_at)}
          </p>
          <p>
            <span className="font-medium">Radius:</span> {session.radius_meters} meters
          </p>
          {session.room && (
            <p>
              <span className="font-medium">Room:</span> {session.room}
            </p>
          )}
        </div>
      </div>

      {/* Countdown Timer */}
      {timeRemaining && (
        <div className="mb-6">
          {timeRemaining.expired ? (
            <div className="bg-red-50 border border-red-200 rounded-md p-3 text-center">
              <p className="text-red-600 font-medium">Session Expired</p>
            </div>
          ) : (
            <div className="bg-blue-50 border border-blue-200 rounded-md p-3 text-center">
              <p className="text-sm text-gray-600 mb-1">Time Remaining</p>
              <p className="text-2xl font-bold text-blue-600">
                {String(timeRemaining.hours).padStart(2, '0')}:
                {String(timeRemaining.minutes).padStart(2, '0')}:
                {String(timeRemaining.seconds).padStart(2, '0')}
              </p>
            </div>
          )}
        </div>
      )}

      {/* QR Code */}
      {session.qr_token && (
        <div className="mb-6 flex justify-center">
          <div className="bg-white p-4 rounded-lg border-2 border-gray-200">
            <QRCodeSVG
              value={session.qr_token}
              size={256}
              level="H"
              includeMargin={true}
            />
          </div>
        </div>
      )}

      {/* 6-Digit Code */}
      {session.code6 && (
        <div className="mb-6">
          <div className="bg-gray-50 border border-gray-200 rounded-md p-4">
            <p className="text-sm text-gray-600 text-center mb-2">
              Alternative 6-Digit Code
            </p>
            <div className="flex items-center justify-center space-x-2">
              <p className="text-3xl font-mono font-bold text-gray-900 tracking-wider">
                {session.code6}
              </p>
              <button
                onClick={handleCopyCode}
                className="px-3 py-1 bg-blue-600 text-white text-sm rounded-md hover:bg-blue-700 transition-colors"
                title="Copy code"
              >
                {copied ? '✓ Copied' : 'Copy'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* QR URL (for sharing) */}
      {session.qr_url && (
        <div className="text-center">
          <p className="text-xs text-gray-500 mb-2">Share this URL:</p>
          <div className="flex items-center justify-center space-x-2">
            <input
              type="text"
              value={session.qr_url}
              readOnly
              className="flex-1 px-3 py-2 text-sm border border-gray-300 rounded-md bg-gray-50"
            />
            <button
              onClick={() => {
                navigator.clipboard.writeText(session.qr_url);
              }}
              className="px-3 py-2 bg-gray-600 text-white text-sm rounded-md hover:bg-gray-700"
            >
              Copy
            </button>
          </div>
        </div>
      )}

      {/* Session Status */}
      <div className="mt-6 pt-6 border-t border-gray-200">
        <div className="flex items-center justify-between text-sm">
          <span className="text-gray-600">Status:</span>
          <span
            className={`px-3 py-1 rounded-full font-medium ${
              session.status === 'active'
                ? 'bg-green-100 text-green-800'
                : session.status === 'expired'
                ? 'bg-red-100 text-red-800'
                : 'bg-gray-100 text-gray-800'
            }`}
          >
            {session.status?.charAt(0).toUpperCase() + session.status?.slice(1)}
          </span>
        </div>
      </div>
    </div>
  );
};

export default QRViewer;
