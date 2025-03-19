'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import SubscriptionPlans from '@/components/subscription/SubscriptionPlans';
import PaymentForm from '@/components/subscription/PaymentForm';
import SubscriptionDetails from '@/components/subscription/SubscriptionDetails';
import BillingHistory from '@/components/subscription/BillingHistory';
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/ui/Tabs';
import { Button } from '@/components/ui/Button';
import { Card } from '@/components/ui/Card';
import { Alert, AlertTitle, AlertDescription } from '@/components/ui/Alert';
import { LoadingSpinner } from '@/components/ui/LoadingSpinner';

interface SubscriptionPlan {
  id: string;
  name: string;
  description: string;
  price: number;
  currency: string;
  interval: string;
  features: Array<{
    name: string;
    description: string;
    included: boolean;
  }>;
  popular?: boolean;
  trial_days: number;
}

interface Subscription {
  id: string;
  user_id: string;
  subscription_plan_id: string;
  status: string;
  billing_period: string;
  amount: number;
  currency: string;
  stripe_subscription_id: string | null;
  payment_method_id: string | null;
  payment_method_type: string | null;
  last_four: string | null;
  card_brand: string | null;
  current_period_start: string | null;
  current_period_end: string | null;
  trial_start: string | null;
  trial_end: string | null;
  cancel_at_period_end: boolean;
  canceled_at: string | null;
  plan_details: any;
  created_at: string;
  updated_at: string;
}

interface BillingHistoryItem {
  id: string;
  user_id: string;
  subscription_id: string | null;
  event_type: string;
  description: string | null;
  event_time: string;
  amount: number | null;
  currency: string | null;
  payment_status: string | null;
  payment_method_type: string | null;
  payment_last_four: string | null;
  payment_brand: string | null;
  invoice_url: string | null;
  receipt_url: string | null;
  created_at: string;
}

interface PaymentResult {
  subscription_id: string;
  requires_payment: boolean;
  client_secret?: string;
  status: string;
}

const SubscriptionPage: React.FC = () => {
  const router = useRouter();
  
  // State for plans and subscriptions
  const [subscriptionPlans, setSubscriptionPlans] = useState<SubscriptionPlan[]>([]);
  const [currentSubscription, setCurrentSubscription] = useState<Subscription | null>(null);
  const [billingHistory, setBillingHistory] = useState<BillingHistoryItem[]>([]);
  const [billingCycle, setBillingCycle] = useState<'monthly' | 'yearly'>('monthly');
  
  // State for UI flow
  const [selectedPlanId, setSelectedPlanId] = useState<string | null>(null);
  const [showPaymentForm, setShowPaymentForm] = useState(false);
  const [processingPayment, setProcessingPayment] = useState(false);
  const [paymentSuccessful, setPaymentSuccessful] = useState(false);
  
  // State for errors and loading
  const [isLoading, setIsLoading] = useState(true);
  const [isLoadingHistory, setIsLoadingHistory] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  // Payment intent details for Stripe
  const [paymentIntentClientSecret, setPaymentIntentClientSecret] = useState<string | null>(null);
  
  // Fetch subscription plans and current subscription
  useEffect(() => {
    const fetchData = async () => {
      try {
        setIsLoading(true);
        setError(null);
        
        // Fetch subscription plans
        const plansResponse = await fetch(`/api/subscriptions/plans?billing_cycle=${billingCycle}`);
        
        if (!plansResponse.ok) {
          throw new Error('Failed to fetch subscription plans');
        }
        
        const plansData = await plansResponse.json();
        setSubscriptionPlans(plansData);
        
        // Fetch current subscription
        const subscriptionResponse = await fetch('/api/subscriptions/my');
        
        if (subscriptionResponse.ok) {
          const subscriptionData = await subscriptionResponse.json();
          setCurrentSubscription(subscriptionData);
        } else if (subscriptionResponse.status !== 404) {
          // 404 means no active subscription, which is fine
          throw new Error('Failed to fetch current subscription');
        }
        
      } catch (err) {
        console.error('Error fetching subscription data:', err);
        setError('Failed to load subscription details. Please try again later.');
      } finally {
        setIsLoading(false);
      }
    };
    
    fetchData();
  }, [billingCycle, paymentSuccessful]);
  
  // Fetch billing history
  useEffect(() => {
    const fetchBillingHistory = async () => {
      if (!currentSubscription) return;
      
      try {
        setIsLoadingHistory(true);
        
        const response = await fetch('/api/subscriptions/billing-history');
        
        if (!response.ok) {
          throw new Error('Failed to fetch billing history');
        }
        
        const data = await response.json();
        setBillingHistory(data);
      } catch (err) {
        console.error('Error fetching billing history:', err);
      } finally {
        setIsLoadingHistory(false);
      }
    };
    
    fetchBillingHistory();
  }, [currentSubscription, paymentSuccessful]);
  
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
      setError(null);
      
      // If user has no active subscription, create a new one
      if (!currentSubscription) {
        const response = await fetch('/api/subscriptions', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            plan_code: selectedPlanId,
            payment_method_id: paymentDetails.paymentMethod === 'existing-card' 
              ? paymentDetails.selectedMethodId 
              : null, // If using a new card, this will be handled by Stripe
            billing_cycle: billingCycle
          }),
        });
        
        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(errorData.detail || 'Failed to create subscription');
        }
        
        const result: PaymentResult = await response.json();
        
        // Check if payment confirmation is required
        if (result.requires_payment && result.client_secret) {
          // Store client secret for payment confirmation
          setPaymentIntentClientSecret(result.client_secret);
          // The payment will be confirmed in the PaymentForm component
        } else {
          // No payment confirmation needed, subscription is active
          setPaymentSuccessful(true);
          setShowPaymentForm(false);
        }
      } else {
        // This is an upgrade or change to an existing subscription
        const response = await fetch(`/api/subscriptions/${currentSubscription.id}/upgrade`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            new_plan_code: selectedPlanId,
            billing_cycle: billingCycle,
          }),
        });
        
        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(errorData.detail || 'Failed to upgrade subscription');
        }
        
        // Upgrade successful
        setPaymentSuccessful(true);
        setShowPaymentForm(false);
      }
      
      // Reset state
      setSelectedPlanId(null);
    } catch (error) {
      console.error('Payment error:', error);
      setError(error instanceof Error ? error.message : 'An unexpected error occurred');
    } finally {
      setProcessingPayment(false);
    }
  };
  
  const handleCancelSubscription = async (atPeriodEnd: boolean = true) => {
    if (!currentSubscription) return;
    
    try {
      setIsLoading(true);
      setError(null);
      
      const response = await fetch(`/api/subscriptions/${currentSubscription.id}/cancel`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          at_period_end: atPeriodEnd,
        }),
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to cancel subscription');
      }
      
      // Refresh current subscription
      const subscriptionResponse = await fetch('/api/subscriptions/my');
      if (subscriptionResponse.ok) {
        const subscriptionData = await subscriptionResponse.json();
        setCurrentSubscription(subscriptionData);
      }
      
    } catch (error) {
      console.error('Error canceling subscription:', error);
      setError(error instanceof Error ? error.message : 'Failed to cancel subscription');
    } finally {
      setIsLoading(false);
    }
  };
  
  const handleReactivateSubscription = async () => {
    if (!currentSubscription) return;
    
    try {
      setIsLoading(true);
      setError(null);
      
      const response = await fetch(`/api/subscriptions/${currentSubscription.id}/reactivate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to reactivate subscription');
      }
      
      // Refresh current subscription
      const subscriptionResponse = await fetch('/api/subscriptions/my');
      if (subscriptionResponse.ok) {
        const subscriptionData = await subscriptionResponse.json();
        setCurrentSubscription(subscriptionData);
      }
      
    } catch (error) {
      console.error('Error reactivating subscription:', error);
      setError(error instanceof Error ? error.message : 'Failed to reactivate subscription');
    } finally {
      setIsLoading(false);
    }
  };
  
  const handleManagePaymentMethod = async () => {
    try {
      setIsLoading(true);
      
      const response = await fetch('/api/subscriptions/billing-portal', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          return_url: window.location.href,
        }),
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to create billing portal');
      }
      
      const { url } = await response.json();
      
      // Redirect to Stripe billing portal
      window.location.href = url;
      
    } catch (error) {
      console.error('Error opening billing portal:', error);
      setError(error instanceof Error ? error.message : 'Failed to open billing portal');
    } finally {
      setIsLoading(false);
    }
  };
  
  const handleCancelPaymentForm = () => {
    setShowPaymentForm(false);
    setSelectedPlanId(null);
    setPaymentIntentClientSecret(null);
  };
  
  const getSelectedPlan = () => {
    return subscriptionPlans.find(plan => plan.id === selectedPlanId);
  };
  
  if (isLoading && !showPaymentForm) {
    return (
      <div className="container mx-auto px-4 py-20 flex justify-center">
        <LoadingSpinner size="lg" />
      </div>
    );
  }
  
  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-5xl mx-auto">
        <div className="text-center mb-10">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Subscription Management</h1>
          <p className="text-gray-600 max-w-2xl mx-auto">
            Manage your interview preparation subscription, view billing history, and update payment methods.
          </p>
        </div>
        
        {error && (
          <Alert variant="destructive" className="mb-6">
            <AlertTitle>Error</AlertTitle>
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}
        
        {paymentSuccessful && (
          <Alert variant="success" className="mb-6">
            <AlertTitle>Success</AlertTitle>
            <AlertDescription>
              Your subscription has been updated successfully.
            </AlertDescription>
          </Alert>
        )}
        
        {/* If no subscription, or in payment flow, show subscription plans */}
        {(!currentSubscription || showPaymentForm) && (
          <>
            {!showPaymentForm ? (
              <>
                <h2 className="text-xl font-semibold mb-4">Choose a Subscription Plan</h2>
                <SubscriptionPlans
                  plans={subscriptionPlans.map(plan => ({
                    id: plan.id,
                    name: plan.name,
                    description: plan.description,
                    price: plan.price * 100, // Convert to cents for the component
                    features: plan.features.map(f => ({
                      name: f.name,
                      included: f.included,
                      description: f.description
                    })),
                    isPopular: plan.popular,
                    yearlyDiscount: plan.interval === 'yearly' ? 16 : 0, // Example discount percentage
                  }))}
                  currentPlanId={currentSubscription?.plan_details?.id}
                  billingCycle={billingCycle}
                  onBillingCycleChange={handleBillingCycleChange}
                  onSelectPlan={handleSelectPlan}
                  currency={subscriptionPlans[0]?.currency || 'USD'}
                />
              </>
            ) : (
              <div>
                <button
                  onClick={handleCancelPaymentForm}
                  className="mb-6 flex items-center text-gray-600 hover:text-gray-900"
                >
                  <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 19l-7-7 7-7" />
                  </svg>
                  Back to plans
                </button>
                
                <PaymentForm
                  onSubmit={handlePaymentSubmit}
                  onCancel={handleCancelPaymentForm}
                  processingPayment={processingPayment}
                  existingPaymentMethods={[]} // Will be fetched from API in a real implementation
                  planName={getSelectedPlan()?.name || ''}
                  amount={getSelectedPlan()?.price || 0}
                  billingCycle={billingCycle}
                  currency={getSelectedPlan()?.currency || 'usd'}
                  clientSecret={paymentIntentClientSecret}
                />
              </div>
            )}
          </>
        )}
        
        {/* If user has a subscription and not in payment flow, show subscription details and tabs */}
        {currentSubscription && !showPaymentForm && (
          <Tabs defaultValue="details">
            <TabsList className="mb-6">
              <TabsTrigger value="details">Subscription Details</TabsTrigger>
              <TabsTrigger value="history">Billing History</TabsTrigger>
              <TabsTrigger value="plans">Change Plan</TabsTrigger>
            </TabsList>
            
            <TabsContent value="details">
              <SubscriptionDetails
                subscription={currentSubscription}
                onCancel={() => handleCancelSubscription(true)}
                onReactivate={handleReactivateSubscription}
                onManagePayment={handleManagePaymentMethod}
              />
            </TabsContent>
            
            <TabsContent value="history">
              <Card className="p-6">
                <h2 className="text-xl font-semibold mb-4">Billing History</h2>
                {isLoadingHistory ? (
                  <div className="flex justify-center py-10">
                    <LoadingSpinner />
                  </div>
                ) : (
                  <BillingHistory items={billingHistory} />
                )}
              </Card>
            </TabsContent>
            
            <TabsContent value="plans">
              <Card className="p-6 mb-6">
                <h2 className="text-xl font-semibold mb-4">Change Your Subscription Plan</h2>
                <p className="text-gray-600 mb-6">
                  You can upgrade or downgrade your plan at any time. Upgrading gives you immediate access to
                  additional features. If you downgrade, your current plan will remain active until the end of your billing period.
                </p>
                
                <SubscriptionPlans
                  plans={subscriptionPlans.map(plan => ({
                    id: plan.id,
                    name: plan.name,
                    description: plan.description,
                    price: plan.price * 100, // Convert to cents for the component
                    features: plan.features.map(f => ({
                      name: f.name,
                      included: f.included,
                      description: f.description
                    })),
                    isPopular: plan.popular,
                    yearlyDiscount: plan.interval === 'yearly' ? 16 : 0, // Example discount percentage
                  }))}
                  currentPlanId={currentSubscription?.plan_details?.id}
                  billingCycle={billingCycle}
                  onBillingCycleChange={handleBillingCycleChange}
                  onSelectPlan={handleSelectPlan}
                  currency={subscriptionPlans[0]?.currency || 'USD'}
                />
              </Card>
            </TabsContent>
          </Tabs>
        )}
      </div>
    </div>
  );
};

export default SubscriptionPage;
