import React from 'react';
import Plot from 'react-plotly.js';
import type { AnalysisResult } from '@/types/financial';

interface TrendChartProps {
  data: AnalysisResult;
  height?: number;
}

const TrendChart: React.FC<TrendChartProps> = ({ data, height = 400 }) => {
  const { trends } = data;
  
  const traces = [
    {
      x: trends.years,
      y: trends.revenue.map(v => v / 1000000),
      type: 'scatter' as const,
      mode: 'lines+markers' as const,
      name: '营业收入',
      line: { color: '#dc0c0c', width: 3 },
      marker: { size: 8, color: '#dc0c0c' },
    },
    {
      x: trends.years,
      y: trends.netIncome.map(v => v / 1000000),
      type: 'scatter' as const,
      mode: 'lines+markers' as const,
      name: '净利润',
      line: { color: '#1a1a1a', width: 3 },
      marker: { size: 8, color: '#1a1a1a' },
    },
  ];
  
  const layout = {
    title: {
      text: '营收与利润趋势',
      font: { size: 16, color: '#1a1a1a', family: 'Inter, sans-serif' },
    },
    xaxis: {
      title: '年度',
      gridcolor: '#e6e6e6',
      linecolor: '#d3d3d3',
      tickfont: { size: 12, color: '#666666' },
    },
    yaxis: {
      title: '金额 (百万元)',
      gridcolor: '#e6e6e6',
      linecolor: '#d3d3d3',
      tickfont: { size: 12, color: '#666666' },
    },
    plot_bgcolor: '#ffffff',
    paper_bgcolor: '#ffffff',
    font: { family: 'Inter, sans-serif' },
    legend: {
      orientation: 'h' as const,
      y: -0.2,
      x: 0.5,
      xanchor: 'center' as const,
    },
    margin: { t: 60, r: 30, b: 80, l: 70 },
    hovermode: 'x unified' as const,
  };
  
  const config = {
    responsive: true,
    displayModeBar: false,
  };
  
  return (
    <Plot
      data={traces as any}
      layout={layout as any}
      config={config}
      style={{ width: '100%', height: `${height}px` }}
    />
  );
};

export default TrendChart;
