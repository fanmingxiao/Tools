import React from 'react';
import Plot from 'react-plotly.js';
import type { AnalysisResult } from '@/types/financial';

interface MetricsRadarChartProps {
  data: AnalysisResult;
  height?: number;
}

const MetricsRadarChart: React.FC<MetricsRadarChartProps> = ({ data, height = 400 }) => {
  const { metrics } = data;
  
  // 标准化指标值到0-100范围
  const normalizedMetrics = {
    毛利率: Math.min(metrics.grossMargin, 100),
    净利率: Math.min(metrics.netMargin * 2, 100),
    ROE: Math.min(metrics.roe * 2, 100),
    ROA: Math.min(metrics.roa * 4, 100),
    流动比率: Math.min(metrics.currentRatio * 33, 100),
    速动比率: Math.min(metrics.quickRatio * 40, 100),
  };
  
  const traces = [
    {
      type: 'scatterpolar' as const,
      r: [
        normalizedMetrics.毛利率,
        normalizedMetrics.净利率,
        normalizedMetrics.ROE,
        normalizedMetrics.ROA,
        normalizedMetrics.流动比率,
        normalizedMetrics.速动比率,
        normalizedMetrics.毛利率, // 闭合
      ],
      theta: ['毛利率', '净利率', 'ROE', 'ROA', '流动比率', '速动比率', '毛利率'],
      fill: 'toself' as const,
      fillcolor: 'rgba(220, 12, 12, 0.3)',
      line: {
        color: '#dc0c0c',
        width: 2,
      },
      marker: {
        size: 6,
        color: '#dc0c0c',
      },
      name: '当前表现',
    },
    {
      type: 'scatterpolar' as const,
      r: [60, 40, 50, 40, 70, 60, 60], // 行业平均水平
      theta: ['毛利率', '净利率', 'ROE', 'ROA', '流动比率', '速动比率', '毛利率'],
      fill: 'toself' as const,
      fillcolor: 'rgba(102, 102, 102, 0.2)',
      line: {
        color: '#666666',
        width: 2,
        dash: 'dash' as const,
      },
      marker: {
        size: 4,
        color: '#666666',
      },
      name: '行业平均',
    },
  ];
  
  const layout = {
    title: {
      text: '财务指标雷达图',
      font: { size: 16, color: '#1a1a1a', family: 'Inter, sans-serif' },
    },
    polar: {
      radialaxis: {
        visible: true,
        range: [0, 100],
        tickfont: { size: 10, color: '#666666' },
      },
      angularaxis: {
        tickfont: { size: 11, color: '#1a1a1a' },
      },
      bgcolor: '#ffffff',
    },
    paper_bgcolor: '#ffffff',
    font: { family: 'Inter, sans-serif' },
    margin: { t: 60, r: 50, b: 40, l: 50 },
    legend: {
      orientation: 'h' as const,
      y: -0.1,
      x: 0.5,
      xanchor: 'center' as const,
    },
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

export default MetricsRadarChart;
