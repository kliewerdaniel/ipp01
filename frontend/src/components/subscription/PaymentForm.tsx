'use client';

import React, { useState } from 'react';
import { Button } from '@/components/ui/Button';

export interface PaymentMethod {
  id: string;
  type: 'card' | 'paypal';
  cardBrand?: string;
  last4?: string;
  expiryMonth?: number;
  expiryYear?: number;
  isDefault?: boolean;
}

interface PaymentFormProps {
  onSubmit: (paymentDetails: any) => Promise<void>;
  onCancel: () => void;
  processingPayment: boolean;
  existingPaymentMethods?: PaymentMethod[];
  onSelectExistingMethod?: (methodId: string) => void;
  planName: string;
  amount: number;
  billingCycle: 'monthly' | 'yearly';
  currency?: string;
}

const PaymentForm: React.FC<PaymentFormProps> = ({
  onSubmit,
  onCancel,
  processingPayment,
  existingPaymentMethods = [],
  onSelectExistingMethod,
  planName,
  amount,
  billingCycle,
  currency = 'USD',
}) => {
  const [paymentMethod, setPaymentMethod] = useState<'new-card' | 'existing-card' | 'paypal'>(
    existingPaymentMethods.length > 0 ? 'existing-card' : 'new-card'
  );
  const [selectedMethodId, setSelectedMethodId] = useState<string>(
    existingPaymentMethods.find(m => m.isDefault)?.id || ''
  );
  
  const [cardDetails, setCardDetails] = useState({
    name: '',
    number: '',
    expiry: '',
    cvc: '',
  });
  
  const [errors, setErrors] = useState<Record<string, string>>({});

  const formatPrice = (amount: number): string => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency,
      minimumFractionDigits: 2,
    }).format(amount / 100);
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    
    // Basic input formatting
    if (name === 'number') {
      // Remove non-digits and add spaces every 4 digits
      const formatted = value.replace(/\D/g, '').replace(/(\d{4})(?=\d)/g, '$1 ');
      setCardDetails({ ...cardDetails, [name]: formatted.substring(0, 19) });
    } else if (name === 'expiry') {
      // Format as MM/YY
      const digits = value.replace(/\D/g, '');
      let formatted = digits;
      if (digits.length > 2) {
        formatted = `${digits.substring(0, 2)}/${digits.substring(2, 4)}`;
      }
      setCardDetails({ ...cardDetails, [name]: formatted });
    } else if (name === 'cvc') {
      // Allow only digits, max 4
      setCardDetails({ ...cardDetails, [name]: value.replace(/\D/g, '').substring(0, 4) });
    } else {
      setCardDetails({ ...cardDetails, [name]: value });
    }
    
    // Clear error for this field
    if (errors[name]) {
      const newErrors = { ...errors };
      delete newErrors[name];
      setErrors(newErrors);
    }
  };

  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {};
    
    if (paymentMethod === 'new-card') {
      if (!cardDetails.name) newErrors.name = 'Name is required';
      if (!cardDetails.number || cardDetails.number.replace(/\s/g, '').length < 16) {
        newErrors.number = 'Valid card number is required';
      }
      if (!cardDetails.expiry || !cardDetails.expiry.includes('/') || cardDetails.expiry.length < 5) {
        newErrors.expiry = 'Valid expiry date (MM/YY) is required';
      } else {
        const [month, year] = cardDetails.expiry.split('/');
        const currentYear = new Date().getFullYear() % 100;
        const currentMonth = new Date().getMonth() + 1;
        
        if (parseInt(year) < currentYear || (parseInt(year) === currentYear && parseInt(month) < currentMonth)) {
          newErrors.expiry = 'Card has expired';
        }
      }
      if (!cardDetails.cvc || cardDetails.cvc.length < 3) {
        newErrors.cvc = 'Valid security code is required';
      }
    } else if (paymentMethod === 'existing-card' && !selectedMethodId) {
      newErrors.method = 'Please select a payment method';
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) return;
    
    try {
      if (paymentMethod === 'existing-card' && onSelectExistingMethod && selectedMethodId) {
        onSelectExistingMethod(selectedMethodId);
      } else {
        await onSubmit({
          paymentMethod,
          ...(paymentMethod === 'new-card' ? { cardDetails } : {}),
        });
      }
    } catch (error) {
      console.error('Payment error:', error);
      setErrors({ submit: 'Payment failed. Please try again.' });
    }
  };

  // Helper to display card brand icon
  const getCardIcon = (brand?: string) => {
    switch (brand?.toLowerCase()) {
      case 'visa':
        return '💳 Visa';
      case 'mastercard':
        return '💳 Mastercard';
      case 'amex':
        return '💳 American Express';
      case 'discover':
        return '💳 Discover';
      default:
        return '💳 Card';
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <div className="mb-6">
        <h2 className="text-xl font-bold text-gray-800 mb-1">Payment Details</h2>
        <p className="text-gray-600">
          Subscribe to {planName} ({formatPrice(amount)}/{billingCycle})
        </p>
      </div>

      <form onSubmit={handleSubmit}>
        {/* Payment Method Selection */}
        <div className="mb-6">
          <label className="block text-sm font-medium text-gray-700 mb-2">Payment Method</label>
          <div className="space-y-2">
            {existingPaymentMethods.length > 0 && (
              <label className="flex items-center">
                <input
                  type="radio"
                  className="h-4 w-4 text-blue-600"
                  checked={paymentMethod === 'existing-card'}
                  onChange={() => setPaymentMethod('existing-card')}
                />
                <span className="ml-2 text-gray-700">Use saved payment method</span>
              </label>
            )}
            
            <label className="flex items-center">
              <input
                type="radio"
                className="h-4 w-4 text-blue-600"
                checked={paymentMethod === 'new-card'}
                onChange={() => setPaymentMethod('new-card')}
              />
              <span className="ml-2 text-gray-700">Use a new card</span>
            </label>
            
            <label className="flex items-center">
              <input
                type="radio"
                className="h-4 w-4 text-blue-600"
                checked={paymentMethod === 'paypal'}
                onChange={() => setPaymentMethod('paypal')}
              />
              <span className="ml-2 text-gray-700">Pay with PayPal</span>
            </label>
          </div>
          {errors.method && <p className="mt-1 text-sm text-red-600">{errors.method}</p>}
        </div>

        {/* Existing Cards Selection */}
        {paymentMethod === 'existing-card' && existingPaymentMethods.length > 0 && (
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Select a card
            </label>
            <div className="space-y-2">
              {existingPaymentMethods.map((method) => (
                <label key={method.id} className="flex items-center p-3 border rounded-md cursor-pointer hover:bg-gray-50">
                  <input
                    type="radio"
                    className="h-4 w-4 text-blue-600"
                    checked={selectedMethodId === method.id}
                    onChange={() => setSelectedMethodId(method.id)}
                  />
                  <div className="ml-3">
                    <p className="text-sm font-medium text-gray-700">
                      {getCardIcon(method.cardBrand)} •••• {method.last4}
                    </p>
                    <p className="text-xs text-gray-500">
                      Expires {method.expiryMonth}/{method.expiryYear}
                      {method.isDefault && <span className="ml-2 text-blue-600">Default</span>}
                    </p>
                  </div>
                </label>
              ))}
            </div>
          </div>
        )}

        {/* New Card Details */}
        {paymentMethod === 'new-card' && (
          <div className="space-y-4">
            <div>
              <label htmlFor="name" className="block text-sm font-medium text-gray-700">
                Name on Card
              </label>
              <input
                type="text"
                id="name"
                name="name"
                className={`mt-1 block w-full px-3 py-2 border ${
                  errors.name ? 'border-red-300' : 'border-gray-300'
                } rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500`}
                placeholder="John Smith"
                value={cardDetails.name}
                onChange={handleInputChange}
              />
              {errors.name && (
                <p className="mt-1 text-sm text-red-600">{errors.name}</p>
              )}
            </div>

            <div>
              <label htmlFor="number" className="block text-sm font-medium text-gray-700">
                Card Number
              </label>
              <input
                type="text"
                id="number"
                name="number"
                className={`mt-1 block w-full px-3 py-2 border ${
                  errors.number ? 'border-red-300' : 'border-gray-300'
                } rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500`}
                placeholder="1234 5678 9012 3456"
                value={cardDetails.number}
                onChange={handleInputChange}
              />
              {errors.number && (
                <p className="mt-1 text-sm text-red-600">{errors.number}</p>
              )}
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label htmlFor="expiry" className="block text-sm font-medium text-gray-700">
                  Expiry Date
                </label>
                <input
                  type="text"
                  id="expiry"
                  name="expiry"
                  className={`mt-1 block w-full px-3 py-2 border ${
                    errors.expiry ? 'border-red-300' : 'border-gray-300'
                  } rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500`}
                  placeholder="MM/YY"
                  value={cardDetails.expiry}
                  onChange={handleInputChange}
                />
                {errors.expiry && (
                  <p className="mt-1 text-sm text-red-600">{errors.expiry}</p>
                )}
              </div>

              <div>
                <label htmlFor="cvc" className="block text-sm font-medium text-gray-700">
                  Security Code
                </label>
                <input
                  type="text"
                  id="cvc"
                  name="cvc"
                  className={`mt-1 block w-full px-3 py-2 border ${
                    errors.cvc ? 'border-red-300' : 'border-gray-300'
                  } rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500`}
                  placeholder="CVC"
                  value={cardDetails.cvc}
                  onChange={handleInputChange}
                />
                {errors.cvc && (
                  <p className="mt-1 text-sm text-red-600">{errors.cvc}</p>
                )}
              </div>
            </div>

            <div className="flex items-center">
              <input
                id="save-card"
                name="save-card"
                type="checkbox"
                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
              />
              <label htmlFor="save-card" className="ml-2 block text-sm text-gray-700">
                Save this card for future payments
              </label>
            </div>
          </div>
        )}

        {/* PayPal Info */}
        {paymentMethod === 'paypal' && (
          <div className="bg-gray-50 p-4 rounded-md text-center mb-6">
            <p className="text-sm text-gray-600 mb-2">
              You will be redirected to PayPal to complete your payment
            </p>
            <div className="flex justify-center">
              <svg className="h-10" viewBox="0 0 101 32" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M12.9 4.858H5.943c-.475 0-.95.348-1.069.823L1.069 25.256c-.119.475.119.823.475.823h3.208c.475 0 .95-.348 1.069-.823l.95-6.057c.119-.475.475-.823 1.069-.823h2.258c5.109 0 8.079-2.496 8.792-7.37.356-2.14 0-3.79-.95-4.969-1.188-1.298-3.089-1.773-5.941-1.18zm.95 7.252c-.394 2.732-2.495 2.732-4.516 2.732h-1.188l.831-5.227c.119-.237.237-.475.594-.475h.475c1.366 0 2.734 0 3.447.823.475.467.594 1.291.356 2.147zm18.425-.592h-3.209c-.356 0-.594.118-.594.474l-.119.475-2.377-3.435c-.356.118-.713.237-1.069.356-1.782.592-3.684.474-4.991-.356-1.307-.823-2.02-2.377-1.663-4.27 0-4.873 3.802-7.37 7.25-7.37 2.139 0 3.803.593 4.991 1.774 1.188 1.18 1.544 2.732 1.188 4.624-.356 1.773-1.307 3.19-2.377 4.132.119.119.119.237.238.356.594.83 1.069 1.654.712 2.72m-5.227-7.251c-.119 1.062-.95 2.496-2.971 2.496-1.425 0-2.495-.83-2.376-2.378 0-1.535 1.069-2.613 2.732-2.613 1.544 0 2.733.949 2.615 2.495zm18.187-.712h-3.208c-.357 0-.594.118-.713.474l-1.9 12.115a.724.724 0 0 0-.119.474c0 .237.238.474.475.474h2.971c.356 0 .594-.237.594-.474l1.9-12.115c.119-.237-.118-.474-.356-.474-.237-.119-.475-.119-.644-.474zm15.929 0h-3.209c-.356 0-.594.118-.594.474l-.118.474-2.378-3.435c-.356.119-.713.237-1.069.356-1.781.593-3.684.475-4.991-.356-1.306-.823-2.02-2.377-1.663-4.27 0-4.872 3.803-7.37 7.251-7.37 2.138 0 3.802.593 4.991 1.774 1.188 1.18 1.544 2.732 1.188 4.624-.357 1.773-1.307 3.19-2.377 4.132.118.119.118.237.237.356.594.83 1.069 1.654.712 2.72l.03-.48zm-5.227-7.251c-.119 1.062-.95 2.496-2.971 2.496-1.425 0-2.496-.83-2.377-2.378 0-1.535 1.07-2.613 2.733-2.613 1.544 0 2.733.949 2.615 2.495zm18.187-.712h-3.209c-.356 0-.594.118-.594.474l-1.9 12.115a.723.723 0 0 0-.119.474c0 .237.238.474.476.474h3.208c.475 0 .95-.348 1.069-.823L80.4 5.8l.119-.475c0-.356-.238-.474-.476-.474-.237-.118-.475-.118-.644-.355zM88.36 4.858h-9.509c-.475 0-.95.348-1.069.823L74.1 25.37c-.119.475.119.823.476.823h3.208c.475 0 .95-.348 1.069-.823l.95-6.057c.118-.475.475-.823 1.069-.823h2.257c5.109 0 8.079-2.495 8.792-7.37.357-2.14 0-3.788-.95-4.968-1.186-1.299-3.087-1.774-5.94-1.18L88.36 4.86zm.95 7.252c-.396 2.733-2.496 2.733-4.516 2.733H83.608l.83-5.228c.12-.237.239-.475.595-.475h.475c1.366 0 2.733 0 3.447.824.356.474.594 1.297.356 2.146zm11.587 6.888c-.12.474.118.823.474.823h3.09c.475 0 .95-.349 1.069-.823L99.76 5.444a.724.724 0 0 0-.119-.474c0-.237-.237-.474-.474-.474h-3.209c-.356 0-.594.237-.594.474l-4.516 13.028z" fill="#253b80"/>
              </svg>
            </div>
          </div>
        )}

        {/* General Error */}
        {errors.submit && (
          <div className="mb-4 p-2 bg-red-50 border border-red-200 rounded text-red-600 text-sm">
            {errors.submit}
          </div>
        )}

        {/* Terms and Conditions */}
        <div className="mt-6 mb-6 text-xs text-gray-500">
          By subscribing, you agree to our{' '}
          <a href="#" className="text-blue-600 hover:underline">Terms of Service</a> and{' '}
          <a href="#" className="text-blue-600 hover:underline">Privacy Policy</a>.
          You can cancel your subscription at any time.
        </div>

        {/* Action Buttons */}
        <div className="flex justify-end space-x-3">
          <Button
            type="button"
            variant="outline"
            onClick={onCancel}
            disabled={processingPayment}
          >
            Cancel
          </Button>
          <Button
            type="submit"
            disabled={processingPayment}
            isLoading={processingPayment}
          >
            {processingPayment ? 'Processing...' : 'Complete Payment'}
          </Button>
        </div>
      </form>
    </div>
  );
};

export default PaymentForm;
