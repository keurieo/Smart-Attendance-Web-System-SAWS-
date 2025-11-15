import LoadingSpinner from './LoadingSpinner';

/**
 * Button component with loading state
 */

const LoadingButton = ({
  children,
  loading = false,
  disabled = false,
  type = 'button',
  variant = 'primary',
  size = 'md',
  fullWidth = false,
  className = '',
  loadingText = 'Loading...',
  onClick,
  ...props
}) => {
  const isDisabled = disabled || loading;

  const baseClasses = 'inline-flex items-center justify-center font-medium rounded-md focus:outline-none focus:ring-2 focus:ring-offset-2 transition-colors';

  const variantClasses = {
    primary: 'bg-blue-600 text-white hover:bg-blue-700 focus:ring-blue-500 disabled:bg-blue-400',
    secondary: 'bg-gray-600 text-white hover:bg-gray-700 focus:ring-gray-500 disabled:bg-gray-400',
    success: 'bg-green-600 text-white hover:bg-green-700 focus:ring-green-500 disabled:bg-green-400',
    danger: 'bg-red-600 text-white hover:bg-red-700 focus:ring-red-500 disabled:bg-red-400',
    outline: 'bg-white border-2 border-gray-300 text-gray-700 hover:bg-gray-50 focus:ring-gray-500 disabled:bg-gray-100',
  };

  const sizeClasses = {
    sm: 'px-3 py-1.5 text-sm',
    md: 'px-4 py-2 text-base',
    lg: 'px-6 py-3 text-lg',
  };

  const widthClass = fullWidth ? 'w-full' : '';

  return (
    <button
      type={type}
      disabled={isDisabled}
      onClick={onClick}
      className={`
        ${baseClasses}
        ${variantClasses[variant]}
        ${sizeClasses[size]}
        ${widthClass}
        ${isDisabled ? 'cursor-not-allowed opacity-60' : ''}
        ${className}
      `}
      {...props}
    >
      {loading && (
        <LoadingSpinner 
          size="sm" 
          color={variant === 'outline' ? 'gray' : 'white'} 
          className="mr-2" 
        />
      )}
      {loading ? loadingText : children}
    </button>
  );
};

export default LoadingButton;
