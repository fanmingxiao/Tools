// 财务数据类型定义

export interface BalanceSheet {
  assets: {
    currentAssets: {
      cash: number;
      accountsReceivable: number;
      inventory: number;
      otherCurrentAssets: number;
    };
    nonCurrentAssets: {
      propertyPlantEquipment: number;
      intangibleAssets: number;
      longTermInvestments: number;
      otherNonCurrentAssets: number;
    };
  };
  liabilities: {
    currentLiabilities: {
      accountsPayable: number;
      shortTermDebt: number;
      accruedExpenses: number;
      otherCurrentLiabilities: number;
    };
    nonCurrentLiabilities: {
      longTermDebt: number;
      deferredTax: number;
      otherNonCurrentLiabilities: number;
    };
  };
  equity: {
    shareCapital: number;
    retainedEarnings: number;
    otherEquity: number;
  };
}

export interface CashFlowStatement {
  operatingActivities: {
    netIncome: number;
    depreciation: number;
    changesInWorkingCapital: number;
    otherOperating: number;
  };
  investingActivities: {
    capitalExpenditure: number;
    acquisitions: number;
    saleOfAssets: number;
    otherInvesting: number;
  };
  financingActivities: {
    debtIssuance: number;
    debtRepayment: number;
    dividendPaid: number;
    shareIssuance: number;
    otherFinancing: number;
  };
}

export interface IncomeStatement {
  revenue: number;
  costOfGoodsSold: number;
  grossProfit: number;
  operatingExpenses: {
    sellingGeneralAdmin: number;
    researchDevelopment: number;
    depreciation: number;
    otherOperating: number;
  };
  operatingIncome: number;
  nonOperatingItems: {
    interestIncome: number;
    interestExpense: number;
    otherIncome: number;
  };
  preTaxIncome: number;
  taxExpense: number;
  netIncome: number;
}

export interface FinancialData {
  companyName: string;
  reportDate: string;
  currency: string;
  balanceSheet: BalanceSheet;
  cashFlow: CashFlowStatement;
  incomeStatement: IncomeStatement;
}

export interface FinancialMetrics {
  // 盈利能力指标
  grossMargin: number;
  operatingMargin: number;
  netMargin: number;
  roe: number;
  roa: number;
  
  // 偿债能力指标
  currentRatio: number;
  quickRatio: number;
  debtToEquity: number;
  debtToAsset: number;
  
  // 营运能力指标
  assetTurnover: number;
  inventoryTurnover: number;
  receivablesTurnover: number;
  
  // 现金流指标
  operatingCashFlowRatio: number;
  freeCashFlow: number;
}

export interface AnalysisResult {
  data: FinancialData;
  metrics: FinancialMetrics;
  trends: {
    revenue: number[];
    netIncome: number[];
    totalAssets: number[];
    totalLiabilities: number[];
    equity: number[];
    years: string[];
  };
  insights: string[];
  risks: string[];
  recommendations: string[];
}

export interface ChartData {
  labels: string[];
  datasets: {
    name: string;
    data: number[];
    color?: string;
  }[];
}
