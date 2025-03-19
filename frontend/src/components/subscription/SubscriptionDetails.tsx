'use client';

import React from 'react';
import { Button } from '@/components/ui/Button';
import { Card } from '@/components/ui/Card';

interface Subscription {
  id: string;
  status: string;
  billing_period: string;
  amount: number;
  currency: string;
  current_period_start: string | null;
  current_period_end: string | null;
  trial_start: string | null;
  trial_end: string | null;
  cancel_at_period_end: boolean;
  canceled_at: string | null;
  last_four: string | null;
  card_brand: string | null;
  plan_details: any;
}

interface SubscriptionDetailsProps {
  subscription: Subscription;
  onCancel: () => void;
  onReactivate: () => void;
  onManagePayment: () => void;
}

const SubscriptionDetails: React.FC<SubscriptionDetailsProps> = ({
  subscription,
  onCancel,
  onReactivate,
  onManagePayment,
}) => {
  // Format date helpers
  const formatDate = (dateString: string | null) => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    });
  };

  // Format currency helper
  const formatCurrency = (amount: number, currency: string) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: currency.toUpperCase(),
    }).format(amount);
  };

  // Get status label and color
  const getStatusDetails = (status: string, cancel_at_period_end: boolean) => {
    if (cancel_at_period_end) {
      return {
        label: 'Canceling',
        color: 'bg-yellow-100 text-yellow-800',
        description: 'Your subscription will end at the end of the current billing period.',
      };
    }

    switch (status.toLowerCase()) {
      case 'active':
        return {
          label: 'Active',
          color: 'bg-green-100 text-green-800',
          description: 'Your subscription is active and will renew automatically.',
        };
      case 'trialing':
        return {
          label: 'Trial',
          color: 'bg-blue-100 text-blue-800',
          description: 'You are currently in a trial period.',
        };
      case 'past_due':
        return {
          label: 'Past Due',
          color: 'bg-orange-100 text-orange-800',
          description: 'Your payment is past due. Please update your payment method.',
        };
      case 'canceled':
        return {
          label: 'Canceled',
          color: 'bg-red-100 text-red-800',
          description: 'Your subscription has been canceled.',
        };
      default:
        return {
          label: status,
          color: 'bg-gray-100 text-gray-800',
          description: '',
        };
    }
  };

  const statusDetails = getStatusDetails(subscription.status, subscription.cancel_at_period_end);

  return (
    <Card className="p-6">
      <div className="flex justify-between items-start mb-6">
        <div>
          <h2 className="text-xl font-semibold">Your Subscription</h2>
          <p className="text-gray-500">{subscription.plan_details?.description || 'Subscription plan'}</p>
        </div>

        <div className={`px-3 py-1 rounded-full text-sm font-medium ${statusDetails.color}`}>
          {statusDetails.label}
        </div>
      </div>

      {statusDetails.description && (
        <div className="mb-6 bg-gray-50 p-3 rounded-md text-sm text-gray-700">
          {statusDetails.description}
        </div>
      )}

      <div className="grid md:grid-cols-2 gap-6 mb-6">
        <div>
          <h3 className="text-lg font-medium mb-4">Plan Details</h3>

          <div className="space-y-3 text-sm">
            <div className="flex justify-between">
              <span className="text-gray-500">Plan</span>
              <span className="font-medium">{subscription.plan_details?.name || 'Standard Plan'}</span>
            </div>

            <div className="flex justify-between">
              <span className="text-gray-500">Billing Period</span>
              <span className="font-medium">
                {subscription.billing_period === 'yearly' ? 'Yearly' : 'Monthly'}
              </span>
            </div>

            <div className="flex justify-between">
              <span className="text-gray-500">Amount</span>
              <span className="font-medium">
                {formatCurrency(subscription.amount, subscription.currency)}
                /{subscription.billing_period === 'yearly' ? 'year' : 'month'}
              </span>
            </div>

            {subscription.trial_end && (
              <div className="flex justify-between">
                <span className="text-gray-500">Trial Ends</span>
                <span className="font-medium">{formatDate(subscription.trial_end)}</span>
              </div>
            )}

            <div className="flex justify-between">
              <span className="text-gray-500">Current Period</span>
              <span className="font-medium">
                {formatDate(subscription.current_period_start)} - {formatDate(subscription.current_period_end)}
              </span>
            </div>

            {subscription.cancel_at_period_end && (
              <div className="flex justify-between text-red-600">
                <span>Cancels On</span>
                <span className="font-medium">{formatDate(subscription.current_period_end)}</span>
              </div>
            )}
          </div>
        </div>

        <div>
          <h3 className="text-lg font-medium mb-4">Payment Method</h3>

          {subscription.last_four ? (
            <div className="space-y-3 text-sm">
              <div className="flex items-center gap-2">
                <span className="font-medium">
                  {subscription.card_brand ? subscription.card_brand.charAt(0).toUpperCase() + subscription.card_brand.slice(1) : 'Card'} ending in {subscription.last_four}
                </span>
              </div>

              <Button variant="outline" onClick={onManagePayment} className="mt-2">
                Manage Payment Method
              </Button>
            </div>
          ) : (
            <div className="text-sm text-gray-500">
              <p>No payment method on file.</p>
              <Button variant="outline" onClick={onManagePayment} className="mt-2">
                Add Payment Method
              </Button>
            </div>
          )}
        </div>
      </div>

      <div className="border-t pt-6 flex flex-wrap gap-3 justify-end">
        {subscription.status === 'active' && !subscription.cancel_at_period_end && (
          <Button variant="outline" onClick={onCancel}>
            Cancel Subscription
          </Button>
        )}

        {subscription.cancel_at_period_end && (
          <Button variant="outline" onClick={onReactivate}>
            Resume Subscription
          </Button>
        )}

        <Button variant="secondary" onClick={onManagePayment}>
          Manage Billing
        </Button>
      </div>
    </Card>
  );
};

export default SubscriptionDetails;
