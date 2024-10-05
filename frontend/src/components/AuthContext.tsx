// AuthContext.tsx
import React, { createContext, useState, useEffect } from 'react';
import { useAuth0 } from '@auth0/auth0-react';

interface AuthContextType {
  isAuthenticated: boolean;
}

const AuthContext = createContext<AuthContextType>({ isAuthenticated: false });

const AuthProvider: React.FC = ({ children }) => {
  const { isAuthenticated } = useAuth0();
  const [userIsAuthenticated, setUserIsAuthenticated] = useState(isAuthenticated);

  useEffect(() => {
    setUserIsAuthenticated(isAuthenticated);
  }, [isAuthenticated]);

  return (
    <AuthContext.Provider value={{ isAuthenticated: userIsAuthenticated }}>
      {children}
    </AuthContext.Provider>
  );
};

export { AuthContext, AuthProvider };