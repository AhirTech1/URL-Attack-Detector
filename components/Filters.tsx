
import React from 'react';
import type { FilterState } from '../types';

interface FiltersProps {
  filters: FilterState;
  onFilterChange: (newFilters: FilterState) => void;
}

const ATTACK_TYPES = ['All', 'SQLi', 'XSS', 'CMD Injection', 'Directory Traversal', 'Web Shell', 'Credential Stuffing', 'SSRF', 'LFI/RFI'];

export const Filters: React.FC<FiltersProps> = ({ filters, onFilterChange }) => {

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    onFilterChange({
      ...filters,
      [e.target.name]: e.target.value
    });
  };
  
  const handleSliderChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    onFilterChange({
      ...filters,
      confidence: parseInt(e.target.value, 10)
    });
  };

  return (
    <div className="bg-surface p-4 rounded-lg shadow-lg flex flex-col md:flex-row gap-4 items-center">
      <div className="w-full md:w-1/3">
        <label htmlFor="ip" className="block text-sm font-medium text-text-secondary mb-1">Source IP</label>
        <input
          type="text"
          id="ip"
          name="ip"
          value={filters.ip}
          onChange={handleInputChange}
          placeholder="e.g., 192.168.1.10"
          className="w-full bg-primary border border-secondary rounded-md p-2 text-text-primary focus:ring-accent focus:border-accent"
        />
      </div>
      <div className="w-full md:w-1/3">
        <label htmlFor="attack_type" className="block text-sm font-medium text-text-secondary mb-1">Attack Type</label>
        <select
          id="attack_type"
          name="attack_type"
          value={filters.attack_type}
          onChange={handleInputChange}
          className="w-full bg-primary border border-secondary rounded-md p-2 text-text-primary focus:ring-accent focus:border-accent"
        >
          {ATTACK_TYPES.map(type => (
            <option key={type} value={type}>{type}</option>
          ))}
        </select>
      </div>
      <div className="w-full md:w-1/3">
        <label htmlFor="confidence" className="block text-sm font-medium text-text-secondary mb-1">Min Confidence: {filters.confidence}%</label>
        <input
          type="range"
          id="confidence"
          name="confidence"
          min="0"
          max="100"
          value={filters.confidence}
          onChange={handleSliderChange}
          className="w-full h-2 bg-primary rounded-lg appearance-none cursor-pointer accent-accent"
        />
      </div>
    </div>
  );
};
