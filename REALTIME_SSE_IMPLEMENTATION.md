"""
Real implementation of realtime.ts using Server-Sent Events
Replace the mock implementation in services/realtime.ts with this
"""
import type { DetectionResult } from '../types';

const API_BASE_URL = 'http://localhost:5000/api';

export const realtimeService = {
  connect: (onAlert: (result: DetectionResult) => void): (() => void) => {
    console.log('Real-time alert service connecting to backend...');
    
    let eventSource: EventSource | null = null;
    
    try {
      // Connect to SSE endpoint
      eventSource = new EventSource(`${API_BASE_URL}/stream/alerts`);
      
      eventSource.onopen = () => {
        console.log('✅ Real-time alert service connected to backend.');
      };
      
      eventSource.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          
          // Handle connection message
          if (data.type === 'connected') {
            console.log('Backend streaming ready');
            return;
          }
          
          // Handle detection alert
          console.log('🚨 High-severity attack detected:', data);
          onAlert(data as DetectionResult);
          
        } catch (error) {
          console.error('Error parsing SSE message:', error);
        }
      };
      
      eventSource.onerror = (error) => {
        console.error('❌ SSE connection error:', error);
        // Will auto-reconnect
      };
      
    } catch (error) {
      console.error('Failed to create EventSource:', error);
    }
    
    // Return disconnect function
    const disconnect = () => {
      if (eventSource) {
        eventSource.close();
        eventSource = null;
        console.log('Real-time alert service disconnected.');
      }
    };
    
    return disconnect;
  },
};
