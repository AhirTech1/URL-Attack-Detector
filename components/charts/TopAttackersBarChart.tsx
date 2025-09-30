import React, { useMemo } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import type { DetectionResult } from '../../types';

interface ChartData {
  ip: string;
  count: number;
}

interface TopAttackersBarChartProps {
  data: DetectionResult[];
  onBarClick: (ip: string) => void;
}

export const TopAttackersBarChart: React.FC<TopAttackersBarChartProps> = ({ data, onBarClick }) => {
  const chartData = useMemo<ChartData[]>(() => {
    const ipCounts = data
      .filter(d => d.attack_prediction !== 'Benign')
      .reduce<Record<string, number>>((acc, curr) => {
        acc[curr.src_ip] = (acc[curr.src_ip] || 0) + 1;
        return acc;
      }, {});
    
    return Object.entries(ipCounts)
      .map(([ip, count]) => ({ ip, count }))
      .sort((a, b) => b.count - a.count)
      .slice(0, 10);
  }, [data]);

  return (
    <>
      <h3 className="text-xl font-semibold mb-4 text-text-primary text-center">Top Attacker IPs</h3>
      {chartData.length === 0 ? (
        <div className="flex items-center justify-center h-64 text-text-secondary">
          <p>No attacker data to display.</p>
        </div>
      ) : (
      <ResponsiveContainer width="100%" height={300}>
        <BarChart
          data={chartData}
          margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
        >
          <CartesianGrid strokeDasharray="3 3" stroke="#4a5568" />
          <XAxis dataKey="ip" stroke="#a0aec0" />
          <YAxis stroke="#a0aec0" />
          <Tooltip
            cursor={{ fill: 'rgba(113, 128, 150, 0.2)' }}
            contentStyle={{
              backgroundColor: '#2d3748',
              borderColor: '#4a5568',
              color: '#edf2f7'
            }}
          />
          <Legend />
          {/* FIX: Moved onClick from BarChart to Bar to resolve typing issues and simplify event handling. The onClick handler on a Bar element receives the data for that specific bar. */}
          {/* FIX: Explicitly type 'data' as 'any' to resolve incorrect type inference from '@types/recharts' which causes a compile error. The 'data' object at runtime contains the properties of the data point. */}
          <Bar dataKey="count" name="Attack Count" fill="#38b2ac" cursor="pointer" onClick={(data: any) => onBarClick(data.ip)} />
        </BarChart>
      </ResponsiveContainer>
      )}
    </>
  );
};