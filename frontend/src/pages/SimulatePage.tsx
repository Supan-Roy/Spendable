import React, { useState } from 'react';
import { postSimulateApi } from '../api/spendable';
import type { ScenarioType, ScenarioResult } from '../api/types';
import { formatCurrency, formatDateTime, getLiquidityBadgeConfig } from '../utils/formatters';
import { Sliders, ArrowRight, RotateCcw, AlertTriangle, Shield } from 'lucide-react';

export const SimulatePage: React.FC = () => {
  const [scenarioType, setScenarioType] = useState<ScenarioType>('ONE_TIME_EXPENSE');
  const [amount, setAmount] = useState<string>('5000');
  const [changePercentage, setChangePercentage] = useState<string>('10');
  const [delayDays, setDelayDays] = useState<string>('7');
  const [description, setDescription] = useState<string>('');

  const [result, setResult] = useState<ScenarioResult | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const handleSimulate = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    setIsLoading(true);
    setError(null);
    try {
      const numAmt = parseFloat(amount) || 0;
      const numPct = parseFloat(changePercentage) || 0;
      const numDays = parseInt(delayDays, 10) || 0;

      const res = await postSimulateApi({
        scenario_type: scenarioType,
        amount: scenarioType === 'ONE_TIME_EXPENSE' || scenarioType === 'ONE_TIME_INCOME' || scenarioType === 'RECURRING_EXPENSE' ? numAmt : undefined,
        change_percentage: scenarioType === 'INCOME_CHANGE' ? numPct : undefined,
        delay_days: scenarioType === 'INCOME_DELAY' ? numDays : undefined,
        description: description.trim() || undefined,
      });

      setResult(res);
    } catch (err: any) {
      setError(err.message || 'Failed to simulate scenario.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleReset = () => {
    setResult(null);
    setError(null);
    setAmount('5000');
    setDescription('');
  };

  const baseBadge = result ? getLiquidityBadgeConfig(result.base_liquidity_state) : null;
  const scenarioBadge = result ? getLiquidityBadgeConfig(result.scenario_liquidity_state) : null;

  return (
    <div className="tab-pane">
      <div className="page-header">
        <h2>What-If Scenario Simulator</h2>
        <p className="subtitle">What happens if I spend more, delay income, or add commitments?</p>
      </div>

      <div className="simulate-layout-grid">
        {/* Left Form Panel */}
        <div className="simulate-form-card">
          <div className="form-card-header">
            <Sliders size={20} color="#00e5a3" />
            <h3>Choose Scenario</h3>
          </div>

          <form onSubmit={handleSimulate}>
            <div className="form-group">
              <label>Scenario Type</label>
              <select
                value={scenarioType}
                onChange={(e) => {
                  setScenarioType(e.target.value as ScenarioType);
                  setResult(null);
                }}
                disabled={isLoading}
              >
                <option value="ONE_TIME_EXPENSE">Spend money (One-time expense)</option>
                <option value="ONE_TIME_INCOME">Receive money (One-time inflow)</option>
                <option value="RECURRING_EXPENSE">Add commitment (Monthly bill/rent)</option>
                <option value="INCOME_CHANGE">Income change (%)</option>
                <option value="INCOME_DELAY">Delay income (Days)</option>
              </select>
            </div>

            {(scenarioType === 'ONE_TIME_EXPENSE' ||
              scenarioType === 'ONE_TIME_INCOME' ||
              scenarioType === 'RECURRING_EXPENSE') && (
              <div className="form-group">
                <label>Amount (৳)</label>
                <div className="input-currency-wrapper">
                  <span className="input-symbol">৳</span>
                  <input
                    type="number"
                    min="1"
                    step="100"
                    value={amount}
                    onChange={(e) => setAmount(e.target.value)}
                    placeholder="5000"
                    disabled={isLoading}
                  />
                </div>
              </div>
            )}

            {scenarioType === 'INCOME_CHANGE' && (
              <div className="form-group">
                <label>Income Change (%)</label>
                <input
                  type="number"
                  step="1"
                  value={changePercentage}
                  onChange={(e) => setChangePercentage(e.target.value)}
                  placeholder="-10 or +15"
                  disabled={isLoading}
                />
              </div>
            )}

            {scenarioType === 'INCOME_DELAY' && (
              <div className="form-group">
                <label>Delay (Days)</label>
                <input
                  type="number"
                  min="1"
                  max="30"
                  value={delayDays}
                  onChange={(e) => setDelayDays(e.target.value)}
                  placeholder="7"
                  disabled={isLoading}
                />
              </div>
            )}

            <div className="form-group">
              <label>Description (Optional)</label>
              <input
                type="text"
                placeholder="e.g. New smartphone purchase"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                disabled={isLoading}
              />
            </div>

            <div className="form-action-group">
              <button type="submit" className="primary-btn full-width" disabled={isLoading}>
                {isLoading ? 'Simulating...' : 'Simulate Scenario'}
              </button>
              {result && (
                <button type="button" className="secondary-btn" onClick={handleReset} disabled={isLoading}>
                  <RotateCcw size={14} />
                  <span>Reset</span>
                </button>
              )}
            </div>
          </form>
        </div>

        {/* Right Output Panel */}
        <div className="simulate-output-container">
          {error && (
            <div className="auth-error-banner">
              <AlertTriangle size={16} />
              <span>{error}</span>
            </div>
          )}

          {!result ? (
            <div className="empty-state-card simulate-placeholder-card">
              <Sliders size={40} className="empty-icon" />
              <h3>Ready to Simulate</h3>
              <p>
                Enter a hypothetical expense or financial change on the left and click <strong>Simulate Scenario</strong> to see how your safe spending runway changes.
              </p>
            </div>
          ) : (
            <div className="scenario-results-card">
              <div className="results-header">
                <div>
                  <h3>Scenario Impact Result</h3>
                  {result.snapshot_time && (
                    <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: '0.2rem' }}>
                      Simulated at {formatDateTime(result.snapshot_time)}
                    </div>
                  )}
                </div>
                {result.state_changed && (
                  <span className="state-changed-tag">State Changed</span>
                )}
              </div>

              {/* Before vs After Visual Comparison */}
              <div className="before-after-grid">
                <div className="comparison-box before-box">
                  <span className="box-title">BEFORE (BASE)</span>
                  <span className="box-amount">{formatCurrency(result.base_spendable)}</span>
                  {baseBadge && (
                    <span className="mini-status-badge" style={{ color: baseBadge.color }}>
                      {baseBadge.label}
                    </span>
                  )}
                </div>

                <div className="comparison-arrow">
                  <ArrowRight size={24} color="#00e5a3" />
                  <span className={`delta-tag ${result.spendable_delta < 0 ? 'negative' : 'positive'}`}>
                    {result.spendable_delta >= 0 ? '+' : ''}
                    {formatCurrency(result.spendable_delta)}
                  </span>
                </div>

                <div className="comparison-box after-box">
                  <span className="box-title">AFTER (SCENARIO)</span>
                  <span className="box-amount scenario-highlight">{formatCurrency(result.scenario_spendable)}</span>
                  {scenarioBadge && (
                    <span className="mini-status-badge" style={{ color: scenarioBadge.color }}>
                      {scenarioBadge.label}
                    </span>
                  )}
                </div>
              </div>

              {/* Scenario Explanation */}
              {result.explanation && (
                <div className="scenario-explanation-box">
                  <div className="explanation-header">
                    <Shield size={16} color="#00e5a3" />
                    <h4>Impact Analysis</h4>
                  </div>
                  <p>{result.explanation}</p>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
