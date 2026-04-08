import { useEffect, useCallback } from 'react';
import { useApp } from '../../context/AppContext';

export default function AnalyticsDashboard() {
  const { state, actions } = useApp();
  const { memoryData, user, studentState } = state;

  useEffect(() => {
    actions.loadMemory();
  }, []);

  const weakTopics = memoryData?.weak_topics || [];
  const mastered = memoryData?.mastered_topics || [];
  const totalSeen = memoryData?.total_topics_seen || 0;
  const avgStrength = memoryData?.avg_strength || 0;
  const dueReviews = memoryData?.due_reviews || [];

  const METRICS = [
    { label: 'Topics Seen', value: totalSeen, icon: '📚', color: '#7c3aed' },
    { label: 'Avg Mastery', value: `${Math.round(avgStrength * 100)}%`, icon: '💪', color: '#06b6d4' },
    { label: 'Mastered', value: mastered.length, icon: '✅', color: '#10b981' },
    { label: 'Need Review', value: dueReviews.length, icon: '🔄', color: '#f59e0b' },
  ];

  const STATE_BARS = [
    { label: 'Understanding', value: studentState?.understanding || 0, color: '#7c3aed' },
    { label: 'Confidence', value: studentState?.confidence || 0, color: '#06b6d4' },
    { label: 'Engagement', value: studentState?.engagement || 0, color: '#10b981' },
    { label: 'Retention', value: studentState?.retention || 0, color: '#f59e0b' },
  ];

  return (
    <div className="analytics-container">
      <div className="analytics-hero">
        <div className="analytics-hero-icon">📊</div>
        <div>
          <h1 className="analytics-title">Learning Analytics</h1>
          <p className="analytics-subtitle">Your personalized intelligence map</p>
        </div>
      </div>

      {/* Stats Row */}
      <div className="analytics-stats-row">
        {METRICS.map((m, i) => (
          <div key={i} className="analytics-stat-card" style={{ '--stat-color': m.color }}>
            <div className="stat-icon">{m.icon}</div>
            <div className="stat-value">{m.value}</div>
            <div className="stat-label">{m.label}</div>
          </div>
        ))}
      </div>

      <div className="analytics-grid">
        {/* Learning State Radar */}
        <div className="analytics-card">
          <div className="ac-header">
            <span className="ac-icon">🧠</span>
            <h3>Current Learning State</h3>
          </div>
          <div className="state-bars">
            {STATE_BARS.map((bar, i) => (
              <div key={i} className="state-bar-row">
                <span className="state-bar-label">{bar.label}</span>
                <div className="state-bar-track">
                  <div
                    className="state-bar-fill"
                    style={{ width: `${bar.value}%`, background: bar.color }}
                  />
                </div>
                <span className="state-bar-value" style={{ color: bar.color }}>{Math.round(bar.value)}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Weak Topics */}
        <div className="analytics-card">
          <div className="ac-header">
            <span className="ac-icon">⚠️</span>
            <h3>Topics Needing Attention</h3>
          </div>
          {weakTopics.length === 0 ? (
            <div className="analytics-empty">
              <span>🎉</span>
              <p>No weak topics! Keep it up.</p>
            </div>
          ) : (
            <div className="weak-topics-list">
              {weakTopics.map((t, i) => (
                <div key={i} className="weak-topic-item">
                  <div className="wt-top">
                    <span className="wt-name">{t.topic}</span>
                    <span className="wt-strength">{Math.round(t.strength * 100)}%</span>
                  </div>
                  <div className="wt-bar-track">
                    <div className="wt-bar-fill" style={{ width: `${t.strength * 100}%` }} />
                  </div>
                  <div className="wt-meta">
                    <span>❌ {t.mistake_count} mistakes</span>
                    <span className="wt-reason">{t.reason.replace('_', ' ')}</span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Spaced Repetition Schedule */}
        <div className="analytics-card">
          <div className="ac-header">
            <span className="ac-icon">📅</span>
            <h3>Review Schedule</h3>
          </div>
          {dueReviews.length === 0 ? (
            <div className="analytics-empty">
              <span>✅</span>
              <p>You're all caught up on reviews!</p>
            </div>
          ) : (
            <div className="review-schedule-list">
              {dueReviews.slice(0, 6).map((r, i) => {
                const priorityColors = { urgent: '#ef4444', today: '#f59e0b', upcoming: '#06b6d4' };
                const color = priorityColors[r.priority] || '#06b6d4';
                return (
                  <div key={i} className="review-item" style={{ '--review-color': color }}>
                    <div className="review-indicator" style={{ background: color }} />
                    <div className="review-content">
                      <div className="review-topic">{r.topic}</div>
                      <div className="review-meta">
                        {r.priority === 'urgent' ? `${r.overdue_days}d overdue` : r.due_date}
                        {r.subject && ` · ${r.subject}`}
                      </div>
                    </div>
                    <div className="review-strength" style={{ color }}>
                      {Math.round(r.strength * 100)}%
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>

        {/* Mastered Topics */}
        <div className="analytics-card">
          <div className="ac-header">
            <span className="ac-icon">🏆</span>
            <h3>Mastered Topics</h3>
          </div>
          {mastered.length === 0 ? (
            <div className="analytics-empty">
              <span>🌱</span>
              <p>Keep learning — mastered topics appear here!</p>
            </div>
          ) : (
            <div className="mastered-chips">
              {mastered.map((topic, i) => (
                <span key={i} className="mastered-chip">✓ {topic}</span>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Knowledge Heatmap */}
      <div className="analytics-card analytics-card-full">
        <div className="ac-header">
          <span className="ac-icon">🗺️</span>
          <h3>Knowledge Strength Map</h3>
          <span className="ac-subtitle">{totalSeen} topics explored</span>
        </div>
        {totalSeen === 0 ? (
          <div className="analytics-empty large">
            <span>💡</span>
            <p>Start chatting to build your knowledge map!</p>
          </div>
        ) : (
          <div className="knowledge-map">
            {[...weakTopics, ...mastered.map(t => ({ topic: t, strength: 0.9 }))].map((item, i) => {
              const strength = item.strength || 0;
              const hue = Math.round(strength * 120); // Red → Green
              return (
                <div
                  key={i}
                  className="knowledge-node"
                  style={{
                    background: `hsla(${hue}, 60%, 50%, 0.2)`,
                    borderColor: `hsla(${hue}, 60%, 50%, 0.5)`,
                    '--node-size': `${70 + strength * 30}px`
                  }}
                  title={`${item.topic}: ${Math.round(strength * 100)}% strength`}
                >
                  <span className="kn-topic">{item.topic}</span>
                  <span className="kn-pct">{Math.round(strength * 100)}%</span>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
