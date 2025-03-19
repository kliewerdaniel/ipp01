'use client';

import React from 'react';
import { Button } from '@/components/ui/Button';

export interface PlanFeature {
  name: string;
  included: boolean;
  limit?: number | string;
}

export interface SubscriptionPlan {
  id: string;
  name: string;
  description: string;
  price: number; // monthly price in cents
  features: PlanFeature[];
  isPopular?: boolean;
  yearlyDiscount?: number; // percentage discount for yearly billing
}

interface SubscriptionPlansProps {
  plans: SubscriptionPlan[];
  currentPlanId?: string;
  billingCycle: 'monthly' | 'yearly';
  onBillingCycleChange: (cycle: 'monthly' | 'yearly') => void;
  onSelectPlan: (planId: string) => void;
  currency?: string;
}

const SubscriptionPlans: React.FC<SubscriptionPlansProps> = ({
  plans,
  currentPlanId,
  billingCycle,
  onBillingCycleChange,
  onSelectPlan,
  currency = 'USD',
}) => {
  const formatPrice = (priceInCents: number, cycle: 'monthly' | 'yearly'): string => {
    let price = priceInCents / 100; // Convert cents to dollars
    
    // Apply yearly discount if applicable
    if (cycle === 'yearly') {
      const plan = plans.find((p) => p.price === priceInCents);
      if (plan?.yearlyDiscount) {
        price = price * (1 - plan.yearlyDiscount / 100);
      }
    }

    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency,
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(price);
  };

  return (
    <div>
      {/* Billing cycle toggle */}
      <div className="flex justify-center mb-8">
        <div className="inline-flex rounded-md p-1 bg-gray-100">
          <button
            className={`px-4 py-2 text-sm font-medium rounded-md ${
              billingCycle === 'monthly'
                ? 'bg-white text-gray-800 shadow-sm'
                : 'text-gray-600 hover:text-gray-800'
            }`}
            onClick={() => onBillingCycleChange('monthly')}
          >
            Monthly Billing
          </button>
          <button
            className={`px-4 py-2 text-sm font-medium rounded-md ${
              billingCycle === 'yearly'
                ? 'bg-white text-gray-800 shadow-sm'
                : 'text-gray-600 hover:text-gray-800'
            }`}
            onClick={() => onBillingCycleChange('yearly')}
          >
            Yearly Billing
            <span className="ml-1 text-xs font-normal text-green-600">
              Save up to 20%
            </span>
          </button>
        </div>
      </div>

      {/* Subscription plans */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {plans.map((plan) => {
          const isCurrentPlan = plan.id === currentPlanId;
          
          return (
            <div
              key={plan.id}
              className={`bg-white rounded-xl shadow-md overflow-hidden border ${
                plan.isPopular
                  ? 'border-blue-500 relative'
                  : isCurrentPlan
                  ? 'border-green-500'
                  : 'border-gray-200'
              }`}
            >
              {/* Popular badge */}
              {plan.isPopular && (
                <div className="absolute top-0 right-0 bg-blue-500 text-white text-xs px-4 py-1 rounded-bl-lg font-medium">
                  Most Popular
                </div>
              )}

              {/* Current plan badge */}
              {isCurrentPlan && (
                <div className="bg-green-100 text-green-800 text-sm px-4 py-2 text-center font-medium">
                  Current Plan
                </div>
              )}

              <div className="p-6">
                <h3 className="text-xl font-bold text-gray-900 mb-1">{plan.name}</h3>
                <p className="text-gray-600 mb-4 h-12">{plan.description}</p>

                <div className="mb-6">
                  <span className="text-4xl font-bold text-gray-900">
                    {formatPrice(plan.price, billingCycle)}
                  </span>
                  <span className="text-gray-500 ml-1">
                    /{billingCycle === 'monthly' ? 'mo' : 'yr'}
                  </span>
                </div>

                <Button
                  onClick={() => onSelectPlan(plan.id)}
                  disabled={isCurrentPlan}
                  className={`w-full ${plan.isPopular ? 'bg-blue-600 hover:bg-blue-700' : ''}`}
                  variant={isCurrentPlan ? 'secondary' : 'default'}
                >
                  {isCurrentPlan ? 'Current Plan' : 'Select Plan'}
                </Button>
              </div>

              <div className="px-6 pt-2 pb-6 bg-gray-50">
                <h4 className="text-sm font-medium text-gray-800 mb-3">What's included:</h4>
                <ul className="space-y-3">
                  {plan.features.map((feature, index) => (
                    <li key={index} className="flex items-start">
                      <div className="flex-shrink-0 mt-0.5">
                        {feature.included ? (
                          <svg
                            className="h-5 w-5 text-green-500"
                            fill="none"
                            stroke="currentColor"
                            viewBox="0 0 24 24"
                          >
                            <path
                              strokeLinecap="round"
                              strokeLinejoin="round"
                              strokeWidth="2"
                              d="M5 13l4 4L19 7"
                            />
                          </svg>
                        ) : (
                          <svg
                            className="h-5 w-5 text-gray-400"
                            fill="none"
                            stroke="currentColor"
                            viewBox="0 0 24 24"
                          >
                            <path
                              strokeLinecap="round"
                              strokeLinejoin="round"
                              strokeWidth="2"
                              d="M6 18L18 6M6 6l12 12"
                            />
                          </svg>
                        )}
                      </div>
                      <span className="ml-2 text-sm text-gray-600">
                        {feature.name}
                        {feature.limit ? ` (${feature.limit})` : ''}
                      </span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          );
        })}
      </div>

      <div className="text-center mt-6 text-sm text-gray-500">
        All plans include a 14-day free trial. No credit card required.
      </div>
    </div>
  );
};

export default SubscriptionPlans;
