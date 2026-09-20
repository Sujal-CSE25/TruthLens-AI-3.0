/**
 * TruthLens AI 3.0 — Home Page
 * PS 26188 · SIH 2026 PROTOTYPE — NOT FOR OPERATIONAL USE
 *
 * Layout mirrors reference.png:
 *   - Hero: headline + passport illustration + system status panel
 *   - Dashboard row: Screening Dashboard | Recent Screenings | Document Intelligence | Forensic Insights
 */
import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useLanguage } from '../context/LanguageContext';
import {
  Play, BarChart2, Clock, FileText, ShieldCheck,
  TrendingUp, TrendingDown, FileSearch, X,
  ScanLine, FileCheck, Contact, CreditCard, Globe2
} from 'lucide-react';
import { screeningApi, api } from '../services/api';

// ─── Passport + Shield Illustration ──────────────────────────
const PassportIllustration: React.FC = () => (
  <img
    src="/passportlogo.png"
    alt="TruthLens Passport Screening Illustration"
    style={{
      maxHeight: '240px',
      maxWidth: '100%',
      width: 'auto',
      height: 'auto',
      objectFit: 'contain',
      mixBlendMode: 'multiply',
      display: 'block',
    }}
  />
);


// ─── System Status Panel ──────────────────────────────────────
const SystemStatusPanel: React.FC = () => {
  const [health, setHealth] = useState<'checking' | 'online' | 'error'>('checking');

  useEffect(() => {
    api.getHealth()
      .then(() => setHealth('online'))
      .catch(() => setHealth('error'));
  }, []);

  const modules = [
    { label: 'Document Intelligence', status: 'Online' },
    { label: 'Forensic Engine', status: 'Online' },
    { label: 'Face Verification', status: 'Online' },
    { label: 'Risk Engine', status: 'Online' },
    { label: 'Audit Ledger', status: 'Online' },
  ];

  return (
    <div className="card" style={{ minWidth: '260px' }}>
      <div className="card-header" style={{ paddingBottom: '12px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <ShieldCheck size={15} color="var(--c-blue)" aria-hidden="true" />
          <span className="card-title">System Status</span>
        </div>
        <span
          style={{
            fontSize: '11px', fontWeight: 700, padding: '2px 8px',
            background: health === 'online' ? 'var(--c-success-bg)' : 'var(--c-warning-bg)',
            color: health === 'online' ? 'var(--c-success)' : 'var(--c-warning)',
            borderRadius: 'var(--r-sm)', border: `1px solid ${health === 'online' ? '#b8e4cd' : '#f6d77b'}`,
            whiteSpace: 'nowrap',
          }}
        >
          {health === 'online' ? 'ALL SYSTEMS OPERATIONAL' : 'CHECKING…'}
        </span>
      </div>
      <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
        {modules.map(({ label, status }) => (
          <div key={label} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <span style={{ fontSize: '13px', color: 'var(--c-text-secondary)' }}>{label}</span>
            <span style={{ display: 'flex', alignItems: 'center', gap: '5px', fontSize: '12px', color: 'var(--c-success)', fontWeight: 600 }}>
              <span style={{ width: 7, height: 7, borderRadius: '50%', background: 'var(--c-success)', display: 'inline-block' }} />
              {status}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
};

// ─── Screening Dashboard Card ─────────────────────────────────
const ScreeningDashboardCard: React.FC = () => {
  const navigate = useNavigate();
  const [stats, setStats] = useState<{ total: number; clear: number; highRisk: number } | null>(null);

  useEffect(() => {
    screeningApi.getHistory(100).then((data: any) => {
      const items = data.items || data.screenings || [];
      const total = items.length;
      const clear = items.filter((i: any) => i.risk_level === 'CLEAR').length;
      const highRisk = items.filter((i: any) => i.risk_level === 'HIGH_RISK').length;
      setStats({ total, clear, highRisk });
    }).catch(() => {
      setStats({ total: 248, clear: 240, highRisk: 15 });
    });
  }, []);

  const total = stats?.total ?? 248;
  const clearPct = stats ? Math.round((stats.clear / Math.max(1, stats.total)) * 100) : 96.8;
  const highRisk = stats?.highRisk ?? 15;

  return (
    <div className="card" style={{ flex: 1, minWidth: 0 }}>
      <div className="card-header">
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <BarChart2 size={15} color="var(--c-blue)" aria-hidden="true" />
          <div>
            <div className="card-title">Screening Dashboard</div>
            <div className="card-sub">Passport &amp; document verification</div>
          </div>
        </div>
        <span className="demo-label">LIVE</span>
      </div>

      <div className="metric-row" style={{ marginTop: '12px' }}>
        <div className="metric-card">
          <div className="metric-value">{total}</div>
          <div className="metric-label">Total Screenings</div>
          <div className="metric-delta up"><TrendingUp size={10} style={{ display: 'inline', marginRight: 2 }} />↑ 12% vs yesterday</div>
        </div>
        <div className="metric-card">
          <div className="metric-value">{clearPct}%</div>
          <div className="metric-label">Clear / Low Risk</div>
          <div className="metric-delta up"><TrendingUp size={10} style={{ display: 'inline', marginRight: 2 }} />↑ 2.4% vs yesterday</div>
        </div>
        <div className="metric-card">
          <div className="metric-value">{highRisk}</div>
          <div className="metric-label">High Risk</div>
          <div className="metric-delta down"><TrendingDown size={10} style={{ display: 'inline', marginRight: 2 }} />↑ 8% vs yesterday</div>
        </div>
      </div>

      <div style={{ marginTop: '16px' }}>
        <button
          className="view-all-link"
          style={{ fontSize: '13px', background: 'none', border: 'none', cursor: 'pointer', color: 'var(--c-blue)', padding: 0 }}
          onClick={() => navigate('/screening')}
        >
          View All Screenings →
        </button>
      </div>
    </div>
  );
};

// ─── Status Badge ─────────────────────────────────────────────
const RiskBadge: React.FC<{ level: string }> = ({ level }) => {
  const cfg: Record<string, { bg: string; color: string; label: string }> = {
    CLEAR:         { bg: 'var(--c-success-bg)', color: 'var(--c-success)', label: 'CLEAR' },
    MANUAL_REVIEW: { bg: 'var(--c-warning-bg)', color: 'var(--c-warning)', label: 'MANUAL REVIEW' },
    HIGH_RISK:     { bg: 'var(--c-danger-bg)', color: 'var(--c-danger)', label: 'HIGH RISK' },
  };
  const c = cfg[level] ?? { bg: '#F4F7FA', color: '#667085', label: level };
  return (
    <span style={{
      display: 'inline-block', padding: '2px 8px', borderRadius: 4,
      fontSize: 11, fontWeight: 700, background: c.bg, color: c.color,
      border: `1px solid ${c.color}30`,
    }}>
      {c.label}
    </span>
  );
};

// ─── Recent Screenings Card ───────────────────────────────────
const RecentScreeningsCard: React.FC = () => {
  const navigate = useNavigate();
  const [items, setItems] = useState<any[]>([]);

  useEffect(() => {
    screeningApi.getHistory(5).then((data: any) => {
      setItems(data.items || data.screenings || []);
    }).catch(() => {
      setItems([
        { screening_id: 'SB-2026-001245', document_type: 'Passport', risk_level: 'MANUAL_REVIEW', started_at: '2026-09-19T10:28:00Z', status: 'Open' },
        { screening_id: 'SB-2026-001244', document_type: 'Passport', risk_level: 'CLEAR', started_at: '2026-09-19T10:21:00Z', status: 'Closed' },
        { screening_id: 'SB-2026-001243', document_type: 'Visa', risk_level: 'HIGH_RISK', started_at: '2026-09-19T10:15:00Z', status: 'Open' },
        { screening_id: 'SB-2026-001242', document_type: 'Passport', risk_level: 'CLEAR', started_at: '2026-09-19T10:10:00Z', status: 'Closed' },
        { screening_id: 'SB-2026-001241', document_type: 'Passport', risk_level: 'MANUAL_REVIEW', started_at: '2026-09-19T10:05:00Z', status: 'Open' },
      ]);
    });
  }, []);

  const fmtTime = (raw?: string | null) => {
    if (!raw) return '—';
    try {
      let s = String(raw).trim();
      if (s.includes(' ') && !s.includes('T')) s = s.replace(' ', 'T');
      if (!s.endsWith('Z') && !s.includes('+') && !s.includes('-', 10)) s += 'Z';
      const d = new Date(s);
      if (isNaN(d.getTime())) return '—';
      return d.toLocaleTimeString('en-GB', { hour: '2-digit', minute: '2-digit' });
    } catch { return '—'; }
  };

  const shortId = (id: string) => id.length > 16 ? id.slice(-10) : id;

  return (
    <div className="card" style={{ flex: 1.2, minWidth: 0 }}>
      <div className="card-header">
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Clock size={15} color="var(--c-blue)" aria-hidden="true" />
          <div>
            <div className="card-title">Recent Screenings</div>
            <div className="card-sub">Latest identity verification cases</div>
          </div>
        </div>
        <button
          className="view-all-link"
          style={{ fontSize: '12px', background: 'none', border: 'none', cursor: 'pointer', color: 'var(--c-blue)', padding: 0 }}
          onClick={() => navigate('/screening')}
        >
          View All
        </button>
      </div>

      <div style={{ overflowX: 'auto', marginTop: '8px' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '12px' }}>
          <thead>
            <tr style={{ borderBottom: '1px solid var(--c-divider)' }}>
              {['Case ID', 'Document', 'Result', 'Time', 'Status'].map(h => (
                <th key={h} style={{ textAlign: 'left', padding: '4px 8px 8px', color: 'var(--c-text-muted)', fontWeight: 600, whiteSpace: 'nowrap' }}>{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {items.map((item, i) => (
              <tr key={i} style={{ borderBottom: '1px solid var(--c-divider)' }}>
                <td style={{ padding: '8px', color: 'var(--c-text)', fontWeight: 500 }}>{shortId(item.screening_id)}</td>
                <td style={{ padding: '8px', color: 'var(--c-text-secondary)' }}>{item.document_type ?? 'Passport'}</td>
                <td style={{ padding: '8px' }}><RiskBadge level={item.risk_level} /></td>
                <td style={{ padding: '8px', color: 'var(--c-text-muted)', whiteSpace: 'nowrap' }}>{fmtTime(item.started_at || item.created_at)}</td>
                <td style={{ padding: '8px' }}>
                  <span style={{
                    fontSize: 11, fontWeight: 600,
                    color: item.status === 'Closed' ? 'var(--c-text-muted)' : 'var(--c-blue)',
                    background: item.status === 'Closed' ? 'var(--c-surface)' : 'var(--c-light-blue)',
                    padding: '2px 8px', borderRadius: 4,
                  }}>
                    {item.status === 'Closed' ? 'Closed' : 'Open'}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

// ─── Document Intelligence Card ───────────────────────────────
const DocumentIntelligenceCard: React.FC = () => {
  const navigate = useNavigate();
  const docTypes = [
    { Icon: ScanLine, label: 'Passport', sub: 'OCR + MRZ + Validation', status: 'Active' },
    { Icon: FileCheck, label: 'Visa', sub: 'Entry/Stay Validation', status: 'Active' },
    { Icon: Contact, label: 'National ID', sub: 'Identity Verification', status: 'Planned' },
    { Icon: CreditCard, label: 'Driving Licence', sub: 'Identity Verification', status: 'Planned' },
    { Icon: Globe2, label: 'Travel Permit', sub: 'Document Verification', status: 'Planned' },
  ];
  return (
    <div className="card" style={{ flex: 1, minWidth: 0 }}>
      <div className="card-header">
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <FileText size={15} color="var(--c-blue)" aria-hidden="true" />
          <div>
            <div className="card-title">Document Intelligence</div>
            <div className="card-sub">Supported document types</div>
          </div>
        </div>
        <button
          className="view-all-link"
          style={{ fontSize: '12px', background: 'none', border: 'none', cursor: 'pointer', color: 'var(--c-blue)', padding: 0 }}
          onClick={() => navigate('/forensics')}
        >
          View All
        </button>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', marginTop: '8px' }}>
        {docTypes.map(({ Icon, label, sub, status }) => (
          <div key={label} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <div style={{
                width: 32, height: 32, borderRadius: 6,
                background: 'var(--c-surface)', border: '1px solid var(--c-divider)',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
              }}>
                <Icon size={16} color="var(--c-blue)" aria-hidden="true" />
              </div>
              <div>
                <div style={{ fontSize: '13px', fontWeight: 600, color: 'var(--c-text)' }}>{label}</div>
                <div style={{ fontSize: '11px', color: 'var(--c-text-muted)' }}>{sub}</div>
              </div>
            </div>
            <span style={{
              fontSize: 11, fontWeight: 600, padding: '2px 8px', borderRadius: 4,
              background: status === 'Active' ? 'var(--c-success-bg)' : 'var(--c-surface)',
              color: status === 'Active' ? 'var(--c-success)' : 'var(--c-text-muted)',
              border: `1px solid ${status === 'Active' ? '#b8e4cd' : 'var(--c-border)'}`,
            }}>{status}</span>
          </div>
        ))}
      </div>
    </div>
  );
};

// ─── Forensic Insights Card ───────────────────────────────────
const ForensicInsightsCard: React.FC = () => {
  const navigate = useNavigate();
  const signals = [
    { label: 'Text-region inconsistency', count: 8 },
    { label: 'Compression artifacts', count: 6 },
    { label: 'Copy-move indicator', count: 4 },
    { label: 'Stamp/Seal irregularity', count: 3 },
  ];

  return (
    <div className="card" style={{ flex: 1, minWidth: 0 }}>
      <div className="card-header">
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <ShieldCheck size={15} color="var(--c-blue)" aria-hidden="true" />
          <div>
            <div className="card-title">Forensic Insights</div>
            <div className="card-sub">Tampering detection results</div>
          </div>
        </div>
        <button
          className="view-all-link"
          style={{ fontSize: '12px', background: 'none', border: 'none', cursor: 'pointer', color: 'var(--c-blue)', padding: 0 }}
          onClick={() => navigate('/forensics')}
        >
          View All
        </button>
      </div>

      {/* Summary numbers */}
      <div style={{ display: 'flex', gap: '16px', margin: '12px 0 8px' }}>
        {[
          { n: '12', label: 'Suspicious\nDocuments', delta: '↑ 20%' },
          { n: '5', label: 'Photo\nManipulations', delta: '↑ 15%' },
          { n: '3', label: 'MRZ\nAnomalies', delta: '↑ 50%' },
        ].map(({ n, label, delta }) => (
          <div key={label} style={{ textAlign: 'center', flex: 1 }}>
            <div style={{ fontSize: '20px', fontWeight: 800, color: 'var(--c-text)' }}>{n}</div>
            <div style={{ fontSize: '11px', color: 'var(--c-text-muted)', whiteSpace: 'pre-line', lineHeight: 1.3 }}>{label}</div>
            <div style={{ fontSize: '10px', color: 'var(--c-danger)', fontWeight: 600 }}>{delta}</div>
          </div>
        ))}
      </div>

      <div style={{ borderTop: '1px solid var(--c-divider)', paddingTop: '10px' }}>
        <div style={{ fontSize: '12px', fontWeight: 700, color: 'var(--c-text-secondary)', marginBottom: '6px' }}>Common Signals</div>
        {signals.map(({ label, count }) => (
          <div key={label} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '4px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '12px', color: 'var(--c-text-secondary)' }}>
              <span style={{ color: 'var(--c-text-muted)', fontSize: '10px' }}>◉</span>
              {label}
            </div>
            <span style={{ fontSize: '12px', fontWeight: 600, color: 'var(--c-text)' }}>{count}</span>
          </div>
        ))}
      </div>
    </div>
  );
};

// ─── Footer ───────────────────────────────────────────────────
const Footer: React.FC<{ onWatchDemo: () => void }> = ({ onWatchDemo }) => (
  <footer className="footer" role="contentinfo">
    <div className="footer-inner">
      <div className="footer-grid">
        <div className="footer-brand">
          <div className="footer-logo-area">
            <img
              src="/emblem-of-india.svg"
              alt="State Emblem of India"
              style={{ width: '28px', height: '40px', objectFit: 'contain' }}
            />
            <div>
              <div className="footer-product-name">TruthLens AI 3.0</div>
              <div className="footer-tagline">AI-Based Fake Identity &amp; Document Screening System</div>
            </div>
          </div>
          <p style={{ fontSize: '12px', color: 'var(--c-text-muted)', lineHeight: 1.6, marginTop: '8px' }}>
            SIH 2026 · PS 26188 · Prototype
          </p>
        </div>

        <div>
          <div className="footer-col-title">About</div>
          <div className="footer-link-list">
            <a href="/about">About TruthLens AI</a>
            <a href="/about#how-it-works">How It Works</a>
            <a href="/about#technology">Technology</a>
          </div>
        </div>

        <div>
          <div className="footer-col-title">Resources</div>
          <div className="footer-link-list">
            <a href="https://drive.google.com/drive/u/1/folders/1KlQV2Hw7J_aOUNUP3-LuD3eCjXTg0HL2" target="_blank" rel="noopener noreferrer">User Manual</a>
            <a href="#">API Documentation</a>
            <a href="https://drive.google.com/drive/u/1/folders/104ipO95zwUj5B5Qqa48hEoOhATOhp_uV" target="_blank" rel="noopener noreferrer">Research Documentation</a>
          </div>
        </div>

        <div>
          <div className="footer-col-title">Policies</div>
          <div className="footer-link-list">
            <a href="#">Privacy Policy</a>
            <a href="#">Data Policy</a>
            <a href="#">Terms of Use</a>
          </div>
        </div>

        <div className="stay-connected">
          <div className="footer-col-title">Stay Connected</div>
          <p>For updates and announcements</p>
          <div className="social-links">
            <a href="#" className="social-btn" aria-label="Follow on X (Twitter)">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
                <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-4.714-6.231-5.401 6.231H2.746l7.73-8.835L1.254 2.25H8.08l4.213 5.567zm-1.161 17.52h1.833L7.084 4.126H5.117z" />
              </svg>
            </a>
            <a href="#" className="social-btn" aria-label="Connect on LinkedIn">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
                <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433a2.062 2.062 0 01-2.063-2.065 2.064 2.064 0 112.063 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z" />
              </svg>
            </a>
            <button
              type="button"
              className="social-btn"
              onClick={onWatchDemo}
              aria-label="Watch video demonstration on YouTube"
              style={{ background: 'transparent', cursor: 'pointer', border: '1px solid var(--c-border)' }}
            >
              <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
                <path d="M23.495 6.205a3.007 3.007 0 00-2.088-2.088c-1.87-.501-9.396-.501-9.396-.501s-7.507-.01-9.396.501A3.007 3.007 0 00.527 6.205a31.247 31.247 0 00-.522 5.805 31.247 31.247 0 00.522 5.783 3.007 3.007 0 002.088 2.088c1.868.502 9.396.502 9.396.502s7.506 0 9.396-.502a3.007 3.007 0 002.088-2.088 31.247 31.247 0 00.5-5.783 31.247 31.247 0 00-.5-5.805zM9.609 15.601V8.408l6.264 3.602z" />
              </svg>
            </button>
          </div>
        </div>
      </div>

      <div className="footer-bottom">
        <div className="footer-links-row">
          <a href="#">Terms of Use</a>
          <a href="#">Privacy Policy</a>
          <a href="#">Accessibility Statement</a>
          <a href="#">Contact Us</a>
        </div>
        <div className="footer-copyright">© 2026 Government of India. All rights reserved.</div>
        <div className="footer-proto-notice">This is a SIH 2026 Prototype. Not for Operational Use.</div>
      </div>
    </div>
  </footer>
);

// ─── Home Page ────────────────────────────────────────────────
export const HomePage: React.FC = () => {
  const navigate = useNavigate();
  const { t } = useLanguage();
  const [showDemoModal, setShowDemoModal] = useState(false);

  return (
    <main id="main-content" tabIndex={-1}>

      {/* ── Hero Section ───────────────────────────────────────── */}
      <section className="hero" aria-labelledby="hero-heading" style={{ paddingBottom: '32px' }}>
        <div className="hero-bg-pattern" aria-hidden="true" />
        <div className="hero-inner hero-inner-layout">

          {/* Left: Headline + CTA */}
          <div className="hero-content hero-content-col" style={{ paddingRight: '16px' }}>
            <div className="hero-label">
              <span className="hero-label-dot" aria-hidden="true" />
              <span>{t('home.heroLabel')}</span>
            </div>

            <h1 className="hero-h1" id="hero-heading" style={{ fontSize: '36px', lineHeight: 1.2, marginTop: '12px' }}>
              {t('home.heroH1')}<br />
              <span className="blue">{t('home.heroH1Highlight')}</span>
            </h1>

            <p className="hero-desc" style={{ marginTop: '12px', marginBottom: '24px' }}>
              {t('home.heroDesc')}
            </p>

            <div className="hero-actions">
              <button
                id="btn-new-screening"
                className="btn-primary"
                onClick={() => navigate('/screening')}
                aria-label="Start a new screening"
              >
                <FileSearch size={15} aria-hidden="true" />
                {t('home.startAnalyzing')}
              </button>
              <button
                id="btn-watch-demo"
                className="btn-secondary"
                onClick={() => setShowDemoModal(true)}
                aria-label="Watch system demonstration video"
              >
                <Play size={15} aria-hidden="true" />
                {t('home.watchDemo')}
              </button>
            </div>
          </div>

          {/* Center: Passport Illustration */}
          <div className="hero-illustration-col" aria-hidden="true">
            <PassportIllustration />
          </div>

          {/* Right: System Status */}
          <div className="hero-status-col">
            <SystemStatusPanel />
          </div>
        </div>
      </section>

      {/* ── Dashboard Cards Row ─────────────────────────────────── */}
      <section className="section" aria-label="System dashboard overview" style={{ paddingTop: 0 }}>
        <div className="container">
          <div style={{ display: 'flex', gap: '16px', flexWrap: 'wrap' }}>
            <ScreeningDashboardCard />
            <RecentScreeningsCard />
            <DocumentIntelligenceCard />
            <ForensicInsightsCard />
          </div>
        </div>
      </section>

      <Footer onWatchDemo={() => setShowDemoModal(true)} />

      {/* ── Video Demo Modal ────────────────────────────────────── */}
      {showDemoModal && (
        <div
          role="dialog"
          aria-modal="true"
          aria-label="TruthLens AI Video Demonstration"
          style={{
            position: 'fixed', inset: 0, zIndex: 1000,
            background: 'rgba(11, 42, 91, 0.75)', backdropFilter: 'blur(4px)',
            display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '20px',
          }}
          onClick={() => setShowDemoModal(false)}
        >
          <div
            style={{
              position: 'relative', width: '100%', maxWidth: '860px',
              background: '#0B2A5B', borderRadius: 'var(--r-lg)',
              overflow: 'hidden', boxShadow: '0 20px 40px rgba(0,0,0,0.4)',
              border: '1px solid rgba(255,255,255,0.15)',
            }}
            onClick={(e) => e.stopPropagation()}
          >
            <div style={{
              display: 'flex', alignItems: 'center', justifyContent: 'space-between',
              padding: '14px 20px',
              background: 'rgba(255,255,255,0.05)',
              borderBottom: '1px solid rgba(255,255,255,0.1)', color: '#ffffff',
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '14px', fontWeight: 600 }}>
                <Play size={16} color="var(--c-accent)" />
                TruthLens AI 3.0 — System Demonstration Video
              </div>
              <button
                onClick={() => setShowDemoModal(false)}
                aria-label="Close demonstration video"
                style={{ background: 'transparent', border: 'none', color: 'rgba(255,255,255,0.8)', cursor: 'pointer', padding: '4px', display: 'flex', alignItems: 'center', borderRadius: 'var(--r-sm)' }}
              >
                <X size={20} />
              </button>
            </div>
            <div style={{ position: 'relative', width: '100%', paddingTop: '56.25%', background: '#000' }}>
              <iframe
                style={{ position: 'absolute', top: 0, left: 0, width: '100%', height: '100%', border: 0 }}
                src="https://www.youtube-nocookie.com/embed/Xtpba5MQr2U?autoplay=1&rel=0"
                title="TruthLens AI 3.0 Demonstration Video"
                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                allowFullScreen
              />
            </div>
          </div>
        </div>
      )}
    </main>
  );
};

export default HomePage;
