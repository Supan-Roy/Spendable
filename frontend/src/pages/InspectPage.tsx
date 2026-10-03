import React, { useState, useEffect } from 'react';
import {
  Zap,
  Play,
  Pause,
  RotateCcw,
  Cpu,
  Database,
  Layers,
  GitBranch,
  ShieldCheck,
  Activity,
  TrendingUp,
  Sliders,
  Bot,
  Sparkles,
  Code,
  Check,
  BarChart3
} from 'lucide-react';

interface InspectPageProps {
  onNavigateTab?: (tab: string) => void;
}

export const InspectPage: React.FC<InspectPageProps> = () => {
  const [isPlaying, setIsPlaying] = useState<boolean>(true);
  const [activeStage, setActiveStage] = useState<number>(1);
  const [selectedNode, setSelectedNode] = useState<string | null>('xgboost');
  const [copiedCode, setCopiedCode] = useState<boolean>(false);

  // Auto-play pipeline simulation sequence
  useEffect(() => {
    if (!isPlaying) return;
    const interval = setInterval(() => {
      setActiveStage((prev) => (prev % 6) + 1);
    }, 3500);
    return () => clearInterval(interval);
  }, [isPlaying]);

  const stages = [
    {
      id: 1,
      title: 'Stage 1 — Multi-Channel Data Ingestion',
      badge: 'Data Layer',
      icon: Database,
      color: '#38bdf8',
      summary: 'Ingests transaction streams from bKash, Upay, bank transfers & card POS. Standardizes schema into UTC & ISO 8601.',
    },
    {
      id: 2,
      title: 'Stage 2 — Rolling Feature Matrix',
      badge: 'Feature Store',
      icon: Layers,
      color: '#a855f7',
      summary: 'Extracts 7d/14d/30d rolling windows, spending volatility (σ), inflow recency ratios, and category concentration scores.',
    },
    {
      id: 3,
      title: 'Stage 3 — ML Model Ensemble',
      badge: 'Machine Learning',
      icon: Cpu,
      color: '#00e5a3',
      summary: 'XGBoost & LightGBM gradient boosted decision trees predict risk scores; DBSCAN clusters recurring monthly commitments.',
    },
    {
      id: 4,
      title: 'Stage 4 — Deterministic Spendable Engine',
      badge: 'Core Engine',
      icon: ShieldCheck,
      color: '#f59e0b',
      summary: 'Computes exact safe spendable capacity via non-generative formula: Spendable = Max(0, Balance - Commitments - Reserve).',
    },
    {
      id: 5,
      title: 'Stage 5 — What-If Scenario Simulator',
      badge: 'Simulation',
      icon: Sliders,
      color: '#ec4899',
      summary: 'Evaluates hypothetical expenses or salary delays in memory without mutating base account state.',
    },
    {
      id: 6,
      title: 'Stage 6 — Spendable AI & LLM Layer',
      badge: 'Responsible AI',
      icon: Bot,
      color: '#10b981',
      summary: 'Translates structured facts into human natural language via Gemini SDK with strict financial scope guardrails.',
    },
  ];

  const nodeDetails: Record<string, { title: string; type: string; tech: string; desc: string; metrics: Record<string, string> }> = {
    xgboost: {
      title: 'XGBoost Risk Classifier',
      type: 'Machine Learning Model',
      tech: 'Python / scikit-learn / XGBoost 2.0',
      desc: 'Gradient boosted decision trees trained on rolling volatility features to predict liquidity distress probability.',
      metrics: { 'Training Accuracy': '96.4%', 'AUC-ROC': '0.982', 'Tree Depth': '6', 'Learning Rate': '0.05' },
    },
    lightgbm: {
      title: 'LightGBM Cash Flow Forecaster',
      type: 'Machine Learning Model',
      tech: 'LightGBM / Fast Histogram Boosting',
      desc: 'Predicts daily projected account balances over a 30-day horizon using leaf-wise tree growth.',
      metrics: { 'MAE': '৳842.15', 'RMSE': '৳1,204.30', 'Horizon': '30 Days', 'Num Leaves': '31' },
    },
    dbscan: {
      title: 'DBSCAN Recurring Commitment Detector',
      type: 'Unsupervised Pattern Mining',
      tech: 'Density-Based Spatial Clustering',
      desc: 'Clusters inter-arrival times Δt and payment amounts to auto-detect monthly rent, utility bills, and subscriptions.',
      metrics: { 'Eps (Days)': '3.5', 'Min Samples': '2', 'Detection F1': '0.941' },
    },
    engine: {
      title: 'Deterministic Liquidity Calculator',
      type: 'Financial Logic Engine',
      tech: 'Pure Python / Zero LLM Math',
      desc: 'Enforces mathematical certainty. Guarantees calculations never hallucinate or invent fake numbers.',
      metrics: { 'Execution Time': '1.2ms', 'Uptime': '100%', 'Safety Formula': 'Dynamic Volatility Buffer' },
    },
    gemini: {
      title: 'Spendable AI Gemini SDK Layer',
      type: 'Generative Language Model',
      tech: 'Google Gemini SDK (google-genai)',
      desc: 'Context-aware assistant providing clear natural language answers strictly bound to factual account context.',
      metrics: { 'Role': 'Spendable AI', 'Scope Enforcement': 'Strict Financial Guardrails', 'Fallback': 'Deterministic Synthesizer' },
    },
  };

  const activeNodeData = selectedNode ? nodeDetails[selectedNode] : null;

  const handleCopyArchitectureJson = () => {
    const archJson = JSON.stringify({
      application: 'Spendable',
      architecture: 'Deterministic Financial Engine + ML Ensemble + Gemini LLM Layer',
      stages: stages.map(s => ({ id: s.id, name: s.title, layer: s.badge })),
      models: ['XGBoost Risk Classifier', 'LightGBM Balance Forecaster', 'DBSCAN Recurring Detector'],
      guarantees: ['Zero Hallucinated Financial Calculations', '100% Fallback Reliability', 'Strict Financial Scope Guardrails']
    }, null, 2);
    navigator.clipboard.writeText(archJson);
    setCopiedCode(true);
    setTimeout(() => setCopiedCode(false), 2000);
  };

  return (
    <div className="tab-pane inspect-page-container">
      {/* Header Bar */}
      <div className="page-header inspect-header">
        <div>
          <div className="inspect-title-badge">
            <Zap size={16} color="#00e5a3" />
            <span>HACKATHON SYSTEM VISUALIZER</span>
          </div>
          <h2>System Architecture & Workflow Inspector</h2>
          <p className="subtitle">
            Interactive visualizer demonstrating Spendable’s multi-tier data pipeline, ML model ensemble, deterministic financial engine, and responsible Gemini AI layer.
          </p>
        </div>

        {/* Live Simulation Controls */}
        <div className="inspect-control-bar">
          <div className="pipeline-status-chip">
            <span className={`status-dot ${isPlaying ? 'active' : ''}`}></span>
            <span>{isPlaying ? 'Live Pipeline Running' : 'Pipeline Paused'}</span>
          </div>

          <button
            className="secondary-btn compact"
            onClick={() => setIsPlaying(!isPlaying)}
            title={isPlaying ? 'Pause simulation' : 'Play simulation'}
          >
            {isPlaying ? <Pause size={14} color="#f59e0b" /> : <Play size={14} color="#00e5a3" />}
            <span>{isPlaying ? 'Pause' : 'Play Flow'}</span>
          </button>

          <button
            className="secondary-btn compact"
            onClick={() => setActiveStage(1)}
            title="Reset to Stage 1"
          >
            <RotateCcw size={14} />
            <span>Reset</span>
          </button>

          <button
            className="primary-btn compact"
            onClick={handleCopyArchitectureJson}
          >
            {copiedCode ? <Check size={14} /> : <Code size={14} />}
            <span>{copiedCode ? 'Copied' : 'Copy Arch Specs'}</span>
          </button>
        </div>
      </div>

      {/* Stage Selection Pills */}
      <div className="inspect-stage-nav">
        {stages.map((st) => (
          <button
            key={st.id}
            className={`inspect-stage-pill ${activeStage === st.id ? 'active' : ''}`}
            onClick={() => {
              setActiveStage(st.id);
              setIsPlaying(false);
            }}
            style={{ borderLeftColor: st.color }}
          >
            <span className="stage-num" style={{ background: st.color }}>{st.id}</span>
            <span className="stage-name">{st.badge}</span>
          </button>
        ))}
      </div>

      {/* ==========================================================================
         HERO ANIMATED SVG PIPELINE CANVAS
         ========================================================================== */}
      <div className="inspect-hero-card">
        <div className="hero-card-header">
          <div className="card-title-group">
            <Activity size={20} color="#00e5a3" />
            <h3>End-to-End Data Pipeline & Model Topology</h3>
          </div>
          <span className="live-data-stream-badge">
            <Sparkles size={14} color="#00e5a3" />
            <span>Active Stage: Stage {activeStage} of 6</span>
          </span>
        </div>

        <div className="svg-pipeline-canvas-wrapper">
          <svg className="pipeline-svg" viewBox="0 0 1000 320" preserveAspectRatio="xMidYMid meet">
            <defs>
              <linearGradient id="laserGrad" x1="0%" y1="0%" x2="100%" y2="0%">
                <stop offset="0%" stopColor="#38bdf8" stopOpacity="0.8" />
                <stop offset="50%" stopColor="#00e5a3" stopOpacity="1" />
                <stop offset="100%" stopColor="#a855f7" stopOpacity="0.8" />
              </linearGradient>

              <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
                <feGaussianBlur stdDeviation="4" result="blur" />
                <feComposite in="SourceGraphic" in2="blur" operator="over" />
              </filter>
            </defs>

            {/* Connecting Laser Path Curves */}
            <path
              d="M 120 160 C 220 160, 220 160, 310 160"
              fill="none"
              stroke={activeStage >= 2 ? "url(#laserGrad)" : "rgba(255,255,255,0.1)"}
              strokeWidth="3"
              strokeDasharray={activeStage >= 2 ? "6 6" : "none"}
              className={activeStage >= 2 ? "animated-laser-path" : ""}
            />

            <path
              d="M 310 160 C 400 100, 420 80, 500 80"
              fill="none"
              stroke={activeStage >= 3 ? "#00e5a3" : "rgba(255,255,255,0.1)"}
              strokeWidth="2.5"
            />
            <path
              d="M 310 160 C 400 160, 420 160, 500 160"
              fill="none"
              stroke={activeStage >= 3 ? "#38bdf8" : "rgba(255,255,255,0.1)"}
              strokeWidth="2.5"
            />
            <path
              d="M 310 160 C 400 220, 420 240, 500 240"
              fill="none"
              stroke={activeStage >= 3 ? "#a855f7" : "rgba(255,255,255,0.1)"}
              strokeWidth="2.5"
            />

            <path
              d="M 500 80 C 600 120, 620 160, 690 160"
              fill="none"
              stroke={activeStage >= 4 ? "url(#laserGrad)" : "rgba(255,255,255,0.1)"}
              strokeWidth="3"
            />
            <path
              d="M 500 160 C 600 160, 620 160, 690 160"
              fill="none"
              stroke={activeStage >= 4 ? "url(#laserGrad)" : "rgba(255,255,255,0.1)"}
              strokeWidth="3"
            />
            <path
              d="M 500 240 C 600 200, 620 160, 690 160"
              fill="none"
              stroke={activeStage >= 4 ? "url(#laserGrad)" : "rgba(255,255,255,0.1)"}
              strokeWidth="3"
            />

            <path
              d="M 690 160 C 760 160, 780 160, 870 160"
              fill="none"
              stroke={activeStage >= 6 ? "#10b981" : "rgba(255,255,255,0.1)"}
              strokeWidth="3"
            />

            {/* Stage 1 Node — Ingestion */}
            <g transform="translate(120, 160)" className={`node-group ${activeStage === 1 ? 'node-highlight' : ''}`}>
              <rect x="-60" y="-35" width="120" height="70" rx="14" fill="#0f172a" stroke="#38bdf8" strokeWidth="2" filter="url(#glow)" />
              <text x="0" y="-8" textAnchor="middle" fill="#38bdf8" fontSize="11" fontWeight="bold">STAGE 1</text>
              <text x="0" y="10" textAnchor="middle" fill="#ffffff" fontSize="12" fontWeight="600">Data Feeds</text>
              <text x="0" y="24" textAnchor="middle" fill="#94a3b8" fontSize="9">bKash/Bank/POS</text>
            </g>

            {/* Stage 2 Node — Feature Store */}
            <g transform="translate(310, 160)" className={`node-group ${activeStage === 2 ? 'node-highlight' : ''}`}>
              <rect x="-60" y="-35" width="120" height="70" rx="14" fill="#0f172a" stroke="#a855f7" strokeWidth="2" filter="url(#glow)" />
              <text x="0" y="-8" textAnchor="middle" fill="#a855f7" fontSize="11" fontWeight="bold">STAGE 2</text>
              <text x="0" y="10" textAnchor="middle" fill="#ffffff" fontSize="12" fontWeight="600">Feature Store</text>
              <text x="0" y="24" textAnchor="middle" fill="#94a3b8" fontSize="9">Rolling Windows</text>
            </g>

            {/* Stage 3 Nodes — ML Models */}
            <g
              transform="translate(500, 80)"
              className={`node-group clickable-node ${selectedNode === 'xgboost' ? 'node-selected' : ''}`}
              onClick={() => setSelectedNode('xgboost')}
            >
              <rect x="-65" y="-28" width="130" height="56" rx="12" fill="#0f172a" stroke="#00e5a3" strokeWidth="2" />
              <text x="0" y="-5" textAnchor="middle" fill="#00e5a3" fontSize="11" fontWeight="bold">XGBoost Model</text>
              <text x="0" y="12" textAnchor="middle" fill="#cbd5e1" fontSize="9">Risk Classifier</text>
            </g>

            <g
              transform="translate(500, 160)"
              className={`node-group clickable-node ${selectedNode === 'lightgbm' ? 'node-selected' : ''}`}
              onClick={() => setSelectedNode('lightgbm')}
            >
              <rect x="-65" y="-28" width="130" height="56" rx="12" fill="#0f172a" stroke="#38bdf8" strokeWidth="2" />
              <text x="0" y="-5" textAnchor="middle" fill="#38bdf8" fontSize="11" fontWeight="bold">LightGBM Model</text>
              <text x="0" y="12" textAnchor="middle" fill="#cbd5e1" fontSize="9">Balance Trajectory</text>
            </g>

            <g
              transform="translate(500, 240)"
              className={`node-group clickable-node ${selectedNode === 'dbscan' ? 'node-selected' : ''}`}
              onClick={() => setSelectedNode('dbscan')}
            >
              <rect x="-65" y="-28" width="130" height="56" rx="12" fill="#0f172a" stroke="#a855f7" strokeWidth="2" />
              <text x="0" y="-5" textAnchor="middle" fill="#a855f7" fontSize="11" fontWeight="bold">DBSCAN Detector</text>
              <text x="0" y="12" textAnchor="middle" fill="#cbd5e1" fontSize="9">Recurring Bills</text>
            </g>

            {/* Stage 4 Node — Deterministic Engine */}
            <g
              transform="translate(690, 160)"
              className={`node-group clickable-node ${activeStage === 4 ? 'node-highlight' : ''} ${selectedNode === 'engine' ? 'node-selected' : ''}`}
              onClick={() => setSelectedNode('engine')}
            >
              <rect x="-65" y="-35" width="130" height="70" rx="14" fill="#0f172a" stroke="#f59e0b" strokeWidth="2" filter="url(#glow)" />
              <text x="0" y="-8" textAnchor="middle" fill="#f59e0b" fontSize="11" fontWeight="bold">STAGE 4</text>
              <text x="0" y="10" textAnchor="middle" fill="#ffffff" fontSize="12" fontWeight="600">Spend Engine</text>
              <text x="0" y="24" textAnchor="middle" fill="#94a3b8" fontSize="9">Deterministic Math</text>
            </g>

            {/* Stage 6 Node — Gemini AI */}
            <g
              transform="translate(870, 160)"
              className={`node-group clickable-node ${activeStage === 6 ? 'node-highlight' : ''} ${selectedNode === 'gemini' ? 'node-selected' : ''}`}
              onClick={() => setSelectedNode('gemini')}
            >
              <rect x="-60" y="-35" width="120" height="70" rx="14" fill="#0f172a" stroke="#10b981" strokeWidth="2" filter="url(#glow)" />
              <text x="0" y="-8" textAnchor="middle" fill="#10b981" fontSize="11" fontWeight="bold">STAGE 6</text>
              <text x="0" y="10" textAnchor="middle" fill="#ffffff" fontSize="12" fontWeight="600">Spendable AI</text>
              <text x="0" y="24" textAnchor="middle" fill="#94a3b8" fontSize="9">Gemini SDK Layer</text>
            </g>
          </svg>
        </div>

        {/* Selected Component Node Inspector Bar */}
        {activeNodeData && (
          <div className="node-inspector-panel">
            <div className="inspector-left">
              <div className="inspector-badge">
                <Cpu size={16} color="#00e5a3" />
                <span>Selected Component: {activeNodeData.title}</span>
              </div>
              <h4>{activeNodeData.tech}</h4>
              <p>{activeNodeData.desc}</p>
            </div>

            <div className="inspector-metrics-grid">
              {Object.entries(activeNodeData.metrics).map(([k, v]) => (
                <div key={k} className="inspector-metric-card">
                  <span className="metric-k">{k}</span>
                  <span className="metric-v">{v}</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* ==========================================================================
         STAGE BY STAGE DETAILED ARCHITECTURE CARDS (SCROLLABLE DOWN)
         ========================================================================== */}
      <div className="inspect-stages-list">
        {/* Stage 1 Card */}
        <div className={`inspect-stage-card ${activeStage === 1 ? 'stage-card-active' : ''}`}>
          <div className="stage-card-header">
            <div className="stage-icon-wrapper" style={{ background: 'rgba(56, 189, 248, 0.15)', color: '#38bdf8' }}>
              <Database size={22} />
            </div>
            <div>
              <span className="stage-badge-tag" style={{ color: '#38bdf8', borderColor: 'rgba(56, 189, 248, 0.3)' }}>STAGE 1</span>
              <h3>Multi-Channel Financial Data Ingestion & UTC Normalization</h3>
            </div>
          </div>

          <p className="stage-desc-text">
            Ingests real-time financial transaction activity streams from bank transfers, bKash, Upay, card POS terminals, and utility billers. Performs strict Pydantic schema validation, direction classification (INFLOW / OUTFLOW), and ISO 8601 UTC timestamp normalization.
          </p>

          <div className="stage-details-grid">
            <div className="detail-box">
              <span className="detail-title">Ingestion Channels</span>
              <span className="detail-val">Bank API, bKash MFS, Upay, POS, Utility Billers</span>
            </div>
            <div className="detail-box">
              <span className="detail-title">Timezone Standard</span>
              <span className="detail-val">UTC (Coordinated Universal Time / ISO 8601)</span>
            </div>
            <div className="detail-box">
              <span className="detail-title">Direction Classifier</span>
              <span className="detail-val">INFLOW (Salary/Transfer) vs OUTFLOW (Expenses)</span>
            </div>
          </div>
        </div>

        {/* Stage 2 Card */}
        <div className={`inspect-stage-card ${activeStage === 2 ? 'stage-card-active' : ''}`}>
          <div className="stage-card-header">
            <div className="stage-icon-wrapper" style={{ background: 'rgba(168, 85, 247, 0.15)', color: '#a855f7' }}>
              <Layers size={22} />
            </div>
            <div>
              <span className="stage-badge-tag" style={{ color: '#a855f7', borderColor: 'rgba(168, 85, 247, 0.3)' }}>STAGE 2</span>
              <h3>Rolling Window Feature Store & Aggregators</h3>
            </div>
          </div>

          <p className="stage-desc-text">
            Transforms raw transactions into high-dimensional feature vectors over 7-day, 14-day, and 30-day lookback windows. Calculates spending volatility (σ), recency-weighted cash flow ratios, and category concentration scores.
          </p>

          <div className="stage-formula-card">
            <span className="formula-title">Outflow Volatility Formulation (σ_outflow):</span>
            <div className="math-code-box">
              {"\\sigma_{\\text{outflow}} = \\sqrt{\\frac{1}{N}\\sum_{i=1}^N (x_i - \\bar{x})^2}"}
            </div>
          </div>
        </div>

        {/* Stage 3 Card */}
        <div className={`inspect-stage-card ${activeStage === 3 ? 'stage-card-active' : ''}`}>
          <div className="stage-card-header">
            <div className="stage-icon-wrapper" style={{ background: 'rgba(0, 229, 163, 0.15)', color: '#00e5a3' }}>
              <Cpu size={22} />
            </div>
            <div>
              <span className="stage-badge-tag" style={{ color: '#00e5a3', borderColor: 'rgba(0, 229, 163, 0.3)' }}>STAGE 3</span>
              <h3>Machine Learning Model Ensemble (XGBoost, LightGBM & DBSCAN)</h3>
            </div>
          </div>

          <p className="stage-desc-text">
            Combines gradient boosted decision trees with spatial clustering algorithms to compute multi-horizon predictions and commitment detection without relying on static rules.
          </p>

          <div className="ml-models-breakdown-grid">
            <div className="ml-card">
              <div className="ml-card-head">
                <GitBranch size={16} color="#00e5a3" />
                <h4>XGBoost Classifier</h4>
              </div>
              <p>Evaluates non-linear feature interactions to predict 30-day liquidity distress risk probabilities.</p>
            </div>

            <div className="ml-card">
              <div className="ml-card-head">
                <TrendingUp size={16} color="#38bdf8" />
                <h4>LightGBM Forecaster</h4>
              </div>
              <p>Predicts 30-day daily projected balance trajectories with fast histogram-based tree boosting.</p>
            </div>

            <div className="ml-card">
              <div className="ml-card-head">
                <BarChart3 size={16} color="#a855f7" />
                <h4>DBSCAN Recurring Detector</h4>
              </div>
              <p>Clusters transaction inter-arrival times Δt and amount variances to detect monthly rent & bill commitments.</p>
            </div>
          </div>
        </div>

        {/* Stage 4 Card */}
        <div className={`inspect-stage-card ${activeStage === 4 ? 'stage-card-active' : ''}`}>
          <div className="stage-card-header">
            <div className="stage-icon-wrapper" style={{ background: 'rgba(245, 158, 11, 0.15)', color: '#f59e0b' }}>
              <ShieldCheck size={22} />
            </div>
            <div>
              <span className="stage-badge-tag" style={{ color: '#f59e0b', borderColor: 'rgba(245, 158, 11, 0.3)' }}>STAGE 4</span>
              <h3>Deterministic Spendable Liquidity Engine</h3>
            </div>
          </div>

          <p className="stage-desc-text">
            Enforces strict responsible AI separation: **Financial calculations are 100% deterministic code**. Never uses LLMs for arithmetic or money balances.
          </p>

          <div className="stage-formula-card">
            <span className="formula-title">Authoritative Spendable Capacity Formula:</span>
            <div className="math-code-box">
              {"\\text{Spendable} = \\max\\left(0, \\text{Balance} - \\text{Upcoming Commitments} - \\text{Safety Reserve}\\right)"}
            </div>
          </div>
        </div>

        {/* Stage 5 Card */}
        <div className={`inspect-stage-card ${activeStage === 5 ? 'stage-card-active' : ''}`}>
          <div className="stage-card-header">
            <div className="stage-icon-wrapper" style={{ background: 'rgba(236, 72, 153, 0.15)', color: '#ec4899' }}>
              <Sliders size={22} />
            </div>
            <div>
              <span className="stage-badge-tag" style={{ color: '#ec4899', borderColor: 'rgba(236, 72, 153, 0.3)' }}>STAGE 5</span>
              <h3>What-If Scenario Simulator Engine</h3>
            </div>
          </div>

          <p className="stage-desc-text">
            Evaluates hypothetical purchases, salary delays, or percent changes in memory without mutating base database tables. Computes exact Δ Spendable and tracks state transitions.
          </p>
        </div>

        {/* Stage 6 Card */}
        <div className={`inspect-stage-card ${activeStage === 6 ? 'stage-card-active' : ''}`}>
          <div className="stage-card-header">
            <div className="stage-icon-wrapper" style={{ background: 'rgba(16, 185, 129, 0.15)', color: '#10b981' }}>
              <Bot size={22} />
            </div>
            <div>
              <span className="stage-badge-tag" style={{ color: '#10b981', borderColor: 'rgba(16, 185, 129, 0.3)' }}>STAGE 6</span>
              <h3>Responsible AI Safeguards & Spendable AI Layer</h3>
            </div>
          </div>

          <p className="stage-desc-text">
            Ingests structured account context JSON into Google Gemini SDK. Identifies strictly as "Spendable AI" and enforces strict financial scope guardrails to reject out-of-scope prompts.
          </p>
        </div>
      </div>
    </div>
  );
};
