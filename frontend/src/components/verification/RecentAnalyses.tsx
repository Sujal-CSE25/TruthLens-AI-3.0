import React, { useEffect, useState } from 'react';
import { Video, FileText, Share2, File, Mic } from 'lucide-react';
import { Link } from 'react-router-dom';
import { api, type HistoryItem } from '../../services/api';

type AnalysisStatus = 'real' | 'fake' | 'review' | 'unverified';

interface DisplayAnalysis {
  id: string;
  title: string;
  type: string;
  status: AnalysisStatus;
  time: string;
  icon: React.ElementType;
}

const defaultAnalyses: DisplayAnalysis[] = [
  { id: '1', title: 'Press Conference Video', type: 'Deepfake Detection', status: 'real', time: '10:28 AM', icon: Video },
  { id: '2', title: 'News Article Screenshot', type: 'Forgery Detection', status: 'fake', time: '10:21 AM', icon: FileText },
  { id: '3', title: 'Social Media Post', type: 'Misinformation', status: 'review', time: '10:15 AM', icon: Share2 },
  { id: '4', title: 'Document — Notice.pdf', type: 'Document Forensics', status: 'real', time: '10:10 AM', icon: File },
  { id: '5', title: 'Interview Audio Clip', type: 'Audio Analysis', status: 'real', time: '10:05 AM', icon: Mic },
];

const statusBadgeClass: Record<AnalysisStatus, string> = {
  real: 'badge badge-real',
  fake: 'badge badge-fake',
  review: 'badge badge-review',
  unverified: 'badge badge-unverified',
};

const statusLabel: Record<AnalysisStatus, string> = {
  real: 'Real',
  fake: 'Fake',
  review: 'Review',
  unverified: 'Unverified',
};

function mapBackendStatus(verdict: string): AnalysisStatus {
  const v = (verdict || '').toUpperCase();
  if (v.includes('REAL')) return 'real';
  if (v.includes('FAKE') || v.includes('MISLEADING') || v.includes('FORGED')) return 'fake';
  if (v.includes('REVIEW') || v.includes('SUSPICIOUS')) return 'review';
  return 'unverified';
}

function mapBackendTypeIcon(type: string): React.ElementType {
  if (type === 'image') return Video;
  if (type === 'document') return File;
  return FileText;
}

export const RecentAnalyses: React.FC = () => {
  const [items, setItems] = useState<DisplayAnalysis[]>(defaultAnalyses);
  const [isLive, setIsLive] = useState(false);

  useEffect(() => {
    api.getHistory(5)
      .then((data) => {
        if (data.items && data.items.length > 0) {
          const mapped: DisplayAnalysis[] = data.items.map((item: HistoryItem, i: number) => ({
            id: item.analysis_id || String(i),
            title: `${item.type.charAt(0).toUpperCase() + item.type.slice(1)} Verification (${item.analysis_id ? item.analysis_id.slice(0, 8) : 'Analysis'})`,
            type: `${item.type.charAt(0).toUpperCase() + item.type.slice(1)} Analysis`,
            status: mapBackendStatus(item.verdict),
            time: item.created_at ? item.created_at.slice(11, 16) : 'Just now',
            icon: mapBackendTypeIcon(item.type),
          }));
          setItems(mapped);
          setIsLive(true);
        }
      })
      .catch(() => {});
  }, []);

  return (
    <div className="card" style={{ height: '100%' }}>
      <div className="card-header">
        <div>
          <div className="card-title">Recent Analyses</div>
          <div className="card-sub">Latest verification results {isLive && '· Live DB'}</div>
        </div>
        <Link to="/dashboard" className="view-all-link" style={{ fontSize: '12px', whiteSpace: 'nowrap' }}>
          View All
        </Link>
      </div>

      <div className="analysis-list" role="list" aria-label="Recent analyses">
        {items.map(({ id, title, type, status, time, icon: Icon }) => (
          <div key={id} className="analysis-row" role="listitem" tabIndex={0}>
            <div className="analysis-icon" aria-hidden="true">
              <Icon size={15} />
            </div>
            <div className="analysis-info">
              <div className="analysis-name">{title}</div>
              <div className="analysis-type">{type}</div>
            </div>
            <div className="analysis-meta">
              <span className={statusBadgeClass[status]} aria-label={`Status: ${statusLabel[status]}`}>
                {statusLabel[status]}
              </span>
              <span className="analysis-time">{time}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default RecentAnalyses;
