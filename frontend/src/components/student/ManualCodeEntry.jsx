import { useState } from 'react';

/**
 * ManualCodeEntry component with 6-digit input field
 * Validates input is 6 digits
 * Submits code to parent component
 */
const ManualCodeEntry = ({ onSubmit, loading = false }) => {
  const [code, setCode] = useState('');
  const [error, setError] = useState('');

  /**
   * Handle input change - only allow numeric input
   */
  const handleChange = (e) => {
    const value = e.target.value;
    
    // Only allow numeric input
    if (value === '' || /^\d+$/.test(value)) {
      // Limit to 6 digits
      const limitedValue = value.slice(0, 6);
      setCode(limitedValue);
      setError('');
    }
  };

  /**
   * Validate and submit the code
   */
  const handleSubmit = (e) => {
    e.preventDefault();
    
    // Validate code is exactly 6 digits
    if (code.length !== 6) {
      setError('Please enter a 6-digit code');
      return;
    }
    
    // Clear error and submit
    setError('');
    if (onSubmit) {
      onSubmit(code);
    }
  };

  /**
   * Handle paste event to clean pasted content
   */
  const handlePaste = (e) => {
    e.preventDefault();
    const pastedText = e.clipboardData.getData('text');
    
    // Extract only digits from pasted text
    const digits = pastedText.replace(/\D/g, '').slice(0, 6);
    setCode(digits);
    setError('');
  };

  return (
    <div className="w-full max-w-md mx-auto">
      <form onSubmit={handleSubmit} className="space-y-4">
        {/* Code input */}
        <div>
          <label htmlFor="code" className="block text-sm font-medium text-gray-700 mb-2">
            Enter 6-Digit Code
          </label>
          <input
            type="text"
            id="code"
            name="code"
            value={code}
            onChange={handleChange}
            onPaste={handlePaste}
            placeholder="000000"
            disabled={loading}
            className={`w-full px-4 py-3 text-center text-2xl font-mono tracking-widest border rounded-md focus:outline-none focus:ring-2 ${
              error
                ? 'border-red-300 focus:ring-red-500 focus:border-red-500'
                : 'border-gray-300 focus:ring-blue-500 focus:border-blue-500'
            } ${loading ? 'bg-gray-100 cursor-not-allowed' : 'bg-white'}`}
            maxLength={6}
            inputMode="numeric"
            pattern="\d{6}"
            autoComplete="off"
          />
          
          {/* Character count indicator */}
          <div className="mt-2 text-sm text-gray-500 text-center">
            {code.length}/6 digits
          </div>
        </div>

        {/* Error message */}
        {error && (
          <div className="p-3 bg-red-50 border border-red-200 rounded-md">
            <p className="text-sm text-red-700">{error}</p>
          </div>
        )}

        {/* Submit button */}
        <button
          type="submit"
          disabled={loading || code.length !== 6}
          className={`w-full py-3 px-4 rounded-md font-medium text-white transition-colors ${
            loading || code.length !== 6
              ? 'bg-gray-400 cursor-not-allowed'
              : 'bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2'
          }`}
        >
          {loading ? (
            <span className="flex items-center justify-center">
              <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Submitting...
            </span>
          ) : (
            'Submit Code'
          )}
        </button>

        {/* Instructions */}
        <div className="p-4 bg-blue-50 border border-blue-200 rounded-md">
          <p className="text-sm text-blue-700">
            Enter the 6-digit code displayed on your teacher's screen to mark your attendance.
          </p>
        </div>
      </form>
    </div>
  );
};

export default ManualCodeEntry;
