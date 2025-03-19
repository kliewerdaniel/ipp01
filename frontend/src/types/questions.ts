// Question difficulty levels
export type QuestionDifficulty = 'easy' | 'medium' | 'hard';

// Question types
export type QuestionType = 'technical' | 'behavioral' | 'system_design' | 'coding' | 'general';

// Question interface
export interface Question {
  id: string;
  content: string;
  questionType: QuestionType;
  difficulty: QuestionDifficulty;
  category: string;
  isAiGenerated?: boolean;
  expectedAnswer?: string;
  position?: number;
  interviewId: string;
  createdAt: string;
  updatedAt: string;
}

// Category interface
export interface Category {
  id: string;
  name: string;
  description?: string;
  questionCount?: number;
}
