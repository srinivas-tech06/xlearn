import { createContext, useContext, useReducer, useCallback } from 'react';
import { api } from '../api';

const AppContext = createContext(null);

const initialState = {
  user: null,
  studentState: { understanding: 50, confidence: 50, engagement: 70, retention: 50 },
  roadmap: null,
  gamification: null,
  chatMessages: [],
  currentQuiz: null,
  currentPage: 'onboarding',
  loading: false,
  xpNotification: null,
  levelUp: null,
  // New fields
  mentor: 'direct',          // active mentor personality
  focusMode: false,          // hide sidebar, distraction-free
  memoryData: null,          // weak topics, due reviews, mastered
  ragSources: [],            // last response RAG sources
};

function reducer(state, action) {
  switch (action.type) {
    case 'SET_USER': return { ...state, user: action.payload };
    case 'SET_STATE': return { ...state, studentState: action.payload };
    case 'SET_ROADMAP': return { ...state, roadmap: action.payload };
    case 'SET_GAMIFICATION': return { ...state, gamification: action.payload };
    case 'ADD_CHAT_MESSAGE': return { ...state, chatMessages: [...state.chatMessages, action.payload] };
    case 'SET_CURRENT_QUIZ': return { ...state, currentQuiz: action.payload };
    case 'SET_PAGE': return { ...state, currentPage: action.payload };
    case 'SET_LOADING': return { ...state, loading: action.payload };
    case 'SHOW_XP': return { ...state, xpNotification: action.payload };
    case 'HIDE_XP': return { ...state, xpNotification: null };
    case 'SHOW_LEVEL_UP': return { ...state, levelUp: action.payload };
    case 'HIDE_LEVEL_UP': return { ...state, levelUp: null };
    case 'SET_MENTOR': return { ...state, mentor: action.payload };
    case 'TOGGLE_FOCUS': return { ...state, focusMode: !state.focusMode };
    case 'SET_MEMORY': return { ...state, memoryData: action.payload };
    case 'SET_RAG_SOURCES': return { ...state, ragSources: action.payload || [] };
    case 'UPDATE_USER_XP': {
      if (!state.user) return state;
      const newXp = state.user.xp + action.payload;
      const oldLevel = state.user.level;
      const newLevel = Math.max(1, Math.floor(newXp / 100) + 1);
      return {
        ...state,
        user: { ...state.user, xp: newXp, level: newLevel },
        levelUp: newLevel > oldLevel ? newLevel : state.levelUp,
      };
    }
    default: return state;
  }
}

export function AppProvider({ children }) {
  const [state, dispatch] = useReducer(reducer, initialState);

  const actions = {
    sendMessage: useCallback(async (message, context) => {
      dispatch({ type: 'ADD_CHAT_MESSAGE', payload: { role: 'user', content: message, timestamp: new Date().toISOString() } });
      dispatch({ type: 'SET_LOADING', payload: true });
      try {
        const response = await api.sendMessage(message, 1, context, state.mentor);
        dispatch({
          type: 'ADD_CHAT_MESSAGE',
          payload: {
            role: 'assistant',
            content: response.content,
            timestamp: new Date().toISOString(),
            data: response,
            ragSources: response.rag_sources || [],
            messageType: response.message_type,
          }
        });
        if (response.feedback) dispatch({ type: 'SET_STATE', payload: response.feedback });
        if (response.quiz) dispatch({ type: 'SET_CURRENT_QUIZ', payload: response.quiz });
        if (response.rag_sources) dispatch({ type: 'SET_RAG_SOURCES', payload: response.rag_sources });
        if (response.xp_earned > 0) {
          dispatch({ type: 'UPDATE_USER_XP', payload: response.xp_earned });
          dispatch({ type: 'SHOW_XP', payload: response.xp_earned });
          setTimeout(() => dispatch({ type: 'HIDE_XP' }), 2500);
        }
        if (response.memory_updated) {
          // Refresh memory silently
          setTimeout(() => actions.loadMemory(), 500);
        }
        return response;
      } catch (e) {
        dispatch({
          type: 'ADD_CHAT_MESSAGE',
          payload: { role: 'assistant', content: "I'm having trouble connecting to the server. Please make sure the backend is running on port 8000.", timestamp: new Date().toISOString() }
        });
      } finally {
        dispatch({ type: 'SET_LOADING', payload: false });
      }
    }, [state.mentor]),

    submitQuizAnswer: useCallback(async (quizQuestion, selectedId, correctId, topic) => {
      dispatch({ type: 'SET_LOADING', payload: true });
      try {
        const response = await api.submitQuizAnswer({ user_id: 1, quiz_question: quizQuestion, selected_option_id: selectedId, correct_option_id: correctId, topic: topic || '' });
        dispatch({ type: 'ADD_CHAT_MESSAGE', payload: { role: 'assistant', content: response.content, timestamp: new Date().toISOString(), data: response } });
        if (response.feedback) dispatch({ type: 'SET_STATE', payload: response.feedback });
        if (response.xp_earned > 0) {
          dispatch({ type: 'UPDATE_USER_XP', payload: response.xp_earned });
          dispatch({ type: 'SHOW_XP', payload: response.xp_earned });
          setTimeout(() => dispatch({ type: 'HIDE_XP' }), 2500);
        }
        dispatch({ type: 'SET_CURRENT_QUIZ', payload: null });
        // Refresh memory (quiz result updates spaced repetition)
        setTimeout(() => actions.loadMemory(), 500);
        return response;
      } catch (e) {
        console.error('Quiz answer error:', e);
      } finally {
        dispatch({ type: 'SET_LOADING', payload: false });
      }
    }, []),

    generateRoadmap: useCallback(async (goal) => {
      dispatch({ type: 'SET_LOADING', payload: true });
      try {
        const roadmap = await api.generateRoadmap(goal);
        dispatch({ type: 'SET_ROADMAP', payload: roadmap });
        return roadmap;
      } catch (e) {
        console.error('Roadmap error:', e);
      } finally {
        dispatch({ type: 'SET_LOADING', payload: false });
      }
    }, []),

    loadRoadmap: useCallback(async () => {
      try {
        const roadmap = await api.getRoadmap();
        if (roadmap) dispatch({ type: 'SET_ROADMAP', payload: roadmap });
      } catch (e) {}
    }, []),

    loadProgress: useCallback(async () => {
      try {
        const progress = await api.getProgress();
        if (progress) {
          dispatch({ type: 'SET_USER', payload: progress.user });
          dispatch({ type: 'SET_STATE', payload: progress.state });
        }
        return progress;
      } catch (e) {}
    }, []),

    loadGamification: useCallback(async () => {
      try {
        const gam = await api.getGamification();
        dispatch({ type: 'SET_GAMIFICATION', payload: gam });
        return gam;
      } catch (e) {}
    }, []),

    loadMemory: useCallback(async () => {
      try {
        const memory = await api.getMemory();
        dispatch({ type: 'SET_MEMORY', payload: memory });
        return memory;
      } catch (e) {}
    }, []),

    setPage: useCallback((page) => dispatch({ type: 'SET_PAGE', payload: page }), []),
    setUser: useCallback((user) => dispatch({ type: 'SET_USER', payload: user }), []),
    hideLevelUp: useCallback(() => dispatch({ type: 'HIDE_LEVEL_UP' }), []),
    setMentor: useCallback((mentor) => dispatch({ type: 'SET_MENTOR', payload: mentor }), []),
    toggleFocusMode: useCallback(() => dispatch({ type: 'TOGGLE_FOCUS' }), []),
  };

  return (
    <AppContext.Provider value={{ state, actions }}>
      {children}
    </AppContext.Provider>
  );
}

export function useApp() {
  const context = useContext(AppContext);
  if (!context) throw new Error('useApp must be used within AppProvider');
  return context;
}
