'use client';

import React, { useState } from 'react';
import { Button } from '@/components/ui/Button';

export interface ProductTemplate {
  id: string;
  name: string;
  description: string;
  features: string[];
  questionCount: number;
  createdAt: string;
}

interface ProductCloneManagerProps {
  templates: ProductTemplate[];
  onCreateClone: (templateId: string, name: string, description: string, settings?: Record<string, any>) => Promise<void>;
  onDeleteClone: (cloneId: string) => Promise<void>;
  existingClones: ProductTemplate[];
  isLoading?: boolean;
}

const ProductCloneManager: React.FC<ProductCloneManagerProps> = ({
  templates,
  onCreateClone,
  onDeleteClone,
  existingClones,
  isLoading = false,
}) => {
  const [selectedTemplate, setSelectedTemplate] = useState<string>(templates[0]?.id || '');
  const [cloneName, setCloneName] = useState('');
  const [cloneDescription, setCloneDescription] = useState('');
  const [advancedSettings, setAdvancedSettings] = useState<Record<string, any>>({
    copyQuestions: true,
    copyAssessmentCriteria: true,
    enableSubscriptions: true,
  });
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [creating, setCreating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleCreateClone = async () => {
    if (!selectedTemplate) {
      setError('Please select a template');
      return;
    }
    
    if (!cloneName.trim()) {
      setError('Please enter a name for your clone');
      return;
    }
    
    try {
      setCreating(true);
      setError(null);
      await onCreateClone(selectedTemplate, cloneName, cloneDescription, advancedSettings);
      // Reset form
      setCloneName('');
      setCloneDescription('');
      setShowAdvanced(false);
    } catch (err) {
      setError('Failed to create clone. Please try again.');
      console.error(err);
    } finally {
      setCreating(false);
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric', 
      month: 'short', 
      day: 'numeric',
    });
  };

  return (
    <div className="bg-white rounded-lg shadow-md overflow-hidden">
      <div className="border-b border-gray-200">
        <div className="px-6 py-4">
          <h2 className="text-xl font-semibold text-gray-800">Product Clone Management</h2>
          <p className="text-sm text-gray-600 mt-1">
            Create and manage copies of your product with custom settings
          </p>
        </div>
      </div>

      <div className="p-6">
        <div className="mb-8">
          <h3 className="text-lg font-medium text-gray-800 mb-4">Create New Clone</h3>
          
          {error && (
            <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-md text-red-600 text-sm">
              {error}
            </div>
          )}
          
          <div className="space-y-4">
            <div>
              <label htmlFor="template" className="block text-sm font-medium text-gray-700 mb-1">
                Template
              </label>
              <select
                id="template"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                value={selectedTemplate}
                onChange={(e) => setSelectedTemplate(e.target.value)}
              >
                <option value="" disabled>Select a template</option>
                {templates.map((template) => (
                  <option key={template.id} value={template.id}>
                    {template.name} ({template.questionCount} questions)
                  </option>
                ))}
              </select>
            </div>
            
            <div>
              <label htmlFor="name" className="block text-sm font-medium text-gray-700 mb-1">
                Clone Name
              </label>
              <input
                type="text"
                id="name"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="E.g., Software Engineering Interview Prep"
                value={cloneName}
                onChange={(e) => setCloneName(e.target.value)}
              />
            </div>
            
            <div>
              <label htmlFor="description" className="block text-sm font-medium text-gray-700 mb-1">
                Description
              </label>
              <textarea
                id="description"
                rows={3}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Describe the purpose of this clone..."
                value={cloneDescription}
                onChange={(e) => setCloneDescription(e.target.value)}
              />
            </div>
            
            <div>
              <button
                type="button"
                className="text-sm text-blue-600 hover:text-blue-800 focus:outline-none"
                onClick={() => setShowAdvanced(!showAdvanced)}
              >
                {showAdvanced ? 'Hide' : 'Show'} Advanced Settings
              </button>
              
              {showAdvanced && (
                <div className="mt-3 p-4 bg-gray-50 rounded-md space-y-3">
                  <div className="flex items-center">
                    <input
                      type="checkbox"
                      id="copyQuestions"
                      checked={advancedSettings.copyQuestions}
                      onChange={(e) => setAdvancedSettings({
                        ...advancedSettings,
                        copyQuestions: e.target.checked
                      })}
                      className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                    />
                    <label htmlFor="copyQuestions" className="ml-2 block text-sm text-gray-700">
                      Copy all questions from template
                    </label>
                  </div>
                  
                  <div className="flex items-center">
                    <input
                      type="checkbox"
                      id="copyAssessmentCriteria"
                      checked={advancedSettings.copyAssessmentCriteria}
                      onChange={(e) => setAdvancedSettings({
                        ...advancedSettings,
                        copyAssessmentCriteria: e.target.checked
                      })}
                      className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                    />
                    <label htmlFor="copyAssessmentCriteria" className="ml-2 block text-sm text-gray-700">
                      Copy assessment criteria
                    </label>
                  </div>
                  
                  <div className="flex items-center">
                    <input
                      type="checkbox"
                      id="enableSubscriptions"
                      checked={advancedSettings.enableSubscriptions}
                      onChange={(e) => setAdvancedSettings({
                        ...advancedSettings,
                        enableSubscriptions: e.target.checked
                      })}
                      className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                    />
                    <label htmlFor="enableSubscriptions" className="ml-2 block text-sm text-gray-700">
                      Enable subscription plans
                    </label>
                  </div>
                  
                  <div>
                    <label htmlFor="accessLevel" className="block text-sm font-medium text-gray-700 mb-1">
                      Default Access Level
                    </label>
                    <select
                      id="accessLevel"
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      value={advancedSettings.accessLevel || 'private'}
                      onChange={(e) => setAdvancedSettings({
                        ...advancedSettings,
                        accessLevel: e.target.value
                      })}
                    >
                      <option value="private">Private (Admin only)</option>
                      <option value="restricted">Restricted (Invite only)</option>
                      <option value="public">Public (Available to all users)</option>
                    </select>
                  </div>
                </div>
              )}
            </div>
            
            <div className="flex justify-end">
              <Button
                onClick={handleCreateClone}
                disabled={creating || isLoading}
                isLoading={creating}
              >
                Create Clone
              </Button>
            </div>
          </div>
        </div>
        
        <div>
          <h3 className="text-lg font-medium text-gray-800 mb-4">Existing Clones</h3>
          
          {isLoading ? (
            <div className="flex justify-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-blue-500"></div>
            </div>
          ) : existingClones.length === 0 ? (
            <div className="text-center py-8 border border-dashed border-gray-300 rounded-lg">
              <p className="text-gray-500">No clones created yet</p>
              <p className="text-sm text-gray-400 mt-1">
                Create your first clone to customize the product experience
              </p>
            </div>
          ) : (
            <div className="border border-gray-200 rounded-lg overflow-hidden">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Name
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Based On
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Questions
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Created
                    </th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {existingClones.map((clone) => {
                    const baseTemplate = templates.find(t => t.id === clone.id.split('-clone-')[0]);
                    
                    return (
                      <tr key={clone.id}>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="text-sm font-medium text-gray-900">{clone.name}</div>
                          <div className="text-sm text-gray-500 truncate max-w-xs">{clone.description}</div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {baseTemplate?.name || 'Custom'}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {clone.questionCount}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {formatDate(clone.createdAt)}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                          <button
                            className="text-blue-600 hover:text-blue-900 mr-3"
                            onClick={() => {/* Navigate to edit page */}}
                          >
                            Manage
                          </button>
                          <button
                            className="text-red-600 hover:text-red-900"
                            onClick={() => onDeleteClone(clone.id)}
                          >
                            Delete
                          </button>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ProductCloneManager;
