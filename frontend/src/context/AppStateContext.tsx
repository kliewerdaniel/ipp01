'use client';

import { createContext, useContext, useReducer, ReactNode } from 'react';

// Types
export interface Interview {
  id: string;
  title: string;
  duration: number;
  difficulty: 'easy' | 'medium' | 'hard';
  topics: string[];
  completed: boolean;
  score?: number;
  date: string;
}

export interface Question {
  id: string;
  title: string;
  description: string;
  difficulty: 'easy' | 'medium' | 'hard';
  topics: string[];
  company?: string;
  completed: boolean;
  solution?: string;
}

interface AppState {
  interviews: Interview[];
  practiceQuestions: Question[];
  isLoading: boolean;
  error: string | null;
}

// Action types
type Action =
  | { type: 'SET_INTERVIEWS'; payload: Interview[] }
  | { type: 'ADD_INTERVIEW'; payload: Interview }
  | { type: 'UPDATE_INTERVIEW'; payload: { id: string; data: Partial<Interview> } }
  | { type: 'DELETE_INTERVIEW'; payload: string }
  | { type: 'SET_QUESTIONS'; payload: Question[] }
  | { type: 'ADD_QUESTION'; payload: Question }
  | { type: 'UPDATE_QUESTION'; payload: { id: string; data: Partial<Question> } }
  | { type: 'DELETE_QUESTION'; payload: string }
  | { type: 'SET_LOADING'; payload: boolean }
  | { type: 'SET_ERROR'; payload: string | null };

// Initial state
const initialState: AppState = {
  interviews: [],
  practiceQuestions: [],
  isLoading: false,
  error: null,
};

// Context
const AppStateContext = createContext<{
  state: AppState;
  dispatch: React.Dispatch<Action>;
} | undefined>(undefined);

// Reducer
function appReducer(state: AppState, action: Action): AppState {
  switch (action.type) {
    case 'SET_INTERVIEWS':
      return { ...state, interviews: action.payload };
    case 'ADD_INTERVIEW':
      return { ...state, interviews: [...state.interviews, action.payload] };
    case 'UPDATE_INTERVIEW':
      return {
        ...state,
        interviews: state.interviews.map(interview =>
          interview.id === action.payload.id
            ? { ...interview, ...action.payload.data }
            : interview
        ),
      };
    case 'DELETE_INTERVIEW':
      return {
        ...state,
        interviews: state.interviews.filter(interview => interview.id !== action.payload),
      };
    case 'SET_QUESTIONS':
      return { ...state, practiceQuestions: action.payload };
    case 'ADD_QUESTION':
      return { ...state, practiceQuestions: [...state.practiceQuestions, action.payload] };
    case 'UPDATE_QUESTION':
      return {
        ...state,
        practiceQuestions: state.practiceQuestions.map(question =>
          question.id === action.payload.id
            ? { ...question, ...action.payload.data }
            : question
        ),
      };
    case 'DELETE_QUESTION':
      return {
        ...state,
        practiceQuestions: state.practiceQuestions.filter(
          question => question.id !== action.payload
        ),
      };
    case 'SET_LOADING':
      return { ...state, isLoading: action.payload };
    case 'SET_ERROR':
      return { ...state, error: action.payload };
    default:
      return state;
  }
}

// Provider component
export function AppStateProvider({ children }: { children: ReactNode }) {
  const [state, dispatch] = useReducer(appReducer, initialState);

  return (
    <AppStateContext.Provider value={{ state, dispatch }}>
      {children}
    </AppStateContext.Provider>
  );
}

// Custom hook to use the app state context
export function useAppState() {
  const context = useContext(AppStateContext);
  if (context === undefined) {
    throw new Error('useAppState must be used within an AppStateProvider');
  }
  return context;
}
