import { useState, useEffect } from 'react';
import QRScanner from './QRScanner';
import ManualCodeEntry from './ManualCodeEntry';
import { useGeolocation } from '../../hooks/useGeolocation';
import { attendanceAPI } from '../../services/api';

/**
 * ScanPage component with tabs for QR scan and manual entry
 * Triggers geolocation capture when page loads
 * Displays location capture status
 * Calls attendance marking API with token and student location
 * Displays result (success with distance, or rejection with reason)
 * Shows error messages for location denial or API errors
 */
const ScanPage = () => {
  const [activeTab, setActiveTab] = useState('qr'); // 'qr' or 'manual'
  const [submitting, setSubmitting] = useState(false);
  const [result, setResult] = useState(null); // { success, message, data }
  const { location, error: locationError, loading: locationLoading, getCurrentLocation } = useGeolocation();

  // Capture location on component mount
  useEffect(() => {
    // Only request location once when component mounts
    getCurrentLocation().catch(err => {
      console.error('Failed to get location:', err);
    });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []); // Empty dependency array - only run once on mount

  /**
   * Handle attendance submission with token and location
   */
  const handleAttendanceSubmit = async (token) => {
    // Check if location is available
    if (!location) {
      setResult({
        success: false,
        message: 'Location not available. Please enable location access and try again.',
        data: null,
      });
      return;
    }

    setSubmitting(true);
    setResult(null);

    try {
      // Prepare attendance data
      const attendanceData = {
        token: token,
        latitude: location.latitude,
        longitude: location.longitude,
        accuracy: location.accuracy,
        device_info: {
          user_agent: navigator.userAgent,
          platform: navigator.platform,
        },
        device_timestamp: new Date().toISOString(),
      };

      // Call attendance marking API
      const response = await attendanceAPI.markAttendance(attendanceData);

      // Success response
      setResult({
        success: true,
        message: response.data.message || 'Attendance marked successfully!',
        data: response.data,
      });
    } catch (error) {
      // Error response
      const errorMessage = error.data?.message || 
                          error.data?.detail || 
                          error.message || 
                          'Failed to mark attendance. Please try again.';
      
      setResult({
        success: false,
        message: errorMessage,
        data: error.data,
      });
    } finally {
      setSubmitting(false);
    }
  };

  /**
   * Handle QR scan success
   */
  const handleQRScanSuccess = (decodedText) => {
    handleAttendanceSubmit(decodedText);
  };

  /**
   * Handle QR scan error
   */
  const handleQRScanError = (error) => {
    setResult({
      success: false,
      message: error.message || 'Failed to scan QR code',
      data: null,
    });
  };

  /**
   * Handle manual code submission
   */
  const handleManualCodeSubmit = (code) => {
    handleAttendanceSubmit(code);
  };

  /**
   * Reset and try again
   */
  const handleTryAgain = () => {
    setResult(null);
    getCurrentLocation();
  };

  return (
    <div className="w-full max-w-2xl mx-auto">
      {/* Location status banner */}
      <div className="mb-6">
        {locationLoading && (
          <div className="p-4 bg-yellow-50 border border-yellow-200 rounded-md">
            <div className="flex items-center">
              <svg className="animate-spin h-5 w-5 text-yellow-600 mr-3" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              <p className="text-sm text-yellow-700">Getting your location...</p>
            </div>
          </div>
        )}

        {locationError && (
          <div className="p-4 bg-red-50 border border-red-200 rounded-md">
            <div className="flex flex-col space-y-3">
              <div className="flex items-start">
                <svg className="h-5 w-5 text-red-400 mr-3 mt-0.5 flex-shrink-0" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                </svg>
                <div className="flex-1">
                  <p className="text-sm font-medium text-red-800 mb-2">Location Access Required</p>
                  <p className="text-sm text-red-700 mb-2">{locationError}</p>
                  <div className="text-xs text-red-600 space-y-1">
                    <p><strong>To fix this:</strong></p>
                    <ol className="list-decimal list-inside space-y-1 ml-2">
                      <li>Enable location services on your device</li>
                      <li>Allow location access for this website in your browser</li>
                      <li>If using a computer, ensure WiFi is enabled</li>
                      <li>Click the "Retry" button below</li>
                    </ol>
                  </div>
                </div>
              </div>
              <button
                onClick={() => getCurrentLocation().catch(err => console.error(err))}
                className="self-start px-4 py-2 text-sm bg-red-600 text-white rounded hover:bg-red-700 transition-colors"
              >
                Retry Location Access
              </button>
            </div>
          </div>
        )}

        {location && !locationError && (
          <div className="p-4 bg-green-50 border border-green-200 rounded-md">
            <div className="flex items-center">
              <svg className="h-5 w-5 text-green-400 mr-3" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
              </svg>
              <p className="text-sm text-green-700">
                Location captured (Accuracy: ±{Math.round(location.accuracy)}m)
              </p>
            </div>
          </div>
        )}
      </div>

      {/* Result display */}
      {result && (
        <div className={`mb-6 p-6 rounded-lg border-2 ${
          result.success 
            ? 'bg-green-50 border-green-300' 
            : 'bg-red-50 border-red-300'
        }`}>
          <div className="flex items-start">
            {result.success ? (
              <svg className="h-8 w-8 text-green-500 mr-4 flex-shrink-0" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
              </svg>
            ) : (
              <svg className="h-8 w-8 text-red-500 mr-4 flex-shrink-0" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
              </svg>
            )}
            <div className="flex-1">
              <h3 className={`text-lg font-semibold mb-2 ${
                result.success ? 'text-green-900' : 'text-red-900'
              }`}>
                {result.success ? 'Success!' : 'Failed'}
              </h3>
              <p className={`text-sm mb-3 ${
                result.success ? 'text-green-700' : 'text-red-700'
              }`}>
                {result.message}
              </p>
              
              {/* Additional details */}
              {result.data && (
                <div className="mt-3 space-y-1">
                  {result.data.status && (
                    <p className="text-sm text-gray-700">
                      <span className="font-medium">Status:</span> {result.data.status}
                    </p>
                  )}
                  {result.data.distance_meters !== undefined && (
                    <p className="text-sm text-gray-700">
                      <span className="font-medium">Distance:</span> {result.data.distance_meters.toFixed(1)}m
                    </p>
                  )}
                  {result.data.marked_at && (
                    <p className="text-sm text-gray-700">
                      <span className="font-medium">Time:</span> {new Date(result.data.marked_at).toLocaleString()}
                    </p>
                  )}
                  {result.data.reason && (
                    <p className="text-sm text-gray-700">
                      <span className="font-medium">Reason:</span> {result.data.reason}
                    </p>
                  )}
                </div>
              )}
              
              {/* Try again button */}
              <button
                onClick={handleTryAgain}
                className={`mt-4 px-4 py-2 rounded-md text-sm font-medium ${
                  result.success
                    ? 'bg-green-600 text-white hover:bg-green-700'
                    : 'bg-red-600 text-white hover:bg-red-700'
                }`}
              >
                {result.success ? 'Mark Another Attendance' : 'Try Again'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Tabs */}
      {!result && (
        <>
          <div className="border-b border-gray-200 mb-6">
            <nav className="-mb-px flex space-x-8">
              <button
                onClick={() => setActiveTab('qr')}
                className={`py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
                  activeTab === 'qr'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <div className="flex items-center">
                  <svg className="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v1m6 11h2m-6 0h-2v4m0-11v3m0 0h.01M12 12h4.01M16 20h4M4 12h4m12 0h.01M5 8h2a1 1 0 001-1V5a1 1 0 00-1-1H5a1 1 0 00-1 1v2a1 1 0 001 1zm12 0h2a1 1 0 001-1V5a1 1 0 00-1-1h-2a1 1 0 00-1 1v2a1 1 0 001 1zM5 20h2a1 1 0 001-1v-2a1 1 0 00-1-1H5a1 1 0 00-1 1v2a1 1 0 001 1z" />
                  </svg>
                  Scan QR Code
                </div>
              </button>
              <button
                onClick={() => setActiveTab('manual')}
                className={`py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
                  activeTab === 'manual'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <div className="flex items-center">
                  <svg className="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 20l4-16m2 16l4-16M6 9h14M4 15h14" />
                  </svg>
                  Enter Code
                </div>
              </button>
            </nav>
          </div>

          {/* Tab content */}
          <div className="bg-white rounded-lg shadow-md p-6">
            {activeTab === 'qr' ? (
              <div>
                <h2 className="text-xl font-semibold text-gray-900 mb-4">Scan QR Code</h2>
                {location && !locationError ? (
                  <QRScanner 
                    onScanSuccess={handleQRScanSuccess}
                    onScanError={handleQRScanError}
                  />
                ) : (
                  <div className="text-center py-8">
                    <p className="text-gray-600">
                      Please enable location access to scan QR codes.
                    </p>
                  </div>
                )}
              </div>
            ) : (
              <div>
                <h2 className="text-xl font-semibold text-gray-900 mb-4">Enter 6-Digit Code</h2>
                {location && !locationError ? (
                  <ManualCodeEntry 
                    onSubmit={handleManualCodeSubmit}
                    loading={submitting}
                  />
                ) : (
                  <div className="text-center py-8">
                    <p className="text-gray-600">
                      Please enable location access to enter attendance code.
                    </p>
                  </div>
                )}
              </div>
            )}
          </div>
        </>
      )}
    </div>
  );
};

export default ScanPage;
