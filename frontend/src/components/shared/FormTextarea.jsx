/**
 * Reusable form textarea component with validation display
 */

const FormTextarea = ({
  label,
  name,
  placeholder,
  value,
  onChange,
  onBlur,
  error,
  touched,
  required = false,
  disabled = false,
  rows = 4,
  className = '',
  textareaClassName = '',
  ...props
}) => {
  const hasError = touched && error;

  return (
    <div className={`form-group ${className}`}>
      {label && (
        <label htmlFor={name} className="block text-sm font-medium text-gray-700 mb-1">
          {label}
          {required && <span className="text-red-500 ml-1">*</span>}
        </label>
      )}
      
      <textarea
        id={name}
        name={name}
        value={value}
        onChange={onChange}
        onBlur={onBlur}
        placeholder={placeholder}
        disabled={disabled}
        rows={rows}
        className={`
          w-full px-3 py-2 border rounded-md shadow-sm
          focus:outline-none focus:ring-2 focus:ring-offset-0
          disabled:bg-gray-100 disabled:cursor-not-allowed
          resize-vertical
          ${hasError 
            ? 'border-red-300 focus:border-red-500 focus:ring-red-500' 
            : 'border-gray-300 focus:border-blue-500 focus:ring-blue-500'
          }
          ${textareaClassName}
        `}
        {...props}
      />
      
      {hasError && (
        <p className="mt-1 text-sm text-red-600 flex items-center">
          <svg className="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
          </svg>
          {error}
        </p>
      )}
    </div>
  );
};

export default FormTextarea;
