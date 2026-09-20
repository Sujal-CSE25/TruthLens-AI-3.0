import React from 'react';
import {
  Search, Globe, CheckSquare, AlertTriangle,
  BookOpen, Gavel
} from 'lucide-react';

const agents = [
  {
    num: '01',
    icon: Search,
    name: 'Claim Extractor',
    desc: 'Finds verifiable claims',
    status: 'Active',
  },
  {
    num: '02',
    icon: Globe,
    name: 'Evidence Finder',
    desc: 'RAG over web + Wikipedia',
    status: 'Active',
  },
  {
    num: '03',
    icon: CheckSquare,
    name: 'Fact Checker',
    desc: 'Claim vs evidence verdict',
    status: 'Active',
  },
  {
    num: '04',
    icon: AlertTriangle,
    name: 'Risk Assessor',
    desc: 'Calibrated fake score',
    status: 'Active',
  },
  {
    num: '05',
    icon: BookOpen,
    name: 'Explainability Agent',
    desc: 'Builds reasoning chain',
    status: 'Active',
  },
  {
    num: '06',
    icon: Gavel,
    name: 'Final Judge',
    desc: 'Verdict + trust score',
    status: 'Active',
  },
];

interface AgentPipelineProps {
  compact?: boolean;
}

export const AgentPipeline: React.FC<AgentPipelineProps> = ({ compact = false }) => {
  return (
    <div className="card" style={{ height: '100%' }}>
      <div className="card-header">
        <div>
          <div className="card-title">AI Agent Pipeline</div>
          {!compact && <div className="card-sub">Six specialized verification agents</div>}
        </div>
      </div>

      <div className="agent-list" role="list" aria-label="AI agent pipeline">
        {agents.map(({ num, icon: Icon, name, desc, status }) => (
          <div key={num} className="agent-row" role="listitem">
            <span className="agent-num" aria-hidden="true">{num}</span>
            <div className="agent-icon" aria-hidden="true">
              <Icon size={14} />
            </div>
            <div className="agent-info">
              <div className="agent-name">{name}</div>
              {!compact && <div className="agent-desc">{desc}</div>}
            </div>
            <div className="agent-status" aria-label={`Status: ${status}`}>
              <span className="status-dot" aria-hidden="true" />
              {status}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default AgentPipeline;
