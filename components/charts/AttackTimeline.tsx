
import React, { useMemo } from 'react';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import type { DetectionResult } from '../../types';

interface ChartData {
  time: string;
  count: number;
}

interface AttackTimelineProps {
  data: DetectionResult[];
}

export const AttackTimeline: React.FC<AttackTimelineProps> = ({ data }) => {
  const chartData = useMemo<ChartData[]>(() => {
    const timeCounts = data
      .filter(d => d.attack_prediction !== 'Benign')
      .reduce<Record<string, number>>((acc, curr) => {
        // Group by hour
        const date = new Date(curr.timestamp);
        date.setMinutes(0, 0, 0);
        const timeKey = date.toISOString();
        acc[timeKey] = (acc[timeKey] || 0) + 1;
        return acc;
      }, {});

    return Object.entries(timeCounts)
      .map(([time, count]) => ({ time, count }))
      .sort((a, b) => new Date(a.time).getTime() - new Date(b.time).getTime());
  }, [data]);
  
  const timeFormatter = (time: string) => {
    return new Date(time).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  return (
    <>
      <h3 className="text-xl font-semibold mb-4 text-text-primary text-center">Attack Timeline (by hour)</h3>
      {chartData.length === 0 ? (
        <div className="flex items-center justify-center h-64 text-text-secondary">
          <p>No timeline data to display.</p>
        </div>
      ) : (
      <ResponsiveContainer width="100%" height={300}>
        <AreaChart
          data={chartData}
          margin={{ top: 10, right: 30, left: 0, bottom: 0 }}
        >
          <defs>
            <linearGradient id="colorUv" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#ef4444" stopOpacity={0.8}/>
              <stop offset="95%" stopColor="#ef4444" stopOpacity={0}/>
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="#4a5568" />
          <XAxis dataKey="time" stroke="#a0aec0" tickFormatter={timeFormatter} />
          <YAxis stroke="#a0aec0" />
          <Tooltip
            labelFormatter={timeFormatter}
            contentStyle={{
              backgroundColor: '#2d3748',
              borderColor: '#4a5568',
              color: '#edf2f7'
            }}
          />
          <Area type="monotone" dataKey="count" name="Attacks" stroke="#ef4444" fillOpacity={1} fill="url(#colorUv)" />
        </AreaChart>
      </ResponsiveContainer>
      )}
    </>
  );
};
