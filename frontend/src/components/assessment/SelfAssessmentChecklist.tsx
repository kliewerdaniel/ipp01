'use client';

import React, { useState } from 'react';
import { Question, QuestionType } from '@/types/questions';

// Define assessment criteria for different question types
interface AssessmentCriterion {
  id: string;
  label: string;
  description: string;
}

interface SelfAssessmentChecklistProps {
  question: Question;
  onAssessmentComplete?: (assessment: Record<string, boolean>) => void;
}

const SelfAssessmentChecklist: React.FC<SelfAssessmentChecklistProps> = ({
  question,
  onAssessmentComplete,
}) => {
  // Generate criteria based on question type
  const getCriteriaForQuestionType = (type: QuestionType): AssessmentCriterion[] => {
    switch (type) {
      case 'technical':
        return [
          { id: 'technical_accuracy', label: 'Technical Accuracy', description: 'Did you provide technically accurate information?' },
          { id: 'problem_solving', label: 'Problem Solving', description: 'Did you demonstrate a clear problem-solving approach?' },
          { id: 'complexity', label: 'Complexity Analysis', description: 'Did you analyze time and space complexity (if applicable)?' },
          { id: 'edge_cases', label: 'Edge Cases', description: 'Did you address potential edge cases?' },
          { id: 'clarity', label: 'Clarity', description: 'Did you explain technical concepts clearly?' },
        ];
      case 'behavioral':
        return [
          { id: 'situation', label: 'Situation', description: 'Did you clearly describe the situation or challenge?' },
          { id: 'task', label: 'Task', description: 'Did you explain your specific responsibilities or tasks?' },
          { id: 'action', label: 'Action', description: 'Did you detail the actions you took to address the situation?' },
          { id: 'result', label: 'Result', description: 'Did you share the outcomes or results of your actions?' },
          { id: 'reflection', label: 'Reflection', description: 'Did you reflect on what you learned or how you grew?' },
        ];
      case 'system_design':
        return [
          { id: 'requirements', label: 'Requirements', description: 'Did you clarify functional and non-functional requirements?' },
          { id: 'architecture', label: 'Architecture', description: 'Did you propose a coherent high-level architecture?' },
          { id: 'components', label: 'Components', description: 'Did you detail the key components and their relationships?' },
          { id: 'scalability', label: 'Scalability', description: 'Did you address how the system would scale?' },
          { id: 'trade_offs', label: 'Trade-offs', description: 'Did you discuss trade-offs in your design decisions?' },
        ];
      case 'coding':
        return [
          { id: 'solution', label: 'Solution Approach', description: 'Did you explain your approach before diving into code?' },
          { id: 'correctness', label: 'Correctness', description: 'Is your solution correct and does it solve the problem?' },
          { id: 'optimization', label: 'Optimization', description: 'Did you optimize your solution where appropriate?' },
          { id: 'clean_code', label: 'Clean Code', description: 'Did you use meaningful variable names and follow best practices?' },
          { id: 'testing', label: 'Testing', description: 'Did you discuss how you would test your solution?' },
        ];
      default:
        return [
          { id: 'clarity', label: 'Clarity', description: 'Was your answer clear and well-structured?' },
          { id: 'relevance', label: 'Relevance', description: 'Did you address the question directly and stay on topic?' },
          { id: 'depth', label: 'Depth', description: 'Did you provide sufficient depth to your answer?' },
          { id: 'examples', label: 'Examples', description: 'Did you include relevant examples or evidence?' },
          { id: 'conciseness', label: 'Conciseness', description: 'Was your answer appropriately concise?' },
        ];
    }
  };

  const criteria = getCriteriaForQuestionType(question.questionType);
  const [assessment, setAssessment] = useState<Record<string, boolean>>(
    Object.fromEntries(criteria.map(criterion => [criterion.id, false]))
  );
  const [expanded, setExpanded] = useState<Record<string, boolean>>(
    Object.fromEntries(criteria.map(criterion => [criterion.id, false]))
  );

  const handleCheckboxChange = (criterionId: string, isChecked: boolean) => {
    const newAssessment = { ...assessment, [criterionId]: isChecked };
    setAssessment(newAssessment);
    
    if (onAssessmentComplete) {
      onAssessmentComplete(newAssessment);
    }
  };

  const toggleDescription = (criterionId: string) => {
    setExpanded(prev => ({ ...prev, [criterionId]: !prev[criterionId] }));
  };

  const getCompletionPercentage = () => {
    const checkedCount = Object.values(assessment).filter(value => value).length;
    return Math.round((checkedCount / criteria.length) * 100);
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-xl font-medium text-gray-800">Self-Assessment</h3>
        <div className="text-sm font-medium text-gray-600">
          {getCompletionPercentage()}% complete
        </div>
      </div>
      
      <p className="text-gray-600 mb-6">
        Evaluate your performance by checking the criteria you believe you met. Be honest with yourself to identify areas for improvement.
      </p>
      
      <div className="space-y-4">
        {criteria.map((criterion) => (
          <div key={criterion.id} className="border border-gray-200 rounded-md p-4">
            <div className="flex items-start">
              <input
                type="checkbox"
                id={criterion.id}
                checked={assessment[criterion.id]}
                onChange={(e) => handleCheckboxChange(criterion.id, e.target.checked)}
                className="mt-1 h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
              />
              <div className="ml-3 flex-1">
                <label htmlFor={criterion.id} className="text-gray-800 font-medium">
                  {criterion.label}
                </label>
                <button
                  type="button"
                  onClick={() => toggleDescription(criterion.id)}
                  className="ml-2 text-gray-400 hover:text-gray-600 focus:outline-none"
                  aria-label={expanded[criterion.id] ? 'Hide description' : 'Show description'}
                >
                  {expanded[criterion.id] ? (
                    <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 15l7-7 7 7" />
                    </svg>
                  ) : (
                    <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 9l-7 7-7-7" />
                    </svg>
                  )}
                </button>
                {expanded[criterion.id] && (
                  <p className="mt-1 text-sm text-gray-600">{criterion.description}</p>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>
      
      {/* Progress visualization */}
      <div className="mt-6">
        <div className="w-full bg-gray-200 rounded-full h-2.5">
          <div
            className="bg-blue-600 h-2.5 rounded-full transition-all duration-300"
            style={{ width: `${getCompletionPercentage()}%` }}
          ></div>
        </div>
      </div>
    </div>
  );
};

export default SelfAssessmentChecklist;
