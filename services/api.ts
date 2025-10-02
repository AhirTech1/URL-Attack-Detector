import type { DetectionResult, AnalysisSummary, FilterState } from '../types';

// API Configuration
const API_BASE_URL = 'http://localhost:5000/api';

// Current analysis ID
let currentAnalysisId: string | null = null;

export const analyzePcap = async (file: File): Promise<AnalysisSummary> => {
  console.log(`Analyzing PCAP file: ${file.name}...`);
  
  const formData = new FormData();
  formData.append('file', file);

  try {
    const response = await fetch(`${API_BASE_URL}/analyze/pcap`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || 'PCAP analysis failed');
    }

    const data = await response.json();
    currentAnalysisId = data.analysis_id;
    
    return {
      count: data.count,
      results: data.results
    };
  } catch (error) {
    console.error('Error analyzing PCAP:', error);
    throw error;
  }
};

export const analyzeHttpLog = async (file: File): Promise<AnalysisSummary> => {
  console.log(`Analyzing HTTP log: ${file.name}...`);
  
  const formData = new FormData();
  formData.append('file', file);

  try {
    const response = await fetch(`${API_BASE_URL}/analyze/log`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || 'Log analysis failed');
    }

    const data = await response.json();
    currentAnalysisId = data.analysis_id;
    
    return {
      count: data.count,
      results: data.results
    };
  } catch (error) {
    console.error('Error analyzing log:', error);
    throw error;
  }
};

export const getResults = async (filters: FilterState, offset: number = 0, limit: number = 20): Promise<DetectionResult[]> => {
  if (!currentAnalysisId) {
    throw new Error('No analysis in progress');
  }

  console.log('Fetching results with filters:', filters, 'offset:', offset, 'limit:', limit);

  try {
    const params = new URLSearchParams({
      offset: offset.toString(),
      limit: limit.toString(),
    });

    if (filters.ip) params.append('ip', filters.ip);
    if (filters.attack_type && filters.attack_type !== 'All') {
      params.append('attack_type', filters.attack_type);
    }
    if (filters.confidence > 0) {
      params.append('confidence', filters.confidence.toString());
    }

    const response = await fetch(`${API_BASE_URL}/results/${currentAnalysisId}?${params}`);

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || 'Failed to fetch results');
    }

    const data = await response.json();
    return data.results;
  } catch (error) {
    console.error('Error fetching results:', error);
    throw error;
  }
};

export const downloadResults = async (format: 'csv' | 'json'): Promise<void> => {
  if (!currentAnalysisId) {
    throw new Error('No analysis in progress');
  }

  console.log(`Downloading results in ${format} format...`);

  try {
    const response = await fetch(`${API_BASE_URL}/export/${currentAnalysisId}/${format}`);

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || 'Export failed');
    }

    // Download file
    const blob = await response.blob();
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `analysis_${currentAnalysisId}.${format}`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  } catch (error) {
    console.error('Error downloading results:', error);
    throw error;
  }
};

export const checkHealth = async (): Promise<boolean> => {
  try {
    const response = await fetch(`${API_BASE_URL}/health`);
    return response.ok;
  } catch (error) {
    console.error('Health check failed:', error);
    return false;
  }
};