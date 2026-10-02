import React, { useState, useEffect, useCallback } from 'react';
import { getActivityApi } from '../api/spendable';
import type { SpendableActivityListResponse, FinancialActivityItem } from '../api/types';
import { formatCurrency, formatDate } from '../utils/formatters';
import { Receipt, AlertTriangle, RefreshCw, ChevronLeft, ChevronRight } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

const ACTIVITY_CACHE_KEY_PREFIX = 'spendable_activity_cache_';

const getCachedActivityData = (accId?: string): SpendableActivityListResponse | null => {
  if (!accId) return null;
  try {
    const raw = localStorage.getItem(`${ACTIVITY_CACHE_KEY_PREFIX}${accId}`);
    return raw ? JSON.parse(raw) : null;
  } catch {
    return null;
  }
};

export const ActivityPage: React.FC = () => {
  const { currentUser } = useAuth();
  const [activityData, setActivityData] = useState<SpendableActivityListResponse | null>(() =>
    getCachedActivityData(currentUser?.account_id)
  );
  const [limit] = useState<number>(50);
  const [offset, setOffset] = useState<number>(0);
  const [isLoading, setIsLoading] = useState<boolean>(() => !getCachedActivityData(currentUser?.account_id));
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const cached = getCachedActivityData(currentUser?.account_id);
    if (cached) {
      setActivityData(cached);
      setIsLoading(false);
    } else {
      setActivityData(null);
      setIsLoading(true);
    }
  }, [currentUser?.account_id]);

  const fetchActivities = useCallback(async () => {
    const hasCache = !!getCachedActivityData(currentUser?.account_id);
    if (!hasCache) {
      setIsLoading(true);
    }
    setError(null);
    try {
      const res = await getActivityApi(limit, offset);
      setActivityData(res);
      if (currentUser?.account_id && offset === 0) {
        try {
          localStorage.setItem(`${ACTIVITY_CACHE_KEY_PREFIX}${currentUser.account_id}`, JSON.stringify(res));
        } catch {}
      }
    } catch (err: any) {
      if (!activityData && !hasCache) {
        setError(err.message || 'Failed to load transaction history.');
      }
    } finally {
      setIsLoading(false);
    }
  }, [currentUser?.account_id, limit, offset, activityData]);

  useEffect(() => {
    fetchActivities();
  }, [currentUser?.account_id, offset]);

  if (isLoading) {
    return (
      <div className="tab-pane">
        <div className="loading-skeleton-container">
          <div className="skeleton-hero"></div>
          <p className="loading-text">Loading observed transaction activity...</p>
        </div>
      </div>
    );
  }

  if (error || !activityData) {
    return (
      <div className="tab-pane">
        <div className="error-state-card">
          <AlertTriangle size={40} className="error-icon" />
          <h3>Activity Log Unavailable</h3>
          <p>{error || 'An error occurred fetching transaction history.'}</p>
          <button className="secondary-btn" onClick={fetchActivities}>
            <RefreshCw size={16} />
            <span>Retry</span>
          </button>
        </div>
      </div>
    );
  }

  const activities: FinancialActivityItem[] = activityData.activities || [];
  const totalCount = activityData.total_count || 0;

  return (
    <div className="tab-pane">
      <div className="page-header">
        <h2>Financial Activity</h2>
        <p className="subtitle">Observable account inflows, payments, and detected commitments.</p>
      </div>

      {activities.length === 0 ? (
        <div className="empty-state-card full-page-empty">
          <Receipt size={44} className="empty-icon" />
          <h3>No Activity Recorded Yet</h3>
          <p>This account does not contain historical transaction activity yet.</p>
        </div>
      ) : (
        <>
          <div className="table-header-meta">
            <span>
              Showing {offset + 1}–{Math.min(offset + activities.length, totalCount)} of {totalCount} transactions
            </span>
          </div>

          <div className="table-responsive-container">
            <table className="spendable-data-table">
              <thead>
                <tr>
                  <th>Date</th>
                  <th>Counterparty / Description</th>
                  <th>Category</th>
                  <th>Type</th>
                  <th>Amount</th>
                  <th>Balance After</th>
                </tr>
              </thead>
              <tbody>
                {activities.map((act, idx) => {
                  const isInflow = act.direction === 'INFLOW';
                  const rowKey = act.transaction_id || act.id || `act_${idx}`;
                  return (
                    <tr key={rowKey}>
                      <td className="font-mono text-dim">{formatDate(act.timestamp_utc)}</td>
                      <td className="bold-text">{act.counterparty_name || 'Observed Transaction'}</td>
                      <td>
                        <span className="category-pill">
                          {act.category || 'General'}
                        </span>
                      </td>
                      <td>
                        <span className="type-tag">{act.activity_type || 'GENERAL'}</span>
                      </td>
                      <td className={`font-mono ${isInflow ? 'inflow-color' : 'outflow-color'}`}>
                        {isInflow ? '+ ' : '− '}
                        {formatCurrency(act.amount)}
                      </td>
                      <td className="font-mono text-muted">
                        {act.balance_after !== undefined && act.balance_after !== null
                          ? formatCurrency(act.balance_after)
                          : '—'}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>

          {/* Pagination Controls */}
          {totalCount > limit && (
            <div className="pagination-bar">
              <button
                className="pagination-btn"
                onClick={() => setOffset(Math.max(0, offset - limit))}
                disabled={offset === 0}
              >
                <ChevronLeft size={16} />
                <span>Previous</span>
              </button>

              <span className="pagination-info">
                Page {Math.floor(offset / limit) + 1} of {Math.ceil(totalCount / limit)}
              </span>

              <button
                className="pagination-btn"
                onClick={() => setOffset(offset + limit)}
                disabled={offset + limit >= totalCount}
              >
                <span>Next</span>
                <ChevronRight size={16} />
              </button>
            </div>
          )}
        </>
      )}
    </div>
  );
};
