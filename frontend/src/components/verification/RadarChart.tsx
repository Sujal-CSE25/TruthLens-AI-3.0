import React from 'react';

interface RadarChartProps {
  data: {
    Fake: number;
    Bias: number;
    Manipulation: number;
    Distrust: number;
    Confidence: number;
  };
  size?: number;
}

export const RadarChart: React.FC<RadarChartProps> = ({ data, size = 260 }) => {
  const center = size / 2;
  const radius = size * 0.38;

  const axes = [
    { key: 'Fake', label: 'Fake', value: Math.min(100, Math.max(0, data.Fake ?? 0)) },
    { key: 'Bias', label: 'Bias', value: Math.min(100, Math.max(0, data.Bias ?? 0)) },
    { key: 'Manipulation', label: 'Manip.', value: Math.min(100, Math.max(0, data.Manipulation ?? 0)) },
    { key: 'Distrust', label: 'Distrust', value: Math.min(100, Math.max(0, data.Distrust ?? 0)) },
    { key: 'Confidence', label: 'Conf.', value: Math.min(100, Math.max(0, data.Confidence ?? 0)) },
  ];

  const totalAxes = axes.length;
  const angleSlice = (Math.PI * 2) / totalAxes;

  // Grid levels (20%, 40%, 60%, 80%, 100%)
  const levels = [0.2, 0.4, 0.6, 0.8, 1.0];

  // Calculate polygon points for each grid level
  const levelPolygons = levels.map((lvl) => {
    return axes
      .map((_, i) => {
        const angle = i * angleSlice - Math.PI / 2;
        const x = center + radius * lvl * Math.cos(angle);
        const y = center + radius * lvl * Math.sin(angle);
        return `${x.toFixed(1)},${y.toFixed(1)}`;
      })
      .join(' ');
  });

  // Calculate data polygon points
  const dataPoints = axes
    .map((axis, i) => {
      const angle = i * angleSlice - Math.PI / 2;
      const normalizedVal = (axis.value / 100) * radius;
      const x = center + normalizedVal * Math.cos(angle);
      const y = center + normalizedVal * Math.sin(angle);
      return `${x.toFixed(1)},${y.toFixed(1)}`;
    })
    .join(' ');

  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
      <svg
        width={size}
        height={size}
        viewBox={`0 0 ${size} ${size}`}
        role="img"
        aria-label="Risk and signal radar breakdown"
      >
        {/* Background circular / polygonal grid lines */}
        {levelPolygons.map((points, idx) => (
          <polygon
            key={idx}
            points={points}
            fill="none"
            stroke="var(--c-border)"
            strokeWidth="1"
            strokeDasharray={idx === levels.length - 1 ? 'none' : '2 2'}
            opacity={0.7}
          />
        ))}

        {/* Axis spokes from center to 100% */}
        {axes.map((_, i) => {
          const angle = i * angleSlice - Math.PI / 2;
          const x = center + radius * Math.cos(angle);
          const y = center + radius * Math.sin(angle);
          return (
            <line
              key={i}
              x1={center}
              y1={center}
              x2={x}
              y2={y}
              stroke="var(--c-border)"
              strokeWidth="1"
            />
          );
        })}

        {/* Data polygon */}
        <polygon
          points={dataPoints}
          fill="rgba(29, 99, 200, 0.22)"
          stroke="var(--c-primary-blue)"
          strokeWidth="2"
        />

        {/* Data vertex dots */}
        {axes.map((axis, i) => {
          const angle = i * angleSlice - Math.PI / 2;
          const normalizedVal = (axis.value / 100) * radius;
          const x = center + normalizedVal * Math.cos(angle);
          const y = center + normalizedVal * Math.sin(angle);
          return (
            <circle
              key={i}
              cx={x}
              cy={y}
              r="3.5"
              fill="var(--c-navy)"
              stroke="var(--c-white)"
              strokeWidth="1.5"
            />
          );
        })}

        {/* Axis Labels */}
        {axes.map((axis, i) => {
          const angle = i * angleSlice - Math.PI / 2;
          const labelDist = radius + 18;
          const x = center + labelDist * Math.cos(angle);
          const y = center + labelDist * Math.sin(angle) + 4;
          return (
            <text
              key={i}
              x={x}
              y={y}
              textAnchor="middle"
              fontSize="11"
              fontWeight="600"
              fill="var(--c-text-secondary)"
              fontFamily="var(--font)"
            >
              {axis.label} ({axis.value}%)
            </text>
          );
        })}
      </svg>
    </div>
  );
};
