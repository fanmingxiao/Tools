import React from 'react';
import type { AnalysisResult } from '@/types/financial';
import { TrendingUp, TrendingDown, Minus, Activity, DollarSign, Percent, BarChart3, Wallet } from 'lucide-react';

interface MetricsCardsProps {
  data: AnalysisResult;
}

interface MetricCardProps {
  title: string;
  value: string;
  subtitle: string;
  trend?: 'up' | 'down' | 'neutral';
  icon: React.ReactNode;
}

const MetricCard: React.FC<MetricCardProps> = ({ title, value, subtitle, trend = 'neutral', icon }) => {
  const trendIcon = {
    up: <TrendingUp className="w-4 h-4 text-green-600" />,
    down: <TrendingDown className="w-4 h-4 text-red-600" />,
    neutral: <Minus className="w-4 h-4 text-gray-500" />,
  };
  
  return (
    <div className="bg-white rounded-lg border border-[#e6e6e6] p-6 hover:shadow-lg transition-shadow duration-300">
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <p className="text-sm text-[#666666] mb-1">{title}</p>
          <p className="text-2xl font-bold text-[#1a1a1a] mb-1">{value}</p>
          <div className="flex items-center gap-1">
            {trendIcon[trend]}
            <span className="text-xs text-[#666666]">{subtitle}</span>
          </div>
        </div>
        <div className="w-10 h-10 rounded-lg bg-[#f5f5f5] flex items-center justify-center text-[#dc0c0c]">
          {icon}
        </div>
      </div>
    </div>
  );
};

const MetricsCards: React.FC<MetricsCardsProps> = ({ data }) => {
  const { metrics, data: financialData } = data;
  
  const cards = [
    {
      title: '净利润率',
      value: `${metrics.netMargin}%`,
      subtitle: '盈利能力指标',
      trend: (metrics.netMargin > 10 ? 'up' : metrics.netMargin > 5 ? 'neutral' : 'down') as 'up' | 'down' | 'neutral',
      icon: <Percent className="w-5 h-5" />,
    },
    {
      title: '净资产收益率',
      value: `${metrics.roe}%`,
      subtitle: 'ROE 股东回报',
      trend: (metrics.roe > 15 ? 'up' : metrics.roe > 10 ? 'neutral' : 'down') as 'up' | 'down' | 'neutral',
      icon: <TrendingUp className="w-5 h-5" />,
    },
    {
      title: '流动比率',
      value: `${metrics.currentRatio}`,
      subtitle: '短期偿债能力',
      trend: (metrics.currentRatio > 2 ? 'up' : metrics.currentRatio > 1.5 ? 'neutral' : 'down') as 'up' | 'down' | 'neutral',
      icon: <Activity className="w-5 h-5" />,
    },
    {
      title: '资产负债率',
      value: `${(metrics.debtToAsset * 100).toFixed(1)}%`,
      subtitle: '财务杠杆水平',
      trend: (metrics.debtToAsset < 0.5 ? 'up' : metrics.debtToAsset < 0.7 ? 'neutral' : 'down') as 'up' | 'down' | 'neutral',
      icon: <BarChart3 className="w-5 h-5" />,
    },
    {
      title: '营业收入',
      value: `¥${(financialData.incomeStatement.revenue / 1000000).toFixed(1)}M`,
      subtitle: '本期收入规模',
      trend: 'neutral' as const,
      icon: <DollarSign className="w-5 h-5" />,
    },
    {
      title: '自由现金流',
      value: `¥${(metrics.freeCashFlow / 1000000).toFixed(1)}M`,
      subtitle: '现金创造能力',
      trend: (metrics.freeCashFlow > 0 ? 'up' : 'down') as 'up' | 'down' | 'neutral',
      icon: <Wallet className="w-5 h-5" />,
    },
  ];
  
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      {cards.map((card, index) => (
        <MetricCard key={index} {...card} />
      ))}
    </div>
  );
};

export default MetricsCards;
