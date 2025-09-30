
import React, { useMemo } from 'react';
import { PieChart, Pie, Cell, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import type { DetectionResult } from '../../types';

interface ChartData {
  name: string;
  value: number;
  // FIX: Added index signature to satisfy 'recharts' internal type requirements for the Pie component's data prop.
  [x: string]: string | number;
}

interface AttackTypePieChartProps {
  data: DetectionResult[];
  onSliceClick: (attackType: string) => void;
}

const COLORS = ['#ef4444', '#f97316', '#eab308', '#84cc16', '#22c55e', '#14b8a6', '#06b6d4', '#3b82f6', '#8b5cf6'];

export const AttackTypePieChart: React.FC<AttackTypePieChartProps> = ({ data, onSliceClick }) => {
  const chartData = useMemo<ChartData[]>(() => {
    const attackCounts = data
      .filter(d => d.attack_prediction !== 'Benign')
      .reduce<Record<string, number>>((acc, curr) => {
        acc[curr.attack_prediction] = (acc[curr.attack_prediction] || 0) + 1;
        return acc;
      }, {});

    return Object.entries(attackCounts)
      .map(([name, value]) => ({ name, value }))
      .sort((a, b) => b.value - a.value);
  }, [data]);

  return (
    <>
      <h3 className="text-xl font-semibold mb-4 text-text-primary text-center">Attack Types Distribution</h3>
      {chartData.length === 0 ? (
        <div className="flex items-center justify-center h-64 text-text-secondary">
          <p>No attack data to display.</p>
        </div>
      ) : (
      <ResponsiveContainer width="100%" height={300}>
        <PieChart>
          <Pie
            data={chartData}
            cx="50%"
            cy="50%"
            labelLine={false}
            outerRadius={80}
            fill="#8884d8"
            dataKey="value"
            nameKey="name"
            onClick={(data) => onSliceClick(data.name)}
            cursor="pointer"
          >
            {chartData.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
            ))}
          </Pie>
          <Tooltip
            contentStyle={{
              backgroundColor: '#2d3748',
              borderColor: '#4a5568',
              color: '#edf2f7'
            }}
          />
          <Legend />
        </PieChart>
      </ResponsiveContainer>
      )}
    </>
  );
};
