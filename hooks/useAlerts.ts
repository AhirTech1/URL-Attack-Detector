import { useState, useCallback } from 'react';
import type { Alert, DetectionResult } from '../types';

const AUTO_DISMISS_DELAY = 10000; // 10 seconds

export const useAlerts = () => {
  const [alerts, setAlerts] = useState<Alert[]>([]);

  const dismissAlert = useCallback((id: string) => {
    setAlerts(currentAlerts => currentAlerts.filter(alert => alert.id !== id));
  }, []);

  const addAlert = useCallback((detection: DetectionResult) => {
    const id = `${new Date().getTime()}-${detection.id}`;
    const newAlert: Alert = { id, detection };

    setAlerts(currentAlerts => [newAlert, ...currentAlerts]);

    setTimeout(() => {
      dismissAlert(id);
    }, AUTO_DISMISS_DELAY);
  }, [dismissAlert]);

  return { alerts, addAlert, dismissAlert };
};
