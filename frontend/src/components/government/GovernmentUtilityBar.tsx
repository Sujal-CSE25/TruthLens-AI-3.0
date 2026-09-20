import React, { useState } from 'react';
import { ExternalLink, Accessibility, ChevronDown, Globe, Check } from 'lucide-react';
import { useLanguage } from '../../context/LanguageContext';

interface GovernmentUtilityBarProps {
  onFontScale: (scale: number) => void;
  currentScale: number;
}

export const GovernmentUtilityBar: React.FC<GovernmentUtilityBarProps> = ({ onFontScale, currentScale }) => {
  const [langOpen, setLangOpen] = useState(false);
  const { language, setLanguage, t } = useLanguage();

  const handleLanguageChange = (lang: 'en' | 'hi') => {
    setLanguage(lang);
    setLangOpen(false);
  };

  return (
    <nav className="gov-utility-bar" role="navigation" aria-label="Government utility bar">
      <div className="container">
        <div className="gov-utility-left">
          <img
            src="/flag-of-india.svg"
            alt="Flag of India"
            className="gov-flag-img"
            width={20}
            height={14}
          />
          <a
            href="https://india.gov.in"
            target="_blank"
            rel="noopener noreferrer"
            aria-label="Government of India - opens in new tab"
          >
            {t('gov.title')}
            <ExternalLink size={10} aria-hidden="true" />
          </a>
          <span aria-hidden="true" style={{ color: 'rgba(255,255,255,0.3)' }}>·</span>
          <span style={{ fontSize: '11px', color: 'rgba(255,255,255,0.7)', fontStyle: 'italic' }}>
            {t('gov.hindiTitle')}
          </span>
        </div>

        <div className="gov-utility-right">
          <a
            href="#main-content"
            className="gov-util-btn"
            style={{ color: 'rgba(255,255,255,0.85)' }}
          >
            {t('gov.skip')}
          </a>
          <span className="divider" aria-hidden="true" />

          {/* Page Zoom & Font size controls */}
          <button
            className="gov-util-btn font-btn"
            onClick={() => onFontScale(Math.max(0.75, +(currentScale - 0.1).toFixed(2)))}
            aria-label="Zoom out (Decrease size)"
            title="Zoom out (Decrease size)"
            style={{
              fontWeight: 700,
              background: currentScale < 1 ? 'rgba(255,255,255,0.2)' : 'transparent',
            }}
          >
            A−
          </button>
          <button
            className="gov-util-btn font-btn"
            onClick={() => onFontScale(1)}
            aria-label="Reset zoom to 100%"
            title="Reset zoom to 100%"
            aria-current={currentScale === 1 ? 'true' : undefined}
            style={{
              fontWeight: 700,
              background: currentScale === 1 ? 'rgba(255,255,255,0.25)' : 'transparent',
              textDecoration: currentScale === 1 ? 'underline' : 'none',
            }}
          >
            A
          </button>
          <button
            className="gov-util-btn font-btn"
            onClick={() => onFontScale(Math.min(1.35, +(currentScale + 0.1).toFixed(2)))}
            aria-label="Zoom in (Increase size)"
            title="Zoom in (Increase size)"
            style={{
              fontWeight: 700,
              background: currentScale > 1 ? 'rgba(255,255,255,0.2)' : 'transparent',
            }}
          >
            A+
          </button>


          <span className="divider" aria-hidden="true" />

          <button
            className="gov-util-btn"
            aria-label="Accessibility options"
            title="Accessibility options"
          >
            <Accessibility size={13} aria-hidden="true" />
            <span className="sr-only">Accessibility</span>
          </button>

          <span className="divider" aria-hidden="true" />

          {/* Language selector: English & Hindi only */}
          <div style={{ position: 'relative' }}>
            <button
              className="gov-util-btn"
              aria-label="Select language"
              aria-expanded={langOpen}
              onClick={() => setLangOpen(o => !o)}
              style={{ fontWeight: 600, color: '#ffffff' }}
            >
              <Globe size={13} aria-hidden="true" />
              {language === 'hi' ? 'हिन्दी' : 'English'}
              <ChevronDown size={11} aria-hidden="true" />
            </button>
            {langOpen && (
              <div
                style={{
                  position: 'absolute',
                  top: '100%',
                  right: 0,
                  background: 'white',
                  border: '1px solid var(--c-border)',
                  borderRadius: 'var(--r-md)',
                  boxShadow: 'var(--shadow-elevated)',
                  padding: '4px',
                  minWidth: '130px',
                  zIndex: 999,
                }}
                role="menu"
              >
                {[
                  { code: 'en', label: 'English' },
                  { code: 'hi', label: 'हिन्दी' },
                ].map(({ code, label }) => (
                  <button
                    key={code}
                    role="menuitem"
                    onClick={() => handleLanguageChange(code as 'en' | 'hi')}
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between',
                      width: '100%',
                      padding: '7px 12px',
                      background: language === code ? 'var(--c-light-blue)' : 'none',
                      border: 'none',
                      textAlign: 'left',
                      font: 'var(--font)',
                      fontSize: '13px',
                      fontWeight: language === code ? 700 : 500,
                      color: language === code ? 'var(--c-blue)' : 'var(--c-text)',
                      cursor: 'pointer',
                      borderRadius: 'var(--r-sm)',
                    }}
                  >
                    <span>{label}</span>
                    {language === code && <Check size={14} color="var(--c-blue)" />}
                  </button>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
};

export default GovernmentUtilityBar;

