/**
 * TruthLens AI 2.0 — Backend API Client
 * Connects frontend to FastAPI backend endpoints:
 *  - /health
 *  - /analyze/text
 *  - /analyze/image
 *  - /analyze/document
 *  - /analyze/{id}/evidence
 *  - /analytics/stats
 *  - /analytics/daily
 *  - /history
 */

const API_BASE = (import.meta.env.VITE_API_BASE_URL || import.meta.env.VITE_API_URL || '').replace(/\/$/, '');



export interface HealthResponse {
  status: string;
  service: string;
  version: string;
}

export interface AnalysisResponse {
  analysis_id?: string;
  verdict: string;
  trust_score?: number;
  fake_score?: number;
  confidence?: number | string;
  risk_level?: string;
  risk_score?: number;
  explanation?: string | any[];
  claims?: any[];
  claim_verification?: any[];
  extracted_claims?: any[];
  evidence_map?: Record<string, any>;
  claim_clusters?: {
    clusters: number[][];
    cluster_count: number;
    duplicate_groups: number;
  };
  reasoning_chain?: string[];
  key_signals?: string[];
  red_flags?: string[];
  risk_factors?: string[];
  linguistic_scores?: {
    clickbait?: number;
    emotional?: number;
    urgency?: number;
    certainty?: number;
    propaganda?: number;
    credibility?: number;
    [key: string]: any;
  };
  bias_score?: number;
  manipulation_score?: number;
  bias_direction?: string;
  fact_check_summary?: string;
  forensic_signals?: any;
  agent_trace?: Array<{
    agent: string;
    [key: string]: any;
  }>;
  explainability_report?: {
    trust_score?: number;
    confidence?: number;
    verdict?: string;
    reasoning_chain?: string[];
    risk_factors?: string[];
    supporting_sources?: Array<{
      title: string;
      url: string;
      source: string;
      relevance: number;
    }>;
    evidence_summary?: string;
    claim_breakdown?: {
      total: number;
      supported: number;
      contradicted: number;
      unverified: number;
    };
    [key: string]: any;
  };

  // Image-specific fields
  ai_generated_score?: number;
  authenticity_score?: number;
  findings?: string[];
  metadata_flags?: string[];
  exif_metadata?: Record<string, any>;
  image_size?: string;
  image_mode?: string;
  file_size?: string;
  format?: string;
  forensic_detail?: {
    ela?: Record<string, any>;
    noise?: Record<string, any>;
    compression?: Record<string, any>;
    edge?: Record<string, any>;
    exif?: Record<string, any>;
  };

  // Document-specific fields
  doc_type?: string;
  doc_id?: string;
  ocr_text?: string;
  forgery_score?: number;
  recommendation?: string;
  forgery_indicators?: string[];
  authenticity_signals?: string[];
  structural_issues?: string[];
  template_analysis?: {
    expected_fields?: string[];
    found_fields?: string[];
    missing_fields?: string[];
    completeness?: number;
  };

  created_at?: string;
}

export interface AnalyticsStats {
  total: number;
  fake: number;
  docs: number;
  images: number;
  texts: number;
  fb_total: number;
  fb_ok: number;
  accuracy: number;
  recent?: Array<{
    verdict: string;
    fake_score: number;
    type: string;
    created_at: string;
  }>;
  [key: string]: any;
}

export interface ContinuousLearningStatus {
  readiness: {
    total_samples: number;
    correct: number;
    incorrect: number;
    target_samples: number;
    progress_pct: number;
    ready_to_retrain: boolean;
    priority_types: Array<{ type: string; error_rate: number }>;
  };
  versions: Array<{
    version: string;
    accuracy: number;
    samples: number;
    notes: string;
    created_at: string;
  }>;
  recommendations: {
    has_recommendation: boolean;
    recommendations?: string[];
    reason?: string;
    sample_size?: number;
  };
}

export interface HistoryItem {
  analysis_id: string;
  type: string;
  verdict: string;
  fake_score: number;
  confidence: string;
  created_at: string;
}

export interface HistoryResponse {
  total: number;
  limit: number;
  offset: number;
  items: HistoryItem[];
}

export const api = {
  // Health check
  async getHealth(): Promise<HealthResponse> {
    const res = await fetch(`${API_BASE}/health`);
    if (!res.ok) throw new Error(`Health check failed: ${res.status}`);
    return res.json();
  },

  // Analyze text
  async analyzeText(text: string): Promise<AnalysisResponse> {
    const res = await fetch(`${API_BASE}/analyze/text`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text }),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: res.statusText }));
      throw new Error(err.detail || 'Text analysis failed');
    }
    return res.json();
  },

  // Analyze image
  async analyzeImage(file: File): Promise<AnalysisResponse> {
    const formData = new FormData();
    formData.append('file', file);
    const res = await fetch(`${API_BASE}/analyze/image`, {
      method: 'POST',
      body: formData,
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: res.statusText }));
      throw new Error(err.detail || 'Image analysis failed');
    }
    return res.json();
  },

  // Analyze document
  async analyzeDocument(file: File): Promise<AnalysisResponse> {
    const formData = new FormData();
    formData.append('file', file);
    const res = await fetch(`${API_BASE}/analyze/document`, {
      method: 'POST',
      body: formData,
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: res.statusText }));
      throw new Error(err.detail || 'Document analysis failed');
    }
    return res.json();
  },

  // Fetch analytics stats
  async getStats(): Promise<AnalyticsStats> {
    const res = await fetch(`${API_BASE}/analytics/stats`);
    if (!res.ok) throw new Error(`Analytics fetch failed: ${res.status}`);
    return res.json();
  },

  // Fetch daily analytics
  async getDailyAnalytics(days = 30): Promise<Array<{ date: string; count: number }>> {
    const res = await fetch(`${API_BASE}/analytics/daily?days=${days}`);
    if (!res.ok) throw new Error(`Daily analytics failed: ${res.status}`);
    return res.json();
  },

  // Fetch continuous learning status
  async getLearningStatus(): Promise<ContinuousLearningStatus> {
    const res = await fetch(`${API_BASE}/analytics/learning`);
    if (!res.ok) throw new Error(`Learning status fetch failed: ${res.status}`);
    return res.json();
  },

  // Submit correctness feedback
  async submitFeedback(analysisId: string, isCorrect: boolean, userNote = ''): Promise<{ message: string }> {
    const res = await fetch(`${API_BASE}/analyze/feedback`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        analysis_id: analysisId,
        is_correct: isCorrect,
        user_note: userNote,
      }),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: res.statusText }));
      throw new Error(err.detail || 'Feedback submission failed');
    }
    return res.json();
  },

  // Fetch history
  async getHistory(limit = 10, offset = 0, type?: string): Promise<HistoryResponse> {
    const params = new URLSearchParams({
      limit: String(limit),
      offset: String(offset),
    });
    if (type) params.append('type', type);
    const res = await fetch(`${API_BASE}/history?${params.toString()}`);
    if (!res.ok) throw new Error(`History fetch failed: ${res.status}`);
    return res.json();
  },
};


// ─── PS 26188 — Border Intelligence API ──────────────────────

export interface ScreeningResult {
  screening_id: string;
  document_type: string;
  risk_level: 'CLEAR' | 'MANUAL_REVIEW' | 'HIGH_RISK';
  risk_score: number;
  verdict: string;
  started_at: string;
  completed_at?: string;
  demo_case?: string | null;
  demo_metadata?: any;
  prototype_notice: string;
  ocr?: any;
  mrz?: any;
  validation?: any;
  forensics?: any;
  heatmap?: any;
  tamper?: any;
  face_verification?: any;
  identity?: any;
  identity_record?: any;
  registry?: any;
  fused_evidence?: any;
  risk?: any;
  status?: string;
  error?: string;
}

export interface DemoCase {
  id: string;
  title: string;
  description: string;
  expected_risk: string;
}

export const screeningApi = {

  /** Run full passport screening with document image + optional probe photo */
  async screenPassport(
    documentFile: File,
    probeFile?: File | null,
    actor = 'officer'
  ): Promise<ScreeningResult> {
    const form = new FormData();
    form.append('document', documentFile);
    if (probeFile) form.append('probe', probeFile);
    form.append('actor', actor);
    const res = await fetch(`${API_BASE}/api/v1/screening/passport`, {
      method: 'POST',
      body: form,
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || `Screening failed: ${res.status}`);
    }
    return res.json();
  },

  /** Get list of available demo cases */
  async getDemoCases(): Promise<{ cases: DemoCase[] }> {
    const res = await fetch(`${API_BASE}/api/v1/screening/demo/cases`);
    if (!res.ok) throw new Error('Failed to fetch demo cases');
    return res.json();
  },

  /** Run a specific demo case through the real pipeline */
  async runDemoCase(caseId: string): Promise<ScreeningResult> {
    const res = await fetch(`${API_BASE}/api/v1/screening/demo/run/${caseId}`, {
      method: 'POST',
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || `Demo failed: ${res.status}`);
    }
    return res.json();
  },

  /** Get screening history */
  async getHistory(limit = 20, offset = 0, riskLevel?: string) {
    const params = new URLSearchParams({ limit: String(limit), offset: String(offset) });
    if (riskLevel) params.append('risk_level', riskLevel);
    const res = await fetch(`${API_BASE}/api/v1/screening/history?${params}`);
    if (!res.ok) throw new Error('Failed to fetch screening history');
    return res.json();
  },

  /** Get a specific screening result */
  async getResult(screeningId: string): Promise<ScreeningResult> {
    const res = await fetch(`${API_BASE}/api/v1/screening/result/${screeningId}`);
    if (!res.ok) throw new Error(`Screening not found: ${screeningId}`);
    return res.json();
  },
};

export interface BlockchainAnchor {
  id?: number;
  anchor_id: string;
  merkle_root: string;
  timestamp: string;
  event_count: number;
  previous_anchor_hash: string;
  anchor_hash: string;
  status: string;
  created_at?: string;
  notice?: string;
}

export interface BlockchainStatusResponse {
  has_anchor: boolean;
  latest_anchor: BlockchainAnchor | null;
  audit_chain_verified: boolean;
  current_audit_events_count: number;
  notice: string;
  anchors_count: number;
}

export interface BlockchainVerifyResponse {
  verified: boolean;
  event_count: number;
  merkle_root: string;
  anchor_hash: string;
  timestamp: string;
  recomputed_merkle_root?: string;
  recomputed_anchor_hash?: string;
  merkle_root_matches?: boolean;
  anchor_hash_matches?: boolean;
  underlying_chain_verified?: boolean;
  details: string;
  notice: string;
}

export const auditApi = {
  /** Verify integrity of the full audit hash chain */
  async verifyChain() {
    const res = await fetch(`${API_BASE}/api/v1/audit/chain/verify`);
    if (!res.ok) throw new Error('Audit chain verification failed');
    return res.json();
  },

  /** Get all audit events */
  async getEvents(limit = 100) {
    const res = await fetch(`${API_BASE}/api/v1/audit/events?limit=${limit}`);
    if (!res.ok) throw new Error('Failed to fetch audit events');
    return res.json();
  },

  /** Get audit events for a specific screening */
  async getScreeningEvents(screeningId: string) {
    const res = await fetch(`${API_BASE}/api/v1/audit/events/${screeningId}`);
    if (!res.ok) throw new Error(`No audit events for: ${screeningId}`);
    return res.json();
  },

  /** Get blockchain integrity anchor status */
  async getBlockchainStatus(): Promise<BlockchainStatusResponse> {
    const res = await fetch(`${API_BASE}/api/v1/audit/blockchain/status`);
    if (!res.ok) throw new Error('Failed to fetch blockchain anchor status');
    return res.json();
  },

  /** Create a new blockchain integrity anchor over current audit events */
  async createBlockchainAnchor(): Promise<BlockchainAnchor> {
    const res = await fetch(`${API_BASE}/api/v1/audit/blockchain/anchor`, {
      method: 'POST',
    });
    if (!res.ok) throw new Error('Failed to create blockchain integrity anchor');
    return res.json();
  },

  /** Independently recompute Merkle Root and verify blockchain anchor */
  async verifyBlockchainAnchor(anchorId?: string): Promise<BlockchainVerifyResponse> {
    const url = anchorId
      ? `${API_BASE}/api/v1/audit/blockchain/verify?anchor_id=${encodeURIComponent(anchorId)}`
      : `${API_BASE}/api/v1/audit/blockchain/verify`;
    const res = await fetch(url);
    if (!res.ok) throw new Error('Failed to verify blockchain integrity anchor');
    return res.json();
  },
};

