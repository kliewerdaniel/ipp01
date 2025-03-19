'use client';

import React from 'react';
import { Button } from '@/components/ui/Button';

interface BillingHistoryItem {
  id: string;
  event_type: string;
  description: string | null;
  event_time: string;
  amount: number | null;
  currency: string | null;
  payment_status: string | null;
  invoice_url: string | null;
  receipt_url: string | null;
}

interface BillingHistoryProps {
  items: BillingHistoryItem[];
}

const BillingHistory: React.FC<BillingHistoryProps> = ({ items }) => {
  // Format date helper
  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    });
  };

  // Format currency helper
  const formatCurrency = (amount: number | null, currency: string | null) => {
    if (amount === null || currency === null) return 'N/A';
    
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: currency.toUpperCase(),
    }).format(amount);
  };

  // Get status badge color
  const getStatusColor = (status: string | null) => {
    if (!status) return 'bg-gray-100 text-gray-800';
    
    switch (status.toLowerCase()) {
      case 'completed':
      case 'succeeded':
        return 'bg-green-100 text-green-800';
      case 'pending':
        return 'bg-yellow-100 text-yellow-800';
      case 'failed':
        return 'bg-red-100 text-red-800';
      case 'refunded':
        return 'bg-purple-100 text-purple-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  // Get event type display name
  const getEventTypeName = (eventType: string) => {
    // Convert snake_case to Title Case with spaces
    const name = eventType
      .split('_')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
      .join(' ');
    
    return name;
  };

  if (items.length === 0) {
    return (
      <div className="text-center py-10 text-gray-500">
        <p>No billing history available.</p>
      </div>
    );
  }

  return (
    <div className="overflow-x-auto">
      <table className="min-w-full divide-y divide-gray-200">
        <thead className="bg-gray-50">
          <tr>
            <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Date
            </th>
            <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Description
            </th>
            <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Amount
            </th>
            <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Status
            </th>
            <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Receipt
            </th>
          </tr>
        </thead>
        <tbody className="bg-white divide-y divide-gray-200">
          {items.map((item) => (
            <tr key={item.id}>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {formatDate(item.event_time)}
              </td>
              <td className="px-6 py-4 text-sm text-gray-900">
                <div className="font-medium">{getEventTypeName(item.event_type)}</div>
                {item.description && <div className="text-gray-500 text-xs mt-1">{item.description}</div>}
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {item.amount !== null ? formatCurrency(item.amount, item.currency) : '—'}
              </td>
              <td className="px-6 py-4 whitespace-nowrap">
                {item.payment_status && (
                  <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${getStatusColor(item.payment_status)}`}>
                    {item.payment_status.charAt(0).toUpperCase() + item.payment_status.slice(1)}
                  </span>
                )}
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {(item.invoice_url || item.receipt_url) && (
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => {
                      const url = item.receipt_url || item.invoice_url;
                      if (url) window.open(url, '_blank');
                    }}
                  >
                    View
                  </Button>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default BillingHistory;
