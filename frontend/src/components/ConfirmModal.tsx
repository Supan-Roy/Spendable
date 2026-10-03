import React from 'react';
import { AlertTriangle, Trash2, Info, X } from 'lucide-react';

export interface ConfirmModalProps {
  isOpen: boolean;
  title: string;
  message: string;
  confirmText?: string;
  cancelText?: string;
  variant?: 'danger' | 'warning' | 'info';
  isLoading?: boolean;
  onConfirm: () => void;
  onCancel: () => void;
}

export const ConfirmModal: React.FC<ConfirmModalProps> = ({
  isOpen,
  title,
  message,
  confirmText = 'Confirm',
  cancelText = 'Cancel',
  variant = 'danger',
  isLoading = false,
  onConfirm,
  onCancel,
}) => {
  if (!isOpen) return null;

  const renderIcon = () => {
    switch (variant) {
      case 'danger':
        return <Trash2 size={26} />;
      case 'warning':
        return <AlertTriangle size={26} />;
      case 'info':
      default:
        return <Info size={26} />;
    }
  };

  return (
    <div className="modal-overlay" onClick={onCancel}>
      <div className="modal-card confirm-modal-card" onClick={(e) => e.stopPropagation()}>
        <button className="modal-close" onClick={onCancel} style={{ position: 'absolute', right: '1.25rem', top: '1.25rem' }}>
          <X size={18} />
        </button>

        <div className={`confirm-icon-badge ${variant}`}>
          {renderIcon()}
        </div>

        <h3>{title}</h3>
        <p>{message}</p>

        <div className="confirm-actions">
          <button className="secondary-btn" onClick={onCancel} disabled={isLoading}>
            {cancelText}
          </button>

          <button
            className={variant === 'danger' ? 'danger-btn' : 'primary-btn'}
            onClick={onConfirm}
            disabled={isLoading}
          >
            {isLoading ? 'Processing...' : confirmText}
          </button>
        </div>
      </div>
    </div>
  );
};
