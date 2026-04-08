const API_BASE = '/api/v1';

async function request(endpoint, options = {}) {
  const url = `${API_BASE}${endpoint}`;
  const config = { headers: { 'Content-Type': 'application/json' }, ...options };
  try {
    const response = await fetch(url, config);
    if (!response.ok) throw new Error(`API Error: ${response.status}`);
    return await response.json();
  } catch (error) {
    console.error(`API call failed: ${endpoint}`, error);
    throw error;
  }
}

export const api = {
  // Chat
  sendMessage: (message, userId = 1, context = null, mentor = 'direct') =>
    request('/chat/', {
      method: 'POST',
      body: JSON.stringify({ message, user_id: userId, context, mentor }),
    }),

  submitQuizAnswer: (data) =>
    request('/chat/quiz-answer', { method: 'POST', body: JSON.stringify(data) }),

  // Roadmap
  generateRoadmap: (goal, timeframe = '4 weeks', userId = 1) =>
    request('/roadmap/generate', { method: 'POST', body: JSON.stringify({ goal, timeframe, user_id: userId }) }),

  getRoadmap: (userId = 1) => request(`/roadmap/${userId}`),

  // Progress
  getProgress: (userId = 1) => request(`/progress/${userId}`),

  // User
  getUser: (userId = 1) => request(`/user/${userId}`),

  // Gamification
  getGamification: (userId = 1) => request(`/gamification/${userId}`),

  // Memory & Spaced Repetition
  getMemory: (userId = 1) => request(`/memory/${userId}`),
  updateMemory: (data) => request('/memory/update', { method: 'POST', body: JSON.stringify(data) }),
};
