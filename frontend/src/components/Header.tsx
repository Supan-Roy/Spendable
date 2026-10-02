import React, { useState, useRef, useEffect } from 'react';
import { useAuth, DEMO_PERSONAS } from '../context/AuthContext';
import { User, ChevronDown, LogOut, Sparkles, ShieldCheck } from 'lucide-react';
import { formatCurrency } from '../utils/formatters';

export type TabType = 'overview' | 'activity' | 'forecast' | 'simulate';

interface HeaderProps {
  activeTab: TabType;
  setActiveTab: (tab: TabType) => void;
  onOpenLogin: () => void;
}

export const Header: React.FC<HeaderProps> = ({ activeTab, setActiveTab, onOpenLogin }) => {
  const { currentUser, loginAsDemo, logout, isAuthenticated } = useAuth();
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  // Close dropdown on outside click
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setDropdownOpen(false);
      }
    }
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleSelectDemo = async (accountId: string) => {
    setDropdownOpen(false);
    await loginAsDemo(accountId);
  };

  return (
    <header className="app-header">
      <div className="header-left">
        <div className="logo-group" onClick={() => setActiveTab('overview')} style={{ cursor: 'pointer' }}>
          <img src="/logo.svg" alt="Spendable Logo" className="logo-img" draggable={false} />
          <span className="brand-name">SPENDABLE</span>
        </div>

        {isAuthenticated && (
          <nav className="top-nav">
            <button
              className={`nav-item ${activeTab === 'overview' ? 'active' : ''}`}
              onClick={() => setActiveTab('overview')}
            >
              Overview
            </button>
            <button
              className={`nav-item ${activeTab === 'activity' ? 'active' : ''}`}
              onClick={() => setActiveTab('activity')}
            >
              Activity
            </button>
            <button
              className={`nav-item ${activeTab === 'forecast' ? 'active' : ''}`}
              onClick={() => setActiveTab('forecast')}
            >
              Forecast
            </button>
            <button
              className={`nav-item ${activeTab === 'simulate' ? 'active' : ''}`}
              onClick={() => setActiveTab('simulate')}
            >
              Simulate
            </button>
          </nav>
        )}
      </div>

      <div className="header-right" ref={dropdownRef}>
        {isAuthenticated && currentUser ? (
          <div className="account-switcher-wrapper">
            <button
              className="account-badge-btn"
              onClick={() => setDropdownOpen(!dropdownOpen)}
              title="Switch Account"
            >
              <span className="user-icon-circle">
                <User size={14} color="#00e5a3" />
              </span>
              <span className="user-name-text">
                {currentUser.display_name || currentUser.username || currentUser.account_id}
              </span>
              {currentUser.is_demo_account && (
                <span className="demo-tag">DEMO</span>
              )}
              <ChevronDown size={14} className={`dropdown-arrow ${dropdownOpen ? 'open' : ''}`} />
            </button>

            {dropdownOpen && (
              <div className="account-dropdown-menu">
                <div className="dropdown-section-header">
                  <Sparkles size={13} color="#00e5a3" />
                  <span>DEMO ACCOUNTS</span>
                </div>

                <div className="demo-list-group">
                  {DEMO_PERSONAS.map((p) => {
                    const isSelected = currentUser?.account_id === p.account_id;
                    return (
                      <button
                        key={p.account_id}
                        className={`demo-dropdown-item ${isSelected ? 'selected' : ''}`}
                        onClick={() => handleSelectDemo(p.account_id)}
                      >
                        <div className="item-left">
                          <span className="item-name">{p.display_name}</span>
                          <span className="item-desc">{p.descriptor}</span>
                        </div>
                        <span className="item-bal">{formatCurrency(p.balance)}</span>
                      </button>
                    );
                  })}
                </div>

                <div className="dropdown-divider"></div>

                <button
                  className="logout-dropdown-item"
                  onClick={() => {
                    setDropdownOpen(false);
                    logout();
                    onOpenLogin();
                  }}
                >
                  <LogOut size={14} />
                  <span>Sign out / Change account</span>
                </button>
              </div>
            )}
          </div>
        ) : (
          <button className="secondary-btn compact" onClick={onOpenLogin}>
            <ShieldCheck size={16} />
            <span>Sign In / Select Account</span>
          </button>
        )}
      </div>
    </header>
  );
};
