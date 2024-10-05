import React from 'react';
import { useAuth0 } from '@auth0/auth0-react';
import { Navigate, useLocation } from 'react-router-dom';

const PrivateRoute = ({ children }: { children: JSX.Element }) => {
  const { isAuthenticated, isLoading } = useAuth0();
  const location = useLocation();

  if (isLoading) {
    // You might want to show a loading indicator here
    return <p>Loading...</p>;
  }

  if (!isAuthenticated) {
    // Redirect to login page with current URL as redirect_url
    return <Navigate to={'/login?url_redirect=/'} />;
  }

  return children;
};

export default PrivateRoute;
