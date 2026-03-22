import React from 'react';
import Plot from 'react-plotly.js';
import type { AnalysisResult } from '@/types/financial';

interface ProfitStructureChartProps {
  data: AnalysisResult;
  height?: number;
}

const ProfitStructureChart: React.FC<ProfitStructureChartProps> = ({ data, height = 400 }) => {
  const { incomeStatement } = data.data;

  const traces = [
    {
      type: 'waterfall' as const,
      orientation: 'v' as const,
      measure: [
        'absolute',
        'relative',
        'total',
        'relative',
        'relative',
        'relative',
        'relative',
        'total'
      ],
      x: [
        '营业收入',
        '营业成本',
        '毛利润',
        '销售管理费',
        '研发费用',
        '折旧费用',
        '其他费用',
        '净利润'
      ],
      y: [
        incomeStatement.revenue / 1000000,
        -incomeStatement.costOfGoodsSold / 1000000,
        null, // total
        -incomeStatement.operatingExpenses.sellingGeneralAdmin / 1000000,
        -incomeStatement.operatingExpenses.researchDevelopment / 1000000,
        -incomeStatement.operatingExpenses.depreciation / 1000000,
        -incomeStatement.operatingExpenses.otherOperating / 1000000,
        null  // total
      ],
      connector: {
        line: { color: 'rgb(63, 63, 63)' }
      },
      decreasing: { marker: { color: '#666666' } },
      increasing: { marker: { color: '#dc0c0c' } },
      totals: { marker: { color: '#1a1a1a' } },
      textposition: 'outside' as const,
      text: [
        (incomeStatement.revenue / 1000000).toFixed(1),
        (-incomeStatement.costOfGoodsSold / 1000000).toFixed(1),
        (incomeStatement.grossProfit / 1000000).toFixed(1),
        (-incomeStatement.operatingExpenses.sellingGeneralAdmin / 1000000).toFixed(1),
        (-incomeStatement.operatingExpenses.researchDevelopment / 1000000).toFixed(1),
        (-incomeStatement.operatingExpenses.depreciation / 1000000).toFixed(1),
        (-incomeStatement.operatingExpenses.otherOperating / 1000000).toFixed(1),
        (incomeStatement.netIncome / 1000000).toFixed(1)
      ],
      textfont: {
        family: 'Inter, sans-serif',
        size: 11
      }
    }
  ];

  const layout = {
    title: {
      text: '利润瀑布图流程分析',
      font: { size: 16, color: '#1a1a1a', family: 'Inter, sans-serif' },
    },
    xaxis: {
      type: 'category' as const,
      tickfont: { size: 11, color: '#666666' }
    },
    yaxis: {
      title: '金额 (百万元)',
      gridcolor: '#e6e6e6',
      zerolinecolor: '#1a1a1a',
      zerolinewidth: 2,
      tickfont: { size: 12, color: '#666666' }
    },
    plot_bgcolor: '#ffffff',
    paper_bgcolor: '#ffffff',
    font: { family: 'Inter, sans-serif' },
    margin: { t: 60, r: 30, b: 60, l: 70 },
    showlegend: false,
    waterfallgap: 0.3
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

export default ProfitStructureChart;
