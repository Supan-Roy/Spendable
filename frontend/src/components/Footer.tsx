import React from 'react';
import { Info } from 'lucide-react';

export const Footer: React.FC = () => {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="product-footer">
      <div className="footer-disclaimer">
        <Info size={14} className="disclaimer-icon" />
        <span>
          <strong>Product Disclaimer:</strong> Spendable is an estimate based on observed account activity. It does not include cash, external accounts, or unobserved liabilities.
        </span>
      </div>

      <div className="footer-container">
        <div className="footer-left">
          <img src="/logo.svg" alt="Spendable Logo" className="footer-logo-img" draggable={false} />
          <span className="footer-brand-text">Spendable</span>
          <span className="footer-divider">•</span>
          <span className="footer-tagline">Personal Liquidity Intelligence Engine</span>
        </div>
        <div className="footer-right">
          © {currentYear} Spendable. All rights reserved.
        </div>
      </div>
    </footer>
  );
};
