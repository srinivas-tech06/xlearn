import { useState, useEffect } from 'react';

const ROUTING_MODES = [
  { id: 'auto', label: 'Auto (Intelligent)', icon: '⚡', desc: 'Ollama for speed, Cloud for complexity' },
  { id: 'ollama_only', label: 'Ollama Only', icon: '🦙', desc: 'Local inference, maximum privacy' },
  { id: 'cloud_only', label: 'Cloud Only', icon: '🌐', desc: 'OpenAI / Gemini preferred' },
  { id: 'fallback_only', label: 'Fallback Only', icon: '📋', desc: 'Template engine, zero latency' },
];

export default function LLMStatusPanel({ onClose }) {
  const [status, setStatus] = useState(null);
  const [models, setModels] = useState(null);
  const [loading, setLoading] = useState(true);
  const [pinging, setPinging] = useState(false);
  const [privacyMode, setPrivacyMode] = useState(false);
  const [routingMode, setRoutingMode] = useState('auto');
  const [message, setMessage] = useState('');

  useEffect(() => {
    loadStatus();
  }, []);

  const loadStatus = async () => {
    setLoading(true);
    try {
      const [s, m] = await Promise.all([
        fetch('/api/v1/llm/status').then(r => r.json()),
        fetch('/api/v1/llm/models').then(r => r.json()),
      ]);
      setStatus(s);
      setModels(m);
      setPrivacyMode(s.routing_mode?.includes('privacy') || false);
      setRoutingMode(s.routing_mode?.includes('privacy') ? 'ollama_only' : (s.routing_mode || 'auto'));
    } catch (e) {
      setMessage('Could not connect to backend.');
    } finally {
      setLoading(false);
    }
  };

  const pingOllama = async () => {
    setPinging(true);
    try {
      const r = await fetch('/api/v1/llm/ping-ollama', { method: 'POST' });
      const data = await r.json();
      setMessage(data.message);
      loadStatus();
    } catch (e) {
      setMessage('Ping failed — backend unreachable.');
    } finally {
      setPinging(false);
    }
  };

  const setMode = async (mode) => {
    try {
      const r = await fetch(`/api/v1/llm/routing-mode?mode=${mode}`, { method: 'POST' });
      const data = await r.json();
      setRoutingMode(mode);
      setMessage(data.message);
      setTimeout(loadStatus, 500);
    } catch (e) {
      setMessage('Failed to change routing mode.');
    }
  };

  const togglePrivacy = async () => {
    const newVal = !privacyMode;
    try {
      await fetch(`/api/v1/llm/privacy-mode?enabled=${newVal}`, { method: 'POST' });
      setPrivacyMode(newVal);
      setMessage(newVal ? '🔒 Privacy Mode ON — all data stays local' : '🔓 Privacy Mode OFF — cloud re-enabled');
      setTimeout(loadStatus, 500);
    } catch (e) {
      setMessage('Failed to toggle privacy mode.');
    }
  };

  const clearCache = async () => {
    try {
      await fetch('/api/v1/llm/cache/clear', { method: 'POST' });
      setMessage('✅ Cache cleared successfully');
      loadStatus();
    } catch (e) {}
  };

  const ollamaOk = status?.ollama?.available;
  const cloudOk = status?.cloud?.available;

  return (
    <div className="llm-overlay" onClick={onClose}>
      <div className="llm-panel" onClick={e => e.stopPropagation()}>
        <div className="llm-panel-header">
          <div>
            <h2>🤖 AI Engine Status</h2>
            <p>Hybrid LLM routing — Local · Cloud · Fallback</p>
          </div>
          <button className="llm-close-btn" onClick={onClose}>✕</button>
        </div>

        {loading ? (
          <div className="llm-loading">
            <div className="llm-spinner" />
            <span>Checking backends...</span>
          </div>
        ) : (
          <>
            {/* Backend Status */}
            <div className="llm-backends">
              <div className={`llm-backend-card ${ollamaOk ? 'online' : 'offline'}`}>
                <div className="lbc-top">
                  <span className="lbc-icon">🦙</span>
                  <div>
                    <div className="lbc-name">Ollama (Local)</div>
                    <div className="lbc-model">{status?.ollama?.model || 'llama3'}</div>
                  </div>
                  <span className={`lbc-badge ${ollamaOk ? 'online' : 'offline'}`}>
                    {ollamaOk ? '● Online' : '● Offline'}
                  </span>
                </div>
                {models?.local_models?.length > 0 && (
                  <div className="lbc-models">
                    {models.local_models.slice(0, 4).map((m, i) => (
                      <span key={i} className="lbc-model-chip">{m.split(':')[0]}</span>
                    ))}
                  </div>
                )}
                {!ollamaOk && (
                  <div className="lbc-install-hint">
                    Install: <code>winget install Ollama.Ollama</code> then <code>ollama pull llama3</code>
                  </div>
                )}
                <button className="lbc-ping-btn" onClick={pingOllama} disabled={pinging}>
                  {pinging ? 'Pinging...' : '🔍 Ping Ollama'}
                </button>
              </div>

              <div className={`llm-backend-card ${cloudOk ? 'online' : 'offline'}`}>
                <div className="lbc-top">
                  <span className="lbc-icon">🌐</span>
                  <div>
                    <div className="lbc-name">Cloud LLM</div>
                    <div className="lbc-model">{status?.cloud?.provider || 'openai'} / {status?.cloud?.model || 'gpt-4'}</div>
                  </div>
                  <span className={`lbc-badge ${cloudOk ? 'online' : 'offline'}`}>
                    {cloudOk ? '● Active' : '● No Key'}
                  </span>
                </div>
                {!cloudOk && (
                  <div className="lbc-install-hint">
                    Add your key to <code>backend/.env</code> → <code>LLM_API_KEY=sk-...</code>
                  </div>
                )}
              </div>
            </div>

            {/* Active Backend */}
            <div className="llm-active-backend">
              <span className="lab-label">Active Backend:</span>
              <span className="lab-value">⚡ {status?.active_backend || 'fallback'}</span>
            </div>

            {/* Routing Mode */}
            <div className="llm-section">
              <div className="llm-section-title">Routing Mode</div>
              <div className="llm-modes-grid">
                {ROUTING_MODES.map(m => (
                  <button
                    key={m.id}
                    className={`llm-mode-btn ${routingMode === m.id && !privacyMode ? 'active' : ''}`}
                    onClick={() => setMode(m.id)}
                    disabled={privacyMode}
                  >
                    <span className="lmb-icon">{m.icon}</span>
                    <span className="lmb-label">{m.label}</span>
                    <span className="lmb-desc">{m.desc}</span>
                  </button>
                ))}
              </div>
            </div>

            {/* Privacy Mode */}
            <div className="llm-privacy-row">
              <div>
                <div className="lpr-title">🔒 Privacy Mode</div>
                <div className="lpr-desc">Forces Ollama only — zero cloud calls, all data local</div>
              </div>
              <button
                className={`lpr-toggle ${privacyMode ? 'on' : 'off'}`}
                onClick={togglePrivacy}
              >
                {privacyMode ? 'ON' : 'OFF'}
              </button>
            </div>

            {/* Cache Stats */}
            {status?.cache && (
              <div className="llm-cache-row">
                <div className="lcr-stats">
                  <span>📦 Cache: {status.cache.size}/{status.cache.max_size}</span>
                  <span>🎯 Hit rate: {(status.cache.hit_rate * 100).toFixed(0)}%</span>
                  <span>✅ {status.cache.hits} hits / ❌ {status.cache.misses} misses</span>
                </div>
                <button className="lcr-clear-btn" onClick={clearCache}>Clear Cache</button>
              </div>
            )}

            {message && (
              <div className="llm-message">{message}</div>
            )}
          </>
        )}
      </div>
    </div>
  );
}
