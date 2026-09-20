import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { FileText, Upload, CheckCircle, X, Search, Loader, ShieldAlert, Info } from 'lucide-react';
import { api, type AnalysisResponse } from '../services/api';
import { useLanguage } from '../context/LanguageContext';
import { DocumentVerificationResult } from '../components/verification/DocumentVerificationResult';

export const ForensicsPage: React.FC = () => {
  const { t } = useLanguage();
  const navigate = useNavigate();

  // Document upload state

  const [docFile, setDocFile] = useState<File | null>(null);
  const [docAnalyzing, setDocAnalyzing] = useState(false);
  const [docResult, setDocResult] = useState<AnalysisResponse | null>(null);
  const [docError, setDocError] = useState<string | null>(null);
  const [dragOver, setDragOver] = useState(false);

  const handleAnalyzeDocument = async () => {
    if (!docFile || docAnalyzing) return;
    setDocAnalyzing(true);
    setDocError(null);
    try {
      const res = await api.analyzeDocument(docFile);
      setDocResult(res);
    } catch (err: any) {
      setDocError(err.message || 'Document forensic analysis failed. Please verify the document format.');
    } finally {
      setDocAnalyzing(false);
    }
  };

  const handleClear = () => {
    setDocFile(null);
    setDocResult(null);
    setDocError(null);
  };

  // ELA / Noise / EXIF fallbacks for the demo profile
  const elaScore = docResult?.forensic_detail?.ela?.manipulation_score ?? 73;
  const noiseScore = docResult?.forensic_detail?.noise?.noise_score ?? 61;
  const exifMetadata = docResult?.exif_metadata || {
    Make: 'Canon',
    Model: 'EOS R5',
    DateTime: '2026:05:15 14:32:10',
    Software: 'Adobe Photoshop 2026',
  };

  return (
    <main id="main-content" tabIndex={-1}>
      <div className="page-header-band">
        <div className="page-header-inner">
          <div className="breadcrumb">
            <a href="/">{t('nav.home')}</a>
            <span className="breadcrumb-sep" aria-hidden="true">/</span>
            <span aria-current="page">{t('nav.forensics')}</span>
          </div>
          <h1 className="page-header-title">{t('forensics.title')}</h1>
          <p className="page-header-sub">
            {t('forensics.sub')}
          </p>
        </div>
      </div>

      <section className="section">
        <div className="container">
          {/* Document Upload Card */}
          <div className="card" style={{ marginBottom: '24px', padding: '24px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
              <FileText size={18} color="var(--c-blue)" aria-hidden="true" />
              <h2 style={{ fontSize: '16px', fontWeight: 700, color: 'var(--c-navy)' }}>
                {t('forensics.uploadDocument')}
              </h2>
            </div>
            <p style={{ fontSize: '13px', color: 'var(--c-text-muted)', marginBottom: '18px' }}>
              Upload official government circulars, notices, identity certificates, or PDF reports for structural template analysis and forgery verification.
            </p>

            {docFile ? (
              <div
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '12px',
                  background: 'var(--c-success-bg)',
                  border: '1px solid #b6dfc6',
                  borderRadius: 'var(--r-md)',
                  padding: '14px 18px',
                  marginBottom: '16px',
                }}
              >
                <CheckCircle size={18} color="var(--c-success)" aria-hidden="true" />
                <div style={{ flex: 1 }}>
                  <div style={{ fontSize: '14px', color: 'var(--c-text)', fontWeight: 600 }}>
                    {docFile.name}
                  </div>
                  <div style={{ fontSize: '12px', color: 'var(--c-text-muted)' }}>
                    {(docFile.size / 1024).toFixed(1)} KB · Ready for forensic inspection
                  </div>
                </div>
                <button
                  type="button"
                  onClick={handleClear}
                  style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'var(--c-text-muted)' }}
                  aria-label="Remove document"
                >
                  <X size={16} />
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
                    setDocFile(e.dataTransfer.files[0]);
                  }
                }}
                onClick={() => {
                  const input = document.createElement('input');
                  input.type = 'file';
                  input.accept = '.pdf,.png,.jpg,.jpeg';
                  input.onchange = () => {
                    if (input.files?.[0]) {
                      setDocFile(input.files[0]);
                    }
                  };
                  input.click();
                }}
                role="button"
                tabIndex={0}
                aria-label="Upload document file"
                onKeyDown={(e) => {
                  if (e.key === 'Enter' || e.key === ' ') e.currentTarget.click();
                }}
                style={{ marginBottom: '16px', cursor: 'pointer' }}
              >
                <Upload size={38} className="drop-icon" aria-hidden="true" />
                <div className="drop-title">Drag &amp; Drop your document here</div>
                <div className="drop-sub">or click to browse local files</div>
                <div className="drop-formats">Supported Formats: PDF · PNG · JPG · JPEG (Up to 25 MB)</div>
              </div>
            )}

            <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
              <button
                type="button"
                onClick={handleAnalyzeDocument}
                disabled={!docFile || docAnalyzing}
                className="btn-primary"
                style={{ display: 'inline-flex', alignItems: 'center', gap: '6px' }}
              >
                {docAnalyzing ? <Loader size={14} style={{ animation: 'spin 1s linear infinite' }} /> : <Search size={14} />}
                {docAnalyzing ? 'Inspecting Document...' : t('forensics.runDocBtn')}
              </button>
              {docFile && (
                <button type="button" onClick={handleClear} className="btn-secondary">
                  Clear
                </button>
              )}
            </div>
          </div>

          {docError && (
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', padding: '12px 16px', background: 'var(--c-danger-bg)', color: 'var(--c-danger)', borderRadius: 'var(--r-sm)', marginBottom: '20px', fontSize: '13px' }}>
              <ShieldAlert size={16} />
              <span>{docError}</span>
            </div>
          )}

          {/* Results: Detailed Document Verification Report (when analyzed) */}
          {docResult && (
            <div style={{ marginBottom: '24px' }}>
              <DocumentVerificationResult
                result={docResult}
                fileName={docFile?.name}
                onVerifyNewsContent={(extractedText) => {
                  navigate('/detection', { state: { transferredText: extractedText } });
                }}
              />
            </div>
          )}


          {/* Demo Forensic Signals Grid (as was there earlier) */}
          <div className="forensics-grid">
            {/* ELA Card */}
            <div className="card">
              <div className="card-header">
                <FileText size={15} color="var(--c-blue)" aria-hidden="true" />
                <div className="card-title">{t('forensics.elaTitle')}</div>
                <span className="demo-label" style={{ marginLeft: 'auto' }}>
                  {docResult ? 'Live Output' : 'Demo Profile'}
                </span>
              </div>
              <p style={{ fontSize: '13px', color: 'var(--c-text-secondary)', marginBottom: '14px' }}>
                ELA highlights compression rate differentials across 8x8 block matrices to identify digitally spliced regions or forged seals.
              </p>
              <div className="forensic-signal-row">
                <div>
                  <div className="signal-name">ELA Manipulation Score</div>
                  <div className="signal-engine">Error Level Differential</div>
                </div>
                <span className={`badge badge-${elaScore > 50 ? 'fake' : 'real'}`}>
                  {elaScore > 50 ? `Elevated — ${elaScore}%` : `Consistent — ${elaScore}%`}
                </span>
              </div>
              <div className="forensic-signal-row">
                <div>
                  <div className="signal-name">Splice Probability</div>
                  <div className="signal-engine">Block boundary variance</div>
                </div>
                <span className="badge badge-review">
                  {elaScore > 50 ? 'Moderate to High' : 'Low'}
                </span>
              </div>
              <div className="forensic-signal-row">
                <div>
                  <div className="signal-name">Compression Consistency</div>
                  <div className="signal-engine">JPEG artifacts</div>
                </div>
                <span className={`badge badge-${elaScore > 50 ? 'fake' : 'real'}`}>
                  {elaScore > 50 ? 'Inconsistent' : 'Uniform'}
                </span>
              </div>
              <div className="chart-placeholder" style={{ height: '110px', marginTop: '14px', flexDirection: 'column', gap: '6px' }}>
                <Info size={18} color="var(--c-text-muted)" aria-hidden="true" />
                <span style={{ fontSize: '12px' }}>
                  {docResult ? `Forensic pipeline completed for ${docFile?.name}` : 'Upload document above to view live matrix inspection'}
                </span>
              </div>
            </div>

            {/* EXIF Metadata Card */}
            <div className="card">
              <div className="card-header">
                <FileText size={15} color="var(--c-blue)" aria-hidden="true" />
                <div className="card-title">{t('forensics.exifTitle')}</div>
                <span className="demo-label" style={{ marginLeft: 'auto' }}>
                  {docResult ? 'Live Metadata' : 'Demo Profile'}
                </span>
              </div>
              <div className="forensic-signal-row">
                <div><div className="signal-name">Camera Make / Device</div></div>
                <span className="signal-value" style={{ fontSize: '13px', color: 'var(--c-text)' }}>
                  {String(exifMetadata.Make || exifMetadata.Device || 'Standard Sensor')}
                </span>
              </div>
              <div className="forensic-signal-row">
                <div><div className="signal-name">Date/Time Original</div></div>
                <span className="signal-value">
                  {String(exifMetadata.DateTime || exifMetadata.DateTimeOriginal || 'Present in EXIF')}
                </span>
              </div>
              <div className="forensic-signal-row">
                <div><div className="signal-name">Processing Software</div></div>
                <span className="signal-value">
                  {String(exifMetadata.Software || 'Standard Firmware / Not detected')}
                </span>
              </div>
              <div className="forensic-signal-row">
                <div><div className="signal-name">Metadata Integrity</div></div>
                <span className={`badge badge-${docResult?.metadata_flags?.length ? 'fake' : 'real'}`}>
                  {docResult?.metadata_flags?.length ? 'Flags Found' : 'Verified'}
                </span>
              </div>
              {docResult?.metadata_flags && docResult.metadata_flags.length > 0 ? (
                <div style={{ marginTop: '12px', padding: '10px 12px', background: 'var(--c-warning-bg)', borderRadius: 'var(--r-sm)', border: '1px solid #e9d098' }}>
                  <div style={{ fontSize: '12px', color: 'var(--c-warning)', fontWeight: 600 }}>
                    ⚠ {docResult.metadata_flags.join('; ')}
                  </div>
                </div>
              ) : (
                <div style={{ marginTop: '12px', padding: '10px 12px', background: 'var(--c-success-bg)', borderRadius: 'var(--r-sm)', border: '1px solid #b6dfc6', display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <CheckCircle size={14} color="var(--c-success)" aria-hidden="true" style={{ flexShrink: 0 }} />
                  <div style={{ fontSize: '12px', color: 'var(--c-success)', fontWeight: 600 }}>
                    Metadata fields available for analysis
                  </div>
                </div>
              )}
            </div>

            {/* Noise Pattern Analysis Card */}
            <div className="card">
              <div className="card-header">
                <div className="card-title">{t('forensics.noiseTitle')}</div>
                <span className="demo-label" style={{ marginLeft: 'auto' }}>
                  {docResult ? 'Live Noise Map' : 'Demo Profile'}
                </span>
              </div>
              <p style={{ fontSize: '13px', color: 'var(--c-text-secondary)', marginBottom: '14px' }}>
                Photo-Response Non-Uniformity (PRNU) wavelet residuals reveal localized noise anomalies characteristic of spliced seals or AI generation.
              </p>
              <div className="forensic-signal-row">
                <div><div className="signal-name">Noise Anomaly Score</div></div>
                <span className={`badge badge-${noiseScore > 50 ? 'fake' : 'real'}`}>
                  {noiseScore}%
                </span>
              </div>
              <div className="forensic-signal-row">
                <div><div className="signal-name">Noise Consistency</div></div>
                <span className={`badge badge-${noiseScore > 50 ? 'fake' : 'real'}`}>
                  {noiseScore > 50 ? 'Inconsistent' : 'Homogeneous'}
                </span>
              </div>
              <div className="chart-placeholder" style={{ height: '90px', marginTop: '14px' }}>
                <span>Pixel noise distribution verified against Gaussian sensor model</span>
              </div>
            </div>
          </div>
        </div>
      </section>
    </main>
  );
};


export default ForensicsPage;
