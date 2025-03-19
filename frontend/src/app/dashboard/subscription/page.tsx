'use client';

import React, { useState } from 'react';
import SubscriptionPlans, { SubscriptionPlan, PlanFeature } from '@/components/subscription/SubscriptionPlans';
import PaymentForm, { PaymentMethod } from '@/components/subscription/PaymentForm';

const SubscriptionPage: React.FC = () => {
  const [selectedPlanId, setSelectedPlanId] = useState<string | null>(null);
  const [billingCycle, setBillingCycle] = useState<'monthly' | 'yearly'>('monthly');
  const [showPaymentForm, setShowPaymentForm] = useState(false);
  const [processingPayment, setProcessingPayment] = useState(false);
  const [currentPlanId, setCurrentPlanId] = useState<string | null>('free');

  // Mock subscription plans data
  const subscriptionPlans: SubscriptionPlan[] = [
    {
      id: 'free',
      name: 'Free',
      description: 'Basic interview preparation for casual users',
      price: 0, // in cents
      features: [
        { name: 'Access to 5 practice questions', included: true },
        { name: 'Basic feedback on answers', included: true },
        { name: 'Access to community forums', included: true },
        { name: 'Personalized feedback', included: false },
        { name: 'Advanced question categories', included: false },
        { name: 'Interview performance analytics', included: false },
      ],
      yearlyDiscount: 0,
    },
    {
      id: 'basic',
      name: 'Basic',
      description: 'Essential features for serious job seekers',
      price: 999, // $9.99 in cents
      features: [
        { name: 'Access to 50 practice questions', included: true },
        { name: 'Basic feedback on answers', included: true },
        { name: 'Access to community forums', included: true },
        { name: 'Personalized feedback', included: true },
        { name: 'Advanced question categories', included: false },
        { name: 'Interview performance analytics', included: false },
      ],
      isPopular: true,
      yearlyDiscount: 16,
    },
    {
      id: 'premium',
      name: 'Premium',
      description: 'Complete preparation for professional interviewees',
      price: 1999, // $19.99 in cents
      features: [
        { name: 'Unlimited practice questions', included: true },
        { name: 'Advanced AI-powered feedback', included: true },
        { name: 'Access to community forums', included: true },
        { name: 'Personalized feedback', included: true },
        { name: 'Advanced question categories', included: true },
        { name: 'Interview performance analytics', included: true },
      ],
      yearlyDiscount: 20,
    },
  ];

  // Mock payment methods
  const existingPaymentMethods: PaymentMethod[] = [
    {
      id: 'card-1',
      type: 'card',
      cardBrand: 'visa',
      last4: '4242',
      expiryMonth: 12,
      expiryYear: 25,
      isDefault: true,
    },
    {
      id: 'card-2',
      type: 'card',
      cardBrand: 'mastercard',
      last4: '8888',
      expiryMonth: 6,
      expiryYear: 27,
    },
  ];

  const handleSelectPlan = (planId: string) => {
    setSelectedPlanId(planId);
    setShowPaymentForm(true);
  };

  const handleBillingCycleChange = (cycle: 'monthly' | 'yearly') => {
    setBillingCycle(cycle);
  };

  const handlePaymentSubmit = async (paymentDetails: any) => {
    try {
      setProcessingPayment(true);
      
      // Simulate payment processing
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      // Mock successful payment
      setCurrentPlanId(selectedPlanId);
      setShowPaymentForm(false);
      setProcessingPayment(false);
      
      // Reset state
      setSelectedPlanId(null);
    } catch (error) {
      console.error('Payment error:', error);
      setProcessingPayment(false);
      // Handle error
    }
  };

  const handleCancelPayment = () => {
    setShowPaymentForm(false);
    setSelectedPlanId(null);
  };

  const getSelectedPlan = () => {
    return subscriptionPlans.find(plan => plan.id === selectedPlanId);
  };

  // Format price helper
  const formatPrice = (priceInCents: number) => {
    return priceInCents / 100;
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-5xl mx-auto">
        <div className="text-center mb-10">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Subscription Plans</h1>
          <p className="text-gray-600 max-w-2xl mx-auto">
            Choose the perfect plan to elevate your interview preparation. 
            Upgrade anytime to access more features and improve your chances of landing your dream job.
          </p>
        </div>

        {!showPaymentForm ? (
          <SubscriptionPlans
            plans={subscriptionPlans}
            currentPlanId={currentPlanId || undefined}
            billingCycle={billingCycle}
            onBillingCycleChange={handleBillingCycleChange}
            onSelectPlan={handleSelectPlan}
          />
        ) : (
          <div>
            <button
              onClick={handleCancelPayment}
              className="mb-6 flex items-center text-gray-600 hover:text-gray-900"
            >
              <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 19l-7-7 7-7" />
              </svg>
              Back to plans
            </button>
            
            <PaymentForm
              onSubmit={handlePaymentSubmit}
              onCancel={handleCancelPayment}
              processingPayment={processingPayment}
              existingPaymentMethods={existingPaymentMethods}
              planName={getSelectedPlan()?.name || ''}
              amount={getSelectedPlan() ? formatPrice(getSelectedPlan()!.price) : 0}
              billingCycle={billingCycle}
            />
          </div>
        )}

        {currentPlanId && currentPlanId !== 'free' && !showPaymentForm && (
          <div className="mt-8 p-4 bg-blue-50 border border-blue-100 rounded-lg">
            <h3 className="text-lg font-medium text-blue-800 mb-2">Your Current Subscription</h3>
            <p className="text-blue-700">
              You are currently subscribed to the <strong>{subscriptionPlans.find(p => p.id === currentPlanId)?.name}</strong> plan with {billingCycle} billing.
            </p>
            <p className="text-sm text-blue-600 mt-1">
              Your next billing date is April 19, 2025. You can change or cancel your subscription at any time.
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

export default SubscriptionPage;
