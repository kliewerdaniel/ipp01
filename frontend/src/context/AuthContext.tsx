import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import axios from 'axios';
import { useRouter } from 'next/router';

// Types
interface User {
  id: string;
  email: string;
  name: string;
  role: string;
}

interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (name: string, email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  refreshToken: () => Promise<void>;
}

// Create the context
const AuthContext = createContext<AuthContextType | undefined>(undefined);

// Create the AuthProvider component
export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const router = useRouter();
  
  // Initialize auth state
  useEffect(() => {
    const initAuth = async () => {
      // Check if a token exists in localStorage
      const token = localStorage.getItem('access_token');
      if (token) {
        try {
          // Set default auth header
          axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
          // Try to get user profile
          await refreshToken();
          
          // If successful, set authenticated
          setIsAuthenticated(true);
        } catch (error) {
          // If token is invalid, clear it
          console.error('Authentication error:', error);
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');
          axios.defaults.headers.common['Authorization'] = '';
        }
      }
      setIsLoading(false);
    };

    initAuth();
  }, []);

  // Login function
  const login = async (email: string, password: string): Promise<void> => {
    setIsLoading(true);
    try {
      const response = await axios.post(`${process.env.NEXT_PUBLIC_API_URL}/api/auth/login`, {
        email,
        password,
      });
      
      const { access_token, refresh_token, user } = response.data;
      
      // Store tokens in localStorage
      localStorage.setItem('access_token', access_token);
      localStorage.setItem('refresh_token', refresh_token);
      
      // Set default auth header
      axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
      
      // Update state
      setUser(user);
      setIsAuthenticated(true);
      
      // Redirect to dashboard
      router.push('/dashboard');
    } catch (error) {
      console.error('Login error:', error);
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  // Register function
  const register = async (name: string, email: string, password: string): Promise<void> => {
    setIsLoading(true);
    try {
      const response = await axios.post(`${process.env.NEXT_PUBLIC_API_URL}/api/auth/register`, {
        name,
        email,
        password,
      });
      
      const { access_token, refresh_token, user } = response.data;
      
      // Store tokens in localStorage
      localStorage.setItem('access_token', access_token);
      localStorage.setItem('refresh_token', refresh_token);
      
      // Set default auth header
      axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
      
      // Update state
      setUser(user);
      setIsAuthenticated(true);
      
      // Redirect to dashboard
      router.push('/dashboard');
    } catch (error) {
      console.error('Registration error:', error);
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  // Logout function
  const logout = async (): Promise<void> => {
    try {
      // Call logout endpoint (optional)
      await axios.post(`${process.env.NEXT_PUBLIC_API_URL}/api/auth/logout`);
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      // Clear tokens from localStorage
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      
      // Remove auth header
      axios.defaults.headers.common['Authorization'] = '';
      
      // Update state
      setUser(null);
      setIsAuthenticated(false);
      
      // Redirect to home
      router.push('/');
    }
  };

  // Token refresh function
  const refreshToken = async (): Promise<void> => {
    try {
      const refresh_token = localStorage.getItem('refresh_token');
      
      if (!refresh_token) {
        throw new Error('No refresh token available');
      }
      
      const response = await axios.post(`${process.env.NEXT_PUBLIC_API_URL}/api/auth/refresh`, {
        refresh_token,
      });
      
      const { access_token, user: userData } = response.data;
      
      // Update access token
      localStorage.setItem('access_token', access_token);
      
      // Update auth header
      axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
      
      // Update user state
      setUser(userData);
    } catch (error) {
      console.error('Token refresh error:', error);
      // Clear tokens and log out
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      axios.defaults.headers.common['Authorization'] = '';
      setUser(null);
      setIsAuthenticated(false);
      
      // Redirect to login
      router.push('/login');
      throw error;
    }
  };

  // Context value
  const value = {
    user,
    isLoading,
    isAuthenticated,
    login,
    register,
    logout,
    refreshToken,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

// Custom hook to use the auth context
export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
