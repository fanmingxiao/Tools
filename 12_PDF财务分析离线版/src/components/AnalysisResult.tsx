import React, { useState } from 'react';
import html2canvas from 'html2canvas';
import { Download, FileBarChart, ArrowRightLeft, TrendingUp, Lightbulb, AlertTriangle, CheckCircle, Loader2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import type { AnalysisResult as AnalysisResultType } from '@/types/financial';
import { exportToWord, type ReportImages } from '@/lib/docxExporter';

// 图表组件
import BalanceSheetChart from './charts/BalanceSheetChart';
import CashFlowChart from './charts/CashFlowChart';
import ProfitStructureChart from './charts/ProfitStructureChart';
import MetricsRadarChart from './charts/MetricsRadarChart';
import MetricsCards from './charts/MetricsCards';

interface AnalysisResultProps {
  data: AnalysisResultType;
}

const AnalysisResult: React.FC<AnalysisResultProps> = ({ data }) => {
  const [isExporting, setIsExporting] = useState(false);

  const handleExport = async () => {
    setIsExporting(true);
    
    try {
      // 等待离线渲染挂载与 Plotly 内部 SVG 布局绘制完成
      await new Promise(resolve => setTimeout(resolve, 800));
      
      const captureNode = async (id: string) => {
        const el = document.getElementById(id);
        if (!el) return undefined;
        // 渲染图表生成高质量 Base64
        const canvas = await html2canvas(el, { scale: 2, useCORS: true });
        return canvas.toDataURL('image/png');
      };

      const images: ReportImages = {};
      images.balance = await captureNode('export-balance');
      images.cashflow = await captureNode('export-cashflow');
      images.profit = await captureNode('export-profit');
      images.radar = await captureNode('export-radar');
      
      await exportToWord(data, data.data.companyName, images);
    } catch (e) {
      console.error('Word 报告导出过程中截图失败：', e);
      // 如果出错，走兜底不带图片的方案
      await exportToWord(data, data.data.companyName);
    } finally {
      setIsExporting(false);
    }
  };

  return (
    <section id="analysis" className="py-24 bg-[#f8f8f8]">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 mb-12">
          <div>
            <h2 className="text-3xl md:text-4xl font-bold text-[#1a1a1a] mb-2">
              财务分析报告
            </h2>
            <p className="text-[#666666]">
              {data.data.companyName} | 报告日期：{data.data.reportDate}
            </p>
          </div>
          <Button
            onClick={handleExport}
            disabled={isExporting}
            className="bg-[#1a1a1a] hover:bg-[#333] text-white px-6 transition-all duration-200"
          >
            {isExporting ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <Download className="w-4 h-4 mr-2" />}
            {isExporting ? '正生成图文报告...' : '导出 Word 报告'}
          </Button>
        </div>

        {/* Key Metrics Cards */}
        <div className="mb-12">
          <MetricsCards data={data} />
        </div>

        {/* Main Analysis Tabs */}
        <Tabs defaultValue="overview" className="space-y-8">
          <TabsList className="bg-white border border-[#e6e6e6] p-1">
            <TabsTrigger value="overview" className="data-[state=active]:bg-[#dc0c0c] data-[state=active]:text-white">
              总览
            </TabsTrigger>
            <TabsTrigger value="balance" className="data-[state=active]:bg-[#dc0c0c] data-[state=active]:text-white">
              资产负债表
            </TabsTrigger>
            <TabsTrigger value="cashflow" className="data-[state=active]:bg-[#dc0c0c] data-[state=active]:text-white">
              现金流量表
            </TabsTrigger>
            <TabsTrigger value="income" className="data-[state=active]:bg-[#dc0c0c] data-[state=active]:text-white">
              利润表
            </TabsTrigger>
            <TabsTrigger value="insights" className="data-[state=active]:bg-[#dc0c0c] data-[state=active]:text-white">
              洞察与建议
            </TabsTrigger>
          </TabsList>

          {/* Overview Tab */}
          <TabsContent value="overview" className="space-y-8">
            <div className="bg-white rounded-xl border border-[#e6e6e6] p-6 max-w-4xl mx-auto">
              <h3 className="text-lg font-semibold text-[#1a1a1a] mb-4 text-center">财务指标雷达图</h3>
              <MetricsRadarChart data={data} height={350} />
            </div>

            {/* Executive Summary */}
            <div className="bg-white rounded-xl border border-[#e6e6e6] p-8">
              <h3 className="text-lg font-semibold text-[#1a1a1a] mb-4">执行摘要</h3>
              <div className="prose max-w-none">
                <p className="text-[#666666] leading-relaxed">
                  基于对 {data.data.companyName} 财务报表的分析，公司整体财务状况
                  <span className={`font-semibold ${data.metrics.currentRatio > 1.5 && data.metrics.netMargin > 5 ? 'text-green-600' : 'text-yellow-600'}`}>
                    {data.metrics.currentRatio > 1.5 && data.metrics.netMargin > 5 ? '稳健' : '需要关注'}
                  </span>。
                  净利润率为 {data.metrics.netMargin}%，净资产收益率(ROE)为 {data.metrics.roe}%，
                  流动比率为 {data.metrics.currentRatio}。
                </p>
                <div className="grid md:grid-cols-3 gap-6 mt-6">
                  <div className="p-4 bg-[#f8f8f8] rounded-lg">
                    <p className="text-sm text-[#666666] mb-1">营业收入</p>
                    <p className="text-xl font-bold text-[#1a1a1a]">
                      ¥{(data.data.incomeStatement.revenue / 1000000).toFixed(1)}M
                    </p>
                  </div>
                  <div className="p-4 bg-[#f8f8f8] rounded-lg">
                    <p className="text-sm text-[#666666] mb-1">净利润</p>
                    <p className="text-xl font-bold text-[#1a1a1a]">
                      ¥{(data.data.incomeStatement.netIncome / 1000000).toFixed(1)}M
                    </p>
                  </div>
                  <div className="p-4 bg-[#f8f8f8] rounded-lg">
                    <p className="text-sm text-[#666666] mb-1">自由现金流</p>
                    <p className="text-xl font-bold text-[#1a1a1a]">
                      ¥{(data.metrics.freeCashFlow / 1000000).toFixed(1)}M
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </TabsContent>

          {/* Balance Sheet Tab */}
          <TabsContent value="balance" className="space-y-8">
            <div className="bg-white rounded-xl border border-[#e6e6e6] p-6 max-w-4xl mx-auto">
              <h3 className="text-lg font-semibold text-[#1a1a1a] mb-4 text-center">资产负债对称结构</h3>
              <BalanceSheetChart data={data} height={350} />
            </div>

            {/* Balance Sheet Details */}
            <div className="bg-white rounded-xl border border-[#e6e6e6] p-8">
              <h3 className="text-lg font-semibold text-[#1a1a1a] mb-6">资产负债表详情</h3>
              <div className="grid md:grid-cols-2 gap-8">
                <div>
                  <h4 className="font-medium text-[#1a1a1a] mb-4 flex items-center gap-2">
                    <FileBarChart className="w-5 h-5 text-[#dc0c0c]" />
                    资产
                  </h4>
                  <table className="w-full text-sm">
                    <tbody className="divide-y divide-[#e6e6e6]">
                      <tr>
                        <td className="py-2 text-[#666666]">货币资金</td>
                        <td className="py-2 text-right font-medium">
                          ¥{(data.data.balanceSheet.assets.currentAssets.cash / 1000000).toFixed(1)}M
                        </td>
                      </tr>
                      <tr>
                        <td className="py-2 text-[#666666]">应收账款</td>
                        <td className="py-2 text-right font-medium">
                          ¥{(data.data.balanceSheet.assets.currentAssets.accountsReceivable / 1000000).toFixed(1)}M
                        </td>
                      </tr>
                      <tr>
                        <td className="py-2 text-[#666666]">存货</td>
                        <td className="py-2 text-right font-medium">
                          ¥{(data.data.balanceSheet.assets.currentAssets.inventory / 1000000).toFixed(1)}M
                        </td>
                      </tr>
                      <tr>
                        <td className="py-2 text-[#666666]">固定资产</td>
                        <td className="py-2 text-right font-medium">
                          ¥{(data.data.balanceSheet.assets.nonCurrentAssets.propertyPlantEquipment / 1000000).toFixed(1)}M
                        </td>
                      </tr>
                    </tbody>
                  </table>
                </div>
                <div>
                  <h4 className="font-medium text-[#1a1a1a] mb-4 flex items-center gap-2">
                    <ArrowRightLeft className="w-5 h-5 text-[#dc0c0c]" />
                    负债与权益
                  </h4>
                  <table className="w-full text-sm">
                    <tbody className="divide-y divide-[#e6e6e6]">
                      <tr>
                        <td className="py-2 text-[#666666]">短期借款</td>
                        <td className="py-2 text-right font-medium">
                          ¥{(data.data.balanceSheet.liabilities.currentLiabilities.shortTermDebt / 1000000).toFixed(1)}M
                        </td>
                      </tr>
                      <tr>
                        <td className="py-2 text-[#666666]">长期借款</td>
                        <td className="py-2 text-right font-medium">
                          ¥{(data.data.balanceSheet.liabilities.nonCurrentLiabilities.longTermDebt / 1000000).toFixed(1)}M
                        </td>
                      </tr>
                      <tr>
                        <td className="py-2 text-[#666666]">实收资本</td>
                        <td className="py-2 text-right font-medium">
                          ¥{(data.data.balanceSheet.equity.shareCapital / 1000000).toFixed(1)}M
                        </td>
                      </tr>
                      <tr>
                        <td className="py-2 text-[#666666]">留存收益</td>
                        <td className="py-2 text-right font-medium">
                          ¥{(data.data.balanceSheet.equity.retainedEarnings / 1000000).toFixed(1)}M
                        </td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          </TabsContent>

          {/* Cash Flow Tab */}
          <TabsContent value="cashflow" className="space-y-8">
            <div className="bg-white rounded-xl border border-[#e6e6e6] p-6 max-w-4xl mx-auto">
              <h3 className="text-lg font-semibold text-[#1a1a1a] mb-4 text-center">现金流量分析</h3>
              <CashFlowChart data={data} height={350} />
            </div>

            {/* Cash Flow Summary */}
            <div className="bg-white rounded-xl border border-[#e6e6e6] p-8">
              <h3 className="text-lg font-semibold text-[#1a1a1a] mb-6">现金流量摘要</h3>
              <div className="grid md:grid-cols-3 gap-6">
                <div className="p-6 bg-[#f8f8f8] rounded-lg border-l-4 border-[#dc0c0c]">
                  <p className="text-sm text-[#666666] mb-2">经营活动现金流</p>
                  <p className="text-2xl font-bold text-[#1a1a1a]">
                    ¥{((data.data.cashFlow.operatingActivities.netIncome + 
                      data.data.cashFlow.operatingActivities.depreciation + 
                      data.data.cashFlow.operatingActivities.changesInWorkingCapital) / 1000000).toFixed(1)}M
                  </p>
                </div>
                <div className="p-6 bg-[#f8f8f8] rounded-lg border-l-4 border-[#1a1a1a]">
                  <p className="text-sm text-[#666666] mb-2">投资活动现金流</p>
                  <p className="text-2xl font-bold text-[#1a1a1a]">
                    ¥{((data.data.cashFlow.investingActivities.capitalExpenditure + 
                      data.data.cashFlow.investingActivities.acquisitions + 
                      data.data.cashFlow.investingActivities.saleOfAssets) / 1000000).toFixed(1)}M
                  </p>
                </div>
                <div className="p-6 bg-[#f8f8f8] rounded-lg border-l-4 border-[#666666]">
                  <p className="text-sm text-[#666666] mb-2">筹资活动现金流</p>
                  <p className="text-2xl font-bold text-[#1a1a1a]">
                    ¥{((data.data.cashFlow.financingActivities.debtIssuance + 
                      data.data.cashFlow.financingActivities.debtRepayment + 
                      data.data.cashFlow.financingActivities.dividendPaid + 
                      data.data.cashFlow.financingActivities.shareIssuance) / 1000000).toFixed(1)}M
                  </p>
                </div>
              </div>
            </div>
          </TabsContent>

          {/* Income Statement Tab */}
          <TabsContent value="income" className="space-y-8">
            <div className="bg-white rounded-xl border border-[#e6e6e6] p-6 max-w-4xl mx-auto">
              <h3 className="text-lg font-semibold text-[#1a1a1a] mb-4 text-center">利润瀑布流程分析</h3>
              <ProfitStructureChart data={data} height={350} />
            </div>

            {/* Income Statement Details */}
            <div className="bg-white rounded-xl border border-[#e6e6e6] p-8">
              <h3 className="text-lg font-semibold text-[#1a1a1a] mb-6">利润表详情</h3>
              <table className="w-full">
                <thead>
                  <tr className="border-b-2 border-[#1a1a1a]">
                    <th className="text-left py-3 font-semibold text-[#1a1a1a]">项目</th>
                    <th className="text-right py-3 font-semibold text-[#1a1a1a]">金额</th>
                    <th className="text-right py-3 font-semibold text-[#1a1a1a]">占收入比</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-[#e6e6e6]">
                  <tr>
                    <td className="py-3 text-[#666666]">营业收入</td>
                    <td className="py-3 text-right font-medium">
                      ¥{(data.data.incomeStatement.revenue / 1000000).toFixed(1)}M
                    </td>
                    <td className="py-3 text-right text-[#666666]">100.0%</td>
                  </tr>
                  <tr>
                    <td className="py-3 text-[#666666]">营业成本</td>
                    <td className="py-3 text-right font-medium">
                      ¥{(data.data.incomeStatement.costOfGoodsSold / 1000000).toFixed(1)}M
                    </td>
                    <td className="py-3 text-right text-[#666666]">
                      {((data.data.incomeStatement.costOfGoodsSold / data.data.incomeStatement.revenue) * 100).toFixed(1)}%
                    </td>
                  </tr>
                  <tr>
                    <td className="py-3 text-[#666666]">毛利润</td>
                    <td className="py-3 text-right font-medium">
                      ¥{(data.data.incomeStatement.grossProfit / 1000000).toFixed(1)}M
                    </td>
                    <td className="py-3 text-right text-[#666666]">
                      {((data.data.incomeStatement.grossProfit / data.data.incomeStatement.revenue) * 100).toFixed(1)}%
                    </td>
                  </tr>
                  <tr>
                    <td className="py-3 text-[#666666]">营业费用</td>
                    <td className="py-3 text-right font-medium">
                      ¥{(Object.values(data.data.incomeStatement.operatingExpenses).reduce((a, b) => a + b, 0) / 1000000).toFixed(1)}M
                    </td>
                    <td className="py-3 text-right text-[#666666]">
                      {((Object.values(data.data.incomeStatement.operatingExpenses).reduce((a, b) => a + b, 0) / data.data.incomeStatement.revenue) * 100).toFixed(1)}%
                    </td>
                  </tr>
                  <tr className="border-b-2 border-[#1a1a1a]">
                    <td className="py-3 font-semibold text-[#1a1a1a]">净利润</td>
                    <td className="py-3 text-right font-bold text-[#dc0c0c]">
                      ¥{(data.data.incomeStatement.netIncome / 1000000).toFixed(1)}M
                    </td>
                    <td className="py-3 text-right font-bold text-[#dc0c0c]">
                      {((data.data.incomeStatement.netIncome / data.data.incomeStatement.revenue) * 100).toFixed(1)}%
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </TabsContent>

          {/* Insights Tab */}
          <TabsContent value="insights" className="space-y-8">
            {/* Key Insights */}
            <div className="bg-white rounded-xl border border-[#e6e6e6] p-8">
              <h3 className="text-lg font-semibold text-[#1a1a1a] mb-6 flex items-center gap-2">
                <Lightbulb className="w-5 h-5 text-[#dc0c0c]" />
                关键洞察
              </h3>
              <ul className="space-y-4">
                {data.insights.map((insight, index) => (
                  <li key={index} className="flex items-start gap-3 p-4 bg-[#f8f8f8] rounded-lg">
                    <CheckCircle className="w-5 h-5 text-[#dc0c0c] flex-shrink-0 mt-0.5" />
                    <span className="text-[#666666]">{insight}</span>
                  </li>
                ))}
              </ul>
            </div>

            {/* Risk Warnings */}
            <div className="bg-white rounded-xl border border-[#e6e6e6] p-8">
              <h3 className="text-lg font-semibold text-[#1a1a1a] mb-6 flex items-center gap-2">
                <AlertTriangle className="w-5 h-5 text-[#e03000]" />
                风险提示
              </h3>
              <ul className="space-y-4">
                {data.risks.map((risk, index) => (
                  <li key={index} className="flex items-start gap-3 p-4 bg-[#fff8f8] rounded-lg border-l-4 border-[#e03000]">
                    <span className="text-[#666666]">{risk}</span>
                  </li>
                ))}
              </ul>
            </div>

            {/* Recommendations */}
            <div className="bg-white rounded-xl border border-[#e6e6e6] p-8">
              <h3 className="text-lg font-semibold text-[#1a1a1a] mb-6 flex items-center gap-2">
                <TrendingUp className="w-5 h-5 text-[#1a1a1a]" />
                改进建议
              </h3>
              <ul className="space-y-4">
                {data.recommendations.map((rec, index) => (
                  <li key={index} className="flex items-start gap-3 p-4 bg-[#f8f8f8] rounded-lg border-l-4 border-[#1a1a1a]">
                    <span className="text-[#666666]">{rec}</span>
                  </li>
                ))}
              </ul>
            </div>
          </TabsContent>
        </Tabs>
      </div>

      {/* 离屏隐藏区：专门用于导出 Word 图片截图，防止 Tab 隐藏带来的大小变化或纯白 */}
      <div style={{ position: 'fixed', top: 0, left: 0, width: '1000px', background: '#fff', opacity: 0, zIndex: -999, pointerEvents: 'none' }}>
        <div id="export-balance" className="p-8 bg-white"><h3 className="text-xl font-bold mb-4 text-[#1a1a1a] text-center">资产负债对称结构</h3><BalanceSheetChart data={data} height={450} /></div>
        <div id="export-cashflow" className="p-8 bg-white"><h3 className="text-xl font-bold mb-4 text-[#1a1a1a] text-center">现金流量分析</h3><CashFlowChart data={data} height={450} /></div>
        <div id="export-profit" className="p-8 bg-white"><h3 className="text-xl font-bold mb-4 text-[#1a1a1a] text-center">利润瀑布图分析</h3><ProfitStructureChart data={data} height={450} /></div>
        <div id="export-radar" className="p-8 bg-white"><h3 className="text-xl font-bold mb-4 text-[#1a1a1a] text-center">财务指标雷达图</h3><MetricsRadarChart data={data} height={450} /></div>
      </div>
    </section>
  );
};

export default AnalysisResult;
