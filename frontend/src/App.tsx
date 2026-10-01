import { useEffect, useState } from 'react'
import { Activity, ShieldCheck, Cpu, Database, HelpCircle, Layers, Server } from 'lucide-react'

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

function App() {
  const [health, setHealth] = useState<HealthState | null>(null)
  const [loading, setLoading] = useState<boolean>(true)
  const [error, setError] = useState<string | null>(null)

  const backendUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000'

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
          <div className="logo-icon">S</div>
          <div>
            <div className="brand-name">SPENDABLE</div>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
              AI DEV FEST 2026 Hackathon
            </div>
          </div>
        </div>
        <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
          <span className="badge badge-track">Track 03 — Customer Innovation</span>
          <span className="badge badge-status">Foundation Skeleton Initialized</span>
        </div>
      </header>

      <main>
        <section className="hero">
          <div className="hero-tagline">"Know what you can safely spend."</div>
          <h1>Predictive Personal Liquidity Intelligence</h1>
          <p>
            Your Upay balance tells you how much money you have. Spendable tells you how much of it you can realistically afford to spend.
          </p>

          <div className="question-box">
            <HelpCircle color="#00e5a3" size={24} />
            <div>
              <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>Core Product Inquiry</div>
              <div className="amount">"I have ৳18,400. How much of it is actually safe for me to spend?"</div>
            </div>
          </div>

          <div style={{ fontSize: '0.875rem', color: 'var(--accent-warning)', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Layers size={16} />
            <span>Initial foundation workspace initialized. Domain business logic & ML models will be integrated incrementally.</span>
          </div>
        </section>

        <div className="grid-2">
          <div className="card">
            <div className="card-title">
              <Server size={20} color="#3b82f6" />
              <span>Backend API & DB Connectivity</span>
            </div>

            {loading ? (
              <div style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>Checking backend health...</div>
            ) : error ? (
              <div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem' }}>
                  <span className="status-dot offline"></span>
                  <span style={{ fontWeight: 600 }}>Backend Connection Unreachable</span>
                </div>
                <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
                  Target: <code>{backendUrl}/api/v1/health</code>
                </div>
                <div style={{ fontSize: '0.8rem', color: '#ef4444', marginTop: '0.5rem' }}>
                  Start backend with <code>uvicorn app.main:app --reload</code> or Docker Compose.
                </div>
              </div>
            ) : (
              <div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1rem' }}>
                  <span className={`status-dot ${health?.status === 'healthy' ? 'healthy' : 'degraded'}`}></span>
                  <span style={{ fontWeight: 600, textTransform: 'capitalize' }}>
                    Backend State: {health?.status}
                  </span>
                </div>
                <table className="meta-table">
                  <tbody>
                    <tr>
                      <td>Application</td>
                      <td>{health?.app_name} ({health?.version})</td>
                    </tr>
                    <tr>
                      <td>Environment</td>
                      <td>{health?.environment}</td>
                    </tr>
                    <tr>
                      <td>PostgreSQL Readiness</td>
                      <td>{health?.database.connected ? 'Connected' : 'Ready (Pending Container DB Startup)'}</td>
                    </tr>
                    <tr>
                      <td>AI Integration Target</td>
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
              <span>Architectural Principles</span>
            </div>
            <ul className="principle-list">
              <li className="principle-item">
                <Cpu size={18} color="#00e5a3" style={{ flexShrink: 0, marginTop: '2px' }} />
                <div>
                  <strong>LLM vs Financial Engine Separation:</strong> The LLM never invents financial math. Structured financial engine owns math; LLM provides explanations.
                </div>
              </li>
              <li className="principle-item">
                <Activity size={18} color="#3b82f6" style={{ flexShrink: 0, marginTop: '2px' }} />
                <div>
                  <strong>Critical Data Honesty:</strong> System relies on observable Upay data and clearly distinguishes Observed vs Inferred vs Predicted states.
                </div>
              </li>
              <li className="principle-item">
                <Database size={18} color="#8b5cf6" style={{ flexShrink: 0, marginTop: '2px' }} />
                <div>
                  <strong>Hackathon Adaptability:</strong> Clean, decoupled foundation built to quickly integrate pre-evaluation final-day updates.
                </div>
              </li>
            </ul>
          </div>
        </div>
      </main>

      <footer>
        Spendable • AI DEV FEST 2026 AI Hackathon • DIU-CPC & Upay Ecosystem
      </footer>
    </div>
  )
}

export default App
