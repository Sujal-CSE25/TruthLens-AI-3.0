import React from 'react';
import { ChevronDown } from 'lucide-react';
import { useLanguage } from '../../context/LanguageContext';

// TruthLens Shield SVG Logo
export const TruthLensShieldLogo: React.FC<{ size?: number }> = ({ size = 56 }) => (
  <svg
    width={size}
    height={Math.round(size * 1.1)}
    viewBox="0 0 56 62"
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
    aria-label="TruthLens AI shield logo"
    role="img"
  >
    {/* Shield outline */}
    <path
      d="M28 2L4 11.5V30C4 44.5 14.5 57.5 28 61C41.5 57.5 52 44.5 52 30V11.5L28 2Z"
      fill="#EAF2FF"
      stroke="#0B2A5B"
      strokeWidth="2.5"
    />
    {/* Inner shield highlight */}
    <path
      d="M28 7L8 15.5V30C8 42.5 16.5 53 28 56.5C39.5 53 48 42.5 48 30V15.5L28 7Z"
      fill="#1D63C8"
      opacity="0.15"
    />
    {/* Checkmark */}
    <path
      d="M17 30L24 37L40 21"
      stroke="#1D63C8"
      strokeWidth="3.5"
      strokeLinecap="round"
      strokeLinejoin="round"
    />
    {/* Lens circle */}
    <circle cx="28" cy="29" r="11" stroke="#0B2A5B" strokeWidth="2" fill="none" opacity="0.3" />
  </svg>
);

// State Emblem of India
export const AshokaEmblem: React.FC<{ size?: number }> = ({ size = 52 }) => (
  <img
    src="/emblem-of-india.svg"
    alt="State Emblem of India"
    width={size}
    height={Math.round(size * 1.55)}
    className="ministry-emblem"
  />
);

// Official Digital India Logo
export const DigitalIndiaLogo: React.FC<{ height?: number }> = ({ height = 38 }) => (
  <div style={{
    display: 'flex',
    alignItems: 'center',
    padding: '2px 8px',
    background: 'white',
    borderRadius: '6px',
    border: '1px solid #D8E0EA',
  }}>
    <img
      src="/digital-india.svg"
      alt="Digital India - Power To Empower"
      style={{
        height: `${height}px`,
        width: 'auto',
        objectFit: 'contain',
        display: 'block',
      }}
    />
  </div>
);


interface InstitutionalHeaderProps {
  onAdminClick?: () => void;
}

export const InstitutionalHeader: React.FC<InstitutionalHeaderProps> = ({ onAdminClick }) => {
  const { t } = useLanguage();

  return (
    <header className="brand-header" role="banner">
      <div className="brand-header-inner">
        <div className="brand-left">
          {/* Ministry block */}
          <div className="ministry-block">
            <AshokaEmblem size={52} />
            <div className="ministry-text">
              <span className="ministry-name" style={{ whiteSpace: 'pre-line' }}>
                {t('header.ministry')}
              </span>
              <span className="ministry-sub">{t('header.gov')}</span>
            </div>
          </div>

          {/* Product block */}
          <div className="product-block">
            <TruthLensShieldLogo size={56} />
            <div className="product-text">
              <div className="product-name">TruthLens AI 3.0</div>
              <div className="product-tagline">{t('header.tagline')}</div>
              <div className="product-badges">
                <span className="badge-sih">SIH 2026</span>
                <span className="badge-ps">PS 26188</span>
                <span className="badge-proto">Prototype</span>

              </div>
            </div>
          </div>
        </div>

        <div className="brand-right">
          <DigitalIndiaLogo />
          <button
            className="admin-btn"
            onClick={onAdminClick}
            aria-label="TruthLens Admin panel"
          >
            <div className="admin-avatar" aria-hidden="true">TL</div>
            <div className="admin-info">
              <div className="admin-name">{t('header.admin')}</div>
              <div className="admin-role">{t('header.role')}</div>
            </div>
            <ChevronDown size={14} color="var(--c-text-muted)" aria-hidden="true" />
          </button>
        </div>
      </div>
    </header>
  );
};


export default InstitutionalHeader;
