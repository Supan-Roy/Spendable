import React, { useState, useEffect, useCallback } from 'react';
import { getForecastApi } from '../api/spendable';
import type { SpendableForecastResponse, LiquidityState } from '../api/types';
import { formatCurrency, formatShortDate, getLiquidityBadgeConfig } from '../utils/formatters';
import { TrendingUp, AlertTriangle, RefreshCw, Calendar } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

const FORECAST_CACHE_KEY_PREFIX = 'spendable_forecast_cache_';

interface DailyTrajectoryItem {
  date: string;
  balance: number;
  requiredBuffer: number;
}

const getCachedForecastData = (accId?: string): SpendableForecastResponse | null => {
  if (!accId) return null;
  try {
    const raw = localStorage.getItem(`${FORECAST_CACHE_KEY_PREFIX}${accId}`);
    return raw ? JSON.parse(raw) : null;
  } catch {
    return null;
  }
};

export const ForecastPage: React.FC = () => {
  const { currentUser } = useAuth();
  const [forecastData, setForecastData] = useState<SpendableForecastResponse | null>(() =>
    getCachedForecastData(currentUser?.account_id)
  );
  const [selectedHorizon, setSelectedHorizon] = useState<'30' | '14' | '7'>('30');
  const [isLoading, setIsLoading] = useState<boolean>(() => !getCachedForecastData(currentUser?.account_id));
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const cached = getCachedForecastData(currentUser?.account_id);
    if (cached) {
      setForecastData(cached);
      setIsLoading(false);
    } else {
      setForecastData(null);
      setIsLoading(true);
    }
  }, [currentUser?.account_id]);

  const fetchForecast = useCallback(async () => {
    const hasCache = !!getCachedForecastData(currentUser?.account_id);
    if (!hasCache) {
      setIsLoading(true);
    }
    setError(null);
    try {
      const data = await getForecastApi();
      setForecastData(data);
      if (currentUser?.account_id) {
        try {
          localStorage.setItem(`${FORECAST_CACHE_KEY_PREFIX}${currentUser.account_id}`, JSON.stringify(data));
        } catch {}
      }
    } catch (err: any) {
      if (!forecastData && !hasCache) {
        setError(err.message || 'Failed to generate cash-flow forecast.');
      }
    } finally {
      setIsLoading(false);
    }
  }, [currentUser?.account_id, forecastData]);

  useEffect(() => {
    fetchForecast();
  }, [currentUser?.account_id]);

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

  const horizonDays = parseInt(selectedHorizon, 10);
  const currentForecastItem =
    selectedHorizon === '7'
      ? forecastData.forecast_7d
      : selectedHorizon === '14'
      ? forecastData.forecast_14d
      : forecastData.forecast_30d;

  const minProjBal =
    (currentForecastItem as any)?.minimum_projected_balance ??
    (currentForecastItem as any)?.forecasted_minimum_balance ??
    0;

  const safetyReserve =
    (currentForecastItem as any)?.safety_reserve ??
    (forecastData as any)?.safety_threshold_bdt ??
    15000;

  let liqState: LiquidityState = 'HEALTHY';
  if (minProjBal < safetyReserve) {
    liqState = 'PRESSURED';
  } else if (minProjBal < safetyReserve * 1.30 || (currentForecastItem?.expected_outflow > currentForecastItem?.expected_inflow)) {
    liqState = 'WATCH';
  } else {
    liqState = 'HEALTHY';
  }

  const badge = getLiquidityBadgeConfig(liqState);

  // Extract daily trajectory points from top-level daily_trajectory or item fallback
  const rawTrajectory =
    forecastData?.daily_trajectory ||
    (currentForecastItem as any)?.daily_balances ||
    [];

  let dailyBalances: DailyTrajectoryItem[] = rawTrajectory.slice(0, horizonDays).map((item: any, idx: number) => {
    const rawDate = item.date_str || item.date || '';
    const rawBal =
      typeof item.projected_balance === 'number'
        ? item.projected_balance
        : typeof item.balance === 'number'
        ? item.balance
        : typeof item.minimum_balance === 'number'
        ? item.minimum_balance
        : 0;

    const reqBuf =
      typeof item.required_buffer === 'number'
        ? item.required_buffer
        : Math.round(safetyReserve * (0.65 + 0.35 * ((idx + 1) / horizonDays)));

    return {
      date: rawDate,
      balance: rawBal,
      requiredBuffer: reqBuf,
    };
  });

  // Fallback for empty trajectory: create trajectory line from current_balance
  if (dailyBalances.length === 0) {
    const today = new Date();
    const curBal = (forecastData as any)?.current_balance || 0;
    dailyBalances = Array.from({ length: horizonDays }, (_, i) => {
      const d = new Date(today);
      d.setDate(d.getDate() + i + 1);
      const reqBuf = Math.round(safetyReserve * (0.65 + 0.35 * ((i + 1) / horizonDays)));
      return {
        date: d.toISOString().split('T')[0],
        balance: curBal,
        requiredBuffer: reqBuf,
      };
    });
  }

  // Render SVG Chart calculations with generous paddings for axes and labels
  const minVal = Math.min(...dailyBalances.map((d: DailyTrajectoryItem) => d.balance), minProjBal, 0);
  const maxVal = Math.max(...dailyBalances.map((d: DailyTrajectoryItem) => d.balance), safetyReserve * 1.2, 10000);
  const range = maxVal - minVal || 1;

  const chartWidth = 760;
  const chartHeight = 260;
  const paddingLeft = 65;
  const paddingRight = 35;
  const paddingTop = 30;
  const paddingBottom = 45;

  const points = dailyBalances.map((item: DailyTrajectoryItem, index: number) => {
    const x = paddingLeft + (index / Math.max(dailyBalances.length - 1, 1)) * (chartWidth - paddingLeft - paddingRight);
    const y = chartHeight - paddingBottom - ((item.balance - minVal) / range) * (chartHeight - paddingTop - paddingBottom);
    return { x, y, balance: item.balance, date: item.date };
  });

  const pathD = points.length > 0
    ? points.reduce((acc: string, p: { x: number; y: number }, i: number) => (i === 0 ? `M ${p.x} ${p.y}` : `${acc} L ${p.x} ${p.y}`), '')
    : '';

  const areaD = points.length > 0
    ? `${pathD} L ${points[points.length - 1].x} ${chartHeight - paddingBottom} L ${points[0].x} ${chartHeight - paddingBottom} Z`
    : '';

  // Calculate SVG Y coordinate for minimum balance line
  const minLineY = chartHeight - paddingBottom - ((minProjBal - minVal) / range) * (chartHeight - paddingTop - paddingBottom);

  // Lowest point callout
  const lowestPoint = points.length > 0
    ? points.reduce((minP, p) => (p.balance < minP.balance ? p : minP), points[0])
    : null;

  // Evenly spaced X-axis date ticks
  const dateTickIndices = points.length > 0
    ? [
        0,
        Math.floor(points.length * 0.2),
        Math.floor(points.length * 0.4),
        Math.floor(points.length * 0.6),
        Math.floor(points.length * 0.8),
        points.length - 1
      ].filter((v, i, a) => a.indexOf(v) === i && points[v])
    : [];

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
            <defs>
              <linearGradient id="chartAreaGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#00e5a3" stopOpacity="0.25" />
                <stop offset="100%" stopColor="#00e5a3" stopOpacity="0.01" />
              </linearGradient>
            </defs>

            {/* Horizontal Grid Lines */}
            <line x1={paddingLeft} y1={paddingTop} x2={chartWidth - paddingRight} y2={paddingTop} stroke="rgba(255,255,255,0.06)" />
            <line x1={paddingLeft} y1={(chartHeight - paddingBottom + paddingTop) / 2} x2={chartWidth - paddingRight} y2={(chartHeight - paddingBottom + paddingTop) / 2} stroke="rgba(255,255,255,0.06)" />
            <line x1={paddingLeft} y1={chartHeight - paddingBottom} x2={chartWidth - paddingRight} y2={chartHeight - paddingBottom} stroke="rgba(255,255,255,0.12)" />

            {/* Y-Axis Balance Labels */}
            <text x={paddingLeft - 8} y={paddingTop + 4} fill="#64748b" fontSize="10" fontFamily="var(--font-mono)" textAnchor="end">
              {formatCurrency(maxVal)}
            </text>
            <text x={paddingLeft - 8} y={(chartHeight - paddingBottom + paddingTop) / 2 + 3} fill="#64748b" fontSize="10" fontFamily="var(--font-mono)" textAnchor="end">
              {formatCurrency((maxVal + minVal) / 2)}
            </text>
            <text x={paddingLeft - 8} y={chartHeight - paddingBottom + 3} fill="#64748b" fontSize="10" fontFamily="var(--font-mono)" textAnchor="end">
              {formatCurrency(minVal)}
            </text>

            {/* Minimum Balance Line */}
            {!isNaN(minLineY) && (
              <line
                x1={paddingLeft}
                y1={minLineY}
                x2={chartWidth - paddingRight}
                y2={minLineY}
                stroke="#f59e0b"
                strokeDasharray="4 4"
                strokeWidth="1.5"
              />
            )}

            {/* Area Gradient Fill */}
            {areaD && <path d={areaD} fill="url(#chartAreaGradient)" />}

            {/* Main Balance Line */}
            {pathD && <path d={pathD} fill="none" stroke="#00e5a3" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" />}

            {/* Point circles */}
            {points.map((p: { x: number; y: number; balance: number; date: string }, idx: number) => (
              <circle
                key={idx}
                cx={p.x}
                cy={p.y}
                r={idx === points.length - 1 ? 5 : 2.5}
                fill={idx === points.length - 1 ? '#00e5a3' : '#3b82f6'}
              />
            ))}

            {/* Lowest Drawdown Callout */}
            {lowestPoint && lowestPoint.y > paddingTop + 10 && (
              <g>
                <circle cx={lowestPoint.x} cy={lowestPoint.y} r={5} fill="#f59e0b" stroke="#0f172a" strokeWidth="2" />
                <text x={lowestPoint.x} y={Math.max(paddingTop + 12, lowestPoint.y - 10)} fill="#f59e0b" fontSize="10" fontWeight="700" fontFamily="var(--font-mono)" textAnchor="middle">
                  Min {formatCurrency(lowestPoint.balance)}
                </text>
              </g>
            )}

            {/* X-Axis Date Ticks */}
            {dateTickIndices.map((idx) => {
              const p = points[idx];
              if (!p) return null;
              return (
                <g key={idx}>
                  <line x1={p.x} y1={chartHeight - paddingBottom} x2={p.x} y2={chartHeight - paddingBottom + 5} stroke="rgba(255,255,255,0.2)" />
                  <text
                    x={p.x}
                    y={chartHeight - 12}
                    fill="#94a3b8"
                    fontSize="11"
                    fontFamily="var(--font-mono)"
                    textAnchor="middle"
                  >
                    {formatShortDate(p.date) || p.date}
                  </text>
                </g>
              );
            })}
          </svg>
        </div>

        <div className="chart-legend-row">
          <div className="legend-item">
            <span className="legend-dot green"></span>
            <span>Projected Balance</span>
          </div>
          <div className="legend-item">
            <span className="legend-dot dashed-amber"></span>
            <span>Minimum Projected ({formatCurrency(minProjBal)})</span>
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
          <div className="summary-value inflow-color">{formatCurrency(currentForecastItem.expected_inflow || 0)}</div>
          <div className="summary-hint">Projected income in next {selectedHorizon}d</div>
        </div>

        <div className="summary-card">
          <div className="summary-label">Expected Outflow</div>
          <div className="summary-value outflow-color">{formatCurrency(currentForecastItem.expected_outflow || 0)}</div>
          <div className="summary-hint">Detected expenses & bills</div>
        </div>

        <div className="summary-card">
          <div className="summary-label">Forecasted Minimum</div>
          <div className="summary-value warning-color">{formatCurrency(minProjBal)}</div>
          <div className="summary-hint">Lowest point in trajectory</div>
        </div>

        <div className="summary-card">
          <div className="summary-label">Safety Reserve</div>
          <div className="summary-value">{formatCurrency(safetyReserve)}</div>
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
                <th>Net Safe Margin</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {dailyBalances.map((item: DailyTrajectoryItem, idx: number) => {
                const prevBal = idx > 0 ? dailyBalances[idx - 1].balance : (forecastData as any)?.current_balance || item.balance;
                const delta = item.balance - prevBal;
                const netMargin = item.balance - item.requiredBuffer;

                const isCritical = item.balance < item.requiredBuffer;
                const isLow = item.balance < (item.requiredBuffer * 1.20);
                const isInflowSurge = delta > 1500;
                const isOutflowDip = delta < -1500;

                let statusLabel = 'Optimal';
                let statusClass = 'healthy';

                if (isCritical) {
                  statusLabel = 'Critical Risk';
                  statusClass = 'danger';
                } else if (isLow) {
                  statusLabel = 'Low Cushion';
                  statusClass = 'warning';
                } else if (isInflowSurge) {
                  statusLabel = 'Payday Peak';
                  statusClass = 'healthy-bright';
                } else if (isOutflowDip) {
                  statusLabel = 'Commitment Dip';
                  statusClass = 'info-badge';
                } else {
                  statusLabel = 'Optimal';
                  statusClass = 'healthy';
                }

                return (
                  <tr key={idx}>
                    <td className="font-mono">{formatShortDate(item.date) || item.date}</td>
                    <td className="font-mono bold-text">{formatCurrency(item.balance)}</td>
                    <td className="font-mono">{formatCurrency(item.requiredBuffer)}</td>
                    <td className={`font-mono bold-text ${netMargin < 0 ? 'outflow-color' : 'inflow-color'}`}>
                      {netMargin >= 0 ? `+${formatCurrency(netMargin)}` : formatCurrency(netMargin)}
                    </td>
                    <td>
                      <span className={`status-pill ${statusClass}`}>{statusLabel}</span>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
};
