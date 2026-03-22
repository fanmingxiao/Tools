import type { FinancialData, FinancialMetrics, AnalysisResult } from '@/types/financial';

// 计算财务指标
export function calculateMetrics(data: FinancialData): FinancialMetrics {
  const { balanceSheet, incomeStatement, cashFlow } = data;
  
  // 计算总资产和总负债
  const totalCurrentAssets = Object.values(balanceSheet.assets.currentAssets).reduce((a, b) => a + b, 0);
  const totalNonCurrentAssets = Object.values(balanceSheet.assets.nonCurrentAssets).reduce((a, b) => a + b, 0);
  const totalAssets = totalCurrentAssets + totalNonCurrentAssets;
  
  const totalCurrentLiabilities = Object.values(balanceSheet.liabilities.currentLiabilities).reduce((a, b) => a + b, 0);
  const totalNonCurrentLiabilities = Object.values(balanceSheet.liabilities.nonCurrentLiabilities).reduce((a, b) => a + b, 0);
  const totalLiabilities = totalCurrentLiabilities + totalNonCurrentLiabilities;
  
  const totalEquity = Object.values(balanceSheet.equity).reduce((a, b) => a + b, 0);
  
  // 盈利能力指标
  const grossMargin = (incomeStatement.grossProfit / incomeStatement.revenue) * 100;
  const operatingMargin = (incomeStatement.operatingIncome / incomeStatement.revenue) * 100;
  const netMargin = (incomeStatement.netIncome / incomeStatement.revenue) * 100;
  const roe = (incomeStatement.netIncome / totalEquity) * 100;
  const roa = (incomeStatement.netIncome / totalAssets) * 100;
  
  // 偿债能力指标
  const currentRatio = totalCurrentAssets / totalCurrentLiabilities;
  const quickRatio = (totalCurrentAssets - balanceSheet.assets.currentAssets.inventory) / totalCurrentLiabilities;
  const debtToEquity = totalLiabilities / totalEquity;
  const debtToAsset = totalLiabilities / totalAssets;
  
  // 营运能力指标（使用假设值）
  const assetTurnover = incomeStatement.revenue / totalAssets;
  const inventoryTurnover = incomeStatement.costOfGoodsSold / balanceSheet.assets.currentAssets.inventory;
  const receivablesTurnover = incomeStatement.revenue / balanceSheet.assets.currentAssets.accountsReceivable;
  
  // 现金流指标
  const operatingCashFlow = cashFlow.operatingActivities.netIncome + 
    cashFlow.operatingActivities.depreciation + 
    cashFlow.operatingActivities.changesInWorkingCapital;
  const operatingCashFlowRatio = operatingCashFlow / totalCurrentLiabilities;
  const freeCashFlow = operatingCashFlow - Math.abs(cashFlow.investingActivities.capitalExpenditure);
  
  return {
    grossMargin: Math.round(grossMargin * 100) / 100,
    operatingMargin: Math.round(operatingMargin * 100) / 100,
    netMargin: Math.round(netMargin * 100) / 100,
    roe: Math.round(roe * 100) / 100,
    roa: Math.round(roa * 100) / 100,
    currentRatio: Math.round(currentRatio * 100) / 100,
    quickRatio: Math.round(quickRatio * 100) / 100,
    debtToEquity: Math.round(debtToEquity * 100) / 100,
    debtToAsset: Math.round(debtToAsset * 100) / 100,
    assetTurnover: Math.round(assetTurnover * 100) / 100,
    inventoryTurnover: Math.round(inventoryTurnover * 100) / 100,
    receivablesTurnover: Math.round(receivablesTurnover * 100) / 100,
    operatingCashFlowRatio: Math.round(operatingCashFlowRatio * 100) / 100,
    freeCashFlow: Math.round(freeCashFlow),
  };
}

// 生成分析洞察
export function generateInsights(data: FinancialData, metrics: FinancialMetrics): string[] {
  const insights: string[] = [];
  
  // 盈利能力分析
  if (metrics.netMargin > 15) {
    insights.push(`公司净利润率达到 ${metrics.netMargin}%，盈利能力强劲，高于行业平均水平。`);
  } else if (metrics.netMargin > 8) {
    insights.push(`公司净利润率为 ${metrics.netMargin}%，盈利能力处于健康水平。`);
  } else {
    insights.push(`公司净利润率为 ${metrics.netMargin}%，盈利能力有待提升，建议关注成本控制。`);
  }
  
  if (metrics.roe > 15) {
    insights.push(`净资产收益率(ROE)为 ${metrics.roe}%，股东回报表现优异。`);
  } else if (metrics.roe > 10) {
    insights.push(`净资产收益率(ROE)为 ${metrics.roe}%，股东回报处于合理区间。`);
  } else {
    insights.push(`净资产收益率(ROE)为 ${metrics.roe}%，资本运用效率有提升空间。`);
  }
  
  // 偿债能力分析
  if (metrics.currentRatio > 2) {
    insights.push(`流动比率为 ${metrics.currentRatio}，短期偿债能力充足，财务安全性高。`);
  } else if (metrics.currentRatio > 1.5) {
    insights.push(`流动比率为 ${metrics.currentRatio}，短期偿债能力良好。`);
  } else if (metrics.currentRatio < 1) {
    insights.push(`流动比率为 ${metrics.currentRatio}，短期偿债压力较大，需关注流动性风险。`);
  }
  
  if (metrics.debtToEquity < 0.5) {
    insights.push(`资产负债率为 ${(metrics.debtToAsset * 100).toFixed(1)}%，财务杠杆保守，债务风险可控。`);
  } else if (metrics.debtToEquity < 1) {
    insights.push(`资产负债率为 ${(metrics.debtToAsset * 100).toFixed(1)}%，财务结构相对稳健。`);
  } else {
    insights.push(`资产负债率为 ${(metrics.debtToAsset * 100).toFixed(1)}%，债务水平较高，需关注财务风险。`);
  }
  
  // 营运能力分析
  if (metrics.assetTurnover > 1) {
    insights.push(`总资产周转率为 ${metrics.assetTurnover}，资产运营效率较高。`);
  } else {
    insights.push(`总资产周转率为 ${metrics.assetTurnover}，资产利用效率有提升空间。`);
  }
  
  // 现金流分析
  const operatingCashFlow = data.cashFlow.operatingActivities.netIncome + 
    data.cashFlow.operatingActivities.depreciation + 
    data.cashFlow.operatingActivities.changesInWorkingCapital;
  
  if (operatingCashFlow > 0) {
    insights.push(`经营活动现金流为正，达 ${operatingCashFlow.toLocaleString()} ${data.currency}，主营业务造血能力良好。`);
  } else {
    insights.push(`经营活动现金流为负，需关注经营质量及回款情况。`);
  }
  
  if (metrics.freeCashFlow > 0) {
    insights.push(`自由现金流为 ${metrics.freeCashFlow.toLocaleString()} ${data.currency}，具备持续投资和分红能力。`);
  } else {
    insights.push(`自由现金流为负，资本支出较大，需评估投资回报率。`);
  }
  
  return insights;
}

// 生成风险警示
export function generateRisks(data: FinancialData, metrics: FinancialMetrics): string[] {
  const risks: string[] = [];
  
  if (metrics.currentRatio < 1.2) {
    risks.push('流动比率偏低，存在短期偿债压力，建议优化营运资金管理。');
  }
  
  if (metrics.debtToEquity > 1) {
    risks.push('资产负债率较高，财务杠杆激进，需关注利率变动风险。');
  }
  
  if (metrics.netMargin < 5) {
    risks.push('净利润率较低，盈利空间有限，抗风险能力较弱。');
  }
  
  const operatingCashFlow = data.cashFlow.operatingActivities.netIncome + 
    data.cashFlow.operatingActivities.depreciation + 
    data.cashFlow.operatingActivities.changesInWorkingCapital;
  
  if (operatingCashFlow < data.incomeStatement.netIncome * 0.5) {
    risks.push('经营现金流与净利润差异较大，需关注收入质量及应收账款回收。');
  }
  
  if (metrics.freeCashFlow < 0) {
    risks.push('自由现金流为负，持续投资可能依赖外部融资，需关注资金链安全。');
  }
  
  if (risks.length === 0) {
    risks.push('当前财务风险整体可控，建议持续关注行业及宏观经济变化。');
  }
  
  return risks;
}

// 生成建议
export function generateRecommendations(_data: FinancialData, metrics: FinancialMetrics): string[] {
  const recommendations: string[] = [];
  
  if (metrics.grossMargin < 30) {
    recommendations.push('建议优化产品结构，提升高毛利产品占比，或寻求供应链成本优化空间。');
  }
  
  if (metrics.currentRatio < 1.5) {
    recommendations.push('建议加强应收账款管理，缩短回款周期，或适当增加长期融资比例。');
  }
  
  if (metrics.assetTurnover < 0.8) {
    recommendations.push('建议评估闲置资产处置可能性，提升资产使用效率。');
  }
  
  if (metrics.debtToEquity > 0.8) {
    recommendations.push('建议逐步优化资本结构，考虑股权融资或利润留存以降低财务杠杆。');
  }
  
  if (metrics.roe < 12) {
    recommendations.push('建议关注净资产收益率提升，可通过提高净利率、加速资产周转或适度杠杆实现。');
  }
  
  recommendations.push('建议建立定期财务分析机制，持续跟踪关键指标变化趋势。');
  recommendations.push('建议关注行业对标分析，识别与领先企业的差距及改进方向。');
  
  return recommendations;
}

// 完整分析函数
export function analyzeFinancialData(data: FinancialData): AnalysisResult {
  const metrics = calculateMetrics(data);
  const insights = generateInsights(data, metrics);
  const risks = generateRisks(data, metrics);
  const recommendations = generateRecommendations(data, metrics);
  
  // 生成趋势数据（模拟5年数据）
  const years = ['2020', '2021', '2022', '2023', '2024'];
  const revenue = data.incomeStatement.revenue;
  const netIncome = data.incomeStatement.netIncome;
  
  const trends = {
    revenue: years.map((_, idx) => Math.round(revenue * (0.7 + idx * 0.075))),
    netIncome: years.map((_, idx) => Math.round(netIncome * (0.6 + idx * 0.1))),
    totalAssets: years.map((_, idx) => {
      const totalAssets = Object.values(data.balanceSheet.assets).flatMap(Object.values).reduce((a, b) => a + b, 0);
      return Math.round(totalAssets * (0.75 + idx * 0.0625));
    }),
    totalLiabilities: years.map((_, idx) => {
      const totalLiabilities = Object.values(data.balanceSheet.liabilities).flatMap(Object.values).reduce((a, b) => a + b, 0);
      return Math.round(totalLiabilities * (0.8 + idx * 0.05));
    }),
    equity: years.map((_, idx) => {
      const totalEquity = Object.values(data.balanceSheet.equity).reduce((a, b) => a + b, 0);
      return Math.round(totalEquity * (0.7 + idx * 0.075));
    }),
    years,
  };
  
  return {
    data,
    metrics,
    trends,
    insights,
    risks,
    recommendations,
  };
}
