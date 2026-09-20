import React from 'react';

interface GaugeChartProps {
  score: number;
  label: string;
  color?: string;
  size?: number;
}

export const GaugeChart: React.FC<GaugeChartProps> = ({
  score,
  label,
  color = '#1D63C8',
  size = 140,
}) => {
  const clamped = Math.min(100, Math.max(0, score));
  const strokeWidth = 10;
  const radius = (size - strokeWidth) / 2;
  const circumference = Math.PI * radius; // Half circle
  const strokeDashoffset = circumference - (clamped / 100) * circumference;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
      <svg
        width={size}
        height={size * 0.65}
        viewBox={`0 0 ${size} ${size * 0.65}`}
        role="img"
        aria-label={`${label}: ${clamped}%`}
      >
        {/* Background track (half circle) */}
        <path
          d={`M ${strokeWidth / 2} ${size / 2} A ${radius} ${radius} 0 0 1 ${size - strokeWidth / 2} ${size / 2}`}
          fill="none"
          stroke="var(--c-surface)"
          strokeWidth={strokeWidth}
          strokeLinecap="round"
        />

        {/* Value arc */}
        <path
          d={`M ${strokeWidth / 2} ${size / 2} A ${radius} ${radius} 0 0 1 ${size - strokeWidth / 2} ${size / 2}`}
          fill="none"
          stroke={color}
          strokeWidth={strokeWidth}
          strokeDasharray={circumference}
          strokeDashoffset={strokeDashoffset}
          strokeLinecap="round"
          style={{ transition: 'stroke-dashoffset 0.8s ease' }}
        />

        {/* Score number inside */}
        <text
          x={size / 2}
          y={size * 0.46}
          textAnchor="middle"
          fontSize="22"
          fontWeight="800"
          fill="var(--c-navy)"
          fontFamily="var(--font)"
        >
          {clamped}%
        </text>
      </svg>
      <div style={{ fontSize: '11px', fontWeight: 600, color: 'var(--c-text-muted)', marginTop: '-4px' }}>
        {label}
      </div>
    </div>
  );
};
