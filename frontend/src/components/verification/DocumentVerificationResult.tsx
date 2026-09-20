import React, { useState } from 'react';
import { FileText, CheckCircle2, XCircle, AlertTriangle, ShieldCheck, Copy, Check, Sparkles, ArrowRight } from 'lucide-react';
import { FeedbackWidget } from './FeedbackWidget';
import type { AnalysisResponse } from '../../services/api';

interface DocumentVerificationResultProps {
  result: AnalysisResponse;
  fileName?: string | null;
  onVerifyNewsContent?: (extractedText: string) => void;
}

export const DocumentVerificationResult: React.FC<DocumentVerificationResultProps> = ({
  result,
  fileName,
  onVerifyNewsContent,
}) => {
  const [copied, setCopied] = useState(false);


  const template = result.template_analysis;
  const expectedFields = template?.expected_fields || [];
  const foundSet = new Set(template?.found_fields || []);
  const completeness = template?.completeness ?? 0;

  const handleCopyOCR = () => {
    if (result.ocr_text) {
      navigator.clipboard.writeText(result.ocr_text);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const docTypeLabel = (result.doc_type || 'General Document').replace(/_/g, ' ').toUpperCase();

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      {/* Top Header Card */}
      <div className="card">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '10px' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '6px' }}>
              <span
                style={{
                  background: 'var(--c-light-blue)',
                  color: 'var(--c-blue)',
                  fontSize: '11px',
                  fontWeight: 700,
                  padding: '3px 8px',
                  borderRadius: 'var(--r-sm)',
                  letterSpacing: '0.05em',
                }}
              >
                {docTypeLabel}
              </span>
              {fileName && (
                <span style={{ fontSize: '13px', color: 'var(--c-text-muted)', fontWeight: 500 }}>
                  {fileName}
                </span>
              )}
            </div>
            <h3 style={{ fontSize: '18px', fontWeight: 700, color: 'var(--c-navy)' }}>
              Document Verification Report
            </h3>
          </div>

          <div style={{ display: 'flex', gap: '12px' }}>
            <div style={{ textAlign: 'right' }}>
              <div style={{ fontSize: '11px', color: 'var(--c-text-muted)', fontWeight: 600 }}>AUTHENTICITY</div>
              <div style={{ fontSize: '18px', fontWeight: 800, color: (result.authenticity_score ?? 70) >= 60 ? 'var(--c-success)' : 'var(--c-danger)' }}>
                {result.authenticity_score ?? (100 - (result.forgery_score ?? 0))}%
              </div>
            </div>
            <div style={{ textAlign: 'right' }}>
              <div style={{ fontSize: '11px', color: 'var(--c-text-muted)', fontWeight: 600 }}>FORGERY RISK</div>
              <div style={{ fontSize: '18px', fontWeight: 800, color: (result.forgery_score ?? 0) >= 40 ? 'var(--c-danger)' : 'var(--c-success)' }}>
                {result.forgery_score ?? 0}%
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Recommendation Banner if provided */}
      {result.recommendation && (
        <div
          style={{
            padding: '14px 18px',
            background: 'var(--c-warning-bg)',
            border: '1px solid #e9d098',
            borderRadius: 'var(--r-md)',
            display: 'flex',
            alignItems: 'flex-start',
            gap: '12px',
          }}
        >
          <AlertTriangle size={18} color="var(--c-warning)" style={{ flexShrink: 0, marginTop: '2px' }} aria-hidden="true" />
          <div>
            <div style={{ fontSize: '12px', fontWeight: 700, textTransform: 'uppercase', color: 'var(--c-warning)', letterSpacing: '0.05em' }}>
              Operational Recommendation
            </div>
            <div style={{ fontSize: '13px', color: 'var(--c-text)', marginTop: '2px', lineHeight: 1.5 }}>
              {result.recommendation}
            </div>
          </div>
        </div>
      )}

      {/* Two Column Section */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
        {/* Template Field Completeness */}
        <div className="card">
          <div className="card-header">
            <ShieldCheck size={16} color="var(--c-blue)" aria-hidden="true" />
            <div className="card-title">Template Field Completeness</div>
            <span
              style={{
                marginLeft: 'auto',
                fontSize: '12px',
                fontWeight: 700,
                color: completeness >= 80 ? 'var(--c-success)' : 'var(--c-warning)',
              }}
            >
              {completeness}% Found
            </span>
          </div>

          <p style={{ fontSize: '12px', color: 'var(--c-text-secondary)', marginBottom: '14px' }}>
            Structural comparison against verified government and institutional templates.
          </p>

          {expectedFields.length > 0 ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              {expectedFields.map((field) => {
                const isFound = foundSet.has(field);
                return (
                  <div
                    key={field}
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between',
                      padding: '8px 12px',
                      borderRadius: 'var(--r-sm)',
                      background: isFound ? 'var(--c-surface)' : 'var(--c-danger-bg)',
                      border: `1px solid ${isFound ? 'var(--c-border)' : '#fed7d7'}`,
                    }}
                  >
                    <span style={{ fontSize: '13px', fontWeight: 500, color: 'var(--c-text)' }}>
                      {field.replace(/_/g, ' ').replace(/\b\w/g, (l) => l.toUpperCase())}
                    </span>
                    <span style={{ display: 'flex', alignItems: 'center', gap: '5px', fontSize: '12px', fontWeight: 600, color: isFound ? 'var(--c-success)' : 'var(--c-danger)' }}>
                      {isFound ? (
                        <>
                          <CheckCircle2 size={15} aria-hidden="true" /> Found
                        </>
                      ) : (
                        <>
                          <XCircle size={15} aria-hidden="true" /> Missing
                        </>
                      )}
                    </span>
                  </div>
                );
              })}
            </div>
          ) : (
            <div style={{ fontSize: '13px', color: 'var(--c-text-muted)', fontStyle: 'italic' }}>
              Standard generic template analyzed without schema constraints.
            </div>
          )}
        </div>

        {/* OCR Text Inspector */}
        <div className="card">
          <div className="card-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '8px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <FileText size={16} color="var(--c-blue)" aria-hidden="true" />
              <div className="card-title">Extracted Text (OCR)</div>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              {result.ocr_text && onVerifyNewsContent && (
                <button
                  type="button"
                  onClick={() => onVerifyNewsContent(result.ocr_text || '')}
                  className="btn-primary"
                  style={{ padding: '5px 10px', fontSize: '11px', display: 'inline-flex', alignItems: 'center', gap: '5px' }}
                  aria-label="Verify extracted news content with 6 Agents"
                >
                  <Sparkles size={13} aria-hidden="true" />
                  Verify this News Content with 6 Agents
                  <ArrowRight size={13} aria-hidden="true" />
                </button>
              )}
              {result.ocr_text && (
                <button
                  type="button"
                  onClick={handleCopyOCR}
                  className="btn-secondary"
                  style={{ padding: '5px 8px', fontSize: '11px', display: 'inline-flex', alignItems: 'center', gap: '4px' }}
                  aria-label="Copy extracted OCR text"
                >
                  {copied ? <Check size={12} color="var(--c-success)" /> : <Copy size={12} />}
                  {copied ? 'Copied' : 'Copy'}
                </button>
              )}
            </div>
          </div>

          <div
            style={{
              maxHeight: '260px',
              overflowY: 'auto',
              background: 'var(--c-surface)',
              border: '1px solid var(--c-border)',
              borderRadius: 'var(--r-sm)',
              padding: '12px',
              fontSize: '12px',
              fontFamily: 'monospace',
              lineHeight: 1.6,
              color: 'var(--c-text)',
              whiteSpace: 'pre-wrap',
            }}
          >
            {result.ocr_text ? result.ocr_text.trim() : 'No textual content extracted from this document.'}
          </div>

          {result.ocr_text && onVerifyNewsContent && (
            <div
              style={{
                marginTop: '10px',
                padding: '8px 12px',
                background: 'var(--c-light-blue)',
                border: '1px solid #cce3f5',
                borderRadius: 'var(--r-sm)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                fontSize: '12px',
                color: 'var(--c-blue)',
              }}
            >
              <span>Does this document contain claims or news articles?</span>
              <button
                type="button"
                onClick={() => onVerifyNewsContent(result.ocr_text || '')}
                style={{
                  background: 'none',
                  border: 'none',
                  color: 'var(--c-blue)',
                  fontWeight: 700,
                  cursor: 'pointer',
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '4px',
                }}
              >
                Send to 6-Agent Fact Checker &rarr;
              </button>
            </div>
          )}
        </div>
      </div>


      {/* Forgery Indicators & Authenticity Signals */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
        {/* Forgery Indicators */}
        <div className="card">
          <div className="card-header">
            <div className="card-title" style={{ color: 'var(--c-danger)' }}>
              Forgery & Tampering Indicators
            </div>
          </div>
          {result.forgery_indicators && result.forgery_indicators.length > 0 ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
              {result.forgery_indicators.map((ind, idx) => (
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
                  <span>{ind}</span>
                </div>
              ))}
            </div>
          ) : (
            <div style={{ fontSize: '13px', color: 'var(--c-text-muted)', fontStyle: 'italic' }}>
              No critical forgery anomalies flagged.
            </div>
          )}
        </div>

        {/* Authenticity Signals */}
        <div className="card">
          <div className="card-header">
            <div className="card-title" style={{ color: 'var(--c-success)' }}>
              Authenticity Signals
            </div>
          </div>
          {result.authenticity_signals && result.authenticity_signals.length > 0 ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
              {result.authenticity_signals.map((sig, idx) => (
                <div
                  key={idx}
                  style={{
                    padding: '8px 12px',
                    borderRadius: 'var(--r-sm)',
                    background: 'var(--c-success-bg)',
                    border: '1px solid #bbf7d0',
                    fontSize: '12px',
                    color: 'var(--c-success)',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '8px',
                  }}
                >
                  <CheckCircle2 size={14} style={{ flexShrink: 0 }} aria-hidden="true" />
                  <span>{sig}</span>
                </div>
              ))}
            </div>
          ) : (
            <div style={{ fontSize: '13px', color: 'var(--c-text-muted)', fontStyle: 'italic' }}>
              General document integrity checked.
            </div>
          )}
        </div>
      </div>

      {/* Operator Feedback Widget */}
      {result.analysis_id || result.doc_id ? (
        <FeedbackWidget analysisId={result.analysis_id || result.doc_id} />
      ) : null}
    </div>
  );
};
