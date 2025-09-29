import React, { useState, useCallback } from 'react';
import { analyzePcap, analyzeHttpLog } from '../services/api';
import type { AnalysisSummary } from '../types';
import { UploadCloudIcon, AlertTriangleIcon, LoaderIcon } from './icons';

interface FileUploadProps {
  onAnalysisStart: () => void;
  onAnalysisSuccess: (summary: AnalysisSummary) => void;
  onAnalysisError: (error: string) => void;
  isLoading: boolean;
  error: string | null;
}

export const FileUpload: React.FC<FileUploadProps> = ({
  onAnalysisStart,
  onAnalysisSuccess,
  onAnalysisError,
  isLoading,
  error,
}) => {
  const [file, setFile] = useState<File | null>(null);
  const [isDragOver, setIsDragOver] = useState(false);
  const [uploadType, setUploadType] = useState<'pcap' | 'log'>('pcap');

  const handleUploadTypeChange = (type: 'pcap' | 'log') => {
    if (isLoading) return;
    setUploadType(type);
    setFile(null); // Reset file selection
    onAnalysisError(''); // Clear errors
  };

  const handleFileChange = (selectedFile: File | null) => {
    if (selectedFile) {
      const isPcap = uploadType === 'pcap' && (selectedFile.name.endsWith('.pcap') || selectedFile.name.endsWith('.pcapng'));
      const isLog = uploadType === 'log' && (selectedFile.name.endsWith('.csv') || selectedFile.name.endsWith('.json'));

      if (isPcap || isLog) {
        setFile(selectedFile);
        onAnalysisError(""); // Clear error on valid file
      } else {
        const expected = uploadType === 'pcap' ? '.pcap or .pcapng' : '.csv or .json';
        onAnalysisError(`Invalid file type. Please upload a ${expected} file.`);
        setFile(null);
      }
    }
  };

  const handleDragEvents = (e: React.DragEvent<HTMLDivElement>, over: boolean) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragOver(over);
  };
  
  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    handleDragEvents(e, false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileChange(e.dataTransfer.files[0]);
    }
  };

  const handleSubmit = useCallback(async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file || isLoading) return;

    onAnalysisStart();
    try {
      const summary = uploadType === 'pcap' 
        ? await analyzePcap(file) 
        : await analyzeHttpLog(file);
      onAnalysisSuccess(summary);
    } catch (err) {
      onAnalysisError(err instanceof Error ? err.message : 'An unknown error occurred.');
    }
  }, [file, isLoading, onAnalysisStart, onAnalysisSuccess, onAnalysisError, uploadType]);

  const pcapTabClasses = `px-6 py-3 text-sm font-medium rounded-t-lg transition-colors duration-200 focus:outline-none ${uploadType === 'pcap' ? 'bg-surface text-accent' : 'text-text-secondary bg-primary hover:bg-surface'}`;
  const logTabClasses = `px-6 py-3 text-sm font-medium rounded-t-lg transition-colors duration-200 focus:outline-none ${uploadType === 'log' ? 'bg-surface text-accent' : 'text-text-secondary bg-primary hover:bg-surface'}`;

  return (
    <div className="max-w-2xl mx-auto">
      <div className="flex">
          <button onClick={() => handleUploadTypeChange('pcap')} className={pcapTabClasses} disabled={isLoading}>
            Analyze PCAP
          </button>
          <button onClick={() => handleUploadTypeChange('log')} className={logTabClasses} disabled={isLoading}>
            Analyze HTTP Log
          </button>
      </div>
      <div className="bg-surface rounded-b-lg rounded-r-lg shadow-xl p-8">
        <h2 className="text-2xl font-bold text-center text-text-primary mb-2">Analyze Network Traffic</h2>
        <p className="text-center text-text-secondary mb-6">
          {uploadType === 'pcap' 
            ? 'Upload a PCAP file to run Zeek and detect URL-based attacks.'
            : 'Upload a pre-parsed Zeek HTTP log in CSV or JSON format.'}
        </p>
        
        <form onSubmit={handleSubmit}>
          <div
            onDragOver={(e) => handleDragEvents(e, true)}
            onDragLeave={(e) => handleDragEvents(e, false)}
            onDrop={handleDrop}
            className={`border-2 border-dashed rounded-lg p-10 text-center transition-colors duration-200 ${isDragOver ? 'border-accent bg-primary' : 'border-secondary'}`}
          >
            <input
              type="file"
              id="file-upload"
              className="hidden"
              onChange={(e) => handleFileChange(e.target.files ? e.target.files[0] : null)}
              accept={uploadType === 'pcap' ? '.pcap,.pcapng' : '.csv,.json'}
              disabled={isLoading}
            />
            <label htmlFor="file-upload" className={isLoading ? 'cursor-not-allowed' : 'cursor-pointer'}>
              <UploadCloudIcon className="w-16 h-16 mx-auto text-secondary" />
              <p className="mt-4 text-text-primary">
                <span className="font-semibold text-accent">Click to upload</span> or drag and drop
              </p>
              <p className="text-xs text-text-secondary mt-1">
                {uploadType === 'pcap' ? 'PCAP or PCAPNG files' : 'CSV or JSON log files'}
              </p>
            </label>
          </div>
          
          {file && (
            <div className="mt-4 text-center text-text-secondary">
              Selected file: <span className="font-semibold text-text-primary">{file.name}</span>
            </div>
          )}
          
          {error && (
              <div className="mt-4 flex items-center justify-center p-3 bg-red-900/50 border border-red-500 text-red-300 rounded-md">
                  <AlertTriangleIcon className="w-5 h-5 mr-2" />
                  <span>{error}</span>
              </div>
          )}

          <div className="mt-6">
            <button
              type="submit"
              disabled={!file || isLoading}
              className="w-full bg-accent hover:bg-teal-500 disabled:bg-primary disabled:cursor-not-allowed text-white font-bold py-3 px-4 rounded-lg transition-all duration-300 flex items-center justify-center"
            >
              {isLoading ? (
                <>
                  <LoaderIcon className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" />
                  Analyzing...
                </>
              ) : (
                'Start Analysis'
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};