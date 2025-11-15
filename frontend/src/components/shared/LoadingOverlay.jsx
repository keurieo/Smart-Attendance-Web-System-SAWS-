import LoadingSpinner from './LoadingSpinner';

/**
 * Full-screen or container loading overlay
 */

const LoadingOverlay = ({ 
  loading = false,
  message = 'Loading...',
  fullScreen = false,
  className = '' 
}) => {
  if (!loading) return null;

  const overlayClasses = fullScreen
    ? 'fixed inset-0 z-50'
    : 'absolute inset-0 z-10';

  return (
    <div className={`${overlayClasses} ${className}`}>
      <div className="absolute inset-0 bg-gray-900 bg-opacity-50 backdrop-blur-sm" />
      <div className="absolute inset-0 flex items-center justify-center">
        <div className="bg-white rounded-lg shadow-xl p-6 flex flex-col items-center space-y-4">
          <LoadingSpinner size="lg" />
          {message && (
            <p className="text-gray-700 font-medium">{message}</p>
          )}
        </div>
      </div>
    </div>
  );
};

export default LoadingOverlay;
