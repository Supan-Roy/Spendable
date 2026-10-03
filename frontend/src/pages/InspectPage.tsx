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
  Eye,
  Zap,
  Calendar,
  DollarSign,
  CornerDownLeft
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
          A step-by-step technical visualizer explaining our standardized UTC activity ingestion feed, 38-feature rolling window store, HistGradientBoosting cash-flow forecaster, point-in-time recurring commitment detector, deterministic math engine, and responsible Spendable AI layer.
        </p>

        <div className="hero-stats-row">
          <div className="hero-stat-card">
            <div className="stat-icon-box" style={{ background: 'rgba(0, 229, 163, 0.15)', color: '#00e5a3' }}>
              <ShieldCheck size={20} />
            </div>
            <div>
              <span className="stat-val">100%</span>
              <span className="stat-lbl">Code-Enforced Financial Math</span>
            </div>
          </div>

          <div className="hero-stat-card">
            <div className="stat-icon-box" style={{ background: 'rgba(56, 189, 248, 0.15)', color: '#38bdf8' }}>
              <Cpu size={20} />
            </div>
            <div>
              <span className="stat-val">2 Core ML Components</span>
              <span className="stat-lbl">HistGradientBoosting + Point-in-Time Detector</span>
            </div>
          </div>

          <div className="hero-stat-card">
            <div className="stat-icon-box" style={{ background: 'rgba(168, 85, 247, 0.15)', color: '#a855f7' }}>
              <Lock size={20} />
            </div>
            <div>
              <span className="stat-val">Zero LLM Math</span>
              <span className="stat-lbl">Calculations Handled Entirely in Code</span>
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
            <p className="section-subtitle">A connected 5-stage processing pipeline passing context down to Spendable AI</p>
          </div>
        </div>

        <div className="architecture-rounded-flow">
          {/* Row 1: Stages 1 to 3 */}
          <div className="flow-row row-3-cols">
            {/* Stage 1 */}
            <div className="flow-node-card node-data glow-card">
              <div className="node-header-flex">
                <span className="node-step-tag badge-blue">STAGE 01</span>
                <span className="step-arrow-indicator">➔</span>
              </div>
              <div className="node-icon-header">
                <Database size={24} color="#38bdf8" />
                <h3>Data Ingestion Layer</h3>
              </div>
              <p>Ingests financial activity across bank and digital wallet accounts. Standardizes transactions to UTC ISO 8601 timestamps, validates schemas, and classifies cash directions.</p>
              <div className="node-tech-badge">Pydantic / UTC ISO 8601 / Schema Validation</div>
            </div>

            {/* Stage 2 */}
            <div className="flow-node-card node-features glow-card">
              <div className="node-header-flex">
                <span className="node-step-tag badge-purple">STAGE 02</span>
                <span className="step-arrow-indicator">➔</span>
              </div>
              <div className="node-icon-header">
                <Layers size={24} color="#a855f7" />
                <h3>Rolling Feature Store</h3>
              </div>
              <p>Computes 38 rolling window features across 7d/14d/30d windows, including spending velocity, burn rate, volatility (σ), and discretionary outflow ratios.</p>
              <div className="node-tech-badge">Pandas / NumPy 38-Feature Matrix</div>
            </div>

            {/* Stage 3 */}
            <div className="flow-node-card node-ml glow-card">
              <div className="node-header-flex">
                <span className="node-step-tag badge-green">STAGE 03</span>
                <span className="step-arrow-indicator loop-down">↴</span>
              </div>
              <div className="node-icon-header">
                <Cpu size={24} color="#00e5a3" />
                <h3>ML & Detection Engine</h3>
              </div>
              <p>HistGradientBoostingRegressor predicts 7d/14d/30d minimum balance horizons & daily trajectories, while RecurringDetector scores payment regularity and category priors.</p>
              <div className="node-tech-badge">HistGradientBoosting / Interval Regularity Scoring</div>
            </div>
          </div>

          {/* Rounded Loop Connector Line */}
          <div className="rounded-loop-connector">
            <div className="connector-pill-badge">
              <CornerDownLeft size={15} color="#00e5a3" />
              <span>PIPELINE DATA FLOW LOOP</span>
            </div>
          </div>

          {/* Row 2: Stages 4 & 5 */}
          <div className="flow-row row-2-cols">
            {/* Stage 4 */}
            <div className="flow-node-card node-engine glow-card">
              <div className="node-header-flex">
                <span className="node-step-tag badge-amber">STAGE 04</span>
                <span className="step-arrow-indicator">➔</span>
              </div>
              <div className="node-icon-header">
                <ShieldCheck size={24} color="#f59e0b" />
                <h3>Deterministic Engine</h3>
              </div>
              <p>Calculates exact Spendable Capacity: Spendable = Max(0, Balance - Commitments - Reserve). Executed entirely in pure Python math routines.</p>
              <div className="node-tech-badge">Python Core Math Engine</div>
            </div>

            {/* Stage 5 */}
            <div className="flow-node-card node-ai glow-card">
              <div className="node-header-flex">
                <span className="node-step-tag badge-pink">STAGE 05</span>
                <span className="step-arrow-indicator">✓</span>
              </div>
              <div className="node-icon-header">
                <Bot size={24} color="#ec4899" />
                <h3>Spendable AI Layer</h3>
              </div>
              <p>Injects calculated facts into Gemini LLM prompt context. Spendable AI answers user questions without performing financial arithmetic in generative AI.</p>
              <div className="node-tech-badge">Gemini SDK + Context Injector</div>
            </div>
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
                <span><strong>Data Source:</strong> Real-time database account balance + point-in-time detected commitments.</span>
              </div>
              <div className="detail-item">
                <CheckCircle2 size={16} color="#00e5a3" />
                <span><strong>Core Calculation:</strong> Subtracts 30-day upcoming bill commitments and safety threshold from current balance.</span>
              </div>
              <div className="detail-item">
                <CheckCircle2 size={16} color="#00e5a3" />
                <span><strong>Visual Widgets:</strong> Liquidity Progress Bar, Safe Daily Spendable Limit, upcoming commitment timeline.</span>
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
              Lists and categorizes every financial transaction ingested across bank accounts and mobile wallet feeds.
            </p>
            <div className="tab-details-list">
              <div className="detail-item">
                <CheckCircle2 size={16} color="#38bdf8" />
                <span><strong>Ingestion Pipeline:</strong> Standardizes raw transactions into UTC ISO 8601 activity records with schema validation.</span>
              </div>
              <div className="detail-item">
                <CheckCircle2 size={16} color="#38bdf8" />
                <span><strong>Direction Classification:</strong> Classifies INFLOW (salaries, transfers) vs OUTFLOW (rent, utilities, food).</span>
              </div>
              <div className="detail-item">
                <CheckCircle2 size={16} color="#38bdf8" />
                <span><strong>Filtering & Analytics:</strong> Filter activities by account ID, category, direction, and date ranges.</span>
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
              Projects daily bank balance trajectories over the next 30 days using machine learning models and baselines.
            </p>
            <div className="tab-details-list">
              <div className="detail-item">
                <CheckCircle2 size={16} color="#a855f7" />
                <span><strong>HistGradientBoosting Forecaster:</strong> Supervised multi-horizon model predicting 7d/14d/30d balance minimums & 30-day daily balance trajectories.</span>
              </div>
              <div className="detail-item">
                <CheckCircle2 size={16} color="#a855f7" />
                <span><strong>Baseline Comparisons:</strong> Compares ML model projections against Rolling Average and Recurring Commitment baselines.</span>
              </div>
              <div className="detail-item">
                <CheckCircle2 size={16} color="#a855f7" />
                <span><strong>Risk Alert:</strong> Highlights projected drawdown dates where balance approaches or crosses safety threshold.</span>
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
                <span><strong>Scenario Engine:</strong> Simulates 5 hypothetical scenario types (One-Time Expense, Additional Income, New Commitment, Spending Reduction, Income Delay).</span>
              </div>
              <div className="detail-item">
                <CheckCircle2 size={16} color="#ec4899" />
                <span><strong>In-Memory Delta Calculation:</strong> Recalculates Spendable Capacity, runway shift, and safe cushion status in memory without mutating database tables.</span>
              </div>
              <div className="detail-item">
                <CheckCircle2 size={16} color="#ec4899" />
                <span><strong>Spendable AI Integration:</strong> Allows user to consult Spendable AI about scenario outcomes with context guardrails.</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* 4. DEEP DIVE: OUR MACHINE LEARNING & DETECTION ENGINE */}
      <section className="inspect-section">
        <div className="section-header-row">
          <div className="section-icon-bubble">
            <Cpu size={22} color="#a855f7" />
          </div>
          <div>
            <h2 className="section-title">Machine Learning & Detection Engine Breakdown</h2>
            <p className="section-subtitle">How we trained our models, how detection works, and why we use specialized algorithms</p>
          </div>
        </div>

        <div className="ml-models-deepdive-grid">
          {/* HistGradientBoosting Card */}
          <div className="ml-model-card">
            <div className="model-card-top">
              <div className="model-icon-box lightgbm-icon">
                <TrendingUp size={22} />
              </div>
              <div>
                <span className="model-tag">SUPERVISED REGRESSOR</span>
                <h3>HistGradientBoosting Cash-Flow Forecaster</h3>
              </div>
            </div>
            <p className="model-desc">
              Supervised gradient boosted regression models predicting multi-horizon (7d, 14d, 30d) minimum balances and 30-day daily trajectory points.
            </p>
            <div className="model-specs-grid">
              <div className="spec-box full-width">
                <span className="spec-lbl">Algorithm</span>
                <span className="spec-val spec-code">sklearn.ensemble.HistGradientBoostingRegressor</span>
              </div>
              <div className="spec-box">
                <span className="spec-lbl">Primary Features</span>
                <span className="spec-val">38 rolling features (burn rate, velocity, 7d/14d/30d min/mean/std)</span>
              </div>
              <div className="spec-box">
                <span className="spec-lbl">Hyper-Parameters</span>
                <span className="spec-val spec-code">max_iter=150, min_samples_leaf=20, random_seed=42</span>
              </div>
              <div className="spec-box full-width">
                <span className="spec-lbl">Evaluation Metric</span>
                <span className="spec-val">Weighted Absolute Percentage Error (WAPE) & MAE</span>
              </div>
            </div>
          </div>

          {/* RecurringDetector Card */}
          <div className="ml-model-card">
            <div className="model-card-top">
              <div className="model-icon-box dbscan-icon">
                <Calendar size={22} />
              </div>
              <div>
                <span className="model-tag">PATTERN SCORING ENGINE</span>
                <h3>Point-in-Time Recurring Commitment Detector</h3>
              </div>
            </div>
            <p className="model-desc">
              Deterministic detection scoring recurring bills, debt payments, subscriptions, and income streams using point-in-time observable transaction history.
            </p>
            <div className="model-specs-grid">
              <div className="spec-box">
                <span className="spec-lbl">Algorithm</span>
                <span className="spec-val">Inter-Arrival Regularity & Prior Category Weighting</span>
              </div>
              <div className="spec-box">
                <span className="spec-lbl">Metrics Scored</span>
                <span className="spec-val">Inter-arrival CV (CV_Δt), Amount CV, Category Priors</span>
              </div>
              <div className="spec-box">
                <span className="spec-lbl">Category Classes</span>
                <span className="spec-val">Core Commitments (Housing, Utilities, Telecom) vs Discretionary</span>
              </div>
              <div className="spec-box">
                <span className="spec-lbl">Output</span>
                <span className="spec-val">Tagged commitments, interval types (Weekly, Monthly), confidence scores ∈ [0, 1]</span>
              </div>
            </div>
          </div>

          {/* Scenario Simulation Card */}
          <div className="ml-model-card">
            <div className="model-card-top">
              <div className="model-icon-box xgboost-icon">
                <BarChart3 size={22} />
              </div>
              <div>
                <span className="model-tag">IN-MEMORY SIMULATOR</span>
                <h3>What-If Scenario Simulation Engine</h3>
              </div>
            </div>
            <p className="model-desc">
              In-memory simulation framework evaluating financial impact across 5 distinct hypothetical scenario types.
            </p>
            <div className="model-specs-grid">
              <div className="spec-box">
                <span className="spec-lbl">Scenario Types</span>
                <span className="spec-val">Expense, Income, New Commitment, Savings, Income Delay</span>
              </div>
              <div className="spec-box">
                <span className="spec-lbl">Computation</span>
                <span className="spec-val">In-Memory Delta Matrix (Δ Spendable, Δ Runway, Δ Cushion)</span>
              </div>
              <div className="spec-box">
                <span className="spec-lbl">State Handling</span>
                <span className="spec-val">100% Immutable (zero DB mutations)</span>
              </div>
              <div className="spec-box">
                <span className="spec-lbl">Integration</span>
                <span className="spec-val">Feeds directly into Spendable AI context payload</span>
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
            <h3>Responsible AI Architecture — Code-Enforced Financial Calculations</h3>
            <p>Why we strictly separate money calculations from LLM Generative AI</p>
          </div>
        </div>

        <div className="responsible-content-grid">
          <div className="responsible-col">
            <div className="col-tag math-tag">DETERMINISTIC MATH ENGINE (100% CODE)</div>
            <h4>Calculates All Financial Figures</h4>
            <p>All numbers, Spendable balances, 30-day bill totals, and scenario deltas are computed in pure Python code using deterministic formulas:</p>
            <div className="formula-code-badge">
              <code>Spendable = Max(0, Current Balance - 30-Day Commitments - Safety Reserve)</code>
            </div>
            <p className="sub-note">✓ Zero LLM arithmetic execution; 100% code-enforced financial math.</p>
          </div>

          <div className="responsible-col">
            <div className="col-tag llm-tag">SPENDABLE AI (GEMINI LLM LAYER)</div>
            <h4>Natural Language Guidance & Explanations</h4>
            <p>Receives pre-computed financial facts from the Deterministic Engine and translates them into clear conversational advice:</p>
            <div className="prompt-facts-badge">
              <span>Injected Facts: Account Balance | 30-Day Commitments | Spendable Capacity | 30-Day Trajectory</span>
            </div>
            <p className="sub-note">✓ Identifies as Spendable AI and stays strictly scoped to financial guidance.</p>
          </div>
        </div>
      </section>
    </div>
  );
};
