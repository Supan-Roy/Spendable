import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import type {
  UserAccountResponse,
  AuthTokenResponse,
} from '../api/types';
import {
  demoLoginApi,
  loginApi,
  registerApi,
  getDemoAccountsApi,
  getMeApi,
  deleteAccountApi,
} from '../api/auth';
import { setStoredToken, getStoredToken, setUnauthorizedHandler } from '../api/client';

export interface DemoPersona {
  account_id: string;
  username: string;
  display_name: string;
  descriptor: string;
  balance: number;
}

export const DEMO_PERSONAS: DemoPersona[] = [
  {
    account_id: 'acc_supan',
    username: 'supan',
    display_name: 'Supan',
    descriptor: 'Stable cash flow',
    balance: 321000,
  },
  {
    account_id: 'acc_meraj',
    username: 'meraj',
    display_name: 'Meraj',
    descriptor: 'Tight liquidity',
    balance: 27000,
  },
  {
    account_id: 'acc_sohana',
    username: 'sohana',
    display_name: 'Sohana',
    descriptor: 'Spending changes',
    balance: 308000,
  },
  {
    account_id: 'acc_noman',
    username: 'noman',
    display_name: 'Noman',
    descriptor: 'Variable income',
    balance: 321000,
  },
  {
    account_id: 'acc_refat',
    username: 'refat',
    display_name: 'Refat',
    descriptor: 'High commitments',
    balance: 192000,
  },
];

interface AuthContextType {
  currentUser: UserAccountResponse | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
  demoAccounts: UserAccountResponse[];
  loginAsDemo: (accountId: string) => Promise<void>;
  loginNormal: (username: string, password: string) => Promise<void>;
  registerNormal: (username: string, password: string, displayName?: string) => Promise<void>;
  logout: () => void;
  deleteAccount: () => Promise<void>;
  clearError: () => void;
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

const PROFILE_CACHE_KEY = 'spendable_user_profile';

const getInitialUser = (): UserAccountResponse | null => {
  try {
    const raw = localStorage.getItem(PROFILE_CACHE_KEY);
    return raw ? JSON.parse(raw) : null;
  } catch {
    return null;
  }
};

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [currentUser, setCurrentUser] = useState<UserAccountResponse | null>(getInitialUser);
  const [demoAccounts, setDemoAccounts] = useState<UserAccountResponse[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(() => !getInitialUser());
  const [error, setError] = useState<string | null>(null);

  const updateUserState = useCallback((user: UserAccountResponse | null) => {
    setCurrentUser(user);
    if (user) {
      try {
        localStorage.setItem(PROFILE_CACHE_KEY, JSON.stringify(user));
      } catch {}
    } else {
      localStorage.removeItem(PROFILE_CACHE_KEY);
    }
  }, []);

  const loginAsDemo = useCallback(async (accountId: string) => {
    setIsLoading(true);
    setError(null);
    try {
      const authRes: AuthTokenResponse = await demoLoginApi(accountId);
      setStoredToken(authRes.access_token);
      const [userRes, demosRes] = await Promise.all([
        getMeApi(),
        getDemoAccountsApi().catch(() => []),
      ]);
      updateUserState(userRes);
      setDemoAccounts(demosRes);
    } catch (err: any) {
      setError(err.message || 'Failed to authenticate demo account');
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, [updateUserState]);

  const loginNormal = useCallback(async (username: string, password: string) => {
    setIsLoading(true);
    setError(null);
    try {
      const authRes = await loginApi({ username, password });
      setStoredToken(authRes.access_token);
      const [userRes, demosRes] = await Promise.all([
        getMeApi(),
        getDemoAccountsApi().catch(() => []),
      ]);
      updateUserState(userRes);
      setDemoAccounts(demosRes);
    } catch (err: any) {
      setError(err.message || 'Invalid username or password');
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, [updateUserState]);

  const registerNormal = useCallback(
    async (username: string, password: string, displayName?: string) => {
      setIsLoading(true);
      setError(null);
      try {
        const authRes = await registerApi({ username, password, display_name: displayName });
        setStoredToken(authRes.access_token);
        const [userRes, demosRes] = await Promise.all([
          getMeApi(),
          getDemoAccountsApi().catch(() => []),
        ]);
        updateUserState(userRes);
        setDemoAccounts(demosRes);
      } catch (err: any) {
        setError(err.message || 'Registration failed');
        throw err;
      } finally {
        setIsLoading(false);
      }
    },
    [updateUserState]
  );

  const logout = useCallback(() => {
    setStoredToken(null);
    updateUserState(null);
    setError(null);
  }, [updateUserState]);

  const deleteAccount = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      await deleteAccountApi();
      logout();
      // Default back to Supan demo
      const authRes = await demoLoginApi('acc_supan');
      setStoredToken(authRes.access_token);
      const [userRes, demosRes] = await Promise.all([
        getMeApi(),
        getDemoAccountsApi().catch(() => []),
      ]);
      updateUserState(userRes);
      setDemoAccounts(demosRes);
    } catch (err: any) {
      setError(err.message || 'Failed to delete account');
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, [logout, updateUserState]);

  const refreshUser = useCallback(async () => {
    try {
      const me = await getMeApi();
      updateUserState(me);
    } catch {
      logout();
    }
  }, [logout, updateUserState]);

  // Initial boot effect: check existing session or default to Supan
  useEffect(() => {
    let isMounted = true;
    
    // Register 401 handler
    setUnauthorizedHandler(() => {
      if (isMounted) {
        logout();
      }
    });

    async function initAuth() {
      const existingToken = getStoredToken();
      if (existingToken) {
        try {
          const [me, demos] = await Promise.all([
            getMeApi(),
            getDemoAccountsApi().catch(() => []),
          ]);
          if (isMounted) {
            updateUserState(me);
            setDemoAccounts(demos);
            setIsLoading(false);
          }
          return;
        } catch {
          // Token invalid, clear and proceed to default Supan login
          setStoredToken(null);
          updateUserState(null);
        }
      }

      // Default First Visit experience: automatically login as Supan
      try {
        const authRes = await demoLoginApi('acc_supan');
        setStoredToken(authRes.access_token);
        const [me, demos] = await Promise.all([
          getMeApi(),
          getDemoAccountsApi().catch(() => []),
        ]);
        if (isMounted) {
          updateUserState(me);
          setDemoAccounts(demos);
        }
      } catch (err: any) {
        if (isMounted) {
          setError('Could not connect to backend server. Make sure FastAPI dev server is running on localhost:8000.');
        }
      } finally {
        if (isMounted) {
          setIsLoading(false);
        }
      }
    }

    initAuth();

    return () => {
      isMounted = false;
    };
  }, [logout, updateUserState]);

  return (
    <AuthContext.Provider
      value={{
        currentUser,
        isAuthenticated: !!currentUser,
        isLoading,
        error,
        demoAccounts,
        loginAsDemo,
        loginNormal,
        registerNormal,
        logout,
        deleteAccount,
        clearError: () => setError(null),
        refreshUser,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
