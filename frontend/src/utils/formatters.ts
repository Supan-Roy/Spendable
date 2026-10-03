/**
 * Utility functions for currency formatting (BDT ৳), numbers, dates, and liquidity badges.
 */

export function formatCurrency(amount: number | null | undefined): string {
  if (amount === null || amount === undefined || isNaN(amount)) {
    return '৳0';
  }
  const rounded = Math.round(amount);
  return `৳${rounded.toLocaleString('en-US')}`;
}

export function formatCurrencyExact(amount: number | null | undefined): string {
  if (amount === null || amount === undefined || isNaN(amount)) {
    return '৳0.00';
  }
  return `৳${amount.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
}

export function formatDateTime(isoDateStr: string | null | undefined): string {
  if (!isoDateStr) return '—';
  try {
    const d = new Date(isoDateStr);
    if (isNaN(d.getTime())) return isoDateStr;
    const dateStr = d.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    });
    const timeStr = d.toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
      hour12: true,
    });
    return `${dateStr}, ${timeStr}`;
  } catch {
    return isoDateStr;
  }
}

export function formatDate(isoDateStr: string | null | undefined): string {
  if (!isoDateStr) return '—';
  try {
    const d = new Date(isoDateStr);
    if (isNaN(d.getTime())) return isoDateStr;
    if (isoDateStr.includes('T') || isoDateStr.includes(':')) {
      return formatDateTime(isoDateStr);
    }
    return d.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    });
  } catch {
    return isoDateStr;
  }
}

export function formatTime(isoDateStr: string | null | undefined): string {
  if (!isoDateStr) return '';
  try {
    const d = new Date(isoDateStr);
    if (isNaN(d.getTime())) return '';
    return d.toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
      hour12: true,
    });
  } catch {
    return '';
  }
}

export function formatShortDate(isoDateStr: string | null | undefined): string {
  if (!isoDateStr) return '';
  try {
    const d = new Date(isoDateStr);
    if (isNaN(d.getTime())) return isoDateStr;
    return `${d.getMonth() + 1}/${d.getDate()}`;
  } catch {
    return isoDateStr;
  }
}

export function getLiquidityBadgeConfig(state: string | null | undefined): {
  label: string;
  className: string;
  color: string;
  description: string;
} {
  const s = (state || 'HEALTHY').toUpperCase();
  switch (s) {
    case 'HEALTHY':
      return {
        label: 'HEALTHY',
        className: 'badge-healthy',
        color: '#00e5a3',
        description: 'Sufficient safe liquidity for projected horizon',
      };
    case 'WATCH':
      return {
        label: 'WATCH',
        className: 'badge-watch',
        color: '#f59e0b',
        description: 'Elevated spending or upcoming obligation pressure detected',
      };
    case 'PRESSURED':
      return {
        label: 'PRESSURED',
        className: 'badge-pressured',
        color: '#ef4444',
        description: 'High commitments or low balance cushion risk',
      };
    default:
      return {
        label: 'HEALTHY',
        className: 'badge-healthy',
        color: '#00e5a3',
        description: 'Liquidity state normal',
      };
  }
}
