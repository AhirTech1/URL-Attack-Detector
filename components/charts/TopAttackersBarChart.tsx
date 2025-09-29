
import React, { useMemo } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import type { DetectionResult } from '../../types';

interface ChartData {
  ip: string;
  count: number;
}

interface TopAttackersBarChartProps {
  data: DetectionResult[];
}

export const TopAttackersBarChart: React.FC<TopAttackersBarChartProps> = ({ data }) => {
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
          <Bar dataKey="count" name="Attack Count" fill="#38b2ac" />
        </BarChart>
      </ResponsiveContainer>
      )}
    </>
  );
};
