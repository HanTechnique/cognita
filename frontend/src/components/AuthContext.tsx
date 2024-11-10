// AuthContext.tsx
import React, { createContext, useState, useEffect } from 'react';
import { useAuth0 } from '@auth0/auth0-react';

interface AuthContextType {
  isAuthenticated: boolean;
}

const AuthContext = createContext<AuthContextType>({ isAuthenticated: false });

const AuthProvider: React.FC = ({ children }) => {
  const { isAuthenticated, getIdTokenClaims } = useAuth0();
  const [userIsAuthenticated, setUserIsAuthenticated] = useState(isAuthenticated);

  useEffect(() => {
    const checkAuthentication = async () => {
      if (isAuthenticated) {
        try {
          // Get and store the idToken
          const claims = await getIdTokenClaims();
          const idToken = claims.__raw;
          localStorage.setItem('idToken', idToken);
        } catch (error) {
          console.error('Error getting and storing idToken:', error);
        }
      }

      setUserIsAuthenticated(isAuthenticated);
    };

    checkAuthentication();
  }, [isAuthenticated]);

  return (
    <AuthContext.Provider value={{ isAuthenticated: userIsAuthenticated }}>
      {children}
    </AuthContext.Provider>
  );
};

export { AuthContext, AuthProvider };