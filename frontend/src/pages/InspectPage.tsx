import React from 'react';
import {
  Database,
  Layers,
  Cpu,
  ShieldCheck,
  Sliders,
  Bot,
  TrendingUp,
  Activity,
  BarChart3,
  GitBranch,
  Lock,
  CheckCircle2,
  ArrowRight,
  Eye,
  Zap,
  Calendar,
  DollarSign
} from 'lucide-react';

export const InspectPage: React.FC = () => {
  return (
    <div className="inspect-page-container">
      {/* 1. HERO BANNER */}
      <section className="inspect-hero-banner">
        <div className="hero-top-badge">
          <Zap size={14} color="#00e5a3" />
          <span>SPENDABLE ARCHITECTURE & WORKFLOW INSPECTOR</span>
        </div>
        <h1 className="hero-title">How Spendable Works — End-to-End System Visualizer</h1>
        <p className="hero-description">
          A step-by-step technical visualizer explaining our multi-channel data ingestion, rolling feature engineering, machine learning model ensemble (XGBoost, LightGBM, DBSCAN), 100% deterministic financial math engine, and responsible Spendable AI layer.
        </p>

        <div className="hero-stats-row">
          <div className="hero-stat-card">
            <div className="stat-icon-box" style={{ background: 'rgba(0, 229, 163, 0.15)', color: '#00e5a3' }}>
              <ShieldCheck size={20} />
            </div>
            <div>
              <span className="stat-val">100%</span>
              <span className="stat-lbl">Deterministic Financial Math</span>
            </div>
          </div>

          <div className="hero-stat-card">
            <div className="stat-icon-box" style={{ background: 'rgba(56, 189, 248, 0.15)', color: '#38bdf8' }}>
              <Cpu size={20} />
            </div>
            <div>
              <span className="stat-val">3 Models</span>
              <span className="stat-lbl">XGBoost + LightGBM + DBSCAN</span>
            </div>
          </div>

          <div className="hero-stat-card">
            <div className="stat-icon-box" style={{ background: 'rgba(168, 85, 247, 0.15)', color: '#a855f7' }}>
              <Lock size={20} />
            </div>
            <div>
              <span className="stat-val">Zero</span>
              <span className="stat-lbl">Hallucination Risk (Zero Math in LLM)</span>
            </div>
          </div>

          <div className="hero-stat-card">
            <div className="stat-icon-box" style={{ background: 'rgba(236, 72, 153, 0.15)', color: '#ec4899' }}>
              <Bot size={20} />
            </div>
            <div>
              <span className="stat-val">Spendable AI</span>
              <span className="stat-lbl">Context-Grounded Gemini Assistant</span>
            </div>
          </div>
        </div>
      </section>

      {/* 2. END-TO-END PIPELINE DIAGRAM */}
      <section className="inspect-section">
        <div className="section-header-row">
          <div className="section-icon-bubble">
            <GitBranch size={22} color="#00e5a3" />
          </div>
          <div>
            <h2 className="section-title">End-to-End System Architecture Flow</h2>
            <p className="section-subtitle">How data flows from multi-channel inputs through ML intelligence down to the UI and Spendable AI</p>
          </div>
        </div>

        <div className="architecture-flow-diagram">
          {/* Node 1 */}
          <div className="flow-node-card node-data">
            <div className="node-step-tag">STAGE 1</div>
            <div className="node-icon-header">
              <Database size={24} color="#38bdf8" />
              <h3>Data Ingestion Layer</h3>
            </div>
            <p>Ingests real-time transactions from Bank APIs, bKash, Upay, & card POS. Standardizes schemas to UTC timestamps & classifies cash directions.</p>
            <div className="node-tech-badge">Plaid / Bank API / Pydantic</div>
          </div>

          <div className="flow-connector-line">
            <ArrowRight size={20} color="#64748b" />
          </div>

          {/* Node 2 */}
          <div className="flow-node-card node-features">
            <div className="node-step-tag">STAGE 2</div>
            <div className="node-icon-header">
              <Layers size={24} color="#a855f7" />
              <h3>Rolling Feature Store</h3>
            </div>
            <p>Computes 7d/14d/30d rolling windows, spending volatility (σ), recency-weighted cash flow ratios, and category concentrations.</p>
            <div className="node-tech-badge">Pandas / NumPy Feature Matrix</div>
          </div>

          <div className="flow-connector-line">
            <ArrowRight size={20} color="#64748b" />
          </div>

          {/* Node 3 */}
          <div className="flow-node-card node-ml">
            <div className="node-step-tag">STAGE 3</div>
            <div className="node-icon-header">
              <Cpu size={24} color="#00e5a3" />
              <h3>ML Model Ensemble</h3>
            </div>
            <p>XGBoost predicts risk distress, LightGBM forecasts 30-day daily balance trajectories, and DBSCAN clusters recurring monthly bills.</p>
            <div className="node-tech-badge">XGBoost / LightGBM / DBSCAN</div>
          </div>

          <div className="flow-connector-line">
            <ArrowRight size={20} color="#64748b" />
          </div>

          {/* Node 4 */}
          <div className="flow-node-card node-engine">
            <div className="node-step-tag">STAGE 4</div>
            <div className="node-icon-header">
              <ShieldCheck size={24} color="#f59e0b" />
              <h3>Deterministic Engine</h3>
            </div>
            <p>Calculates exact Spendable Capacity: Spendable = Max(0, Balance - Upcoming Commitments - Safety Reserve). 100% hardcoded math.</p>
            <div className="node-tech-badge">Python Core Math Engine</div>
          </div>

          <div className="flow-connector-line">
            <ArrowRight size={20} color="#64748b" />
          </div>

          {/* Node 5 */}
          <div className="flow-node-card node-ai">
            <div className="node-step-tag">STAGE 5</div>
            <div className="node-icon-header">
              <Bot size={24} color="#ec4899" />
              <h3>Spendable AI Layer</h3>
            </div>
            <p>Injects calculated context into Gemini LLM. Identifies as Spendable AI to answer liquidity queries with zero hallucination.</p>
            <div className="node-tech-badge">Gemini SDK + Context Injector</div>
          </div>
        </div>
      </section>

      {/* 3. APPLICATION TABS FUNCTIONALITY (How Overview, Activity, Forecast, Simulate work) */}
      <section className="inspect-section">
        <div className="section-header-row">
          <div className="section-icon-bubble">
            <Eye size={22} color="#38bdf8" />
          </div>
          <div>
            <h2 className="section-title">How Our 4 Application Tabs Work</h2>
            <p className="section-subtitle">Understanding the data sources, calculations, and AI integration for each tab in Spendable</p>
          </div>
        </div>

        <div className="app-tabs-explain-grid">
          {/* Overview Tab */}
          <div className="tab-explain-card">
            <div className="tab-card-header">
              <div className="tab-badge overview-badge">
                <DollarSign size={16} />
                <span>OVERVIEW TAB</span>
              </div>
              <h3>Real-Time Spendable Liquidity Dashboard</h3>
            </div>
            <p className="tab-card-desc">
              Shows how much money you can <em>actually spend today</em> without risking upcoming bills or falling below your safety threshold.
            </p>
            <div className="tab-details-list">
              <div className="detail-item">
                <CheckCircle2 size={16} color="#00e5a3" />
                <span><strong>Data Source:</strong> Real-time account balance from database + DBSCAN detected upcoming commitments.</span>
              </div>
              <div className="detail-item">
                <CheckCircle2 size={16} color="#00e5a3" />
                <span><strong>Core Calculation:</strong> Subtracts 30-day bill commitments and safety buffer from current balance.</span>
              </div>
              <div className="detail-item">
                <CheckCircle2 size={16} color="#00e5a3" />
                <span><strong>Visual Widgets:</strong> Liquidity Progress Bar, Safe Daily Limit, upcoming commitment timeline cards.</span>
              </div>
            </div>
          </div>

          {/* Activity Tab */}
          <div className="tab-explain-card">
            <div className="tab-card-header">
              <div className="tab-badge activity-badge">
                <Activity size={16} />
                <span>ACTIVITY TAB</span>
              </div>
              <h3>Multi-Channel Financial Activity Stream</h3>
            </div>
            <p className="tab-card-desc">
              Lists and categorizes every financial transaction ingested across bank accounts, bKash, Upay, and card terminals.
            </p>
            <div className="tab-details-list">
              <div className="detail-item">
                <CheckCircle2 size={16} color="#38bdf8" />
                <span><strong>Ingestion Pipeline:</strong> Standardizes all timestamps into UTC ISO 8601 strings and validates schemas.</span>
              </div>
              <div className="detail-item">
                <CheckCircle2 size={16} color="#38bdf8" />
                <span><strong>Direction Classification:</strong> Separates INFLOW (salaries, transfers) vs OUTFLOW (bills, food, rent).</span>
              </div>
              <div className="detail-item">
                <CheckCircle2 size={16} color="#38bdf8" />
                <span><strong>Filtering & Analytics:</strong> Filter by date ranges, categories, channels, or payment sources.</span>
              </div>
            </div>
          </div>

          {/* Forecast Tab */}
          <div className="tab-explain-card">
            <div className="tab-card-header">
              <div className="tab-badge forecast-badge">
                <TrendingUp size={16} />
                <span>FORECAST TAB</span>
              </div>
              <h3>30-Day Predictive Cash Flow & Trajectory</h3>
            </div>
            <p className="tab-card-desc">
              Projects daily bank balance trajectories over the next 30 days using machine learning, pointing out potential deficit drop dates.
            </p>
            <div className="tab-details-list">
              <div className="detail-item">
                <CheckCircle2 size={16} color="#a855f7" />
                <span><strong>LightGBM Forecaster:</strong> Predicts daily balance trajectory using histogram-based gradient boosting.</span>
              </div>
              <div className="detail-item">
                <CheckCircle2 size={16} color="#a855f7" />
                <span><strong>DBSCAN Bill Clustering:</strong> Automatically flags monthly recurring bills (rent, utilities) on calendar dates.</span>
              </div>
              <div className="detail-item">
                <CheckCircle2 size={16} color="#a855f7" />
                <span><strong>Risk Alert:</strong> Highlights projected cash crunch dates with exact recommended savings buffers.</span>
              </div>
            </div>
          </div>

          {/* Simulate Tab */}
          <div className="tab-explain-card">
            <div className="tab-card-header">
              <div className="tab-badge simulate-badge">
                <Sliders size={16} />
                <span>SIMULATE TAB</span>
              </div>
              <h3>What-If Scenario Engine & Spendable AI</h3>
            </div>
            <p className="tab-card-desc">
              Allows users to test hypothetical purchases, salary delays, or expense spikes in real-time, coupled with our Spendable AI chat assistant.
            </p>
            <div className="tab-details-list">
              <div className="detail-item">
                <CheckCircle2 size={16} color="#ec4899" />
                <span><strong>In-Memory Simulation:</strong> Recalculates Spendable Capacity instantly without touching underlying DB tables.</span>
              </div>
              <div className="detail-item">
                <CheckCircle2 size={16} color="#ec4899" />
                <span><strong>Delta Evaluation:</strong> Shows immediate Δ Spendable impact (e.g. buying a $350 phone drops Spendable by $350).</span>
              </div>
              <div className="detail-item">
                <CheckCircle2 size={16} color="#ec4899" />
                <span><strong>Spendable AI Integration:</strong> Ask Spendable AI questions about your financial context with full guardrails.</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* 4. DEEP DIVE: OUR MACHINE LEARNING MODELS */}
      <section className="inspect-section">
        <div className="section-header-row">
          <div className="section-icon-bubble">
            <Cpu size={22} color="#a855f7" />
          </div>
          <div>
            <h2 className="section-title">Machine Learning Model Ensemble Breakdown</h2>
            <p className="section-subtitle">How we trained our models, how detection works, and why we use specialized ML algorithms</p>
          </div>
        </div>

        <div className="ml-models-deepdive-grid">
          {/* XGBoost Card */}
          <div className="ml-model-card">
            <div className="model-card-top">
              <div className="model-icon-box xgboost-icon">
                <BarChart3 size={24} />
              </div>
              <div>
                <span className="model-tag">CLASSIFIER</span>
                <h3>XGBoost Liquidity Distress Predictor</h3>
              </div>
            </div>
            <p className="model-desc">
              Evaluates non-linear feature interactions to predict the probability of liquidity distress over a 30-day horizon (P(distress) ∈ [0, 1]).
            </p>
            <div className="model-specs-grid">
              <div className="spec-box">
                <span className="spec-lbl">Algorithm</span>
                <span className="spec-val">Gradient Boosted Decision Trees</span>
              </div>
              <div className="spec-box">
                <span className="spec-lbl">Primary Features</span>
                <span className="spec-val">14-day spending volatility (σ), cash flow buffer ratio</span>
              </div>
              <div className="spec-box">
                <span className="spec-lbl">Hyper-Parameters</span>
                <span className="spec-val">100 trees, learning rate 0.05, max depth 6</span>
              </div>
              <div className="spec-box">
                <span className="spec-lbl">Training Method</span>
                <span className="spec-val">5-fold cross-validation on 6-month transaction series</span>
              </div>
            </div>
          </div>

          {/* LightGBM Card */}
          <div className="ml-model-card">
            <div className="model-card-top">
              <div className="model-icon-box lightgbm-icon">
                <TrendingUp size={24} />
              </div>
              <div>
                <span className="model-tag">FORECASTER</span>
                <h3>LightGBM Daily Balance Forecaster</h3>
              </div>
            </div>
            <p className="model-desc">
              Predicts daily closing balances for each day t in range [1, 30] into the future with fast, histogram-based tree splitting.
            </p>
            <div className="model-specs-grid">
              <div className="spec-box">
                <span className="spec-lbl">Algorithm</span>
                <span className="spec-val">Histogram-based Gradient Boosting</span>
              </div>
              <div className="spec-box">
                <span className="spec-lbl">Primary Features</span>
                <span className="spec-val">Day-of-week, day-of-month, 7d/30d moving average balance</span>
              </div>
              <div className="spec-box">
                <span className="spec-lbl">Optimization Metric</span>
                <span className="spec-val">Mean Absolute Error (MAE)</span>
              </div>
              <div className="spec-box">
                <span className="spec-lbl">Execution Speed</span>
                <span className="spec-val">&lt; 15ms inference latency</span>
              </div>
            </div>
          </div>

          {/* DBSCAN Card */}
          <div className="ml-model-card">
            <div className="model-card-top">
              <div className="model-icon-box dbscan-icon">
                <Calendar size={24} />
              </div>
              <div>
                <span className="model-tag">CLUSTERING</span>
                <h3>DBSCAN Recurring Commitment Detector</h3>
              </div>
            </div>
            <p className="model-desc">
              Unsupervised spatial clustering that detects recurring monthly bills (rent, Spotify, utilities) without hardcoded rules.
            </p>
            <div className="model-specs-grid">
              <div className="spec-box">
                <span className="spec-lbl">Algorithm</span>
                <span className="spec-val">Density-Based Spatial Clustering (DBSCAN)</span>
              </div>
              <div className="spec-box">
                <span className="spec-lbl">Clustering Space</span>
                <span className="spec-val">Inter-arrival time (Δt ≈ 30 days) & amount variance</span>
              </div>
              <div className="spec-box">
                <span className="spec-lbl">Parameters</span>
                <span className="spec-val">Epsilon ε = 3.0 days, Min Samples = 2</span>
              </div>
              <div className="spec-box">
                <span className="spec-lbl">Output</span>
                <span className="spec-val">Auto-tagged recurring bills & expected due dates</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* 5. RESPONSIBLE AI ARCHITECTURE */}
      <section className="inspect-section responsible-ai-banner">
        <div className="responsible-header">
          <div className="responsible-icon-box">
            <ShieldCheck size={28} color="#00e5a3" />
          </div>
          <div>
            <h3>Responsible AI Architecture — 100% Deterministic Financial Calculations</h3>
            <p>Why we strictly separate money calculations from LLM Generative AI</p>
          </div>
        </div>

        <div className="responsible-content-grid">
          <div className="responsible-col">
            <div className="col-tag math-tag">DETERMINISTIC MATH ENGINE (100% CODE)</div>
            <h4>Calculates All Financial Figures</h4>
            <p>All numbers, Spendable balances, 30-day bill totals, and scenario deltas are computed in pure Python code using hardcoded formulas:</p>
            <div className="formula-code-badge">
              <code>Spendable = Max(0, Current Balance - 30-Day Commitments - Safety Buffer)</code>
            </div>
            <p className="sub-note">✓ Guarantees 0% math error and 0% financial hallucination.</p>
          </div>

          <div className="responsible-col">
            <div className="col-tag llm-tag">SPENDABLE AI (GEMINI LLM LAYER)</div>
            <h4>Natural Language Guidance & Explanations</h4>
            <p>Receives exact calculated facts from the Deterministic Engine and translates them into friendly conversational advice:</p>
            <div className="prompt-facts-badge">
              <span>Injected Facts: <code>Account Balance = $1,850</code> | <code>Upcoming Rent = $850</code> | <code>Spendable = $700</code></span>
            </div>
            <p className="sub-note">✓ Identifies as Spendable AI and stays strictly on money management topics.</p>
          </div>
        </div>
      </section>
    </div>
  );
};
