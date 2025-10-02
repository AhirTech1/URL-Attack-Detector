export interface DetectionResult {
  id: number;
  timestamp: string;
  src_ip: string;
  dst_ip?: string;
  host: string;
  uri: string;
  method?: string;
  attack_prediction: 'Benign' | 'SQLi' | 'XSS' | 'CMD Injection' | 'Directory Traversal' | 'Web Shell' | 'Credential Stuffing' | 'SSRF' | 'LFI/RFI' | 'Typosquatting' | 'HTTP Parameter Pollution' | 'XXE';
  confidence: number;
  rule_matched: string | null;
  success_flag: boolean;
  features?: {
    url_length?: number;
    num_special_chars?: number;
    entropy?: number;
  };
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

export interface Alert {
  id: string;
  detection: DetectionResult;
}