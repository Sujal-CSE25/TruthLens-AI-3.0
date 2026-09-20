import React, { useState, useEffect } from 'react';
import { Calendar, RefreshCw, Database, Globe, ChevronDown } from 'lucide-react';
import { useLanguage } from '../../context/LanguageContext';

const formatLiveDateTime = (lang: string): string => {
  try {
    const now = new Date();
    const formattedDate = new Intl.DateTimeFormat(lang === 'hi' ? 'hi-IN' : 'en-GB', {
      day: '2-digit',
      month: 'short',
      year: 'numeric',
    }).format(now);

    const formattedTime = new Intl.DateTimeFormat(lang === 'hi' ? 'hi-IN' : 'en-GB', {
      hour: '2-digit',
      minute: '2-digit',
      hour12: false,
    }).format(now);

    return `${formattedDate}, ${formattedTime} IST`;
  } catch {
    return new Date().toLocaleString();
  }
};

export const SystemInfoStrip: React.FC = () => {
  const { language, t } = useLanguage();
  const [currentDateTime, setCurrentDateTime] = useState<string>(() => formatLiveDateTime(language));
  const [showFreshnessNotice, setShowFreshnessNotice] = useState<boolean>(false);

  useEffect(() => {
    setCurrentDateTime(formatLiveDateTime(language));
    const timer = setInterval(() => {
      setCurrentDateTime(formatLiveDateTime(language));
    }, 60000);
    return () => clearInterval(timer);
  }, [language]);


  return (
    <div className="system-strip" role="complementary" aria-label="System status information">
      <div className="system-strip-inner">
        <div className="system-strip-items">
          <div className="system-strip-item">
            <Calendar size={14} className="strip-icon" aria-hidden="true" />
            <div>
              <div className="strip-label">{t('strip.dataUpdated')}</div>
              <div className="strip-value">{currentDateTime}</div>
            </div>
          </div>

          <div className="system-strip-item">
            <RefreshCw size={14} className="strip-icon" aria-hidden="true" />
            <div>
              <div className="strip-label">{t('strip.nextCycle')}</div>
              <div className="strip-value">+3h 00m</div>
            </div>
          </div>

          <div className="system-strip-item">
            <Database size={14} className="strip-icon" aria-hidden="true" />
            <div>
              <div className="strip-label">{t('strip.dataSources')}</div>
              <div className="strip-value" style={{ display: 'flex', alignItems: 'center', gap: '5px' }}>
                <span className="strip-status-dot" aria-hidden="true" />
                {t('strip.allSynced')}
              </div>
            </div>
          </div>

          <div className="system-strip-item">
            <Globe size={14} className="strip-icon" aria-hidden="true" />
            <div>
              <div className="strip-label">{t('strip.region')}</div>
              <div className="strip-value">{t('strip.india')}</div>
            </div>
          </div>
        </div>

        <button
          className="view-freshness-btn"
          aria-label="View system status details"
          onClick={() => setShowFreshnessNotice(!showFreshnessNotice)}
        >
          <Calendar size={13} aria-hidden="true" />
          {t('strip.viewFreshness')}
          <ChevronDown
            size={12}
            aria-hidden="true"
            style={{
              transform: showFreshnessNotice ? 'rotate(180deg)' : 'rotate(0deg)',
              transition: 'transform 0.2s ease',
            }}
          />
        </button>
      </div>

      {showFreshnessNotice && (
        <div
          style={{
            maxWidth: '1400px',
            margin: '8px auto 0',
            padding: '8px 16px',
            background: 'var(--c-surface)',
            border: '1px solid var(--c-border)',
            borderRadius: 'var(--r-sm)',
            fontSize: '12px',
            color: 'var(--c-text-secondary)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
          }}
        >
          <span>
            {t('strip.syncNotice')} <strong>{currentDateTime}</strong>.
          </span>
          <span style={{ color: 'var(--c-success)', fontWeight: 600 }}>{t('strip.operational')}</span>
        </div>
      )}

    </div>
  );
};

export default SystemInfoStrip;

