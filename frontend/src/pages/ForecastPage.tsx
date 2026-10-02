import React, { useState, useEffect, useCallback } from 'react';
import { getForecastApi } from '../api/spendable';
import type { SpendableForecastResponse, SpendableForecastItem, DailyBalance } from '../api/types';
import { formatCurrency, formatShortDate, getLiquidityBadgeConfig } from '../utils/formatters';
import { TrendingUp, AlertTriangle, RefreshCw, Calendar } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

export const ForecastPage: React.FC = () => {
  const { currentUser } = useAuth();
  const [forecastData, setForecastData] = useState<SpendableForecastResponse | null>(null);
  const [selectedHorizon, setSelectedHorizon] = useState<'30' | '14' | '7'>('30');
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const fetchForecast = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await getForecastApi();
      setForecastData(data);
    } catch (err: any) {
      setError(err.message || 'Failed to generate cash-flow forecast.');
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchForecast();
  }, [fetchForecast, currentUser?.account_id]);

  if (isLoading) {
    return (
      <div className="tab-pane">
        <div className="loading-skeleton-container">
          <div className="skeleton-hero"></div>
          <p className="loading-text">Loading cash-flow forecast trajectory...</p>
        </div>
      </div>
    );
  }

  if (error || !forecastData) {
    return (
      <div className="tab-pane">
        <div className="error-state-card">
          <AlertTriangle size={40} className="error-icon" />
          <h3>Forecast Unavailable</h3>
          <p>{error || 'An unexpected error occurred.'}</p>
          <button className="secondary-btn" onClick={fetchForecast}>
            <RefreshCw size={16} />
            <span>Retry</span>
          </button>
        </div>
      </div>
    );
  }

  const currentForecastItem: SpendableForecastItem =
    selectedHorizon === '7'
      ? forecastData.forecast_7d
      : selectedHorizon === '14'
      ? forecastData.forecast_14d
      : forecastData.forecast_30d;

  const badge = getLiquidityBadgeConfig(currentForecastItem.liquidity_state);
  const dailyBalances: DailyBalance[] = currentForecastItem.daily_balances || [];

  // Render SVG Chart calculations
  const minVal = Math.min(...dailyBalances.map((d) => d.balance), currentForecastItem.forecasted_minimum_balance, 0);
  const maxVal = Math.max(...dailyBalances.map((d) => d.balance), 10000);
  const range = maxVal - minVal || 1;

  const chartWidth = 760;
  const chartHeight = 220;
  const padding = 30;

  const points = dailyBalances.map((item, index) => {
    const x = padding + (index / Math.max(dailyBalances.length - 1, 1)) * (chartWidth - padding * 2);
    const y = chartHeight - padding - ((item.balance - minVal) / range) * (chartHeight - padding * 2);
    return { x, y, balance: item.balance, date: item.date };
  });

  const pathD = points.length > 0
    ? points.reduce((acc, p, i) => (i === 0 ? `M ${p.x} ${p.y}` : `${acc} L ${p.x} ${p.y}`), '')
    : '';

  // Calculate SVG Y coordinate for minimum balance line
  const minLineY = chartHeight - padding - ((currentForecastItem.forecasted_minimum_balance - minVal) / range) * (chartHeight - padding * 2);

  return (
    <div className="tab-pane">
      <div className="page-header forecast-page-header">
        <div>
          <h2>Cash-Flow Forecast</h2>
          <p className="subtitle">Projected balance trajectories and liquidity pressure analysis.</p>
        </div>

        {/* Horizon Switcher Buttons */}
        <div className="horizon-picker">
          <button
            className={`horizon-btn ${selectedHorizon === '7' ? 'active' : ''}`}
            onClick={() => setSelectedHorizon('7')}
          >
            7 Days
          </button>
          <button
            className={`horizon-btn ${selectedHorizon === '14' ? 'active' : ''}`}
            onClick={() => setSelectedHorizon('14')}
          >
            14 Days
          </button>
          <button
            className={`horizon-btn ${selectedHorizon === '30' ? 'active' : ''}`}
            onClick={() => setSelectedHorizon('30')}
          >
            30 Days
          </button>
        </div>
      </div>

      {/* Main SVG Trajectory Chart */}
      <section className="forecast-chart-card">
        <div className="chart-card-header">
          <div className="chart-title-group">
            <TrendingUp size={20} color="#00e5a3" />
            <h3>{selectedHorizon}-Day Balance Trajectory</h3>
          </div>
          <div className="chart-badge-wrapper">
            <span className="status-indicator" style={{ backgroundColor: badge.color }}></span>
            <span className="status-label-bold" style={{ color: badge.color }}>{badge.label}</span>
          </div>
        </div>

        <div className="svg-chart-wrapper">
          <svg viewBox={`0 0 ${chartWidth} ${chartHeight}`} className="trajectory-svg">
            {/* Grid Lines */}
            <line x1={padding} y1={padding} x2={chartWidth - padding} y2={padding} stroke="rgba(255,255,255,0.06)" />
            <line x1={padding} y1={chartHeight / 2} x2={chartWidth - padding} y2={chartHeight / 2} stroke="rgba(255,255,255,0.06)" />
            <line x1={padding} y1={chartHeight - padding} x2={chartWidth - padding} y2={chartHeight - padding} stroke="rgba(255,255,255,0.08)" />

            {/* Minimum Balance Line */}
            {!isNaN(minLineY) && (
              <line
                x1={padding}
                y1={minLineY}
                x2={chartWidth - padding}
                y2={minLineY}
                stroke="#f59e0b"
                strokeDasharray="4 4"
                strokeWidth="1.5"
              />
            )}

            {/* Main Balance Line */}
            {pathD && <path d={pathD} fill="none" stroke="#00e5a3" strokeWidth="3" strokeLinecap="round" />}

            {/* Point circles */}
            {points.map((p, idx) => (
              <circle
                key={idx}
                cx={p.x}
                cy={p.y}
                r={idx === points.length - 1 || idx === 0 ? 5 : 2}
                fill={idx === points.length - 1 ? '#00e5a3' : '#3b82f6'}
              />
            ))}
          </svg>
        </div>

        <div className="chart-legend-row">
          <div className="legend-item">
            <span className="legend-dot green"></span>
            <span>Projected Balance</span>
          </div>
          <div className="legend-item">
            <span className="legend-dot dashed-amber"></span>
            <span>Minimum Projected ({formatCurrency(currentForecastItem.forecasted_minimum_balance)})</span>
          </div>
          <div className="legend-item">
            <Calendar size={13} color="#94a3b8" />
            <span>Range: Next {selectedHorizon} Days</span>
          </div>
        </div>
      </section>

      {/* Horizon Summary Grid */}
      <section className="summary-grid">
        <div className="summary-card">
          <div className="summary-label">Expected Inflow</div>
          <div className="summary-value inflow-color">{formatCurrency(currentForecastItem.expected_inflow)}</div>
          <div className="summary-hint">Projected income in next {selectedHorizon}d</div>
        </div>

        <div className="summary-card">
          <div className="summary-label">Expected Outflow</div>
          <div className="summary-value outflow-color">{formatCurrency(currentForecastItem.expected_outflow)}</div>
          <div className="summary-hint">Detected expenses & bills</div>
        </div>

        <div className="summary-card">
          <div className="summary-label">Forecasted Minimum</div>
          <div className="summary-value warning-color">{formatCurrency(currentForecastItem.forecasted_minimum_balance)}</div>
          <div className="summary-hint">Lowest point in trajectory</div>
        </div>

        <div className="summary-card">
          <div className="summary-label">Safety Reserve</div>
          <div className="summary-value">{formatCurrency(currentForecastItem.safety_reserve)}</div>
          <div className="summary-hint">Protected volatility buffer</div>
        </div>
      </section>

      {/* Detailed Daily Table */}
      <section className="product-section">
        <div className="section-header">
          <h3>Daily Forecast Trajectory Breakdown</h3>
        </div>

        <div className="table-responsive-container">
          <table className="spendable-data-table">
            <thead>
              <tr>
                <th>Date</th>
                <th>Projected Balance</th>
                <th>Safety Buffer Required</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {dailyBalances.map((item, idx) => (
                <tr key={idx}>
                  <td className="font-mono">{formatShortDate(item.date)}</td>
                  <td className="font-mono bold-text">{formatCurrency(item.balance)}</td>
                  <td className="font-mono">{formatCurrency(currentForecastItem.safety_reserve)}</td>
                  <td>
                    <span className="status-pill healthy">Normal</span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
};
