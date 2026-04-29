import React, { useEffect, useState } from 'react';
import LoginForm from '../components/auth/LoginForm';
import { useLocation } from 'react-router-dom';

const LoginPage = () => {
  const [sessionMessage, setSessionMessage] = useState('');
  const location = useLocation();

  useEffect(() => {
    const message = sessionStorage.getItem('session_expired') || location.state?.error;
    if (message) {
      setSessionMessage(message);
      sessionStorage.removeItem('session_expired');
    }
  }, [location.state]);

  return (
    <div>
      {sessionMessage && (
        <div className="bg-yellow-50 border border-yellow-200 text-yellow-800 px-4 py-3 text-sm">
          {sessionMessage}
        </div>
      )}
      <LoginForm />
    </div>
  );
};

export default LoginPage;
