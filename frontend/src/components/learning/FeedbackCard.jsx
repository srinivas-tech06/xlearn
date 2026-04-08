const METRICS = [
  { key: 'understanding', label: 'Understanding', color: '#7c3aed' },
  { key: 'confidence', label: 'Confidence', color: '#06b6d4' },
  { key: 'engagement', label: 'Engagement', color: '#10b981' },
  { key: 'retention', label: 'Retention', color: '#f59e0b' },
];

function MetricCircle({ value, color, label }) {
  const radius = 28;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (value / 100) * circumference;

  return (
    <div className="metric-item">
      <div className="metric-circle">
        <svg viewBox="0 0 64 64">
          <circle className="track" cx="32" cy="32" r={radius} />
          <circle
            className="fill"
            cx="32" cy="32" r={radius}
            stroke={color}
            strokeDasharray={circumference}
            strokeDashoffset={offset}
          />
        </svg>
        <span className="value" style={{ color }}>{Math.round(value)}</span>
      </div>
      <div className="metric-label">{label}</div>
    </div>
  );
}

export default function FeedbackCard({ state }) {
  if (!state) return null;

  return (
    <div className="learning-card feedback-card">
      <div className="learning-card-header">
        <div className="learning-card-icon" style={{ background: 'rgba(6, 182, 212, 0.2)' }}>
          📊
        </div>
        <div>
          <div className="learning-card-title">Your State</div>
          <div className="learning-card-subtitle">Real-time learning metrics</div>
        </div>
      </div>

      <div className="feedback-metrics">
        {METRICS.map(m => (
          <MetricCircle
            key={m.key}
            value={state[m.key] || 50}
            color={m.color}
            label={m.label}
          />
        ))}
      </div>
    </div>
  );
}
