import { useEffect, useRef, useState } from 'react';
import { Html5QrcodeScanner } from 'html5-qrcode';

/**
 * QRScanner component using html5-qrcode library
 * Requests camera permission, displays camera preview with scan overlay
 * Emits scanned token to parent component
 * Handles camera errors and permission denial
 */
const QRScanner = ({ onScanSuccess, onScanError }) => {
  const scannerRef = useRef(null);
  const [isScanning, setIsScanning] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    // Initialize scanner only once
    if (scannerRef.current || isScanning) {
      return;
    }

    setIsScanning(true);
    setError(null);

    // Create scanner instance
    const scanner = new Html5QrcodeScanner(
      'qr-reader',
      {
        fps: 10, // Frames per second for scanning
        qrbox: { width: 250, height: 250 }, // Scanning box dimensions
        aspectRatio: 1.0,
        showTorchButtonIfSupported: true, // Show flashlight button if available
        showZoomSliderIfSupported: true, // Show zoom slider if available
      },
      false // verbose logging
    );

    // Success callback
    const handleScanSuccess = (decodedText, decodedResult) => {
      // Stop scanning after successful scan
      scanner.clear().catch(err => {
        console.error('Error clearing scanner:', err);
      });
      
      setIsScanning(false);
      
      // Emit scanned token to parent
      if (onScanSuccess) {
        onScanSuccess(decodedText, decodedResult);
      }
    };

    // Error callback (called on every failed scan attempt)
    const handleScanError = (errorMessage) => {
      // Don't show errors for normal scan failures (no QR code in view)
      // Only show critical errors
      if (errorMessage.includes('NotAllowedError') || 
          errorMessage.includes('NotFoundError') ||
          errorMessage.includes('NotReadableError')) {
        
        let userFriendlyError = 'Camera access error';
        
        if (errorMessage.includes('NotAllowedError')) {
          userFriendlyError = 'Camera permission denied. Please enable camera access in your browser settings.';
        } else if (errorMessage.includes('NotFoundError')) {
          userFriendlyError = 'No camera found. Please ensure your device has a camera.';
        } else if (errorMessage.includes('NotReadableError')) {
          userFriendlyError = 'Camera is already in use by another application.';
        }
        
        setError(userFriendlyError);
        setIsScanning(false);
        
        if (onScanError) {
          onScanError(new Error(userFriendlyError));
        }
      }
    };

    // Render the scanner
    scanner.render(handleScanSuccess, handleScanError);
    
    // Store scanner reference
    scannerRef.current = scanner;

    // Cleanup function
    return () => {
      if (scannerRef.current) {
        scannerRef.current.clear().catch(err => {
          console.error('Error clearing scanner on unmount:', err);
        });
        scannerRef.current = null;
      }
    };
  }, [onScanSuccess, onScanError, isScanning]);

  return (
    <div className="w-full">
      {/* Scanner container */}
      <div id="qr-reader" className="w-full"></div>
      
      {/* Error message */}
      {error && (
        <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-md">
          <div className="flex">
            <div className="flex-shrink-0">
              <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
              </svg>
            </div>
            <div className="ml-3">
              <p className="text-sm text-red-700">{error}</p>
            </div>
          </div>
        </div>
      )}
      
      {/* Instructions */}
      {!error && (
        <div className="mt-4 p-4 bg-blue-50 border border-blue-200 rounded-md">
          <p className="text-sm text-blue-700">
            Position the QR code within the scanning box. The camera will automatically detect and scan it.
          </p>
        </div>
      )}
    </div>
  );
};

export default QRScanner;
