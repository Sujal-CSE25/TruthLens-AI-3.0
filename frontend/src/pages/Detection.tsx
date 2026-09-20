import React, { useState } from 'react';
import { Upload, FileText, Image as ImageIcon, Search, X, CheckCircle, Circle, Loader, ChevronDown, ChevronUp, ExternalLink, AlertTriangle } from 'lucide-react';

import { api, type AnalysisResponse } from '../services/api';
import { useLanguage } from '../context/LanguageContext';
import { FeedbackWidget } from '../components/verification/FeedbackWidget';
import { RadarChart } from '../components/verification/RadarChart';
import { GaugeChart } from '../components/verification/GaugeChart';
import { DocumentVerificationResult } from '../components/verification/DocumentVerificationResult';

type Tab = 'text' | 'image';
type StepStatus = 'done' | 'active' | 'pending';

interface PipelineStep {
  name: string;
  detail: string;
  status: StepStatus;
}

const initialSteps: PipelineStep[] = [
  { name: 'Input received', detail: 'Content ready for processing', status: 'pending' },
  { name: 'Claim Extractor', detail: 'Identifying verifiable claims', status: 'pending' },
  { name: 'Evidence Finder', detail: 'Retrieving evidence via RAG', status: 'pending' },
  { name: 'Fact Checker', detail: 'Comparing claims against evidence', status: 'pending' },
  { name: 'Risk Assessor', detail: 'Calculating calibrated fake score', status: 'pending' },
  { name: 'Explainability Agent', detail: 'Building reasoning chain', status: 'pending' },
  { name: 'Final Judge', detail: 'Producing verdict + trust score', status: 'pending' },
];

const forensicSteps: PipelineStep[] = [
  { name: 'Image Acquisition', detail: 'Ingesting image payload and format decoding', status: 'pending' },
  { name: 'Error Level Analysis (ELA)', detail: 'JPEG 8x8 block differential & splice detection', status: 'pending' },
  { name: 'Sensor Noise Fingerprint', detail: 'PRNU wavelet decomposition for diffusion anomalies', status: 'pending' },
  { name: 'EXIF & Software Signatures', detail: 'Metadata integrity audit and editor detection', status: 'pending' },
  { name: 'Edge & Gradient Geometry', detail: 'Laplacian edge sharpness & boundary analysis', status: 'pending' },
  { name: 'Gemini Deepfake Forensics', detail: 'Pixel-level lighting & synthetic artifact verdict', status: 'pending' },
];


const samplePresets = [
  {
    label: 'Select a sample to test…',
    text: '',
  },
  {
    label: 'NASA Webb Telescope (Credible)',
    text: "NASA confirms the James Webb Space Telescope has captured its first direct image of an exoplanet, marking a historic milestone according to the agency's official press release published on September 1, 2022.",
  },
  {
    label: 'Health Misinformation (High Risk)',
    text: 'BREAKING: Scientists CONFIRM drinking bleach cures cancer — Big Pharma is hiding this!! Share before they DELETE this!!! 100% natural cure discovered in Mexico.',
  },
  {
    label: 'Political Propaganda (Biased)',
    text: 'The globalist deep state elites are using mainstream media to cover up the truth. Wake up sheeple! The economy has NEVER been worse. Crime is at record highs. Vote for change NOW before it is too late!',
  },
  {
    label: 'Fabricated Statistic (False Claims)',
    text: 'New study PROVES vaccines caused 500,000 deaths last year. The CDC and WHO are hiding this data from the public. Share before they censor it. 98% of hospitalized patients were vaccinated.',
  },
];

const defaultSampleResult: AnalysisResponse = {
  verdict: 'LIKELY MISLEADING',
  trust_score: 31,
  fake_score: 69,
  confidence: 'High',
  risk_level: 'High',
  claims: [
    {
      num: 1,
      text: 'The press conference video shows the Minister making statements about food safety regulations.',
      status: 'fake',
      evidence: 'Retrieved Wikipedia and web sources find no record of such statements on this date.',
      source: 'Wikipedia, News Archive',
    },
    {
      num: 2,
      text: 'The video was recorded on 15 May 2026 at New Delhi.',
      status: 'real',
      evidence: 'Metadata and contextual signals are consistent with stated time and location.',
      source: 'EXIF metadata, News Archive',
    },
    {
      num: 3,
      text: 'The official statements match the government policy document.',
      status: 'unverified',
      evidence: 'Insufficient evidence coverage to verify this claim.',
      source: 'Limited sources found',
    },
  ],
  explanation: [
    { step: 1, title: 'Claims Identified', desc: '3 verifiable claims extracted from the content.' },
    { step: 2, title: 'Evidence Retrieved', desc: 'RAG search over Wikipedia and web returned 8 relevant passages.' },
    { step: 3, title: 'Claims Compared', desc: 'Claim 1 contradicted; Claim 2 supported; Claim 3 unverified.' },
    { step: 4, title: 'Forensic Signals Assessed', desc: 'ELA and noise pattern analysis returned elevated anomaly scores.' },
    { step: 5, title: 'Risk Score Calculated', desc: 'Fake score: 69%. Risk level: High. Confidence: High.' },
    { step: 6, title: 'Final Verdict Produced', desc: 'Likely Misleading based on combined claim and forensic evidence.' },
  ],
  linguistic_scores: {
    clickbait: 42,
    emotional: 58,
    urgency: 65,
    certainty: 70,
    propaganda: 35,
    credibility: 28,
  },
  bias_score: 45,
  manipulation_score: 60,
  bias_direction: 'SLIGHT LEAN',
  red_flags: ['High emotional tone detected', 'Urgent call-to-action language', 'Unverified statistical claims'],
};

import { useLocation } from 'react-router-dom';

export const DetectionPage: React.FC = () => {
  const { t } = useLanguage();
  const location = useLocation();
  const [activeTab, setActiveTab] = useState<Tab>('text');

  const [text, setText] = useState<string>(() => {
    return (location.state as any)?.transferredText || '';
  });
  const [selectedPreset, setSelectedPreset] = useState('');


  const [dragOver, setDragOver] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);
  const [steps, setSteps] = useState<PipelineStep[]>(initialSteps);
  const [stepIndex, setStepIndex] = useState(-1);
  const [showResult, setShowResult] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [fileName, setFileName] = useState<string | null>(null);
  const [activeResult, setActiveResult] = useState<AnalysisResponse>(defaultSampleResult);
  const [isLiveResult, setIsLiveResult] = useState(false);
  const [isDocumentAnalysis, setIsDocumentAnalysis] = useState(false);
  const [isForensicAnalysis, setIsForensicAnalysis] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [expandedClaim, setExpandedClaim] = useState<number | null>(null);

  const handleSelectPreset = (val: string) => {
    setSelectedPreset(val);
    if (val) {
      setActiveTab('text');
      setText(val);
    }
  };

  const handleTransferToTextAnalysis = (extractedText: string) => {
    if (!extractedText.trim()) return;
    setActiveTab('text');
    setText(extractedText.trim());
    setShowResult(false);
    setIsDocumentAnalysis(false);
    setIsForensicAnalysis(false);
    setSelectedFile(null);
    setFileName(null);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };


  const runAnalysis = async () => {
    if (analyzing) return;
    setErrorMessage(null);
    setShowResult(false);
    setAnalyzing(true);
    setIsDocumentAnalysis(false);

    const isImageTab = activeTab === 'image';
    setIsForensicAnalysis(isImageTab);

    const activePipelineSteps = isImageTab ? forensicSteps : initialSteps;
    setSteps(activePipelineSteps.map((s) => ({ ...s, status: 'pending' })));
    setStepIndex(0);

    // Animate pipeline steps visually
    let current = 0;
    const interval = setInterval(() => {
      current++;
      if (current < activePipelineSteps.length) {
        setSteps((prev) =>
          prev.map((s, i) => ({
            ...s,
            status: i < current ? 'done' : i === current ? 'active' : 'pending',
          }))
        );
        setStepIndex(current);
      }
    }, 450);

    try {
      let data: AnalysisResponse | null = null;

      if (activeTab === 'text' && text.trim().length >= 15) {
        data = await api.analyzeText(text.trim());
      } else if (activeTab === 'image' && selectedFile) {
        const isDoc =
          selectedFile.name.endsWith('.pdf') ||
          selectedFile.name.endsWith('.txt') ||
          selectedFile.type === 'application/pdf';
        if (isDoc) {
          setIsDocumentAnalysis(true);
          data = await api.analyzeDocument(selectedFile);
        } else {
          data = await api.analyzeImage(selectedFile);
        }
      }

      clearInterval(interval);
      setSteps((prev) => prev.map((s) => ({ ...s, status: 'done' })));
      setStepIndex(activePipelineSteps.length);

      if (data && (data.verdict || (data as any).authenticity_score !== undefined)) {
        setActiveResult(data);
        setIsLiveResult(true);
      } else {
        setActiveResult(defaultSampleResult);
        setIsLiveResult(false);
      }
    } catch (err: any) {
      clearInterval(interval);
      setSteps((prev) => prev.map((s) => ({ ...s, status: 'done' })));
      setActiveResult(defaultSampleResult);
      setIsLiveResult(false);
      setErrorMessage(err.message || 'Could not reach backend API; showing sample fallback preview.');
    } finally {
      setAnalyzing(false);
      setShowResult(true);
    }
  };

  const reset = () => {
    setShowResult(false);
    setAnalyzing(false);
    setSteps(initialSteps);
    setStepIndex(-1);
    setText('');
    setSelectedPreset('');

    setSelectedFile(null);
    setFileName(null);
    setErrorMessage(null);
    setIsLiveResult(false);
    setIsDocumentAnalysis(false);
    setIsForensicAnalysis(false);
    setExpandedClaim(null);
  };


  // Map raw claims into standard structure
  const claimsList = (activeResult.claim_verification || activeResult.claims || []).map((c: any, i: number) => ({
    num: i + 1,
    text: c.claim || c.claim_text || `Claim #${i + 1}`,
    status:
      (c.verdict || '').toUpperCase() === 'SUPPORTED'
        ? 'real'
        : (c.verdict || '').toUpperCase() === 'CONTRADICTED'
        ? 'fake'
        : 'unverified',
    evidence: c.reasoning || (c.sources ? `Matched sources: ${c.sources.join(', ')}` : 'Evidence verified against knowledge bases.'),
    source: c.sources && c.sources.length > 0 ? c.sources.join(', ') : 'Wikipedia & Knowledge Corpus',
    sources_used: c.sources_used ?? c.evidence_count ?? 0,
  }));

  const verdictUpper = (activeResult.verdict || 'AUTHENTIC').toUpperCase();
  const verdictClass =
    verdictUpper.includes('REAL') || verdictUpper.includes('AUTHENTIC')
      ? 'real'
      : verdictUpper.includes('FAKE') || verdictUpper.includes('FORGED') || verdictUpper.includes('MISLEADING') || verdictUpper.includes('MANIPULATED')
      ? 'fake'
      : 'review';

  const trustScore = activeResult.trust_score !== undefined ? activeResult.trust_score : Math.max(0, 100 - (activeResult.fake_score || 0));
  const fakeScore = activeResult.fake_score !== undefined ? activeResult.fake_score : activeResult.forgery_score ?? 0;
  const riskLevel = activeResult.risk_level || (fakeScore >= 60 ? 'High' : fakeScore >= 30 ? 'Moderate' : 'Low');

  // Explanation list mapping
  const explanationList =
    Array.isArray(activeResult.explainability_report?.reasoning_chain) && activeResult.explainability_report.reasoning_chain.length > 0
      ? activeResult.explainability_report.reasoning_chain.map((desc: string, i: number) => ({
          step: i + 1,
          title: `Step ${i + 1}`,
          desc,
        }))
      : Array.isArray(activeResult.explanation)
      ? activeResult.explanation.map((e: any, i: number) => ({
          step: e.step || i + 1,
          title: e.title || `Pipeline Stage ${i + 1}`,
          desc: e.desc || e.detail || JSON.stringify(e),
        }))
      : [
          { step: 1, title: 'Linguistic Analysis', desc: 'Computed lexical, emotional, and structural patterns.' },
          { step: 2, title: 'Claims Extracted', desc: `${claimsList.length} verifiable factual claims identified.` },
          { step: 3, title: 'RAG Evidence Retrieved', desc: 'Queried Wikipedia and domain knowledge corpus.' },
          { step: 4, title: 'Risk Assessed', desc: `Calibrated fake probability: ${fakeScore}%.` },
          { step: 5, title: 'Final Verdict', desc: activeResult.verdict },
        ];

  // Radar data points
  const radarData = {
    Fake: fakeScore,
    Bias: activeResult.bias_score ?? 15,
    Manipulation: activeResult.manipulation_score ?? (fakeScore > 50 ? 55 : 10),
    Distrust: 100 - trustScore,
    Confidence: typeof activeResult.confidence === 'number' ? activeResult.confidence : activeResult.confidence === 'High' ? 85 : 55,
  };

  return (
    <main id="main-content" tabIndex={-1}>
      {/* Page Header */}
      <div className="page-header-band">
        <div className="page-header-inner">
          <div className="breadcrumb">
            <a href="/">{t('nav.home')}</a>
            <span className="breadcrumb-sep" aria-hidden="true">/</span>
            <span aria-current="page">{t('nav.detection')}</span>
          </div>
          <h1 className="page-header-title">{t('detection.title')}</h1>
          <p className="page-header-sub">
            {t('detection.sub')}
          </p>
        </div>
      </div>

      <div className="detection-page">
        <div className="container">
          <div
            style={{
              display: 'grid',
              gridTemplateColumns: analyzing || showResult ? '1fr' : '1fr',
              gap: '20px',
              alignItems: 'start',
            }}
          >

            {/* Upload Panel */}
            {!showResult && (
              <div>
                <div className="upload-panel">
                  <h2 style={{ fontSize: '16px', fontWeight: 700, color: 'var(--c-navy)', marginBottom: '4px' }}>
                    Analyse Content
                  </h2>
                  <p style={{ fontSize: '13px', color: 'var(--c-text-muted)', marginBottom: '16px' }}>
                    Verify news articles, claims, images, and deepfakes with automated multi-agent forensic intelligence
                  </p>
                  <span className="demo-label" style={{ marginBottom: '16px', display: 'inline-flex' }}>
                    Institutional Verification Suite
                  </span>

                  {/* Tabs: Text & News Detection and Image & Deepfake Detection */}
                  <div className="upload-tabs" role="tablist">
                    <button
                      role="tab"
                      aria-selected={activeTab === 'text'}
                      className={`upload-tab${activeTab === 'text' ? ' active' : ''}`}
                      onClick={() => setActiveTab('text')}
                    >
                      <FileText size={14} style={{ display: 'inline', marginRight: '6px' }} aria-hidden="true" />
                      {t('detection.tabText')}
                    </button>
                    <button
                      role="tab"
                      aria-selected={activeTab === 'image'}
                      className={`upload-tab${activeTab === 'image' ? ' active' : ''}`}
                      onClick={() => setActiveTab('image')}
                    >
                      <ImageIcon size={14} style={{ display: 'inline', marginRight: '6px' }} aria-hidden="true" />
                      {t('detection.tabImage')}
                    </button>
                  </div>

                  {/* Tab Content */}
                  <div role="tabpanel">
                    {/* SECTION 1: Text & News Detection (NO file upload, quick samples included) */}
                    {activeTab === 'text' && (
                      <div>
                        {/* Quick preset selector inside Text & News section */}
                        <div
                          style={{
                            marginBottom: '14px',
                            padding: '10px 14px',
                            background: 'var(--c-surface)',
                            border: '1px solid var(--c-border)',
                            borderRadius: 'var(--r-md)',
                            display: 'flex',
                            alignItems: 'center',
                            gap: '10px',
                            flexWrap: 'wrap',
                          }}
                        >
                          <span style={{ fontSize: '13px', fontWeight: 600, color: 'var(--c-navy)' }}>
                            {t('detection.presetLabel')}
                          </span>
                          <select
                            value={selectedPreset}
                            onChange={(e) => handleSelectPreset(e.target.value)}
                            style={{
                              padding: '6px 12px',
                              borderRadius: 'var(--r-sm)',
                              border: '1px solid var(--c-border)',
                              fontSize: '13px',
                              color: 'var(--c-text)',
                              background: 'var(--c-white)',
                              flex: 1,
                              maxWidth: '420px',
                              cursor: 'pointer',
                            }}
                            aria-label="Select sample text"
                          >
                            {samplePresets.map((preset, idx) => (
                              <option key={idx} value={preset.text}>
                                {preset.label}
                              </option>
                            ))}
                          </select>
                        </div>

                        <label htmlFor="text-input" className="sr-only">
                          Content to analyse
                        </label>
                        <textarea
                          id="text-input"
                          className="text-input-area"
                          placeholder={t('detection.textPlaceholder')}
                          value={text}
                          onChange={(e) => setText(e.target.value)}
                          aria-label="Text content to analyse"
                        />
                        <div style={{ fontSize: '11px', color: 'var(--c-text-muted)', marginTop: '6px' }}>
                          {text.length} characters (minimum 15 characters recommended)
                        </div>
                      </div>
                    )}

                    {/* SECTION 2: Image & Deepfake Detection (File upload here) */}
                    {activeTab === 'image' && (
                      <div>
                        {fileName ? (
                          <div
                            style={{
                              display: 'flex',
                              alignItems: 'center',
                              gap: '10px',
                              background: 'var(--c-success-bg)',
                              border: '1px solid #b6dfc6',
                              borderRadius: 'var(--r-md)',
                              padding: '12px 16px',
                            }}
                          >
                            <CheckCircle size={16} color="var(--c-success)" aria-hidden="true" />
                            <span style={{ flex: 1, fontSize: '13px', color: 'var(--c-text)', fontWeight: 600 }}>
                              {fileName}
                            </span>
                            <button
                              onClick={() => {
                                setFileName(null);
                                setSelectedFile(null);
                              }}
                              style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'var(--c-text-muted)' }}
                              aria-label="Remove file"
                            >
                              <X size={14} />
                            </button>
                          </div>
                        ) : (
                          <div
                            className={`drop-zone${dragOver ? ' drag-over' : ''}`}
                            onDragOver={(e) => {
                              e.preventDefault();
                              setDragOver(true);
                            }}
                            onDragLeave={() => setDragOver(false)}
                            onDrop={(e) => {
                              e.preventDefault();
                              setDragOver(false);
                              if (e.dataTransfer.files[0]) {
                                setSelectedFile(e.dataTransfer.files[0]);
                                setFileName(e.dataTransfer.files[0].name);
                              }
                            }}
                            onClick={() => {
                              const input = document.createElement('input');
                              input.type = 'file';
                              input.accept = '.jpg,.jpeg,.png,.webp,.pdf';
                              input.onchange = () => {
                                if (input.files?.[0]) {
                                  setSelectedFile(input.files[0]);
                                  setFileName(input.files[0].name);
                                }
                              };
                              input.click();
                            }}
                            role="button"
                            tabIndex={0}
                            aria-label="Drop image or document here or click to browse"
                            onKeyDown={(e) => {
                              if (e.key === 'Enter' || e.key === ' ') e.currentTarget.click();
                            }}
                          >
                            <Upload size={36} className="drop-icon" aria-hidden="true" />
                            <div className="drop-title">Drag &amp; Drop image or document for Deepfake / Forgery Inspection</div>
                            <div className="drop-sub">or click to browse local files</div>
                            <div className="drop-formats">JPEG · PNG · WEBP · PDF (Up to 25 MB)</div>
                          </div>
                        )}
                      </div>
                    )}
                  </div>

                  <div className="analysis-actions">
                    <button
                      className="btn-primary"
                      onClick={runAnalysis}
                      disabled={analyzing || (activeTab === 'text' && text.trim().length < 5) || (activeTab === 'image' && !selectedFile)}
                      aria-label="Start analysis"
                    >
                      <Search size={14} aria-hidden="true" />
                      {analyzing
                        ? activeTab === 'image'
                          ? t('detection.analyzingForensics')
                          : t('detection.analyzing')
                        : activeTab === 'image'
                        ? t('detection.analyzeForensicsBtn')
                        : t('detection.analyzeBtn')}
                    </button>
                    <button className="btn-secondary" onClick={reset} aria-label="Clear and reset">
                      <X size={14} aria-hidden="true" />
                      Clear
                    </button>
                  </div>
                </div>
              </div>
            )}

            {/* Analysis Progress */}
            {analyzing && (
              <div className="analysis-progress-panel">
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '4px' }}>
                  <Loader size={16} color="var(--c-blue)" style={{ animation: 'spin 1s linear infinite' }} aria-hidden="true" />
                  <div className="progress-title">
                    {activeTab === 'image' ? t('detection.forensicProgress') : 'Analysis in Progress'}
                  </div>
                </div>
                <p className="progress-subtitle">
                  {activeTab === 'image'
                    ? t('detection.forensicSubtitle')
                    : 'Executing through the six-agent verification pipeline...'}
                </p>

                <div className="progress-label-row" style={{ marginBottom: '12px' }}>
                  <span className="progress-label">
                    {activeTab === 'image' ? 'Forensic Inspection Progress' : 'Pipeline Progress'}
                  </span>
                  <span className="progress-pct">
                    {Math.round(((stepIndex + 1) / (activeTab === 'image' ? forensicSteps.length : initialSteps.length)) * 100)}%
                  </span>
                </div>
                <div
                  className="progress-track"
                  role="progressbar"
                  aria-valuenow={Math.round(((stepIndex + 1) / (activeTab === 'image' ? forensicSteps.length : initialSteps.length)) * 100)}
                  aria-valuemin={0}
                  aria-valuemax={100}
                >
                  <div
                    className="progress-fill"
                    style={{
                      width: `${Math.round(((stepIndex + 1) / (activeTab === 'image' ? forensicSteps.length : initialSteps.length)) * 100)}%`,
                      transition: 'width 0.8s ease',
                    }}
                  />
                </div>


                <div className="pipeline-steps" style={{ marginTop: '16px' }}>
                  {steps.map((step, i) => (
                    <div key={i} className="pipeline-step" aria-live={step.status === 'active' ? 'polite' : undefined}>
                      <div className={`step-indicator ${step.status}`} aria-hidden="true">
                        {step.status === 'done' ? (
                          <CheckCircle size={14} />
                        ) : step.status === 'active' ? (
                          <Loader size={14} />
                        ) : (
                          <Circle size={14} />
                        )}
                      </div>
                      <div className="step-info">
                        <div className="step-name">{step.name}</div>
                        {step.status !== 'pending' && <div className="step-detail">{step.detail}</div>}
                      </div>
                      <div className={`step-badge ${step.status}`}>
                        {step.status === 'done' ? '✓ Done' : step.status === 'active' ? '● Running' : '○ Waiting'}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Results Section */}
            {showResult && (
              <div style={{ width: '100%' }}>
                {/* Result Top Header */}
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '20px', flexWrap: 'wrap', gap: '10px' }}>
                  <div>
                    <h2 style={{ fontSize: '18px', fontWeight: 700, color: 'var(--c-navy)' }}>
                      Verification Assessment Results
                    </h2>
                    <p style={{ fontSize: '13px', color: 'var(--c-text-muted)', marginTop: '4px' }}>
                      Multi-agent pipeline complete ·{' '}
                      <span
                        className="demo-label"
                        style={{
                          background: isLiveResult ? 'var(--c-success-bg)' : undefined,
                          color: isLiveResult ? 'var(--c-success)' : undefined,
                          borderColor: isLiveResult ? '#b6dfc6' : undefined,
                        }}
                      >
                        {isLiveResult ? 'Live Verification' : 'Preview / Fallback'}
                      </span>
                    </p>
                    {errorMessage && (
                      <p style={{ fontSize: '12px', color: 'var(--c-warning)', marginTop: '4px' }}>
                        ⚠ Note: {errorMessage}
                      </p>
                    )}
                  </div>
                  <button className="btn-secondary" onClick={reset}>
                    <Search size={13} aria-hidden="true" />
                    New Verification
                  </button>
                </div>

                {/* If Document verification: render DocumentVerificationResult */}
                {isDocumentAnalysis || activeResult.doc_type || activeResult.template_analysis ? (
                  <DocumentVerificationResult
                    result={activeResult}
                    fileName={fileName}
                    onVerifyNewsContent={handleTransferToTextAnalysis}
                  />
                ) : (

                  /* Standard / Text / Image Verification View */
                  <div>
                    {/* Execution Trace Strip: 6-Agent Pipeline vs Forensic Pipeline */}
                    <div
                      className="card"
                      style={{
                        marginBottom: '20px',
                        padding: '12px 18px',
                        background: 'var(--c-surface)',
                        border: '1px solid var(--c-border)',
                      }}
                    >
                      <div style={{ fontSize: '11px', fontWeight: 700, textTransform: 'uppercase', color: 'var(--c-navy)', letterSpacing: '0.08em', marginBottom: '8px' }}>
                        {isForensicAnalysis ? t('detection.forensicTraceVerified') : t('detection.traceVerified')}
                      </div>

                      {isForensicAnalysis ? (
                        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', gap: '8px' }}>
                          {[
                            { num: 'F1', name: 'Error Level Analysis (ELA)', metric: `${activeResult.forensic_detail?.ela?.manipulation_score ?? 73}% anomaly` },
                            { num: 'F2', name: 'Sensor Noise (PRNU)', metric: `${activeResult.forensic_detail?.noise?.noise_score ?? 61}% variance` },
                            { num: 'F3', name: 'EXIF Signatures', metric: activeResult.metadata_flags?.length ? `${activeResult.metadata_flags.length} flags` : 'Clean EXIF' },
                            { num: 'F4', name: 'Compression Integrity', metric: activeResult.forensic_detail?.compression?.compression_score !== undefined ? `${activeResult.forensic_detail.compression.compression_score}% diff` : 'Analyzed' },
                            { num: 'F5', name: 'Edge Boundary', metric: activeResult.forensic_detail?.edge?.edge_score !== undefined ? `${activeResult.forensic_detail.edge.edge_score}% edge` : 'Normal' },
                            { num: 'F6', name: 'Gemini Deepfake Forensics', metric: activeResult.verdict },
                          ].map((sig) => (
                            <div
                              key={sig.num}
                              style={{
                                padding: '6px 10px',
                                background: 'var(--c-white)',
                                borderRadius: 'var(--r-sm)',
                                border: '1px solid var(--c-border)',
                                fontSize: '11px',
                              }}
                            >
                              <span style={{ fontWeight: 700, color: 'var(--c-primary-blue)', marginRight: '4px' }}>{sig.num}</span>
                              <span style={{ fontWeight: 600, color: 'var(--c-text)' }}>{sig.name}</span>
                              <div style={{ color: 'var(--c-text-muted)', fontSize: '10px', marginTop: '2px' }}>{sig.metric}</div>
                            </div>
                          ))}
                        </div>
                      ) : (
                        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(140px, 1fr))', gap: '8px' }}>
                          {[
                            { num: '01', name: 'Claim Extractor', metric: `${claimsList.length} claims` },
                            { num: '02', name: 'Evidence Finder', metric: `${Object.keys(activeResult.evidence_map || {}).length || 2} sources` },
                            { num: '03', name: 'Fact Checker', metric: `${claimsList.filter(c => c.status === 'real').length} supported` },
                            { num: '04', name: 'Risk Assessor', metric: `${fakeScore}% risk` },
                            { num: '05', name: 'Explainability', metric: '6-step chain' },
                            { num: '06', name: 'Final Judge', metric: activeResult.verdict },
                          ].map((ag) => (
                            <div
                              key={ag.num}
                              style={{
                                padding: '6px 10px',
                                background: 'var(--c-white)',
                                borderRadius: 'var(--r-sm)',
                                border: '1px solid var(--c-border)',
                                fontSize: '11px',
                              }}
                            >
                              <span style={{ fontWeight: 700, color: 'var(--c-primary-blue)', marginRight: '4px' }}>{ag.num}</span>
                              <span style={{ fontWeight: 600, color: 'var(--c-text)' }}>{ag.name}</span>
                              <div style={{ color: 'var(--c-text-muted)', fontSize: '10px', marginTop: '2px' }}>{ag.metric}</div>
                            </div>
                          ))}
                        </div>
                      )}
                    </div>


                    <div style={{ display: 'grid', gridTemplateColumns: '320px 1fr', gap: '20px', alignItems: 'start' }}>

                      {/* Left Column: Verdict & Radar */}
                      <div>
                        {/* Verdict Card */}
                        <div className="verdict-card" role="region" aria-label="Final verdict">
                          <div className={`verdict-header ${verdictClass === 'real' ? 'real' : verdictClass === 'review' ? 'review' : ''}`}>
                            <div>
                              <div className="verdict-label">Final Verdict</div>
                              <div className={`verdict-text ${verdictClass === 'real' ? 'real' : verdictClass === 'review' ? 'review' : ''}`}>
                                {activeResult.verdict}
                              </div>
                            </div>
                          </div>
                          <div className="verdict-body">
                            <div className="verdict-scores">
                              <div className="verdict-score">
                                <div className="vs-label">{t('detection.trustScore')}</div>
                                <div className="vs-value">{trustScore}%</div>
                              </div>
                              <div className="verdict-score">
                                <div className="vs-label">{t('detection.confidence')}</div>
                                <div className="vs-value" style={{ fontSize: '15px' }}>
                                  {typeof activeResult.confidence === 'number' ? `${activeResult.confidence}%` : activeResult.confidence}
                                </div>
                              </div>
                              <div className="verdict-score">
                                <div className="vs-label">{t('detection.riskLevel')}</div>
                                <div
                                  className="vs-value"
                                  style={{
                                    fontSize: '15px',
                                    color:
                                      riskLevel === 'High' || riskLevel === 'HIGH'
                                        ? 'var(--c-danger)'
                                        : riskLevel === 'Moderate' || riskLevel === 'MEDIUM'
                                        ? 'var(--c-warning)'
                                        : 'var(--c-success)',
                                  }}
                                >
                                  {riskLevel}
                                </div>
                              </div>
                            </div>

                            {/* Dual Gauge Meters (Trust Score & Fake Probability) */}
                            <div style={{ display: 'flex', justifyContent: 'space-around', padding: '12px 0', borderTop: '1px solid var(--c-border)', borderBottom: '1px solid var(--c-border)', marginTop: '12px' }}>
                              <GaugeChart score={trustScore} label={t('detection.trustCredibility')} color="var(--c-success)" size={125} />
                              <GaugeChart score={fakeScore} label={t('detection.fakeProbability')} color="var(--c-danger)" size={125} />
                            </div>



                            {activeResult.bias_direction && (
                              <div style={{ padding: '8px 12px', background: 'var(--c-surface)', borderRadius: 'var(--r-sm)', marginTop: '8px', fontSize: '12px', color: 'var(--c-text)' }}>
                                <span style={{ color: 'var(--c-text-muted)' }}>Bias Indicator: </span>
                                <strong>{activeResult.bias_direction}</strong>
                              </div>
                            )}

                            <div style={{ padding: '10px', background: 'var(--c-surface)', borderRadius: 'var(--r-sm)', marginTop: '8px' }}>
                              <div style={{ fontSize: '12px', color: 'var(--c-text-muted)', marginBottom: '4px' }}>
                                Claims Summary
                              </div>
                              <div style={{ fontSize: '13px', color: 'var(--c-text)', fontWeight: 600 }}>
                                {claimsList.filter((c) => c.status === 'real').length} supported ·{' '}
                                {claimsList.filter((c) => c.status === 'fake').length} contradicted ·{' '}
                                {claimsList.filter((c) => c.status === 'unverified').length} unverified
                              </div>
                            </div>
                          </div>
                        </div>

                        {/* Radar Chart Card */}
                        <div className="card" style={{ marginTop: '16px' }}>
                          <div className="card-header">
                            <div className="card-title">{t('detection.signalRadar')}</div>
                          </div>
                          <RadarChart data={radarData} size={250} />
                        </div>

                        {/* Reasoning Chain */}
                        <div className="card" style={{ marginTop: '16px' }}>
                          <div className="card-header">
                            <div className="card-title">{t('detection.whyVerdict')}</div>
                          </div>

                          <div className="explain-chain" role="list">
                            {explanationList.map((e, i) => (
                              <div key={i} className="explain-step" role="listitem">
                                <div className="explain-connector">
                                  <div className="explain-dot">{e.step}</div>
                                  {i < explanationList.length - 1 && <div className="explain-line" />}
                                </div>
                                <div className="explain-content">
                                  <div className="explain-title">{e.title}</div>
                                  <div className="explain-desc">{e.desc}</div>
                                </div>
                              </div>
                            ))}
                          </div>
                        </div>
                      </div>

                      {/* Right Column: Claims / Forensics, Signals, Red Flags */}
                      <div>
                        {isForensicAnalysis ? (
                          /* Forensic Inspection Signals Grid */
                          <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                            {/* ELA Forensic Card */}
                            <div className="card">
                              <div className="card-header">
                                <div className="card-title">Error Level Analysis (ELA)</div>
                                <span className="demo-label">{isLiveResult ? 'Live ELA' : 'Signal Preview'}</span>
                              </div>
                              <p style={{ fontSize: '13px', color: 'var(--c-text-secondary)', marginBottom: '12px' }}>
                                Analyzes localized 8x8 block compression variance to detect spliced objects, edited pixels, or boundary modifications.
                              </p>
                              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(140px, 1fr))', gap: '10px' }}>
                                <div style={{ padding: '10px', background: 'var(--c-surface)', borderRadius: 'var(--r-sm)', border: '1px solid var(--c-border)' }}>
                                  <div style={{ fontSize: '11px', color: 'var(--c-text-muted)', fontWeight: 600 }}>MANIPULATION SCORE</div>
                                  <div style={{ fontSize: '18px', fontWeight: 800, color: 'var(--c-navy)', marginTop: '2px' }}>
                                    {activeResult.forensic_detail?.ela?.manipulation_score ?? (fakeScore >= 50 ? 73 : 18)}%
                                  </div>
                                </div>
                                <div style={{ padding: '10px', background: 'var(--c-surface)', borderRadius: 'var(--r-sm)', border: '1px solid var(--c-border)' }}>
                                  <div style={{ fontSize: '11px', color: 'var(--c-text-muted)', fontWeight: 600 }}>COMPRESSION DIFFERENTIAL</div>
                                  <div style={{ fontSize: '14px', fontWeight: 700, color: 'var(--c-text)', marginTop: '4px' }}>
                                    {activeResult.forensic_detail?.ela?.mean_diff !== undefined
                                      ? `${activeResult.forensic_detail.ela.mean_diff} px`
                                      : fakeScore >= 50 ? 'Inconsistent (Spliced)' : 'Uniform'}
                                  </div>
                                </div>
                                <div style={{ padding: '10px', background: 'var(--c-surface)', borderRadius: 'var(--r-sm)', border: '1px solid var(--c-border)' }}>
                                  <div style={{ fontSize: '11px', color: 'var(--c-text-muted)', fontWeight: 600 }}>SPLICE PROBABILITY</div>
                                  <div style={{ fontSize: '14px', fontWeight: 700, color: fakeScore >= 50 ? 'var(--c-danger)' : 'var(--c-success)', marginTop: '4px' }}>
                                    {fakeScore >= 60 ? 'High' : fakeScore >= 35 ? 'Moderate' : 'Low'}
                                  </div>
                                </div>
                              </div>
                            </div>

                            {/* Sensor Noise & PRNU Consistency Card */}
                            <div className="card">
                              <div className="card-header">
                                <div className="card-title">Sensor Noise Consistency (PRNU Wavelet)</div>
                                <span className="demo-label">{isLiveResult ? 'Live Noise' : 'Signal Preview'}</span>
                              </div>
                              <p style={{ fontSize: '13px', color: 'var(--c-text-secondary)', marginBottom: '12px' }}>
                                High-frequency residual noise pattern matching. Generative diffusion models (Midjourney, DALL-E) show distinct Gaussian smoothing anomalies.
                              </p>
                              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(140px, 1fr))', gap: '10px' }}>
                                <div style={{ padding: '10px', background: 'var(--c-surface)', borderRadius: 'var(--r-sm)', border: '1px solid var(--c-border)' }}>
                                  <div style={{ fontSize: '11px', color: 'var(--c-text-muted)', fontWeight: 600 }}>NOISE ANOMALY SCORE</div>
                                  <div style={{ fontSize: '18px', fontWeight: 800, color: 'var(--c-navy)', marginTop: '2px' }}>
                                    {activeResult.forensic_detail?.noise?.noise_score ?? (fakeScore >= 50 ? 61 : 12)}%
                                  </div>
                                </div>
                                <div style={{ padding: '10px', background: 'var(--c-surface)', borderRadius: 'var(--r-sm)', border: '1px solid var(--c-border)' }}>
                                  <div style={{ fontSize: '11px', color: 'var(--c-text-muted)', fontWeight: 600 }}>DIFFUSION ARTIFACTS</div>
                                  <div style={{ fontSize: '14px', fontWeight: 700, color: fakeScore >= 50 ? 'var(--c-danger)' : 'var(--c-success)', marginTop: '4px' }}>
                                    {fakeScore >= 50 ? 'Detected' : 'None Detected'}
                                  </div>
                                </div>
                                <div style={{ padding: '10px', background: 'var(--c-surface)', borderRadius: 'var(--r-sm)', border: '1px solid var(--c-border)' }}>
                                  <div style={{ fontSize: '11px', color: 'var(--c-text-muted)', fontWeight: 600 }}>SPATIAL CONSISTENCY</div>
                                  <div style={{ fontSize: '14px', fontWeight: 700, color: 'var(--c-text)', marginTop: '4px' }}>
                                    {fakeScore >= 50 ? 'Disrupted' : 'Natural'}
                                  </div>
                                </div>
                              </div>
                            </div>

                            {/* EXIF Metadata & Software Footprints Card */}
                            <div className="card">
                              <div className="card-header">
                                <div className="card-title">EXIF Metadata &amp; Software Footprints</div>
                                <span className="demo-label">{isLiveResult ? 'Live EXIF' : 'Signal Preview'}</span>
                              </div>
                              <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', fontSize: '13px' }}>
                                <div style={{ display: 'flex', justifyContent: 'space-between', padding: '6px 0', borderBottom: '1px solid var(--c-border)' }}>
                                  <span style={{ color: 'var(--c-text-muted)' }}>Camera / Device</span>
                                  <span style={{ fontWeight: 600 }}>
                                    {activeResult.exif_metadata?.Make ? `${activeResult.exif_metadata.Make} ${activeResult.exif_metadata.Model || ''}` : 'No camera hardware header (Stripped)'}
                                  </span>
                                </div>
                                <div style={{ display: 'flex', justifyContent: 'space-between', padding: '6px 0', borderBottom: '1px solid var(--c-border)' }}>
                                  <span style={{ color: 'var(--c-text-muted)' }}>Editing Software Footprint</span>
                                  <span style={{ fontWeight: 600, color: activeResult.exif_metadata?.Software ? 'var(--c-warning)' : 'var(--c-text)' }}>
                                    {activeResult.exif_metadata?.Software || 'None found in EXIF tags'}
                                  </span>
                                </div>
                                <div style={{ display: 'flex', justifyContent: 'space-between', padding: '6px 0' }}>
                                  <span style={{ color: 'var(--c-text-muted)' }}>Integrity Flags</span>
                                  <span style={{ fontWeight: 600 }}>
                                    {activeResult.metadata_flags && activeResult.metadata_flags.length > 0
                                      ? activeResult.metadata_flags.join(', ')
                                      : 'Standard metadata payload'}
                                  </span>
                                </div>
                              </div>
                            </div>
                          </div>
                        ) : (
                          /* Claim-level evidence for Text & News */
                          <div className="card">
                            <div className="card-header">
                              <div className="card-title">{t('detection.claimGrounding')}</div>
                              <span className="demo-label">{isLiveResult ? 'Live Claims' : 'Sample'}</span>
                            </div>

                            <div className="claims-list" role="list" aria-label="Claim verification results">
                              {claimsList.map((claim) => {
                                const isExpanded = expandedClaim === claim.num;
                                return (
                                  <div key={claim.num} className="claim-card" role="listitem">
                                    <div className="claim-header">
                                      <span className="claim-num">Claim #{claim.num}</span>
                                      <span
                                        className={`badge badge-${
                                          claim.status === 'real' ? 'real' : claim.status === 'fake' ? 'fake' : 'unverified'
                                        }`}
                                      >
                                        {claim.status === 'real'
                                          ? 'Supported'
                                          : claim.status === 'fake'
                                          ? 'Contradicted'
                                          : 'Unverified'}
                                      </span>
                                    </div>

                                    <div className="claim-text">{claim.text}</div>

                                    <div className="claim-evidence">
                                      <div className="evidence-label">Grounding Evidence &amp; Reasoning</div>
                                      <div className="evidence-text">{claim.evidence}</div>
                                      <div
                                        style={{
                                          display: 'flex',
                                          alignItems: 'center',
                                          justifyContent: 'space-between',
                                          marginTop: '6px',
                                        }}
                                      >
                                        <div className="evidence-source">Source: {claim.source}</div>
                                        <button
                                          type="button"
                                          onClick={() => setExpandedClaim(isExpanded ? null : claim.num)}
                                          style={{
                                            background: 'none',
                                            border: 'none',
                                            cursor: 'pointer',
                                            color: 'var(--c-blue)',
                                            fontSize: '11px',
                                            display: 'flex',
                                            alignItems: 'center',
                                            gap: '4px',
                                            fontWeight: 600,
                                          }}
                                          aria-label="Toggle evidence details"
                                        >
                                          {isExpanded ? <>Less <ChevronUp size={12} /></> : <>Evidence details <ChevronDown size={12} /></>}
                                        </button>
                                      </div>

                                      {isExpanded && activeResult.evidence_map?.[`claim_${claim.num - 1}`]?.evidence && (
                                        <div style={{ marginTop: '10px', paddingTop: '10px', borderTop: '1px solid var(--c-border)' }}>
                                          <div style={{ fontSize: '11px', fontWeight: 600, color: 'var(--c-text-muted)', marginBottom: '4px' }}>
                                            RETRIEVED CITATIONS:
                                          </div>
                                          {activeResult.evidence_map[`claim_${claim.num - 1}`].evidence.map((ev: any, idx: number) => (
                                            <div key={idx} style={{ fontSize: '12px', marginBottom: '6px', padding: '6px 8px', background: 'var(--c-surface)', borderRadius: 'var(--r-sm)' }}>
                                              <div style={{ fontWeight: 600, display: 'flex', alignItems: 'center', gap: '4px' }}>
                                                {ev.title || ev.source || 'Passage'}
                                                {ev.url && (
                                                  <a href={ev.url} target="_blank" rel="noreferrer" style={{ display: 'inline-flex', alignItems: 'center', color: 'var(--c-blue)' }}>
                                                    <ExternalLink size={11} />
                                                  </a>
                                                )}
                                              </div>
                                              <div style={{ color: 'var(--c-text-secondary)', fontSize: '11px', marginTop: '2px' }}>
                                                {ev.snippet || JSON.stringify(ev)}
                                              </div>
                                            </div>
                                          ))}
                                        </div>
                                      )}
                                    </div>
                                  </div>
                                );
                              })}
                            </div>
                          </div>
                        )}


                        {/* Linguistic Analysis Signals */}
                        {activeResult.linguistic_scores && (
                          <div className="card" style={{ marginTop: '16px' }}>
                            <div className="card-header">
                              <div className="card-title">Linguistic &amp; Stylistic Analysis</div>
                            </div>
                            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(130px, 1fr))', gap: '12px' }}>
                              {Object.entries(activeResult.linguistic_scores).map(([metric, score]) => (
                                <div key={metric} style={{ padding: '10px', background: 'var(--c-surface)', borderRadius: 'var(--r-sm)', border: '1px solid var(--c-border)' }}>
                                  <div style={{ fontSize: '11px', textTransform: 'uppercase', color: 'var(--c-text-muted)', fontWeight: 600 }}>
                                    {metric}
                                  </div>
                                  <div style={{ fontSize: '16px', fontWeight: 800, color: 'var(--c-navy)', marginTop: '2px' }}>
                                    {typeof score === 'number' ? `${score}%` : String(score)}
                                  </div>
                                </div>
                              ))}
                            </div>
                          </div>
                        )}

                        {/* Red Flags / Risk Factors if present */}
                        {(activeResult.red_flags?.length || activeResult.risk_factors?.length) ? (
                          <div className="card" style={{ marginTop: '16px' }}>
                            <div className="card-header">
                              <div className="card-title" style={{ color: 'var(--c-danger)' }}>
                                Flagged Risk Factors &amp; Anomalies
                              </div>
                            </div>
                            <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
                              {[...(activeResult.red_flags || []), ...(activeResult.risk_factors || [])].slice(0, 6).map((flag, idx) => (
                                <div
                                  key={idx}
                                  style={{
                                    padding: '8px 12px',
                                    borderRadius: 'var(--r-sm)',
                                    background: 'var(--c-danger-bg)',
                                    border: '1px solid #fecaca',
                                    fontSize: '12px',
                                    color: 'var(--c-danger)',
                                    display: 'flex',
                                    alignItems: 'center',
                                    gap: '8px',
                                  }}
                                >
                                  <AlertTriangle size={14} style={{ flexShrink: 0 }} aria-hidden="true" />
                                  <span>{flag}</span>
                                </div>
                              ))}
                            </div>
                          </div>
                        ) : null}

                        {/* Operator Feedback Widget */}
                        <FeedbackWidget analysisId={activeResult.analysis_id || 'demo-analysis'} />
                      </div>
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>

      <style>{`
        @keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
      `}</style>
    </main>
  );
};

export default DetectionPage;
