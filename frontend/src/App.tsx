import { useEffect, useState } from 'react'
import { Activity, ShieldCheck, Cpu, Database, Server, Mail, Heart, Wallet, ArrowRight } from 'lucide-react'

interface HealthState {
  status: string
  timestamp: string
  app_name: string
  version: string
  environment: string
  database: {
    connected: boolean
    status: string
  }
  services: {
    api: string
    database_readiness: string
    ai_integration: string
  }
}

// Minimal Brand Icon Components
const LinkedInIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M16 8a6 6 0 0 1 6 6v7h-4v-7a2 2 0 0 0-2-2 2 2 0 0 0-2 2v7h-4v-7a6 6 0 0 1 6-6z"/>
    <rect x="2" y="9" width="4" height="12"/>
    <circle cx="4" cy="4" r="2"/>
  </svg>
)

const GitHubIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M15 22v-4a4.8 4.8 0 0 0-1-3.5c3 0 6-2 6-5.5.08-1.25-.27-2.48-1-3.5.28-1.15.28-2.35 0-3.5 0 0-1 0-3 1.5-2.64-.5-5.36-.5-8 0C6 2 5 2 5 2c-.3 1.15-.3 2.35 0 3.5A5.403 5.403 0 0 0 4 9c0 3.5 3 5.5 6 5.5-.39.49-.68 1.05-.85 1.65-.17.6-.22 1.23-.15 1.85v4"/>
    <path d="M9 18c-4.51 2-5-2-7-2"/>
  </svg>
)

function App() {
  const [health, setHealth] = useState<HealthState | null>(null)
  const [loading, setLoading] = useState<boolean>(true)
  const [error, setError] = useState<string | null>(null)
  const [userBalance, setUserBalance] = useState<string>('')

  const backendUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000'
  const currentYear = new Date().getFullYear()

  useEffect(() => {
    fetch(`${backendUrl}/api/v1/health`)
      .then((res) => {
        if (!res.ok) throw new Error(`HTTP ${res.status}`)
        return res.json()
      })
      .then((data) => {
        setHealth(data)
        setLoading(false)
      })
      .catch((err) => {
        setError(err.message)
        setLoading(false)
      })
  }, [backendUrl])

  return (
    <div className="container">
      <header>
        <div className="logo-group">
          <img src="/logo.svg" alt="Spendable Logo" className="logo-img" />
          <div>
            <div className="brand-name">SPENDABLE</div>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
              Personal Liquidity Intelligence Platform
            </div>
          </div>
        </div>
      </header>

      <main>
        <section className="hero">
          <div className="hero-tagline">"Know what you can safely spend."</div>
          <h1>Predictive Personal Liquidity Intelligence</h1>
          <p>
            Your account balance tells you how much money you have. Spendable tells you how much of it you can realistically afford to spend after upcoming commitments and expected outflows.
          </p>

          <div className="interactive-calculator">
            <div className="calc-header">
              <Wallet color="#00e5a3" size={20} />
              <span>Simulate Account Runway</span>
            </div>
            <div className="calc-input-row">
              <div className="input-wrapper">
                <span className="currency-symbol">৳</span>
                <input
                  type="number"
                  className="balance-input"
                  placeholder="Enter observable balance..."
                  value={userBalance}
                  onChange={(e) => setUserBalance(e.target.value)}
                />
              </div>
              <button className="calc-btn" onClick={() => {}}>
                <span>Analyze Runway</span>
                <ArrowRight size={16} />
              </button>
            </div>
            {userBalance && (
              <div className="calc-preview-msg">
                Estimated observable input: <strong>৳{Number(userBalance).toLocaleString()}</strong>.
              </div>
            )}
          </div>
        </section>

        <div className="grid-2">
          <div className="card">
            <div className="card-title">
              <Server size={20} color="#3b82f6" />
              <span>System Health & API Connectivity</span>
            </div>

            {loading ? (
              <div style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>Connecting to backend service...</div>
            ) : error ? (
              <div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem' }}>
                  <span className="status-dot offline"></span>
                  <span style={{ fontWeight: 600 }}>Backend Service Offline</span>
                </div>
                <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
                  Target Endpoint: <code>{backendUrl}/api/v1/health</code>
                </div>
                <div style={{ fontSize: '0.8rem', color: '#ef4444', marginTop: '0.5rem' }}>
                  Start backend using <code>pnpm run dev</code> or Docker Compose.
                </div>
              </div>
            ) : (
              <div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1rem' }}>
                  <span className={`status-dot ${health?.status === 'healthy' ? 'healthy' : 'degraded'}`}></span>
                  <span style={{ fontWeight: 600, textTransform: 'capitalize' }}>
                    System Status: {health?.status}
                  </span>
                </div>
                <table className="meta-table">
                  <tbody>
                    <tr>
                      <td>Application Engine</td>
                      <td>{health?.app_name} ({health?.version})</td>
                    </tr>
                    <tr>
                      <td>Environment</td>
                      <td>{health?.environment}</td>
                    </tr>
                    <tr>
                      <td>Database Readiness</td>
                      <td>{health?.database.connected ? 'Connected' : 'Ready'}</td>
                    </tr>
                    <tr>
                      <td>AI Engine Readiness</td>
                      <td>{health?.services.ai_integration}</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            )}
          </div>

          <div className="card">
            <div className="card-title">
              <ShieldCheck size={20} color="#00e5a3" />
              <span>Core Architectural Guarantees</span>
            </div>
            <ul className="principle-list">
              <li className="principle-item">
                <Cpu size={18} color="#00e5a3" style={{ flexShrink: 0, marginTop: '2px' }} />
                <div>
                  <strong>Engine vs LLM Separation:</strong> Deterministic calculations are handled by the analytical engine; LLM provides natural language insights.
                </div>
              </li>
              <li className="principle-item">
                <Activity size={18} color="#3b82f6" style={{ flexShrink: 0, marginTop: '2px' }} />
                <div>
                  <strong>Data Transparency:</strong> Distinguishes verified Observed account facts from Inferred patterns and Predicted projections.
                </div>
              </li>
              <li className="principle-item">
                <Database size={18} color="#8b5cf6" style={{ flexShrink: 0, marginTop: '2px' }} />
                <div>
                  <strong>Clean Extensibility:</strong> Modular codebase designed for high-performance iteration and easy deployment.
                </div>
              </li>
            </ul>
          </div>
        </div>
      </main>

      <footer className="site-footer">
        <div className="footer-content">
          <div className="footer-brand">
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', justifyContent: 'center' }}>
              <img src="/logo.svg" alt="Spendable Logo" className="footer-logo-img" />
              <span className="footer-title">Spendable</span>
            </div>
            <span className="footer-tag">Predictive Liquidity Intelligence</span>
          </div>

          <div className="footer-links">
            <a href="mailto:contact@supanroy.com" className="footer-link" target="_blank" rel="noopener noreferrer">
              <Mail size={16} />
              <span>contact@supanroy.com</span>
            </a>
            <a href="https://linkedin.com/in/supanroy" className="footer-link" target="_blank" rel="noopener noreferrer">
              <LinkedInIcon />
              <span>linkedin.com/in/supanroy</span>
            </a>
            <a href="https://github.com/Supan-Roy" className="footer-link" target="_blank" rel="noopener noreferrer">
              <GitHubIcon />
              <span>github.com/Supan-Roy</span>
            </a>
          </div>

          <div className="footer-copyright">
            © {currentYear} Spendable. Crafted with <Heart size={14} color="#00e5a3" style={{ display: 'inline', margin: '0 2px' }} /> by <strong>Supan Roy</strong>. All rights reserved.
          </div>
        </div>
      </footer>
    </div>
  )
}

export default App
