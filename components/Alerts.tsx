import React from 'react';
import type { Alert } from '../types';
import { BellIcon, XIcon } from './icons';

interface AlertsContainerProps {
  alerts: Alert[];
  onDismiss: (id: string) => void;
}

export const AlertsContainer: React.FC<AlertsContainerProps> = ({ alerts, onDismiss }) => {
  if (alerts.length === 0) {
    return null;
  }

  return (
    <div
      aria-live="polite"
      aria-atomic="true"
      className="fixed top-20 right-4 z-50 w-full max-w-sm space-y-3"
    >
      {alerts.map((alert) => (
        <div
          key={alert.id}
          role="alert"
          className="relative w-full p-4 pr-10 overflow-hidden text-white bg-red-800 border border-red-600 rounded-lg shadow-2xl animate-fade-in-right"
        >
          <div className="flex items-start">
            <div className="flex-shrink-0">
              <BellIcon className="w-6 h-6 text-red-300" />
            </div>
            <div className="ml-3">
              <h4 className="font-bold">High-Severity Alert</h4>
              <p className="text-sm text-red-200">
                <strong className="font-semibold">{alert.detection.attack_prediction}</strong> detected from IP: 
                <span className="font-mono ml-1">{alert.detection.src_ip}</span>
              </p>
            </div>
            <button
              onClick={() => onDismiss(alert.id)}
              aria-label="Dismiss alert"
              className="absolute top-2 right-2 p-1 text-red-300 rounded-md hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-white"
            >
              <XIcon className="w-5 h-5" />
            </button>
          </div>
        </div>
      ))}
    </div>
  );
};