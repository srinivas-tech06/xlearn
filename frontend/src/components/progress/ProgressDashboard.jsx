import { useEffect, useState } from 'react';
import { useApp } from '../../context/AppContext';

const DAYS = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];

export default function ProgressDashboard() {
  const { state, actions } = useApp();
  const { user, studentState, gamification } = state;
  const [progress, setProgress] = useState(null);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    const p = await actions.loadProgress();
    if (p) setProgress(p);
    await actions.loadGamification();
  };

  const stats = [
    { icon: '⚡', value: user?.xp || 0, label: 'Total XP' },
    { icon: '🏆', value: user?.level || 1, label: 'Level' },
    { icon: '🔥', value: user?.streak || 0, label: 'Day Streak' },
    { icon: '📚', value: user?.total_sessions || 0, label: 'Sessions' },
  ];

  // Generate weekly activity data
  const weekData = [];
  const today = new Date();
  for (let i = 6; i >= 0; i--) {
    const d = new Date(today);
    d.setDate(d.getDate() - i);
    const dayStr = d.toISOString().split('T')[0];
    const calEntry = progress?.calendar?.find(c => c.date === dayStr);
    weekData.push({
      day: DAYS[d.getDay()],
      xp: calEntry?.xp_earned || 0,
      level: calEntry?.completion_level || 0,
    });
  }

  const maxXp = Math.max(...weekData.map(d => d.xp), 1);

  // Calendar data
  const calendarDays = progress?.calendar || [];

  const getCompletionLevel = (level) => {
    if (level >= 80) return 'level-4';
    if (level >= 50) return 'level-3';
    if (level >= 20) return 'level-2';
    if (level > 0) return 'level-1';
    return 'level-0';
  };

  const todayStr = new Date().toISOString().split('T')[0];

  return (
    <div>
      <h1 style={{
        fontSize: '2rem', fontWeight: 700, marginBottom: '24px',
        background: 'var(--accent-gradient)', WebkitBackgroundClip: 'text',
        WebkitTextFillColor: 'transparent', backgroundClip: 'text'
      }}>
        📊 Progress Dashboard
      </h1>

      {/* Stats Grid */}
      <div className="progress-grid">
        {stats.map((s, i) => (
          <div key={i} className="stat-card" style={{ animationDelay: `${i * 0.1}s` }}>
            <div className="stat-icon">{s.icon}</div>
            <div className="stat-value">{s.value}</div>
            <div className="stat-label">{s.label}</div>
          </div>
        ))}
      </div>

      <div className="progress-charts">
        {/* Activity Chart */}
        <div className="activity-chart">
          <div className="chart-title">📈 Weekly Activity</div>
          <div className="chart-bars">
            {weekData.map((d, i) => (
              <div key={i} className="chart-bar-wrapper">
                <div
                  className="chart-bar"
                  style={{ height: `${Math.max(4, (d.xp / maxXp) * 100)}%` }}
                  title={`${d.xp} XP`}
                />
                <span className="chart-bar-label">{d.day}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Calendar */}
        <div className="calendar-container">
          <div className="chart-title">📅 Activity Calendar</div>
          <div className="calendar-grid">
            {DAYS.map(d => (
              <div key={d} className="calendar-day-header">{d.charAt(0)}</div>
            ))}
            {calendarDays.slice(-28).map((entry, i) => {
              const d = new Date(entry.date);
              return (
                <div
                  key={i}
                  className={`calendar-day ${getCompletionLevel(entry.completion_level)} ${entry.date === todayStr ? 'today' : ''}`}
                  title={`${entry.date}: ${entry.xp_earned} XP`}
                >
                  {d.getDate()}
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* Learning Metrics */}
      <div style={{ marginTop: '24px' }}>
        <div className="glass-card">
          <div className="chart-title">🧠 Learning Metrics</div>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '16px', marginTop: '16px' }}>
            {[
              { label: 'Understanding', value: studentState?.understanding || 50, color: '#7c3aed' },
              { label: 'Confidence', value: studentState?.confidence || 50, color: '#06b6d4' },
              { label: 'Engagement', value: studentState?.engagement || 70, color: '#10b981' },
              { label: 'Retention', value: studentState?.retention || 50, color: '#f59e0b' },
            ].map((m, i) => (
              <div key={i} style={{ textAlign: 'center' }}>
                <div style={{ fontSize: '1.5rem', fontWeight: 700, color: m.color, marginBottom: '4px' }}>
                  {Math.round(m.value)}%
                </div>
                <div style={{ height: '6px', background: 'rgba(255,255,255,0.08)', borderRadius: '99px', overflow: 'hidden' }}>
                  <div style={{
                    width: `${m.value}%`, height: '100%', background: m.color,
                    borderRadius: '99px', transition: 'width 0.8s ease'
                  }} />
                </div>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-tertiary)', marginTop: '6px' }}>{m.label}</div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Badges */}
      {gamification?.badges && gamification.badges.length > 0 && (
        <div style={{ marginTop: '24px' }}>
          <div className="glass-card">
            <div className="chart-title">🏅 Badges</div>
            <div className="badges-grid" style={{ marginTop: '16px' }}>
              {gamification.badges.map((badge, i) => (
                <div key={i} className={`badge-item ${badge.earned ? 'earned' : 'locked'}`}>
                  <div className="badge-icon">{badge.icon}</div>
                  <div className="badge-name">{badge.name}</div>
                  <div className="badge-desc">{badge.description}</div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
