import React, { useEffect, useState } from 'react';
import { Shield, Bot, Monitor, Clock, Activity } from 'lucide-react';
import { api } from '../../services/api';

export const SystemStatusCard: React.FC = () => {
  const [isLive, setIsLive] = useState<boolean | null>(null);
  const [version, setVersion] = useState<string>('2.0.0');

  useEffect(() => {
    api.getHealth()
      .then((data) => {
        setIsLive(data.status === 'ok');
        if (data.version) setVersion(data.version);
      })
      .catch(() => {
        setIsLive(false);
      });
  }, []);

  return (
    <aside className="system-status-card" aria-label="System status">
      <div className="ss-header">
        <Shield size={16} color="var(--c-blue)" aria-hidden="true" />
        <h3>System Status</h3>
        <span
          className="demo-label"
          style={{
            marginLeft: 'auto',
            background: isLive ? 'var(--c-success-bg)' : undefined,
            color: isLive ? 'var(--c-success)' : undefined,
            borderColor: isLive ? '#b6dfc6' : undefined,
          }}
        >
          {isLive === true ? 'Backend Connected' : isLive === false ? 'API Offline' : 'Checking…'}
        </span>
      </div>

      <dl>
        <div className="ss-row">
          <dt className="ss-label">
            <Bot size={14} color="var(--c-text-muted)" aria-hidden="true" />
            AI Agents
          </dt>
          <dd className="ss-value blue">6/6 Active</dd>
        </div>

        <div className="ss-row">
          <dt className="ss-label">
            <Monitor size={14} color="var(--c-text-muted)" aria-hidden="true" />
            FastAPI Service
          </dt>
          <dd className={`ss-value ${isLive ? 'success' : 'text-danger'}`}>
            {isLive ? `v${version} Online` : isLive === false ? 'Disconnected' : 'Checking…'}
          </dd>
        </div>

        <div className="ss-row">
          <dt className="ss-label">
            <Clock size={14} color="var(--c-text-muted)" aria-hidden="true" />
            Last Updated
          </dt>
          <dd className="ss-value">Live (Real-time)</dd>
        </div>

        <div className="ss-row">
          <dt className="ss-label">
            <Activity size={14} color="var(--c-text-muted)" aria-hidden="true" />
            Uptime
          </dt>
          <dd className="ss-value">99.98%</dd>
        </div>
      </dl>
    </aside>
  );
};

export default SystemStatusCard;
