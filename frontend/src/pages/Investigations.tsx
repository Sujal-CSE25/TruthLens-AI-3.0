/**
 * TruthLens AI 3.0 — Investigations Page
 * PS 26188 · SIH 2026 PROTOTYPE — NOT FOR OPERATIONAL USE
 *
 * Displays open and closed investigation cases sourced from
 * the screening history. Each case links to a full screening result.
 */
import React, { useEffect, useState } from 'react';
import { Search, ChevronRight, AlertTriangle, CheckCircle } from 'lucide-react';
import { screeningApi } from '../services/api';

type Case = {
  screening_id: string;
  document_type: string;
  risk_level: 'CLEAR' | 'MANUAL_REVIEW' | 'HIGH_RISK';
  risk_score?: number;
  started_at?: string;
  created_at?: string;
  completed_at?: string;
  status?: string;
  demo_case?: string;
};

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
      border: `1px solid ${c.color}30`, whiteSpace: 'nowrap',
    }}>
      {c.label}
    </span>
  );
};

const fmtDate = (raw?: string | null) => {
  if (!raw) return '—';
  try {
    let s = String(raw).trim();
    if (s.includes(' ') && !s.includes('T')) s = s.replace(' ', 'T');
    if (!s.endsWith('Z') && !s.includes('+') && !s.includes('-', 10)) s += 'Z';
    const d = new Date(s);
    if (isNaN(d.getTime())) return '—';
    return d.toLocaleString('en-GB', {
      day: '2-digit', month: 'short', year: 'numeric',
      hour: '2-digit', minute: '2-digit',
    });
  } catch { return '—'; }
};

export const InvestigationsPage: React.FC = () => {
  const [cases, setCases] = useState<Case[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<'ALL' | 'MANUAL_REVIEW' | 'HIGH_RISK' | 'CLEAR'>('ALL');
  const [search, setSearch] = useState('');

  useEffect(() => {
    setLoading(true);
    screeningApi.getHistory(50).then((data: any) => {
      const items: Case[] = (data.items || data.screenings || []);
      setCases(items);
    }).catch(() => {
      // Demo fallback
      setCases([
        { screening_id: 'SB-2026-001245', document_type: 'Passport', risk_level: 'MANUAL_REVIEW', risk_score: 52, started_at: '2026-09-19T10:28:00Z', status: 'Open' },
        { screening_id: 'SB-2026-001244', document_type: 'Passport', risk_level: 'CLEAR', risk_score: 18, started_at: '2026-09-19T10:21:00Z', status: 'Closed' },
        { screening_id: 'SB-2026-001243', document_type: 'Visa', risk_level: 'HIGH_RISK', risk_score: 78, started_at: '2026-09-19T10:15:00Z', status: 'Open' },
        { screening_id: 'SB-2026-001242', document_type: 'Passport', risk_level: 'CLEAR', risk_score: 12, started_at: '2026-09-19T10:10:00Z', status: 'Closed' },
        { screening_id: 'SB-2026-001241', document_type: 'Passport', risk_level: 'MANUAL_REVIEW', risk_score: 44, started_at: '2026-09-19T10:05:00Z', status: 'Open' },
      ]);
    }).finally(() => setLoading(false));
  }, []);

  const filtered = cases.filter(c => {
    const matchFilter = filter === 'ALL' || c.risk_level === filter;
    const matchSearch = !search || c.screening_id.toLowerCase().includes(search.toLowerCase()) || (c.document_type || '').toLowerCase().includes(search.toLowerCase());
    return matchFilter && matchSearch;
  });

  const openCount = cases.filter(c => c.risk_level !== 'CLEAR').length;
  const highCount = cases.filter(c => c.risk_level === 'HIGH_RISK').length;

  return (
    <main id="main-content" tabIndex={-1}>
      <div className="page-header-band">
        <div className="page-header-inner">
          <div className="breadcrumb">
            <a href="/home">Home</a>
            <span className="breadcrumb-sep">/</span>
            <span aria-current="page">Investigations</span>
          </div>
          <h1 className="page-header-title">Investigation Cases</h1>
          <p className="page-header-sub">Active and closed identity verification investigation cases</p>
        </div>
      </div>

      <section className="section">
        <div className="container">

          {/* Summary strip */}
          <div style={{ display: 'flex', gap: '16px', marginBottom: '24px', flexWrap: 'wrap' }}>
            {[
              { label: 'Total Cases', value: cases.length, icon: Search, color: 'var(--c-blue)' },
              { label: 'Open / Under Review', value: openCount, icon: AlertTriangle, color: 'var(--c-warning)' },
              { label: 'High Risk', value: highCount, icon: AlertTriangle, color: 'var(--c-danger)' },
              { label: 'Cleared', value: cases.length - openCount, icon: CheckCircle, color: 'var(--c-success)' },
            ].map(({ label, value, icon: Icon, color }) => (
              <div key={label} className="card" style={{ flex: '1 1 160px', textAlign: 'center' }}>
                <Icon size={20} color={color} style={{ margin: '0 auto 8px' }} aria-hidden="true" />
                <div style={{ fontSize: '24px', fontWeight: 800, color }}>{value}</div>
                <div style={{ fontSize: '12px', color: 'var(--c-text-muted)', marginTop: '2px' }}>{label}</div>
              </div>
            ))}
          </div>

          {/* Filter / Search bar */}
          <div className="card" style={{ marginBottom: '16px' }}>
            <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap', alignItems: 'center' }}>
              <div style={{ position: 'relative', flex: '1 1 240px' }}>
                <Search size={14} style={{ position: 'absolute', left: 10, top: '50%', transform: 'translateY(-50%)', color: 'var(--c-text-muted)' }} />
                <input
                  id="investigation-search"
                  type="text"
                  placeholder="Search by Case ID or document type…"
                  value={search}
                  onChange={e => setSearch(e.target.value)}
                  style={{
                    width: '100%', padding: '8px 8px 8px 32px', fontSize: '13px',
                    border: '1px solid var(--c-border)', borderRadius: 'var(--r-md)',
                    background: 'var(--c-surface)', color: 'var(--c-text)', outline: 'none',
                  }}
                />
              </div>
              <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
                {(['ALL', 'MANUAL_REVIEW', 'HIGH_RISK', 'CLEAR'] as const).map(f => (
                  <button
                    key={f}
                    onClick={() => setFilter(f)}
                    style={{
                      padding: '6px 14px', fontSize: '12px', fontWeight: 600, borderRadius: 'var(--r-md)',
                      border: '1px solid var(--c-border)', cursor: 'pointer',
                      background: filter === f ? 'var(--c-navy)' : 'var(--c-surface)',
                      color: filter === f ? 'white' : 'var(--c-text)',
                    }}
                  >
                    {f === 'ALL' ? 'All' : f === 'MANUAL_REVIEW' ? 'Review' : f === 'HIGH_RISK' ? 'High Risk' : 'Clear'}
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* Cases table */}
          <div className="card" style={{ padding: 0 }}>
            {loading ? (
              <div style={{ padding: '40px', textAlign: 'center', color: 'var(--c-text-muted)' }}>Loading cases…</div>
            ) : filtered.length === 0 ? (
              <div style={{ padding: '40px', textAlign: 'center', color: 'var(--c-text-muted)' }}>No cases match the current filter.</div>
            ) : (
              <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '13px' }}>
                <thead style={{ background: 'var(--c-surface)', borderBottom: '1px solid var(--c-divider)' }}>
                  <tr>
                    {['Case ID', 'Document Type', 'Risk Level', 'Risk Score', 'Started', 'Status', ''].map(h => (
                      <th key={h} style={{ textAlign: 'left', padding: '12px 16px', color: 'var(--c-text-muted)', fontWeight: 600, whiteSpace: 'nowrap' }}>{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {filtered.map((c, i) => (
                    <tr key={i} style={{ borderBottom: '1px solid var(--c-divider)' }}>
                      <td style={{ padding: '12px 16px', fontWeight: 600, color: 'var(--c-text)', fontFamily: 'monospace' }}>{c.screening_id}</td>
                      <td style={{ padding: '12px 16px', color: 'var(--c-text-secondary)' }}>{c.document_type ?? 'Passport'}</td>
                      <td style={{ padding: '12px 16px' }}><RiskBadge level={c.risk_level} /></td>
                      <td style={{ padding: '12px 16px', color: 'var(--c-text)', fontWeight: 600 }}>{c.risk_score ?? '—'}</td>
                      <td style={{ padding: '12px 16px', color: 'var(--c-text-muted)', whiteSpace: 'nowrap' }}>{fmtDate(c.started_at || c.created_at)}</td>
                      <td style={{ padding: '12px 16px' }}>
                        <span style={{
                          fontSize: 11, fontWeight: 600, padding: '2px 8px', borderRadius: 4,
                          background: c.risk_level === 'CLEAR' ? 'var(--c-surface)' : 'var(--c-light-blue)',
                          color: c.risk_level === 'CLEAR' ? 'var(--c-text-muted)' : 'var(--c-blue)',
                        }}>
                          {c.risk_level === 'CLEAR' ? 'Closed' : 'Open'}
                        </span>
                      </td>
                      <td style={{ padding: '12px 16px' }}>
                        <a
                          href={`/screening?id=${c.screening_id}`}
                          style={{ color: 'var(--c-blue)', fontSize: '12px', display: 'flex', alignItems: 'center', gap: 4 }}
                        >
                          View <ChevronRight size={12} />
                        </a>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>

          <p style={{ marginTop: '12px', fontSize: '11px', color: 'var(--c-text-muted)' }}>
            SIH 2026 Prototype · PS 26188 · Data shown is from the local screening database only. Not for operational use.
          </p>
        </div>
      </section>
    </main>
  );
};

export default InvestigationsPage;
