
import React from 'react';
import { ShieldCheckIcon } from './icons';

export const Header: React.FC = () => {
  return (
    <header className="bg-surface shadow-md">
      <div className="container mx-auto px-4 md:px-8 py-4 flex items-center">
        <ShieldCheckIcon className="w-8 h-8 text-accent" />
        <h1 className="ml-3 text-2xl font-bold text-text-primary tracking-tight">
          URL-Based Attack Detector
        </h1>
      </div>
    </header>
  );
};
