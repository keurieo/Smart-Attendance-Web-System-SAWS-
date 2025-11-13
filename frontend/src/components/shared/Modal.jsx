import React from 'react';

// Modal component will be implemented in task 19.2
const Modal = ({ isOpen, onClose, title, children }) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      <div className="flex items-center justify-center min-h-screen px-4">
        <div className="fixed inset-0 bg-black opacity-50" onClick={onClose}></div>
        <div className="relative bg-white rounded-lg max-w-lg w-full p-6">
          <h3 className="text-xl font-bold mb-4">{title}</h3>
          {children}
        </div>
      </div>
    </div>
  );
};

export default Modal;
