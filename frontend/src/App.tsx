import { useState } from 'react'
import { TrendingUp, Receipt, Sliders, HelpCircle, ArrowRight, Shield, Info, X } from 'lucide-react'

type TabType = 'overview' | 'activity' | 'forecast' | 'simulate'

function App() {
  const [activeTab, setActiveTab] = useState<TabType>('overview')
  const [showCalculationInfo, setShowCalculationInfo] = useState<boolean>(false)

  const currentYear = new Date().getFullYear()

  return (
    <div className="container">
      {/* Top Application Header */}
      <header className="app-header">
        <div className="header-left">
          <div className="logo-group">
            <img src="/logo.svg" alt="Spendable Logo" className="logo-img" draggable={false} />
            <span className="brand-name">SPENDABLE</span>
          </div>

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
        </div>

        <div className="header-right">
          <span className="account-badge">
            <span className="badge-dot"></span>
            Account Not Connected
          </span>
        </div>
      </header>

      {/* Main Product Application Shell */}
      <main className="main-content">
        {activeTab === 'overview' && (
          <div className="tab-pane">
            <div className="welcome-banner">
              <div>
                <h2>Good evening</h2>
                <p className="subtitle">Know what you can safely spend.</p>
              </div>
            </div>

            {/* Central Spendable Amount Card */}
            <section className="spendable-hero-card">
              <div className="spendable-card-header">
                <span className="card-label">YOU CAN SAFELY SPEND</span>
                <button
                  className="info-trigger-btn"
                  onClick={() => setShowCalculationInfo(true)}
                  title="How is this calculated?"
                >
                  <HelpCircle size={16} />
                  <span>How is this calculated?</span>
                </button>
              </div>

              <div className="spendable-value-display">
                <span className="currency-symbol">৳</span>
                <span className="empty-value">—</span>
              </div>

              <div className="spendable-status-bar">
                <span className="status-indicator"></span>
                <span>Waiting for financial activity</span>
              </div>
            </section>

            {/* Financial Summary Grid (4 Visual Slots) */}
            <section className="summary-grid">
              <div className="summary-card">
                <div className="summary-label">Current Balance</div>
                <div className="summary-value">—</div>
                <div className="summary-hint">Observable wallet total</div>
              </div>

              <div className="summary-card">
                <div className="summary-label">Upcoming Outflows</div>
                <div className="summary-value">—</div>
                <div className="summary-hint">Detected commitments</div>
              </div>

              <div className="summary-card">
                <div className="summary-label">Expected Inflows</div>
                <div className="summary-value">—</div>
                <div className="summary-hint">Projected short-term income</div>
              </div>

              <div className="summary-card">
                <div className="summary-label">Safety Buffer</div>
                <div className="summary-value">—</div>
                <div className="summary-hint">Protected reserve cushion</div>
              </div>
            </section>

            {/* Forecast Section Slot */}
            <section className="product-section">
              <div className="section-header">
                <h3>Cash-Flow Forecast</h3>
                <button className="view-more-btn" onClick={() => setActiveTab('forecast')}>
                  <span>View Forecast</span>
                  <ArrowRight size={14} />
                </button>
              </div>
              <div className="empty-state-card">
                <TrendingUp size={36} className="empty-icon" />
                <h4>Liquidity Forecast Unavailable</h4>
                <p>Connect or import financial activity to calculate short-term and 30-day cash flow projections.</p>
              </div>
            </section>

            {/* Scenario Simulator Entry Banner */}
            <section className="simulate-banner">
              <div className="banner-content">
                <div className="banner-icon-wrapper">
                  <Sliders size={24} color="#00e5a3" />
                </div>
                <div>
                  <h4>What-If Scenario Explorer</h4>
                  <p>Explore how a potential expense or purchase affects your safe spending runway.</p>
                </div>
              </div>
              <button className="secondary-btn" onClick={() => setActiveTab('simulate')}>
                <span>Explore Scenarios</span>
                <ArrowRight size={16} />
              </button>
            </section>
          </div>
        )}

        {activeTab === 'activity' && (
          <div className="tab-pane">
            <div className="page-header">
              <h2>Financial Activity</h2>
              <p className="subtitle">Observable account inflows, payments, and commitments.</p>
            </div>
            <div className="empty-state-card full-page-empty">
              <Receipt size={44} className="empty-icon" />
              <h3>No Activity Recorded Yet</h3>
              <p>Import your account activity to calculate your safe spending liquidity.</p>
            </div>
          </div>
        )}

        {activeTab === 'forecast' && (
          <div className="tab-pane">
            <div className="page-header">
              <h2>Cash-Flow Forecast</h2>
              <p className="subtitle">Projected balance trajectories and liquidity pressure analysis.</p>
            </div>
            <div className="empty-state-card full-page-empty">
              <TrendingUp size={44} className="empty-icon" />
              <h3>Forecast Unavailable</h3>
              <p>Your financial activity data is required to generate short-term and 30-day liquidity forecasts.</p>
            </div>
          </div>
        )}

        {activeTab === 'simulate' && (
          <div className="tab-pane">
            <div className="page-header">
              <h2>Scenario Simulator</h2>
              <p className="subtitle">What happens if I spend more?</p>
            </div>
            <div className="empty-state-card full-page-empty">
              <Sliders size={44} className="empty-icon" />
              <h3>Simulation Engine Standby</h3>
              <p>Scenario modeling will allow you to test what-if expenses against your projected liquidity runway once financial activity is available.</p>
            </div>
          </div>
        )}
      </main>

      {/* Calculation Explanation Modal */}
      {showCalculationInfo && (
        <div className="modal-overlay" onClick={() => setShowCalculationInfo(false)}>
          <div className="modal-card" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <Shield size={20} color="#00e5a3" />
                <h3>How Spendable Is Calculated</h3>
              </div>
              <button className="modal-close" onClick={() => setShowCalculationInfo(false)}>
                <X size={18} />
              </button>
            </div>
            <div className="modal-body">
              <p>
                Spendable calculates how much money you can safely spend without risking upcoming financial pressure.
              </p>
              <div className="calc-formula-box">
                <div className="formula-row">+ Current Observable Balance</div>
                <div className="formula-row">+ Expected Short-Term Inflows</div>
                <div className="formula-row minus">- Upcoming Commitments & Bills</div>
                <div className="formula-row minus">- Expected Essential Outflows</div>
                <div className="formula-row minus">- Protected Safety Buffer</div>
                <div className="formula-result">= Estimated Safe Spendable Amount</div>
              </div>
              <div className="data-honesty-note">
                <Info size={16} style={{ flexShrink: 0, marginTop: '2px' }} />
                <span>Spendable estimates are based exclusively on observable financial activity. Unrecorded cash or external bank accounts are not included.</span>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Clean Product Footer */}
      <footer className="product-footer">
        <div className="footer-container">
          <div className="footer-left">
            <img src="/logo.svg" alt="Spendable Logo" className="footer-logo-img" draggable={false} />
            <span className="footer-brand-text">Spendable</span>
            <span className="footer-divider">•</span>
            <span className="footer-tagline">Personal Liquidity Intelligence</span>
          </div>
          <div className="footer-right">
            © {currentYear} Spendable. All rights reserved.
          </div>
        </div>
      </footer>
    </div>
  )
}

export default App
