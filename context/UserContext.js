import React, { createContext, useState, useEffect, useContext } from 'react';
import AsyncStorage from '@react-native-async-storage/async-storage';

const UserContext = createContext();

export const UserProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  // Load user from AsyncStorage on mount
  useEffect(() => {
    const loadUser = async () => {
      try {
        const storedUser = await AsyncStorage.getItem('@transitvoice_user');
        if (storedUser) {
          setUser(JSON.parse(storedUser));
        }
      } catch (error) {
        console.error('[UserContext] Failed to load user', error);
      } finally {
        setIsLoading(false);
      }
    };
    loadUser();
  }, []);

  // login receives { user_id, name, language }
  const login = async (userData) => {
    try {
      await AsyncStorage.setItem('@transitvoice_user', JSON.stringify(userData));
      setUser(userData);
    } catch (error) {
      console.error('[UserContext] Failed to save user info', error);
    }
  };

  const logout = async () => {
    try {
      await AsyncStorage.removeItem('@transitvoice_user');
      setUser(null);
    } catch (error) {
      console.error('[UserContext] Failed to remove user info', error);
    }
  };

  return (
    <UserContext.Provider value={{ user, isLoading, login, logout }}>
      {children}
    </UserContext.Provider>
  );
};

export const useUser = () => useContext(UserContext);
