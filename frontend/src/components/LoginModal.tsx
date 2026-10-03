import React, { useState, useEffect } from 'react';
import { useAuth, DEMO_PERSONAS } from '../context/AuthContext';
import { Sparkles, ArrowRight, UserCheck, UserPlus, AlertCircle, X } from 'lucide-react';
import { formatCurrency } from '../utils/formatters';

interface LoginModalProps {
  isOpen: boolean;
  onClose?: () => void;
}

export const LoginModal: React.FC<LoginModalProps> = ({ isOpen, onClose }) => {

  const { loginAsDemo, loginNormal, registerNormal, isLoading, error, clearError, demoAccounts } = useAuth();
  const [activeTab, setActiveTab] = useState<'demo' | 'login' | 'register'>('demo');
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [displayName, setDisplayName] = useState('');
  const [localError, setLocalError] = useState<string | null>(null);

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && onClose) {
        onClose();
      }
    };
    if (isOpen) {
      window.addEventListener('keydown', handleKeyDown);
    }
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  const handleSelectDemo = async (accountId: string) => {
    setLocalError(null);
    clearError();
    try {
      await loginAsDemo(accountId);
      if (onClose) onClose();
    } catch (err: any) {
      setLocalError(err.message || 'Demo authentication failed');
    }
  };

  const handleNormalLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLocalError(null);
    clearError();
    if (!username.trim() || !password) {
      setLocalError('Please enter username and password');
      return;
    }
    try {
      await loginNormal(username, password);
      if (onClose) onClose();
    } catch (err: any) {
      setLocalError(err.message || 'Login failed');
    }
  };

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    setLocalError(null);
    clearError();
    if (!username.trim() || !password) {
      setLocalError('Please enter username and password');
      return;
    }
    try {
      await registerNormal(username, password, displayName.trim() || undefined);
      if (onClose) onClose();
    } catch (err: any) {
      setLocalError(err.message || 'Registration failed');
    }
  };

  const currentErr = localError || error;

  return (
    <div
      className="modal-overlay auth-modal-overlay"
      onClick={() => {
        if (onClose) onClose();
      }}
    >
      <div className="modal-card auth-modal-card" onClick={(e) => e.stopPropagation()}>
        {onClose && (
          <button className="modal-close auth-close" onClick={onClose} aria-label="Close modal">
            <X size={18} />
          </button>
        )}


        <div className="auth-header-section">
          <div className="auth-brand-badge">
            <img src="/logo.svg" alt="Spendable Logo" className="auth-logo-img" draggable={false} />
            <span className="auth-brand-text">Spendable</span>
          </div>
          <h2>Welcome to Spendable</h2>
          <p className="subtitle">Know what you can safely spend.</p>
        </div>

        {currentErr && (
          <div className="auth-error-banner">
            <AlertCircle size={16} />
            <span>{currentErr}</span>
          </div>
        )}

        {/* Mode Selector Tabs */}
        <div className="auth-tab-bar">
          <button
            className={`auth-tab-btn ${activeTab === 'demo' ? 'active' : ''}`}
            onClick={() => {
              setActiveTab('demo');
              setLocalError(null);
            }}
          >
            <Sparkles size={14} />
            <span>Demo Accounts</span>
          </button>
          <button
            className={`auth-tab-btn ${activeTab === 'login' ? 'active' : ''}`}
            onClick={() => {
              setActiveTab('login');
              setLocalError(null);
            }}
          >
            <UserCheck size={14} />
            <span>Sign In</span>
          </button>
          <button
            className={`auth-tab-btn ${activeTab === 'register' ? 'active' : ''}`}
            onClick={() => {
              setActiveTab('register');
              setLocalError(null);
            }}
          >
            <UserPlus size={14} />
            <span>Create Account</span>
          </button>
        </div>

        {/* Tab 1: Demo Accounts Grid */}
        {activeTab === 'demo' && (
          <div className="demo-accounts-container">
            <p className="demo-section-hint">
              Select a persona to immediately explore genuinely different historical cash-flow behaviors.
            </p>
            <div className="demo-card-grid">
              {DEMO_PERSONAS.map((p) => {
                const liveAcc = demoAccounts.find(
                  (d) => d.account_id === p.account_id || d.username === p.username
                );
                const displayBalance = liveAcc ? liveAcc.current_balance : p.balance;
                return (
                  <button
                    key={p.account_id}
                    className={`demo-select-card ${p.account_id === 'acc_supan' ? 'default-persona' : ''}`}
                    onClick={() => handleSelectDemo(p.account_id)}
                    disabled={isLoading}
                  >
                    <div className="card-top">
                      <span className="persona-name">{p.display_name}</span>
                      {p.account_id === 'acc_supan' && (
                        <span className="default-badge">DEFAULT</span>
                      )}
                    </div>
                    <div className="persona-descriptor">{p.descriptor}</div>
                    <div className="persona-balance">{formatCurrency(displayBalance)}</div>
                    <div className="card-action">
                      <span>Explore Dashboard</span>
                      <ArrowRight size={13} />
                    </div>
                  </button>
                );
              })}
            </div>
          </div>
        )}

        {/* Tab 2: Normal User Sign In */}
        {activeTab === 'login' && (
          <form className="auth-form" onSubmit={handleNormalLogin}>
            <div className="form-group">
              <label>Username</label>
              <input
                type="text"
                placeholder="Enter your username"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                disabled={isLoading}
              />
            </div>
            <div className="form-group">
              <label>Password</label>
              <input
                type="password"
                placeholder="Enter password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                disabled={isLoading}
              />
            </div>
            <button type="submit" className="primary-btn full-width" disabled={isLoading}>
              {isLoading ? 'Authenticating...' : 'Sign In'}
            </button>
          </form>
        )}

        {/* Tab 3: Create Normal User Account */}
        {activeTab === 'register' && (
          <form className="auth-form" onSubmit={handleRegister}>
            <div className="form-group">
              <label>Username</label>
              <input
                type="text"
                placeholder="Choose a username"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                disabled={isLoading}
              />
            </div>
            <div className="form-group">
              <label>Display Name (Optional)</label>
              <input
                type="text"
                placeholder="Your full name"
                value={displayName}
                onChange={(e) => setDisplayName(e.target.value)}
                disabled={isLoading}
              />
            </div>
            <div className="form-group">
              <label>Password</label>
              <input
                type="password"
                placeholder="Create password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                disabled={isLoading}
              />
            </div>
            <p className="no-verification-note">
              No email or OTP verification required. Hackathon prototype registration.
            </p>
            <button type="submit" className="primary-btn full-width" disabled={isLoading}>
              {isLoading ? 'Creating Account...' : 'Create Account'}
            </button>
          </form>
        )}
      </div>
    </div>
  );
};
