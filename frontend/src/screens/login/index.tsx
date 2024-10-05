import React from 'react';
import { useAuth0 } from '@auth0/auth0-react';
import { useLocation, useNavigate } from 'react-router-dom';

const LoginPage = () => {
  const { loginWithRedirect } = useAuth0();
  const location = useLocation();
  const navigate = useNavigate();

  const handleLogin = async () => {
    const redirectUrl = new URLSearchParams(location.search).get('url_redirect') || '/';

    // Store the redirect URL in Auth0's state parameter
    await loginWithRedirect({
      appState: { returnTo: redirectUrl },
    });
  };

  // Check if already logged in and redirect if needed
  const { isAuthenticated, isLoading } = useAuth0();
  if (!isLoading && isAuthenticated) {
    const redirectUrl = new URLSearchParams(location.search).get('url_redirect') || '/';
    navigate(redirectUrl);
    return null; // Don't render anything while redirecting
  }

  return (
    <div className="w-full h-screen grid place-items-center">
      <div className="flex flex-col sm:flex-row gap-4 items-center sm:pb-72">
        <div className="divider sm:divider-horizontal" />
        <div className="flex flex-col gap-2">
          <h2 className="font-inter font-black text-6xl">Login</h2>
          <button onClick={handleLogin} className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded">
            Log in with Auth0
          </button>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;
