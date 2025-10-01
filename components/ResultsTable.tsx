
import React, { useState, useEffect, useCallback, Fragment } from 'react';
import { getResults } from '../services/api';
import type { DetectionResult, FilterState } from '../types';
import { LoaderIcon, AlertTriangleIcon } from './icons';
import { DetectionDetails } from './DetectionDetails';

interface ResultsTableProps {
    filters: FilterState;
}

const ROWS_PER_PAGE = 15;

export const ResultsTable: React.FC<ResultsTableProps> = ({ filters }) => {
  const [results, setResults] = useState<DetectionResult[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [currentPage, setCurrentPage] = useState(1);
  const [hasMore, setHasMore] = useState(true);
  const [expandedRowId, setExpandedRowId] = useState<number | null>(null);
  
  const fetchAndSetResults = useCallback(async (page: number) => {
    setIsLoading(true);
    setError(null);
    try {
      const offset = (page - 1) * ROWS_PER_PAGE;
      const newResults = await getResults(filters, offset, ROWS_PER_PAGE);
      setResults(newResults);
      setHasMore(newResults.length === ROWS_PER_PAGE);
    } catch (err) {
      setError('Failed to load detection results.');
    } finally {
      setIsLoading(false);
    }
  }, [filters]);
  
  useEffect(() => {
    setCurrentPage(1);
    setExpandedRowId(null); // Collapse any open row when filters change
    fetchAndSetResults(1);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [filters]);

  const handlePageChange = (newPage: number) => {
    if (newPage < 1) return;
    setCurrentPage(newPage);
    setExpandedRowId(null); // Collapse any open row when page changes
    fetchAndSetResults(newPage);
  }

  const getConfidenceColor = (confidence: number) => {
    if (confidence > 0.8) return 'text-red-400';
    if (confidence > 0.6) return 'text-orange-400';
    if (confidence > 0.4) return 'text-yellow-400';
    return 'text-green-400';
  }

  const truncateUri = (uri: string, length: number = 50) => {
    if (uri.length <= length) return uri;
    return uri.substring(0, length) + '...';
  }

  return (
    <div>
        <h3 className="text-xl font-semibold mb-4 text-text-primary">Detection Results</h3>
        <div className="overflow-x-auto">
            <table className="min-w-full">
                <thead className="bg-primary">
                    <tr>
                        {['Timestamp', 'Source IP', 'Host', 'URI', 'Attack Type', 'Confidence', 'Rule', 'Success'].map(header => (
                            <th key={header} scope="col" className="px-6 py-3 text-left text-xs font-medium text-text-secondary uppercase tracking-wider">{header}</th>
                        ))}
                    </tr>
                </thead>
                <tbody className="bg-surface divide-y divide-primary">
                    {isLoading && (
                        <tr><td colSpan={8} className="text-center p-8"><LoaderIcon className="w-8 h-8 animate-spin text-accent mx-auto" /></td></tr>
                    )}
                    {error && (
                        <tr><td colSpan={8} className="text-center p-8 text-red-400"><AlertTriangleIcon className="w-6 h-6 mx-auto mb-2" />{error}</td></tr>
                    )}
                    {!isLoading && !error && results.length === 0 && (
                        <tr><td colSpan={8} className="text-center p-8 text-text-secondary">No results found for the current filters.</td></tr>
                    )}
                    {!isLoading && !error && results.map((r) => (
                        <Fragment key={r.id}>
                            <tr
                              onClick={() => setExpandedRowId(expandedRowId === r.id ? null : r.id)}
                              className={`hover:bg-primary transition-colors duration-150 cursor-pointer ${expandedRowId === r.id ? 'bg-primary' : ''}`}
                            >
                                <td className="px-6 py-4 whitespace-nowrap text-sm text-text-secondary">{new Date(r.timestamp).toLocaleString()}</td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm font-mono text-text-primary">{r.src_ip}</td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm text-text-secondary">{r.host}</td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm font-mono text-text-secondary" title={r.uri}>{truncateUri(r.uri)}</td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm font-semibold">{r.attack_prediction === 'Benign' ? <span className="text-green-400">{r.attack_prediction}</span> : <span className="text-red-400">{r.attack_prediction}</span>}</td>
                                <td className={`px-6 py-4 whitespace-nowrap text-sm font-bold ${getConfidenceColor(r.confidence)}`}>{(r.confidence * 100).toFixed(1)}%</td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm">{r.rule_matched ? <span className="px-2 py-1 bg-yellow-800/50 text-yellow-300 rounded-full text-xs">{r.rule_matched}</span> : 'N/A'}</td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm">{r.success_flag ? <span className="text-red-400 font-bold">Yes</span> : 'No'}</td>
                            </tr>
                            {expandedRowId === r.id && (
                                <tr>
                                    <td colSpan={8} className="p-0">
                                        <DetectionDetails detection={r} />
                                    </td>
                                </tr>
                            )}
                        </Fragment>
                    ))}
                </tbody>
            </table>
        </div>
        <div className="flex justify-between items-center mt-4">
            <button
              onClick={() => handlePageChange(currentPage - 1)}
              disabled={currentPage === 1 || isLoading}
              className="px-4 py-2 bg-primary text-sm font-medium rounded-md disabled:opacity-50 disabled:cursor-not-allowed hover:bg-secondary transition"
            >
              Previous
            </button>
            <span className="text-sm text-text-secondary">Page {currentPage}</span>
            <button
              onClick={() => handlePageChange(currentPage + 1)}
              disabled={!hasMore || isLoading}
              className="px-4 py-2 bg-primary text-sm font-medium rounded-md disabled:opacity-50 disabled:cursor-not-allowed hover:bg-secondary transition"
            >
              Next
            </button>
        </div>
    </div>
  );
};
