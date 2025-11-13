import React from 'react';
import { BrowserRouter as Router } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
      staleTime: 5 * 60 * 1000, // 5 minutes
    },
  },
});

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <Router>
        <div className="min-h-screen bg-gray-50">
          <div className="container mx-auto px-4 py-8">
            <h1 className="text-3xl font-bold text-center text-primary-600">
              Smart Attendance System
            </h1>
            <p className="text-center text-gray-600 mt-2">
              Project structure initialized. Components will be added in later tasks.
            </p>
          </div>
        </div>
      </Router>
    </QueryClientProvider>
  );
}

export default App;
