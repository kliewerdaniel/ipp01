'use client';

import React, { useState } from 'react';
import { Button } from '@/components/ui/Button';
import { QuestionType } from '@/types/questions';

// Interfaces for assessment criteria
export interface CriterionItem {
  id: string;
  label: string;
  description: string;
  weight: number; // Weight in percentage (0-100)
}

export interface AssessmentCriteria {
  id: string;
  name: string;
  questionType: QuestionType;
  criteria: CriterionItem[];
  isDefault?: boolean;
}

interface AssessmentCriteriaManagerProps {
  assessmentCriteria: AssessmentCriteria[];
  onAddCriteria: (criteria: Omit<AssessmentCriteria, 'id'>) => void;
  onUpdateCriteria: (id: string, criteria: Partial<AssessmentCriteria>) => void;
  onDeleteCriteria: (id: string) => void;
  isLoading?: boolean;
}

const AssessmentCriteriaManager: React.FC<AssessmentCriteriaManagerProps> = ({
  assessmentCriteria,
  onAddCriteria,
  onUpdateCriteria,
  onDeleteCriteria,
  isLoading = false,
}) => {
  const [selectedCriteria, setSelectedCriteria] = useState<AssessmentCriteria | null>(null);
  const [isEditMode, setIsEditMode] = useState(false);
  const [newCriteria, setNewCriteria] = useState<Omit<AssessmentCriteria, 'id'>>({
    name: '',
    questionType: 'technical',
    criteria: [],
  });
  const [newCriterionItem, setNewCriterionItem] = useState<Omit<CriterionItem, 'id'>>({
    label: '',
    description: '',
    weight: 20,
  });

  // Get the question type display name
  const getQuestionTypeDisplay = (type: QuestionType) => {
    return type.split('_').map(word => 
      word.charAt(0).toUpperCase() + word.slice(1)
    ).join(' ');
  };

  // Handler for selecting a criteria set to view/edit
  const handleSelectCriteria = (criteria: AssessmentCriteria) => {
    setSelectedCriteria(criteria);
    setIsEditMode(false);
  };

  // Handler for updating an existing criteria item in the selected criteria
  const handleUpdateCriterionItem = (id: string, updates: Partial<CriterionItem>) => {
    if (selectedCriteria) {
      const updatedCriteria = {
        ...selectedCriteria,
        criteria: selectedCriteria.criteria.map(item => 
          item.id === id ? { ...item, ...updates } : item
        ),
      };
      setSelectedCriteria(updatedCriteria);
    }
  };

  // Handler for deleting a criterion item from the selected criteria
  const handleDeleteCriterionItem = (id: string) => {
    if (selectedCriteria) {
      const updatedCriteria = {
        ...selectedCriteria,
        criteria: selectedCriteria.criteria.filter(item => item.id !== id),
      };
      setSelectedCriteria(updatedCriteria);
    }
  };

  // Handler for adding a new criterion item to the selected criteria
  const handleAddCriterionItem = () => {
    if (selectedCriteria && isEditMode) {
      // Generate a temporary ID for the UI
      const newItem: CriterionItem = {
        ...newCriterionItem,
        id: `temp-${Date.now()}`,
      };
      
      setSelectedCriteria({
        ...selectedCriteria,
        criteria: [...selectedCriteria.criteria, newItem],
      });
      
      // Reset the form
      setNewCriterionItem({
        label: '',
        description: '',
        weight: 20,
      });
    }
  };

  // Handler for adding a criterion item to the new criteria
  const handleAddCriterionToNew = () => {
    // Generate a temporary ID for the UI
    const newItem: CriterionItem = {
      ...newCriterionItem,
      id: `temp-${Date.now()}`,
    };
    
    setNewCriteria({
      ...newCriteria,
      criteria: [...newCriteria.criteria, newItem],
    });
    
    // Reset the form
    setNewCriterionItem({
      label: '',
      description: '',
      weight: 20,
    });
  };

  // Handler for saving changes to an existing criteria set
  const handleSaveCriteria = () => {
    if (selectedCriteria) {
      onUpdateCriteria(selectedCriteria.id, selectedCriteria);
      setIsEditMode(false);
    }
  };

  // Handler for creating a new criteria set
  const handleCreateCriteria = () => {
    onAddCriteria(newCriteria);
    setNewCriteria({
      name: '',
      questionType: 'technical',
      criteria: [],
    });
  };

  // Check if the total weight of criteria adds up to 100%
  const getTotalWeight = (criteria: CriterionItem[]) => {
    return criteria.reduce((sum, item) => sum + item.weight, 0);
  };

  return (
    <div className="bg-white rounded-lg shadow-md overflow-hidden">
      <div className="border-b border-gray-200">
        <div className="px-6 py-4">
          <h2 className="text-xl font-semibold text-gray-800">Assessment Criteria Management</h2>
          <p className="text-sm text-gray-600 mt-1">
            Define how answers are evaluated based on question type
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 h-full">
        {/* Left Sidebar: Criteria Sets List */}
        <div className="border-r border-gray-200 md:col-span-1 p-4">
          <div className="flex justify-between items-center mb-4">
            <h3 className="text-lg font-medium text-gray-800">Criteria Sets</h3>
            <Button 
              size="sm" 
              variant="outline"
              onClick={() => {
                setSelectedCriteria(null);
                setIsEditMode(false);
              }}
            >
              Create New
            </Button>
          </div>
          
          {isLoading ? (
            <div className="flex justify-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-blue-500"></div>
            </div>
          ) : (
            <div className="space-y-2">
              {assessmentCriteria.map((criteria) => (
                <div 
                  key={criteria.id}
                  className={`p-3 rounded-md cursor-pointer ${
                    selectedCriteria?.id === criteria.id 
                      ? 'bg-blue-50 border border-blue-200' 
                      : 'hover:bg-gray-50 border border-gray-200'
                  }`}
                  onClick={() => handleSelectCriteria(criteria)}
                >
                  <div className="flex justify-between items-center">
                    <div>
                      <h4 className="font-medium text-gray-800">{criteria.name}</h4>
                      <p className="text-sm text-gray-600">
                        {getQuestionTypeDisplay(criteria.questionType)}
                      </p>
                    </div>
                    {criteria.isDefault && (
                      <span className="bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded">
                        Default
                      </span>
                    )}
                  </div>
                  <div className="text-xs text-gray-500 mt-1">
                    {criteria.criteria.length} criteria
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Main Content: Selected Criteria Details or New Criteria Form */}
        <div className="md:col-span-2 p-6 overflow-auto">
          {selectedCriteria ? (
            <div>
              <div className="flex justify-between items-center mb-6">
                <div>
                  <h3 className="text-xl font-semibold text-gray-800">{selectedCriteria.name}</h3>
                  <p className="text-sm text-gray-600">
                    For {getQuestionTypeDisplay(selectedCriteria.questionType)} questions
                  </p>
                </div>
                
                <div className="space-x-2">
                  {!isEditMode ? (
                    <>
                      <Button 
                        size="sm" 
                        variant="outline"
                        onClick={() => setIsEditMode(true)}
                        disabled={selectedCriteria.isDefault}
                      >
                        Edit
                      </Button>
                      {!selectedCriteria.isDefault && (
                        <Button 
                          size="sm" 
                          variant="destructive"
                          onClick={() => onDeleteCriteria(selectedCriteria.id)}
                        >
                          Delete
                        </Button>
                      )}
                    </>
                  ) : (
                    <>
                      <Button 
                        size="sm" 
                        variant="outline"
                        onClick={() => {
                          setIsEditMode(false);
                          // Reset to original state
                          const original = assessmentCriteria.find(c => c.id === selectedCriteria.id);
                          if (original) {
                            setSelectedCriteria(original);
                          }
                        }}
                      >
                        Cancel
                      </Button>
                      <Button 
                        size="sm"
                        onClick={handleSaveCriteria}
                      >
                        Save Changes
                      </Button>
                    </>
                  )}
                </div>
              </div>

              {/* Weight status indicator */}
              <div className="mb-4">
                <div className="flex justify-between items-center mb-1">
                  <span className="text-sm font-medium text-gray-700">Total Weight:</span>
                  <span className={`text-sm font-medium ${
                    getTotalWeight(selectedCriteria.criteria) === 100 
                      ? 'text-green-600' 
                      : 'text-red-600'
                  }`}>
                    {getTotalWeight(selectedCriteria.criteria)}%
                  </span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div 
                    className={`h-2 rounded-full ${
                      getTotalWeight(selectedCriteria.criteria) === 100 
                        ? 'bg-green-500' 
                        : getTotalWeight(selectedCriteria.criteria) > 100
                          ? 'bg-red-500'
                          : 'bg-yellow-500'
                    }`}
                    style={{ width: `${Math.min(100, getTotalWeight(selectedCriteria.criteria))}%` }}
                  ></div>
                </div>
                {getTotalWeight(selectedCriteria.criteria) !== 100 && (
                  <p className="text-xs text-red-600 mt-1">
                    {getTotalWeight(selectedCriteria.criteria) < 100
                      ? `Weights should add up to 100% (currently ${getTotalWeight(selectedCriteria.criteria)}%)`
                      : `Weights exceed 100% (currently ${getTotalWeight(selectedCriteria.criteria)}%)`
                    }
                  </p>
                )}
              </div>

              {/* Criteria List */}
              <div className="space-y-4 mb-6">
                {selectedCriteria.criteria.length === 0 ? (
                  <div className="text-center py-8 border border-dashed border-gray-300 rounded-lg">
                    <p className="text-gray-500">No criteria defined yet</p>
                    {isEditMode && (
                      <p className="text-sm text-gray-400 mt-1">Add criteria using the form below</p>
                    )}
                  </div>
                ) : (
                  selectedCriteria.criteria.map((criterion, index) => (
                    <div 
                      key={criterion.id}
                      className="border border-gray-200 rounded-lg p-4"
                    >
                      <div className="flex justify-between items-start">
                        <div className="flex-1">
                          {isEditMode ? (
                            <input
                              type="text"
                              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 mb-2"
                              value={criterion.label}
                              onChange={(e) => handleUpdateCriterionItem(criterion.id, { label: e.target.value })}
                            />
                          ) : (
                            <h4 className="font-medium text-gray-800 mb-1">{criterion.label}</h4>
                          )}
                          
                          {isEditMode ? (
                            <textarea
                              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 mb-2"
                              rows={2}
                              value={criterion.description}
                              onChange={(e) => handleUpdateCriterionItem(criterion.id, { description: e.target.value })}
                            />
                          ) : (
                            <p className="text-sm text-gray-600 mb-2">{criterion.description}</p>
                          )}
                        </div>
                        
                        <div className="ml-4 flex items-center">
                          {isEditMode ? (
                            <div className="flex items-center space-x-2">
                              <input
                                type="number"
                                min="1"
                                max="100"
                                className="w-16 px-2 py-1 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                                value={criterion.weight}
                                onChange={(e) => handleUpdateCriterionItem(criterion.id, { 
                                  weight: Math.min(100, Math.max(1, parseInt(e.target.value) || 1)) 
                                })}
                              />
                              <span className="text-gray-600">%</span>
                              <button
                                onClick={() => handleDeleteCriterionItem(criterion.id)}
                                className="text-red-500 hover:text-red-700 ml-2"
                              >
                                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
                                </svg>
                              </button>
                            </div>
                          ) : (
                            <span className="bg-gray-100 text-gray-800 text-sm px-2 py-1 rounded">
                              {criterion.weight}%
                            </span>
                          )}
                        </div>
                      </div>
                    </div>
                  ))
                )}
              </div>

              {/* Add New Criterion Form (in edit mode) */}
              {isEditMode && (
                <div className="bg-gray-50 p-4 rounded-lg">
                  <h4 className="font-medium text-gray-800 mb-4">Add New Criterion</h4>
                  <div className="space-y-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Label
                      </label>
                      <input
                        type="text"
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                        placeholder="E.g., Technical Accuracy, Communication, etc."
                        value={newCriterionItem.label}
                        onChange={(e) => setNewCriterionItem({ ...newCriterionItem, label: e.target.value })}
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Description
                      </label>
                      <textarea
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                        rows={2}
                        placeholder="Explain how this criterion should be evaluated..."
                        value={newCriterionItem.description}
                        onChange={(e) => setNewCriterionItem({ ...newCriterionItem, description: e.target.value })}
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Weight (%)
                      </label>
                      <div className="flex items-center">
                        <input
                          type="number"
                          min="1"
                          max="100"
                          className="w-24 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                          value={newCriterionItem.weight}
                          onChange={(e) => setNewCriterionItem({ 
                            ...newCriterionItem, 
                            weight: Math.min(100, Math.max(1, parseInt(e.target.value) || 1)) 
                          })}
                        />
                        <span className="ml-2 text-gray-600">%</span>
                      </div>
                    </div>
                    <div className="flex justify-end">
                      <Button 
                        onClick={handleAddCriterionItem}
                        disabled={!newCriterionItem.label || !newCriterionItem.description}
                      >
                        Add Criterion
                      </Button>
                    </div>
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div>
              <h3 className="text-xl font-semibold text-gray-800 mb-6">Create New Assessment Criteria</h3>
              
              <div className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Name
                    </label>
                    <input
                      type="text"
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      placeholder="E.g., Technical Interview Criteria"
                      value={newCriteria.name}
                      onChange={(e) => setNewCriteria({ ...newCriteria, name: e.target.value })}
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Question Type
                    </label>
                    <select
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      value={newCriteria.questionType}
                      onChange={(e) => setNewCriteria({ ...newCriteria, questionType: e.target.value as QuestionType })}
                    >
                      <option value="technical">Technical</option>
                      <option value="behavioral">Behavioral</option>
                      <option value="system_design">System Design</option>
                      <option value="coding">Coding</option>
                      <option value="general">General</option>
                    </select>
                  </div>
                </div>

                {/* Weight status for new criteria */}
                <div>
                  <div className="flex justify-between items-center mb-1">
                    <span className="text-sm font-medium text-gray-700">Total Weight:</span>
                    <span className={`text-sm font-medium ${
                      getTotalWeight(newCriteria.criteria) === 100 
                        ? 'text-green-600' 
                        : 'text-red-600'
                    }`}>
                      {getTotalWeight(newCriteria.criteria)}%
                    </span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div 
                      className={`h-2 rounded-full ${
                        getTotalWeight(newCriteria.criteria) === 100 
                          ? 'bg-green-500' 
                          : getTotalWeight(newCriteria.criteria) > 100
                            ? 'bg-red-500'
                            : 'bg-yellow-500'
                      }`}
                      style={{ width: `${Math.min(100, getTotalWeight(newCriteria.criteria))}%` }}
                    ></div>
                  </div>
                  {getTotalWeight(newCriteria.criteria) !== 100 && newCriteria.criteria.length > 0 && (
                    <p className="text-xs text-red-600 mt-1">
                      {getTotalWeight(newCriteria.criteria) < 100
                        ? `Weights should add up to 100% (currently ${getTotalWeight(newCriteria.criteria)}%)`
                        : `Weights exceed 100% (currently ${getTotalWeight(newCriteria.criteria)}%)`
                      }
                    </p>
                  )}
                </div>

                {/* Added criteria for new set */}
                <div className="space-y-4">
                  {newCriteria.criteria.map((criterion, index) => (
                    <div 
                      key={criterion.id}
                      className="border border-gray-200 rounded-lg p-4"
                    >
                      <div className="flex justify-between items-start">
                        <div className="flex-1">
                          <h4 className="font-medium text-gray-800 mb-1">{criterion.label}</h4>
                          <p className="text-sm text-gray-600 mb-2">{criterion.description}</p>
                        </div>
                        <div className="ml-4 flex items-center space-x-2">
                          <span className="bg-gray-100 text-gray-800 text-sm px-2 py-1 rounded">
                            {criterion.weight}%
                          </span>
                          <button
                            onClick={() => {
                              setNewCriteria({
                                ...newCriteria,
                                criteria: newCriteria.criteria.filter(item => item.id !== criterion.id)
                              });
                            }}
                            className="text-red-500 hover:text-red-700"
                          >
                            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
                            </svg>
                          </button>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>

                {/* Add criterion form for new criteria set */}
                <div className="bg-gray-50 p-4 rounded-lg">
                  <h4 className="font-medium text-gray-800 mb-4">Add Criterion</h4>
                  <div className="space-y-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Label
                      </label>
                      <input
                        type="text"
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                        placeholder="E.g., Technical Accuracy, Communication, etc."
                        value={newCriterionItem.label}
                        onChange={(e) => setNewCriterionItem({ ...newCriterionItem, label: e.target.value })}
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Description
                      </label>
                      <textarea
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                        rows={2}
                        placeholder="Explain how this criterion should be evaluated..."
                        value={newCriterionItem.description}
                        onChange={(e) => setNewCriterionItem({ ...newCriterionItem, description: e.target.value })}
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Weight (%)
                      </label>
                      <div className="flex items-center">
                        <input
                          type="number"
                          min="1"
                          max="100"
                          className="w-24 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                          value={newCriterionItem.weight}
                          onChange={(e) => setNewCriterionItem({ 
                            ...newCriterionItem, 
                            weight: Math.min(100, Math.max(1, parseInt(e.target.value) || 1)) 
                          })}
                        />
                        <span className="ml-2 text-gray-600">%</span>
                      </div>
                    </div>
                    <div className="flex justify-end">
                      <Button 
                        onClick={handleAddCriterionToNew}
                        disabled={!newCriterionItem.label || !newCriterionItem.description}
                      >
                        Add Criterion
                      </Button>
                    </div>
                  </div>
                </div>

                <div className="flex justify-end pt-4">
                  <Button 
                    onClick={handleCreateCriteria}
                    disabled={
                      !newCriteria.name || 
                      newCriteria.criteria.length === 0 || 
                      getTotalWeight(newCriteria.criteria) !== 100
                    }
                  >
                    Create Assessment Criteria
                  </Button>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default AssessmentCriteriaManager;
