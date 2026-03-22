import type { FinancialData } from '@/types/financial';

// 生成模拟财务数据
export function generateMockFinancialData(companyName: string = '示例科技有限公司'): FinancialData {
  const currency = 'CNY';
  const reportDate = new Date().toISOString().split('T')[0];
  
  // 生成合理的财务数据
  const revenue = Math.round(500000000 + Math.random() * 500000000); // 5-10亿收入
  const grossProfit = Math.round(revenue * (0.25 + Math.random() * 0.2)); // 25-45% 毛利率
  const operatingIncome = Math.round(grossProfit * (0.3 + Math.random() * 0.3)); // 营业利润
  const netIncome = Math.round(operatingIncome * (0.7 + Math.random() * 0.15)); // 净利润
  
  // 资产负债表数据
  const cash = Math.round(netIncome * (0.8 + Math.random() * 0.4));
  const accountsReceivable = Math.round(revenue * 0.15);
  const inventory = Math.round(revenue * 0.1);
  const otherCurrentAssets = Math.round(revenue * 0.05);
  
  const propertyPlantEquipment = Math.round(revenue * 0.4);
  const intangibleAssets = Math.round(revenue * 0.08);
  const longTermInvestments = Math.round(revenue * 0.1);
  const otherNonCurrentAssets = Math.round(revenue * 0.05);
  
  const accountsPayable = Math.round(revenue * 0.12);
  const shortTermDebt = Math.round(revenue * 0.08);
  const accruedExpenses = Math.round(revenue * 0.05);
  const otherCurrentLiabilities = Math.round(revenue * 0.03);
  
  const longTermDebt = Math.round(revenue * 0.2);
  const deferredTax = Math.round(revenue * 0.02);
  const otherNonCurrentLiabilities = Math.round(revenue * 0.03);
  
  const shareCapital = Math.round(revenue * 0.15);
  const retainedEarnings = Math.round(revenue * 0.25);
  const otherEquity = Math.round(revenue * 0.05);
  
  // 现金流量表数据
  const depreciation = Math.round(propertyPlantEquipment * 0.05);
  const changesInWorkingCapital = Math.round((Math.random() - 0.5) * revenue * 0.05);
  
  const capitalExpenditure = -Math.round(revenue * 0.08);
  const acquisitions = Math.random() > 0.7 ? -Math.round(revenue * 0.1) : 0;
  const saleOfAssets = Math.random() > 0.6 ? Math.round(revenue * 0.03) : 0;
  
  const debtIssuance = Math.round(revenue * 0.05);
  const debtRepayment = -Math.round(revenue * 0.03);
  const dividendPaid = -Math.round(netIncome * 0.3);
  const shareIssuance = Math.random() > 0.8 ? Math.round(revenue * 0.1) : 0;
  
  return {
    companyName,
    reportDate,
    currency,
    balanceSheet: {
      assets: {
        currentAssets: {
          cash,
          accountsReceivable,
          inventory,
          otherCurrentAssets,
        },
        nonCurrentAssets: {
          propertyPlantEquipment,
          intangibleAssets,
          longTermInvestments,
          otherNonCurrentAssets,
        },
      },
      liabilities: {
        currentLiabilities: {
          accountsPayable,
          shortTermDebt,
          accruedExpenses,
          otherCurrentLiabilities,
        },
        nonCurrentLiabilities: {
          longTermDebt,
          deferredTax,
          otherNonCurrentLiabilities,
        },
      },
      equity: {
        shareCapital,
        retainedEarnings,
        otherEquity,
      },
    },
    cashFlow: {
      operatingActivities: {
        netIncome,
        depreciation,
        changesInWorkingCapital,
        otherOperating: 0,
      },
      investingActivities: {
        capitalExpenditure,
        acquisitions,
        saleOfAssets,
        otherInvesting: 0,
      },
      financingActivities: {
        debtIssuance,
        debtRepayment,
        dividendPaid,
        shareIssuance,
        otherFinancing: 0,
      },
    },
    incomeStatement: {
      revenue,
      costOfGoodsSold: revenue - grossProfit,
      grossProfit,
      operatingExpenses: {
        sellingGeneralAdmin: Math.round(grossProfit * 0.4),
        researchDevelopment: Math.round(grossProfit * 0.15),
        depreciation: Math.round(depreciation * 0.3),
        otherOperating: Math.round(grossProfit * 0.05),
      },
      operatingIncome,
      nonOperatingItems: {
        interestIncome: Math.round(cash * 0.02),
        interestExpense: -Math.round(longTermDebt * 0.05),
        otherIncome: Math.round(revenue * 0.01),
      },
      preTaxIncome: operatingIncome + Math.round(revenue * 0.01),
      taxExpense: Math.round(netIncome * 0.25),
      netIncome,
    },
  };
}

// 模拟PDF解析（实际项目中需要集成真实的PDF解析库）
export async function parsePDFFinancialData(file: File): Promise<FinancialData> {
  return new Promise((resolve, reject) => {
    // 模拟解析延迟
    setTimeout(() => {
      try {
        // 在实际项目中，这里应该使用pdf-lib或其他PDF解析库
        // 现在返回模拟数据
        const companyName = file.name.replace(/\.pdf$/i, '');
        const data = generateMockFinancialData(companyName);
        resolve(data);
      } catch (error) {
        reject(new Error('PDF解析失败：' + (error as Error).message));
      }
    }, 2000);
  });
}
