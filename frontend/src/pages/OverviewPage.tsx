import React, { useState, useEffect, useCallback } from 'react';
import { getOverviewApi, getRecommendationsApi } from '../api/spendable';
import { injectSampleDataApi } from '../api/auth';
import type { SpendableOverviewResponse, SpendableRecommendationsResponse } from '../api/types';
import { formatCurrency, getLiquidityBadgeConfig } from '../utils/formatters';
import {
  HelpCircle,
  Sliders,
  ArrowRight,
  ShieldCheck,
  AlertTriangle,
  CheckCircle2,
  RefreshCw,
  Sparkles,
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { ConfirmModal } from '../components/ConfirmModal';

interface OverviewPageProps {

  onNavigateTab: (tab: 'forecast' | 'simulate' | 'activity') => void;
  onOpenCalcModal: () => void;
}

const OVERVIEW_CACHE_KEY_PREFIX = 'spendable_overview_cache_';

const getCachedOverviewData = (accId?: string): SpendableOverviewResponse | null => {
  if (!accId) return null;
  try {
    const raw = localStorage.getItem(`${OVERVIEW_CACHE_KEY_PREFIX}${accId}`);
    return raw ? JSON.parse(raw) : null;
  } catch {
    return null;
  }
};

export const OverviewPage: React.FC<OverviewPageProps> = ({ onNavigateTab, onOpenCalcModal }) => {
  const { currentUser, refreshUser } = useAuth();
  const [overview, setOverview] = useState<SpendableOverviewResponse | null>(() =>
    getCachedOverviewData(currentUser?.account_id)
  );
  const [recs, setRecs] = useState<SpendableRecommendationsResponse | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(() => !getCachedOverviewData(currentUser?.account_id));
  const [isInjecting, setIsInjecting] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  // Sync state when current user changes
  useEffect(() => {
    const cached = getCachedOverviewData(currentUser?.account_id);
    if (cached) {
      setOverview(cached);
      setIsLoading(false);
    } else {
      setOverview(null);
      setIsLoading(true);
    }
  }, [currentUser?.account_id]);

  const fetchData = useCallback(async () => {
    const hasCache = !!getCachedOverviewData(currentUser?.account_id);
    if (!hasCache) {
      setIsLoading(true);
    }
    setError(null);
    try {
      const [overviewRes, recsRes] = await Promise.all([
        getOverviewApi(),
        getRecommendationsApi().catch(() => null),
      ]);
      setOverview(overviewRes);
      setRecs(recsRes);
      if (currentUser?.account_id) {
        try {
          localStorage.setItem(`${OVERVIEW_CACHE_KEY_PREFIX}${currentUser.account_id}`, JSON.stringify(overviewRes));
        } catch {}
      }
    } catch (err: any) {
      if (!overview && !hasCache) {
        setError(err.message || 'Failed to load your financial overview.');
      }
    } finally {
      setIsLoading(false);
    }
  }, [currentUser?.account_id, overview]);

  useEffect(() => {
    fetchData();
  }, [currentUser?.account_id]);

  const [injectErrorMsg, setInjectErrorMsg] = useState<string | null>(null);

  const handleInjectSampleData = async () => {
    setIsInjecting(true);
    try {
      await injectSampleDataApi();
      await refreshUser();
      await fetchData();
    } catch (err: any) {
      setInjectErrorMsg(err.message || 'Failed to inject sample transaction data');
    } finally {
      setIsInjecting(false);
    }
  };


  if (isLoading) {
    return (
      <div className="tab-pane">
        <div className="loading-skeleton-container">
          <div className="skeleton-hero"></div>
          <div className="skeleton-grid">
            <div className="skeleton-card"></div>
            <div className="skeleton-card"></div>
            <div className="skeleton-card"></div>
            <div className="skeleton-card"></div>
          </div>
          <p className="loading-text">Loading your financial picture...</p>
        </div>
      </div>
    );
  }

  if (error || !overview) {
    return (
      <div className="tab-pane">
        <div className="error-state-card">
          <AlertTriangle size={40} className="error-icon" />
          <h3>We couldn't load your financial picture.</h3>
          <p>{error || 'An unexpected error occurred while fetching your data.'}</p>
          <button className="secondary-btn" onClick={fetchData}>
            <RefreshCw size={16} />
            <span>Retry</span>
          </button>
        </div>
      </div>
    );
  }

  // Handle empty state for newly registered normal users
  const isNewAccountEmpty =
    !currentUser?.is_demo_account && overview.spendable_amount === 0 && overview.current_balance === 0;

  const badge = getLiquidityBadgeConfig(overview.liquidity_state);

  const getFirstName = (name?: string | null) => {
    if (!name) return 'Spendable User';
    const clean = name.trim();
    return clean.split(' ')[0] || clean;
  };

  return (
    <div className="tab-pane">
      <div className="welcome-banner">
        <div>
          <h2>Good day, {getFirstName(currentUser?.display_name || currentUser?.username)}</h2>
          <p className="subtitle">Know what you can safely spend.</p>
        </div>
      </div>

      {isNewAccountEmpty ? (
        <div className="empty-state-card full-page-empty new-account-card">
          <Sparkles size={48} className="empty-icon text-teal" />
          <h3>Welcome to Spendable!</h3>
          <p className="main-empty-desc">
            This is a new account with <strong>৳0 balance</strong> and no observed transaction history yet.
          </p>
          <p className="sub-empty-desc">
            To immediately test safe spending calculations, commitment detection, and 30-day forecast trajectory for your account, click below:
          </p>
          <button
            className="primary-btn inject-sample-btn"
            onClick={handleInjectSampleData}
            disabled={isInjecting}
          >
            <Sparkles size={16} />
            <span>{isInjecting ? 'Generating 1-Year Sample Activity...' : 'Inject Sample Financial Data'}</span>
          </button>
        </div>
      ) : (
        <>
          {/* Main Hero Card */}
          <section className="spendable-hero-card">
            <div className="spendable-card-header">
              <span className="card-label">YOU CAN SAFELY SPEND</span>
              <button className="info-trigger-btn" onClick={onOpenCalcModal} title="How is this calculated?">
                <HelpCircle size={16} />
                <span>How is this calculated?</span>
              </button>
            </div>

            <div className="spendable-value-display">
              <span className="currency-symbol">৳</span>
              <span className="hero-amount-value">{overview.spendable_amount.toLocaleString('en-US')}</span>
            </div>

            <div className="hero-subline">
              <span>over the next {overview.planning_horizon_days || 30} days</span>
            </div>

            <div className="spendable-status-bar">
              <span className="status-indicator" style={{ backgroundColor: badge.color }}></span>
              <span className="status-label-bold" style={{ color: badge.color }}>{badge.label}</span>
              <span className="status-divider">•</span>
              <span className="status-desc">{badge.description}</span>
            </div>
          </section>

          {/* Core Financial Summary Grid */}
          <section className="summary-grid">
            <div className="summary-card">
              <div className="summary-label">Current Balance</div>
              <div className="summary-value">{formatCurrency(overview.current_balance)}</div>
              <div className="summary-hint">Observable wallet total</div>
            </div>

            <div className="summary-card">
              <div className="summary-label">Protected Amount</div>
              <div className="summary-value protected-color">{formatCurrency(overview.protected_amount)}</div>
              <div className="summary-hint">Commitments & safety reserve</div>
            </div>

            <div className="summary-card">
              <div className="summary-label">Expected Outflows</div>
              <div className="summary-value outflow-color">{formatCurrency(overview.expected_outflow)}</div>
              <div className="summary-hint">Detected commitments</div>
            </div>

            <div className="summary-card">
              <div className="summary-label">Expected Inflows</div>
              <div className="summary-value inflow-color">{formatCurrency(overview.expected_inflow)}</div>
              <div className="summary-hint">Projected 30-day income</div>
            </div>
          </section>

          {/* Section: Why This Number? */}
          <section className="product-section">
            <div className="section-header">
              <h3>Why is your spendable amount {formatCurrency(overview.spendable_amount)}?</h3>
            </div>

            <div className="factors-card-grid">
              <div className="factor-box">
                <span className="factor-title">Upcoming Commitments</span>
                <span className="factor-val minus">− {formatCurrency(overview.upcoming_commitments)}</span>
                <span className="factor-desc">Bills, subscriptions, housing, and obligations</span>
              </div>

              <div className="factor-box">
                <span className="factor-title">Expected Inflow</span>
                <span className="factor-val plus">+ {formatCurrency(overview.expected_inflow)}</span>
                <span className="factor-desc">Projected short-term incoming cash flow</span>
              </div>

              <div className="factor-box">
                <span className="factor-title">Forecasted Minimum</span>
                <span className="factor-val neutral">{formatCurrency(overview.forecasted_minimum_balance)}</span>
                <span className="factor-desc">Lowest projected balance in 30 days</span>
              </div>

              <div className="factor-box">
                <span className="factor-title">Safety Reserve</span>
                <span className="factor-val minus">− {formatCurrency(overview.safety_reserve)}</span>
                <span className="factor-desc">Adaptive reserve cushion for volatility</span>
              </div>
            </div>
          </section>

          {/* Section: Pay Attention To (Deterministic Recommendations + Gemini Explanation) */}
          {recs && (recs.recommendations.length > 0 || recs.explanation) && (
            <section className="product-section">
              <div className="section-header">
                <h3>Pay Attention To</h3>
              </div>

              <div className="recommendations-container">
                {recs.recommendations.map((rec) => (
                  <div key={rec.rule_id} className={`recommendation-card priority-${rec.priority.toLowerCase()}`}>
                    <div className="rec-badge-icon">
                      {rec.priority === 'HIGH' ? (
                        <AlertTriangle size={18} color="#ef4444" />
                      ) : (
                        <CheckCircle2 size={18} color="#00e5a3" />
                      )}
                    </div>
                    <div className="rec-content">
                      <h4>{rec.title}</h4>
                      <p>{rec.message}</p>
                      {rec.action_suggested && (
                        <div className="rec-action-hint">
                          <span className="action-tag">Suggested Action:</span> {rec.action_suggested}
                        </div>
                      )}
                    </div>
                  </div>
                ))}

                {/* Gemini Explanation Integration Block */}
                {recs.explanation && recs.explanation.summary && (
                  <div className="gemini-explanation-box">
                    <div className="explanation-header">
                      <ShieldCheck size={18} color="#00e5a3" />
                      <h4>Why this matters</h4>
                      {recs.explanation.is_fallback && (
                        <span className="fallback-tag">Standard Insight</span>
                      )}
                    </div>
                    <p className="explanation-text">{recs.explanation.summary}</p>
                    {recs.explanation.bullet_points && recs.explanation.bullet_points.length > 0 && (
                      <ul className="explanation-bullets">
                        {recs.explanation.bullet_points.map((pt, idx) => (
                          <li key={idx}>{pt}</li>
                        ))}
                      </ul>
                    )}
                  </div>
                )}
              </div>
            </section>
          )}

          {/* Banner Shortcuts */}
          <div className="shortcuts-grid">
            <section className="product-section shortcut-card">
              <div className="section-header">
                <h3>Cash-Flow Forecast</h3>
                <button className="view-more-btn" onClick={() => onNavigateTab('forecast')}>
                  <span>View Forecast</span>
                  <ArrowRight size={14} />
                </button>
              </div>
              <p className="shortcut-desc">Explore your 30-day balance trajectory and short-term liquidity projection.</p>
            </section>

            <section className="simulate-banner shortcut-card">
              <div className="banner-content">
                <div className="banner-icon-wrapper">
                  <Sliders size={24} color="#00e5a3" />
                </div>
                <div>
                  <h4>What-If Scenario Simulator</h4>
                  <p>Test how a ৳5,000 expense or purchase affects your safe spending runway.</p>
                </div>
              </div>
              <button className="secondary-btn" onClick={() => onNavigateTab('simulate')}>
                <span>Explore Scenarios</span>
                <ArrowRight size={16} />
              </button>
            </section>
          </div>
        </>
      )}

      <ConfirmModal
        isOpen={!!injectErrorMsg}
        title="Sample Data Injection Notice"
        message={injectErrorMsg || ''}
        confirmText="OK"
        cancelText="Close"
        variant="warning"
        onConfirm={() => setInjectErrorMsg(null)}
        onCancel={() => setInjectErrorMsg(null)}
      />
    </div>
  );
};

