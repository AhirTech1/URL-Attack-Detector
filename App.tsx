
import React, { useState } from 'react';
import { FileUpload } from './components/FileUpload';
import { Dashboard } from './components/Dashboard';
import { Header } from './components/Header';
import type { DetectionResult, AnalysisSummary } from './types';

const App: React.FC = () => {
  const [analysisSummary, setAnalysisSummary] = useState<AnalysisSummary | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [analysisId, setAnalysisId] = useState<string | null>(null);

  const handleAnalysisSuccess = (summary: AnalysisSummary) => {
    setAnalysisSummary(summary);
    setAnalysisId(new Date().toISOString()); // Use timestamp as a unique ID for re-fetching
    setIsLoading(false);
    setError(null);
  };

  const handleAnalysisStart = () => {
    setIsLoading(true);
    setError(null);
    setAnalysisSummary(null);
  };

  const handleAnalysisError = (errorMessage: string) => {
    setError(errorMessage);
    setIsLoading(false);
  };

  const handleNewAnalysis = () => {
    setAnalysisSummary(null);
    setAnalysisId(null);
  };

  return (
    <div className="min-h-screen bg-background font-sans">
      <Header />
      <main className="container mx-auto p-4 md:p-8">
        {!analysisId ? (
          <FileUpload
            onAnalysisStart={handleAnalysisStart}
            onAnalysisSuccess={handleAnalysisSuccess}
            onAnalysisError={handleAnalysisError}
            isLoading={isLoading}
            error={error}
          />
        ) : (
          <Dashboard
            key={analysisId}
            initialSummary={analysisSummary}
            onNewAnalysis={handleNewAnalysis}
          />
        )}
      </main>
    </div>
  );
};

export default App;
