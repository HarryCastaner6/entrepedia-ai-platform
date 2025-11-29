import React, { useEffect } from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuthStore } from '../../stores/authStore';
import { authApi } from '../../services/api';
import toast from 'react-hot-toast';

interface ProtectedRouteProps {
  children: React.ReactNode;
  redirectTo?: string;
}

export function ProtectedRoute({ children, redirectTo = '/login' }: ProtectedRouteProps) {
  const { isAuthenticated, token, setLoading, logout } = useAuthStore();
  const location = useLocation();

  useEffect(() => {
    // If we have a token but not authenticated state, verify the token
    const verifyToken = async () => {
      if (token && !isAuthenticated) {
        setLoading(true);
        try {
          // Try to get user info to verify token is still valid
          await authApi.getProfile();
          // Token is valid, user should be logged in already via store
        } catch (error) {
          // Token is invalid, log out
          logout();
          toast.error('Your session has expired. Please log in again.');
        } finally {
          setLoading(false);
        }
      }
    };

    verifyToken();
  }, [token, isAuthenticated, setLoading, logout]);

  // If not authenticated and no token, redirect to login
  if (!isAuthenticated && !token) {
    return <Navigate to={redirectTo} state={{ from: location }} replace />;
  }

  // If authenticated or has token (being verified), show protected content
  return <>{children}</>;
}

// Higher-order component for protecting routes
export function withAuth<T extends object>(Component: React.ComponentType<T>) {
  return function AuthenticatedComponent(props: T) {
    return (
      <ProtectedRoute>
        <Component {...props} />
      </ProtectedRoute>
    );
  };
}