
import React, { useState, useEffect, useCallback } from 'react';
import { Filters } from './Filters';
import { ResultsTable } from './ResultsTable';
import { AttackTypePieChart } from './charts/AttackTypePieChart';
import { TopAttackersBarChart } from './charts/TopAttackersBarChart';
import { AttackTimeline } from './charts/AttackTimeline';
import { getResults, downloadResults } from '../services/api';
import type { DetectionResult, AnalysisSummary, FilterState } from '../types';
import { LoaderIcon, DownloadIcon } from './icons';

interface DashboardProps {
  initialSummary: AnalysisSummary | null;
  onNewAnalysis: () => void;
}

export const Dashboard: React.FC<DashboardProps> = ({ initialSummary, onNewAnalysis }) => {
  const [results, setResults] = useState<DetectionResult[]>(initialSummary?.results || []);
  const [allFetchedResults, setAllFetchedResults] = useState<DetectionResult[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [isDownloading, setIsDownloading] = useState<false | 'csv' | 'json'>(false);
  const [error, setError] = useState<string | null>(null);
  const [filters, setFilters] = useState<FilterState>({
    ip: '',
    attack_type: 'All',
    confidence: 0,
  });

  const fetchAllResults = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      // In a real app, this would fetch all pages. Here we just fetch a larger dataset.
      const allData = await getResults(filters, 0, 1000); 
      setAllFetchedResults(allData);
    } catch (err) {
      setError('Failed to load full dataset for charts.');
    } finally {
      setIsLoading(false);
    }
  }, [filters]);

  useEffect(() => {
    fetchAllResults();
  }, [fetchAllResults]);

  const handleDownload = async (format: 'csv' | 'json') => {
    setIsDownloading(format);
    try {
      await downloadResults(format);
    } catch (err) {
      setError(`Failed to download ${format} file.`);
    } finally {
      setIsDownloading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-3xl font-bold">Analysis Dashboard</h2>
        <div className="flex space-x-2">
            <button
              onClick={() => handleDownload('csv')}
              disabled={!!isDownloading}
              className="bg-blue-600 hover:bg-blue-700 disabled:bg-primary text-white font-bold py-2 px-4 rounded-lg transition flex items-center"
            >
              {isDownloading === 'csv' ? <LoaderIcon className="animate-spin h-5 w-5 mr-2"/> : <DownloadIcon className="h-5 w-5 mr-2"/>}
              Export CSV
            </button>
            <button
              onClick={() => handleDownload('json')}
              disabled={!!isDownloading}
              className="bg-green-600 hover:bg-green-700 disabled:bg-primary text-white font-bold py-2 px-4 rounded-lg transition flex items-center"
            >
              {isDownloading === 'json' ? <LoaderIcon className="animate-spin h-5 w-5 mr-2"/> : <DownloadIcon className="h-5 w-5 mr-2"/>}
              Export JSON
            </button>
            <button onClick={onNewAnalysis} className="bg-secondary hover:bg-gray-600 text-white font-bold py-2 px-4 rounded-lg transition">
              New Analysis
            </button>
        </div>
      </div>
      
      <Filters filters={filters} onFilterChange={setFilters} />

      {isLoading && <div className="flex justify-center items-center p-8"><LoaderIcon className="w-8 h-8 animate-spin text-accent" /> <span className="ml-3">Loading Chart Data...</span></div>}
      {error && <p className="text-red-400 text-center">{error}</p>}
      
      {!isLoading && !error && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-1 bg-surface rounded-lg shadow-lg p-4"><AttackTypePieChart data={allFetchedResults} /></div>
          <div className="lg:col-span-2 bg-surface rounded-lg shadow-lg p-4"><TopAttackersBarChart data={allFetchedResults} /></div>
          <div className="lg:col-span-3 bg-surface rounded-lg shadow-lg p-4"><AttackTimeline data={allFetchedResults} /></div>
        </div>
      )}

      <div className="bg-surface rounded-lg shadow-lg p-4">
        <ResultsTable filters={filters} />
      </div>
    </div>
  );
};
