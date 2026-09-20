import React, { useState } from 'react';
import { ThumbsUp, ThumbsDown, CheckCircle, Send, MessageSquare } from 'lucide-react';
import { api } from '../../services/api';

interface FeedbackWidgetProps {
  analysisId?: string;
}

export const FeedbackWidget: React.FC<FeedbackWidgetProps> = ({ analysisId }) => {
  const [selected, setSelected] = useState<boolean | null>(null);
  const [note, setNote] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [submitted, setSubmitted] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (!analysisId) return null;

  const handleSubmit = async () => {
    if (selected === null) return;
    setSubmitting(true);
    setError(null);
    try {
      await api.submitFeedback(analysisId, selected, note.trim());
      setSubmitted(true);
    } catch (err: any) {
      setError(err.message || 'Failed to submit feedback. Please try again.');
    } finally {
      setSubmitting(false);
    }
  };

  if (submitted) {
    return (
      <div
        className="card"
        style={{
          marginTop: '20px',
          background: 'var(--c-success-bg)',
          borderColor: '#b6dfc6',
          display: 'flex',
          alignItems: 'center',
          gap: '12px',
          padding: '16px 20px',
        }}
        role="status"
        aria-live="polite"
      >
        <CheckCircle size={20} color="var(--c-success)" aria-hidden="true" />
        <div>
          <div style={{ fontWeight: 600, fontSize: '14px', color: 'var(--c-text)' }}>
            Feedback Recorded
          </div>
          <div style={{ fontSize: '12px', color: 'var(--c-text-secondary)', marginTop: '2px' }}>
            Thank you. Your assessment feeds into our human-in-the-loop continuous learning pipeline.
          </div>
        </div>
      </div>
    );
  }

  return (
    <div
      className="card"
      style={{ marginTop: '20px', borderLeft: '4px solid var(--c-blue)' }}
      role="region"
      aria-label="Operator Verification Feedback"
    >
      <div className="card-header" style={{ marginBottom: '10px' }}>
        <MessageSquare size={16} color="var(--c-blue)" aria-hidden="true" />
        <div className="card-title">Operator Correctness Assessment</div>
        <span className="demo-label" style={{ marginLeft: 'auto' }}>Human-in-the-Loop</span>
      </div>

      <p style={{ fontSize: '13px', color: 'var(--c-text-secondary)', marginBottom: '14px' }}>
        Does this verdict accurately reflect the authenticity of the analyzed content?
      </p>

      <div style={{ display: 'flex', gap: '10px', alignItems: 'center', flexWrap: 'wrap' }}>
        <button
          type="button"
          onClick={() => setSelected(true)}
          className={`btn-secondary`}
          style={{
            borderColor: selected === true ? 'var(--c-success)' : undefined,
            background: selected === true ? 'var(--c-success-bg)' : undefined,
            color: selected === true ? 'var(--c-success)' : undefined,
            display: 'inline-flex',
            alignItems: 'center',
            gap: '8px',
            padding: '8px 14px',
            fontSize: '13px',
            fontWeight: 600,
          }}
          aria-pressed={selected === true}
        >
          <ThumbsUp size={15} aria-hidden="true" />
          Accurate Verdict
        </button>

        <button
          type="button"
          onClick={() => setSelected(false)}
          className={`btn-secondary`}
          style={{
            borderColor: selected === false ? 'var(--c-danger)' : undefined,
            background: selected === false ? 'var(--c-danger-bg)' : undefined,
            color: selected === false ? 'var(--c-danger)' : undefined,
            display: 'inline-flex',
            alignItems: 'center',
            gap: '8px',
            padding: '8px 14px',
            fontSize: '13px',
            fontWeight: 600,
          }}
          aria-pressed={selected === false}
        >
          <ThumbsDown size={15} aria-hidden="true" />
          Inaccurate Verdict
        </button>
      </div>

      {selected !== null && (
        <div style={{ marginTop: '14px' }}>
          <label
            htmlFor={`feedback-note-${analysisId}`}
            style={{ fontSize: '12px', fontWeight: 600, color: 'var(--c-text-secondary)', display: 'block', marginBottom: '6px' }}
          >
            Operator Note (Optional):
          </label>
          <textarea
            id={`feedback-note-${analysisId}`}
            value={note}
            onChange={(e) => setNote(e.target.value)}
            placeholder="Add context or notes regarding this verdict for dataset calibration..."
            rows={2}
            style={{
              width: '100%',
              padding: '8px 12px',
              fontSize: '13px',
              border: '1px solid var(--c-border)',
              borderRadius: 'var(--r-md)',
              background: 'var(--c-white)',
              color: 'var(--c-text)',
              fontFamily: 'inherit',
              resize: 'vertical',
            }}
          />

          {error && (
            <div style={{ color: 'var(--c-danger)', fontSize: '12px', marginTop: '6px' }}>
              ⚠ {error}
            </div>
          )}

          <div style={{ marginTop: '10px', display: 'flex', justifyContent: 'flex-end' }}>
            <button
              type="button"
              onClick={handleSubmit}
              disabled={submitting}
              className="btn-primary"
              style={{ display: 'inline-flex', alignItems: 'center', gap: '6px', fontSize: '12px', padding: '6px 14px' }}
            >
              <Send size={13} aria-hidden="true" />
              {submitting ? 'Submitting...' : 'Submit Feedback'}
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
