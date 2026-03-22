import React from 'react';
import Plot from 'react-plotly.js';
import type { AnalysisResult } from '@/types/financial';

interface BalanceSheetChartProps {
  data: AnalysisResult;
  height?: number;
}

const BalanceSheetChart: React.FC<BalanceSheetChartProps> = ({ data, height = 400 }) => {
  const { balanceSheet } = data.data;

  const currentAssets = Object.values(balanceSheet.assets.currentAssets).reduce((a, b) => a + b, 0);
  const nonCurrentAssets = Object.values(balanceSheet.assets.nonCurrentAssets).reduce((a, b) => a + b, 0);
  const currentLiabilities = Object.values(balanceSheet.liabilities.currentLiabilities).reduce((a, b) => a + b, 0);
  const nonCurrentLiabilities = Object.values(balanceSheet.liabilities.nonCurrentLiabilities).reduce((a, b) => a + b, 0);
  const equity = Object.values(balanceSheet.equity).reduce((a, b) => a + b, 0);

  // Trace: 底层数据
  const trace1 = {
    x: ['资产总计', '负债与权益总计'],
    y: [nonCurrentAssets / 1000000, equity / 1000000],
    name: ['非流动资产', '所有者权益'],
    type: 'bar' as const,
    marker: { color: ['#666666', '#1a1a1a'] },
    text: [(nonCurrentAssets / 1000000).toFixed(1), (equity / 1000000).toFixed(1)],
    textposition: 'inside' as const,
  };

  // Trace: 中层数据
  const trace2 = {
    x: ['资产总计', '负债与权益总计'],
    y: [0, nonCurrentLiabilities / 1000000],
    name: ['', '非流动负债'],
    type: 'bar' as const,
    marker: { color: ['transparent', '#999999'] },
    text: ['', (nonCurrentLiabilities / 1000000).toFixed(1)],
    textposition: 'inside' as const,
  };

  // Trace: 顶层数据
  const trace3 = {
    x: ['资产总计', '负债与权益总计'],
    y: [currentAssets / 1000000, currentLiabilities / 1000000],
    name: ['流动资产', '流动负债'],
    type: 'bar' as const,
    marker: { color: ['#dc0c0c', '#e6e6e6'] },
    text: [(currentAssets / 1000000).toFixed(1), (currentLiabilities / 1000000).toFixed(1)],
    textposition: 'inside' as const,
  };

  const layout = {
    title: {
      text: '资产负债对称结构图',
      font: { size: 16, color: '#1a1a1a', family: 'Inter, sans-serif' },
    },
    barmode: 'stack' as const,
    xaxis: {
      gridcolor: '#e6e6e6',
      linecolor: '#d3d3d3',
      tickfont: { size: 13, color: '#1a1a1a', bold: true },
    },
    yaxis: {
      title: '金额 (百万元)',
      gridcolor: '#e6e6e6',
      linecolor: '#d3d3d3',
      tickfont: { size: 12, color: '#666666' },
      zeroline: true,
    },
    plot_bgcolor: '#ffffff',
    paper_bgcolor: '#ffffff',
    font: { family: 'Inter, sans-serif' },
    margin: { t: 60, r: 30, b: 60, l: 70 },
    showlegend: false,
  };

  const config = { responsive: true, displayModeBar: false };

  return (
    <Plot
      data={[trace1, trace2, trace3] as any}
      layout={layout as any}
      config={config}
      style={{ width: '100%', height: `${height}px` }}
    />
  );
};

export default BalanceSheetChart;
