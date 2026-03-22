import React from 'react';
import Plot from 'react-plotly.js';
import type { AnalysisResult } from '@/types/financial';

interface CashFlowChartProps {
  data: AnalysisResult;
  height?: number;
}

const CashFlowChart: React.FC<CashFlowChartProps> = ({ data, height = 400 }) => {
  const { cashFlow } = data.data;
  
  // 计算各类现金流
  const operatingCF = cashFlow.operatingActivities.netIncome + 
    cashFlow.operatingActivities.depreciation + 
    cashFlow.operatingActivities.changesInWorkingCapital;
  
  const investingCF = cashFlow.investingActivities.capitalExpenditure + 
    cashFlow.investingActivities.acquisitions + 
    cashFlow.investingActivities.saleOfAssets;
  
  const financingCF = cashFlow.financingActivities.debtIssuance + 
    cashFlow.financingActivities.debtRepayment + 
    cashFlow.financingActivities.dividendPaid + 
    cashFlow.financingActivities.shareIssuance;
  
  const traces = [
    {
      x: ['经营活动', '投资活动', '筹资活动'],
      y: [
        operatingCF / 1000000,
        investingCF / 1000000,
        financingCF / 1000000,
      ],
      type: 'bar' as const,
      marker: {
        color: ['#dc0c0c', '#1a1a1a', '#666666'],
      },
      text: [
        (operatingCF / 1000000).toFixed(1),
        (investingCF / 1000000).toFixed(1),
        (financingCF / 1000000).toFixed(1),
      ],
      textposition: 'outside' as const,
    },
  ];
  
  const layout = {
    title: {
      text: '现金流量分析',
      font: { size: 16, color: '#1a1a1a', family: 'Inter, sans-serif' },
    },
    xaxis: {
      gridcolor: '#e6e6e6',
      linecolor: '#d3d3d3',
      tickfont: { size: 12, color: '#666666' },
    },
    yaxis: {
      title: '金额 (百万元)',
      gridcolor: '#e6e6e6',
      linecolor: '#d3d3d3',
      tickfont: { size: 12, color: '#666666' },
      zeroline: true,
      zerolinecolor: '#1a1a1a',
      zerolinewidth: 2,
    },
    plot_bgcolor: '#ffffff',
    paper_bgcolor: '#ffffff',
    font: { family: 'Inter, sans-serif' },
    margin: { t: 60, r: 30, b: 60, l: 70 },
    showlegend: false,
    shapes: [
      {
        type: 'line' as const,
        x0: -0.5,
        x1: 2.5,
        y0: 0,
        y1: 0,
        line: {
          color: '#1a1a1a',
          width: 2,
        },
      },
    ],
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

export default CashFlowChart;
