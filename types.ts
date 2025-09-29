
export interface DetectionResult {
  id: number;
  timestamp: string;
  src_ip: string;
  host: string;
  uri: string;
  attack_prediction: 'Benign' | 'SQLi' | 'XSS' | 'CMD Injection' | 'Directory Traversal' | 'Web Shell' | 'Credential Stuffing' | 'SSRF' | 'LFI/RFI';
  confidence: number;
  rule_matched: string | null;
  success_flag: boolean;
}

export interface AnalysisSummary {
  count: number;
  results: DetectionResult[];
}

export interface FilterState {
  ip: string;
  attack_type: string;
  confidence: number;
}
