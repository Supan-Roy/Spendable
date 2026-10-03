import React, { useState, useRef, useEffect } from 'react';
import { useAuth, DEMO_PERSONAS } from '../context/AuthContext';
import { User, ChevronDown, LogOut, Sparkles, ShieldCheck, Trash2, Menu, X as CloseIcon } from 'lucide-react';
import { formatCurrency } from '../utils/formatters';

import { ConfirmModal } from './ConfirmModal';

export type TabType = 'overview' | 'activity' | 'forecast' | 'simulate';

interface HeaderProps {
  activeTab: TabType;
  setActiveTab: (tab: TabType) => void;
  onOpenLogin: () => void;
}

export const Header: React.FC<HeaderProps> = ({ activeTab, setActiveTab, onOpenLogin }) => {
  const { currentUser, loginAsDemo, deleteAccount, isAuthenticated, demoAccounts } = useAuth();
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);
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

  const confirmDeleteAccount = async () => {
    setIsDeleting(true);
    try {
      await deleteAccount();
      setShowDeleteConfirm(false);
    } catch (err) {
      console.error(err);
    } finally {
      setIsDeleting(false);
    }
  };

  const getFirstName = (name?: string | null, username?: string | null, accId?: string | null) => {
    const raw = name || username || accId || 'User';
    return raw.trim().split(' ')[0] || raw;
  };

  return (
    <header className="app-header">
      <div className="header-left">
        <div
          className="logo-group"
          onClick={() => {
            setActiveTab('overview');
            setMobileMenuOpen(false);
          }}
          style={{ cursor: 'pointer' }}
        >
          <img src="/logo.svg" alt="Spendable Logo" className="logo-img" draggable={false} />
          <span className="brand-name">SPENDABLE</span>
        </div>

        {isAuthenticated && (
          <nav className="top-nav desktop-top-nav">
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
                {getFirstName(currentUser.display_name, currentUser.username, currentUser.account_id)}
              </span>
              {currentUser.is_demo_account && (
                <span className="demo-tag">D</span>
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
                    const liveAcc = demoAccounts.find(
                      (d) => d.account_id === p.account_id || d.username === p.username
                    );
                    const displayBalance = liveAcc ? liveAcc.current_balance : p.balance;
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
                        <span className="item-bal">{formatCurrency(displayBalance)}</span>
                      </button>
                    );
                  })}
                </div>

                <div className="dropdown-divider"></div>

                {!currentUser.is_demo_account && (
                  <button
                    className="delete-account-dropdown-item"
                    onClick={() => {
                      setDropdownOpen(false);
                      setShowDeleteConfirm(true);
                    }}
                  >
                    <Trash2 size={14} color="#ef4444" />
                    <span>Delete account</span>
                  </button>
                )}

                <button
                  className="logout-dropdown-item"
                  onClick={() => {
                    setDropdownOpen(false);
                    onOpenLogin();
                  }}
                >
                  <LogOut size={14} />
                  <span>Sign out / Create / Change account</span>
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

        {isAuthenticated && (
          <button
            className="mobile-menu-toggle-btn"
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            aria-label="Toggle navigation menu"
          >
            {mobileMenuOpen ? <CloseIcon size={20} /> : <Menu size={20} />}
          </button>
        )}
      </div>

      {/* Mobile Navigation Drawer Sidebar */}
      {isAuthenticated && mobileMenuOpen && (
        <div className="mobile-drawer-backdrop" onClick={() => setMobileMenuOpen(false)}>
          <div className="mobile-drawer-content" onClick={(e) => e.stopPropagation()}>
            <div className="mobile-drawer-header">
              <div className="logo-group">
                <img src="/logo.svg" alt="Spendable Logo" className="logo-img" />
                <span className="brand-name">SPENDABLE</span>
              </div>
              <button className="modal-close" onClick={() => setMobileMenuOpen(false)}>
                <CloseIcon size={20} />
              </button>
            </div>

            <div className="mobile-user-greeting">
              <User size={16} color="#00e5a3" />
              <span>Logged in as <strong>{getFirstName(currentUser?.display_name, currentUser?.username, currentUser?.account_id)}</strong></span>
            </div>

            <nav className="mobile-drawer-nav">
              <button
                className={`drawer-nav-item ${activeTab === 'overview' ? 'active' : ''}`}
                onClick={() => {
                  setActiveTab('overview');
                  setMobileMenuOpen(false);
                }}
              >
                Overview
              </button>
              <button
                className={`drawer-nav-item ${activeTab === 'activity' ? 'active' : ''}`}
                onClick={() => {
                  setActiveTab('activity');
                  setMobileMenuOpen(false);
                }}
              >
                Financial Activity
              </button>
              <button
                className={`drawer-nav-item ${activeTab === 'forecast' ? 'active' : ''}`}
                onClick={() => {
                  setActiveTab('forecast');
                  setMobileMenuOpen(false);
                }}
              >
                30-Day Forecast
              </button>
              <button
                className={`drawer-nav-item ${activeTab === 'simulate' ? 'active' : ''}`}
                onClick={() => {
                  setActiveTab('simulate');
                  setMobileMenuOpen(false);
                }}
              >
                Scenario Simulator
              </button>
            </nav>
          </div>
        </div>
      )}

      <ConfirmModal
        isOpen={showDeleteConfirm}
        title="Delete Account?"
        message={`Are you sure you want to permanently delete your account (${currentUser?.display_name || currentUser?.username})?\n\nAll database entries and financial records for this account will be erased with no trace.`}
        confirmText="Delete Account"
        cancelText="Keep Account"
        variant="danger"
        isLoading={isDeleting}
        onConfirm={confirmDeleteAccount}
        onCancel={() => setShowDeleteConfirm(false)}
      />
    </header>
  );
};


