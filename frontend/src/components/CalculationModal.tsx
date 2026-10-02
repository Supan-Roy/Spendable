import React from 'react';
import { Shield, X, Info } from 'lucide-react';

interface CalculationModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const CalculationModal: React.FC<CalculationModalProps> = ({ isOpen, onClose }) => {
  if (!isOpen) return null;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-card" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Shield size={20} color="#00e5a3" />
            <h3>How Spendable Is Calculated</h3>
          </div>
          <button className="modal-close" onClick={onClose}>
            <X size={18} />
          </button>
        </div>
        <div className="modal-body">
          <p>
            Spendable calculates how much money you can safely spend over the next 30 days without risking upcoming obligations or cash-flow pressure.
          </p>
          <div className="calc-formula-box">
            <div className="formula-row">+ Current Observable Balance</div>
            <div className="formula-row">+ Expected Short-Term Inflows</div>
            <div className="formula-row minus">- Upcoming Commitments & Bills</div>
            <div className="formula-row minus">- Expected Essential Outflows</div>
            <div className="formula-row minus">- Protected Safety Reserve</div>
            <div className="formula-result">= Estimated Safe Spendable Amount</div>
          </div>
          <div className="data-honesty-note">
            <Info size={16} style={{ flexShrink: 0, marginTop: '2px' }} />
            <span>
              Spendable estimates are based exclusively on observed account activity. Unrecorded cash or external accounts are not included.
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};
