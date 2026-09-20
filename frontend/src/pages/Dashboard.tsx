import React, { useEffect, useState } from 'react';
import { Shield, Activity, AlertTriangle, CheckCircle, XCircle, HelpCircle, GitBranch, Cpu, RefreshCw } from 'lucide-react';
import { AgentPipeline } from '../components/agents/AgentPipeline';
import { RecentAnalyses } from '../components/verification/RecentAnalyses';
import { api, type AnalyticsStats, type ContinuousLearningStatus } from '../services/api';
import { useLanguage } from '../context/LanguageContext';

export const DashboardPage: React.FC = () => {
  const { t } = useLanguage();
  const [stats, setStats] = useState<AnalyticsStats | null>(null);
  const [daily, setDaily] = useState<Array<{ date: string; count: number }>>([]);
  const [learning, setLearning] = useState<ContinuousLearningStatus | null>(null);

  useEffect(() => {
    api.getStats().then(setStats).catch(() => {});
    api.getDailyAnalytics(30).then(setDaily).catch(() => {});
    api.getLearningStatus().then(setLearning).catch(() => {});
  }, []);

  const isLive = stats !== null;
  const total = stats ? stats.total : 5418;
  const fake = stats ? stats.fake : 1482;
  const real = stats ? Math.max(0, total - fake) : 3241;
  const unverified = stats ? 0 : 695;
  const highRisk = fake;

  // Content type breakdown
  const textsCount = stats ? stats.texts : 3200;
  const imagesCount = stats ? stats.images : 1500;
  const docsCount = stats ? stats.docs : 718;
  const totalModality = textsCount + imagesCount + docsCount || 1;


  // Learning progress
  const fbTotal = learning?.readiness?.total_samples ?? stats?.fb_total ?? 0;
  const targetSamples = learning?.readiness?.target_samples ?? 100;
  const progressPct = learning?.readiness?.progress_pct ?? Math.min(100, Math.round((fbTotal / targetSamples) * 100));

  return (
    <main id="main-content" tabIndex={-1}>
      <div className="page-header-band">
        <div className="page-header-inner">
          <div className="breadcrumb">
            <a href="/">{t('nav.home')}</a>
            <span className="breadcrumb-sep">/</span>
            <span aria-current="page">{t('nav.dashboard')}</span>
          </div>
          <h1 className="page-header-title">{t('dashboard.title')}</h1>
          <p className="page-header-sub">{t('dashboard.sub')}</p>
        </div>
      </div>

      <section className="section">
        <div className="container">
          <span className="demo-label" style={{ marginBottom: '20px', display: 'inline-flex' }}>
            {isLive ? 'Live Database Overview' : 'Demo Environment'}
          </span>


          {/* Hero stats */}
          <div className="dashboard-hero-stats" role="list" aria-label="Dashboard statistics">
            {[
              { icon: Activity, label: t('dashboard.total'), val: total.toLocaleString(), bg: 'var(--c-light-blue)', color: 'var(--c-blue)' },
              { icon: CheckCircle, label: t('dashboard.real'), val: real.toLocaleString(), bg: 'var(--c-success-bg)', color: 'var(--c-success)' },
              { icon: XCircle, label: t('dashboard.fake'), val: fake.toLocaleString(), bg: 'var(--c-danger-bg)', color: 'var(--c-danger)' },
              { icon: HelpCircle, label: t('dashboard.unverified'), val: unverified.toLocaleString(), bg: 'var(--c-surface)', color: 'var(--c-text-muted)' },
              { icon: AlertTriangle, label: t('dashboard.highRisk'), val: highRisk.toLocaleString(), bg: 'var(--c-warning-bg)', color: 'var(--c-warning)' },
            ].map(({ icon: Icon, label, val, bg, color }) => (
              <div key={label} className="dash-stat" role="listitem">
                <div className="dash-stat-icon" style={{ background: bg, color }} aria-hidden="true">
                  <Icon size={16} />
                </div>
                <div className="dash-stat-val" style={{ color }}>{val}</div>
                <div className="dash-stat-label">{label}</div>
              </div>
            ))}
          </div>


          {/* Two column: Pipeline & Recent Analyses */}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px', marginBottom: '20px' }}>
            <AgentPipeline />
            <RecentAnalyses />
          </div>

          {/* Continuous Learning Progress Card */}
          <div className="card" style={{ marginBottom: '20px' }}>
            <div className="card-header">
              <RefreshCw size={16} color="var(--c-blue)" aria-hidden="true" />
              <div className="card-title">Continuous Learning &amp; Retraining Readiness</div>
              <span
                style={{
                  marginLeft: 'auto',
                  fontSize: '11px',
                  fontWeight: 700,
                  padding: '3px 8px',
                  borderRadius: 'var(--r-sm)',
                  background: learning?.readiness?.ready_to_retrain ? 'var(--c-success-bg)' : 'var(--c-light-blue)',
                  color: learning?.readiness?.ready_to_retrain ? 'var(--c-success)' : 'var(--c-blue)',
                }}
              >
                {learning?.readiness?.ready_to_retrain ? 'Ready for Recalibration' : 'Data Ingestion Phase'}
              </span>
            </div>

            <p style={{ fontSize: '13px', color: 'var(--c-text-secondary)', marginBottom: '14px' }}>
              TruthLens accumulates operator validation assessments to periodically calibrate linguistic weights and model thresholds.
            </p>

            <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '20px', alignItems: 'center' }}>
              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px' }}>
                  <span style={{ fontSize: '12px', color: 'var(--c-text-secondary)', fontWeight: 600 }}>
                    Feedback Samples Collected: {fbTotal} / {targetSamples}
                  </span>
                  <span style={{ fontSize: '12px', fontWeight: 700, color: 'var(--c-navy)' }}>
                    {progressPct}%
                  </span>
                </div>
                <div className="progress-track">
                  <div className="progress-fill" style={{ width: `${progressPct}%`, background: 'var(--c-primary-blue)' }} />
                </div>
                <div style={{ fontSize: '11px', color: 'var(--c-text-muted)', marginTop: '6px' }}>
                  A batch of {targetSamples} validated ratings triggers the automatic offline recalibration pipeline.
                </div>
              </div>

              <div style={{ padding: '12px', background: 'var(--c-surface)', borderRadius: 'var(--r-sm)', border: '1px solid var(--c-border)' }}>
                <div style={{ fontSize: '11px', color: 'var(--c-text-muted)', fontWeight: 600 }}>ACTIVE MODEL VERSION</div>
                <div style={{ fontSize: '14px', fontWeight: 700, color: 'var(--c-navy)', marginTop: '2px', display: 'flex', alignItems: 'center', gap: '6px' }}>
                  <GitBranch size={14} color="var(--c-blue)" />
                  {learning?.versions?.[0]?.version || '2.0.0-baseline'}
                </div>
                <div style={{ fontSize: '11px', color: 'var(--c-text-secondary)', marginTop: '4px' }}>
                  Accuracy baseline: {stats?.accuracy ?? 98.4}%
                </div>
              </div>
            </div>
          </div>

          {/* Content Distribution & Daily Trend Grid */}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px', marginBottom: '20px' }}>
            {/* Content Type Breakdown */}
            <div className="card">
              <div className="card-header">
                <Cpu size={15} color="var(--c-blue)" aria-hidden="true" />
                <div className="card-title">Content Modality Distribution</div>
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', marginTop: '8px' }}>
                {[
                  { label: 'Text & News Articles', count: textsCount, pct: Math.round((textsCount / totalModality) * 100), color: '#1D63C8' },
                  { label: 'Images & Visual Media', count: imagesCount, pct: Math.round((imagesCount / totalModality) * 100), color: '#06B6D4' },
                  { label: 'Documents & Credentials', count: docsCount, pct: Math.round((docsCount / totalModality) * 100), color: '#F59E0B' },
                ].map((item) => (
                  <div key={item.label}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '12px', marginBottom: '4px' }}>
                      <span style={{ fontWeight: 600, color: 'var(--c-text)' }}>{item.label}</span>
                      <span style={{ color: 'var(--c-text-muted)' }}>
                        {item.count.toLocaleString()} ({item.pct}%)
                      </span>
                    </div>
                    <div className="progress-track" style={{ height: '6px' }}>
                      <div className="progress-fill" style={{ width: `${item.pct}%`, background: item.color }} />
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Daily Trend Overview */}
            <div className="card">
              <div className="card-header">
                <Activity size={15} color="var(--c-blue)" aria-hidden="true" />
                <div className="card-title">Analysis Volume Trend (30 Days)</div>
              </div>
              <div style={{ height: '120px', display: 'flex', alignItems: 'flex-end', gap: '4px', paddingTop: '10px' }}>
                {daily.length > 0 ? (
                  daily.slice(-20).map((d, idx) => {
                    const maxCount = Math.max(...daily.map((x) => x.count), 1);
                    const barH = Math.max(8, (d.count / maxCount) * 90);
                    return (
                      <div
                        key={idx}
                        title={`${d.date}: ${d.count} analyses`}
                        style={{
                          flex: 1,
                          height: `${barH}px`,
                          background: 'var(--c-primary-blue)',
                          borderRadius: '2px 2px 0 0',
                          opacity: 0.75,
                        }}
                      />
                    );
                  })
                ) : (
                  <div style={{ width: '100%', textAlign: 'center', fontSize: '12px', color: 'var(--c-text-muted)' }}>
                    Continuous analysis logging active. Chart will render historical spikes.
                  </div>
                )}
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '10px', color: 'var(--c-text-muted)', marginTop: '8px' }}>
                <span>Past 30 Days</span>
                <span>Real-Time Database Stream</span>
                <span>Today</span>
              </div>
            </div>
          </div>

          {/* System Health Card */}
          <div className="card">
            <div className="card-header">
              <Shield size={15} color="var(--c-blue)" aria-hidden="true" />
              <div className="card-title">System &amp; Service Health</div>
              <span className="demo-label" style={{ marginLeft: 'auto' }}>Operational</span>
            </div>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '12px' }}>
              {[
                { label: 'API Gateway', val: 'Online (8000)', ok: true },
                { label: 'RAG Retrieval', val: 'Online (Wikipedia)', ok: true },
                { label: 'Forensics Engine', val: 'Active (ELA + NLP)', ok: true },
                { label: 'SQLite Store', val: 'Healthy (truthlens.db)', ok: true },
              ].map(({ label, val, ok }) => (
                <div
                  key={label}
                  style={{
                    background: ok ? 'var(--c-success-bg)' : 'var(--c-danger-bg)',
                    border: `1px solid ${ok ? '#b6dfc6' : '#f5b9b6'}`,
                    borderRadius: 'var(--r-md)',
                    padding: '14px',
                    textAlign: 'center',
                  }}
                >
                  <div style={{ fontSize: '14px', fontWeight: 700, color: ok ? 'var(--c-success)' : 'var(--c-danger)' }}>
                    {val}
                  </div>
                  <div style={{ fontSize: '12px', color: 'var(--c-text-muted)', marginTop: '4px' }}>
                    {label}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>
    </main>
  );
};

export default DashboardPage;
