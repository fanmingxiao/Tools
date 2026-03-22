import React, { useState } from 'react';
import { CheckCircle, AlertCircle, Save } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import type { FinancialData } from '@/types/financial';

interface DataVerificationProps {
  initialData: FinancialData;
  onConfirm: (data: FinancialData) => void;
  onCancel: () => void;
}

const DataVerification: React.FC<DataVerificationProps> = ({ initialData, onConfirm, onCancel }) => {
  const [data, setData] = useState<FinancialData>(initialData);

  // Helper to deep update values easily given a path like ['balanceSheet', 'assets', 'currentAssets', 'cash']
  const updateValue = (path: string[], value: number) => {
    setData((prev) => {
      const newData = JSON.parse(JSON.stringify(prev));
      let current = newData;
      for (let i = 0; i < path.length - 1; i++) {
        current = current[path[i]];
      }
      current[path[path.length - 1]] = value;
      return newData;
    });
  };

  // Helper to calculate totals
  const totalAssets = Object.values(data.balanceSheet.assets.currentAssets).reduce((a, b) => a + b, 0) + 
                      Object.values(data.balanceSheet.assets.nonCurrentAssets).reduce((a, b) => a + b, 0);
  const totalLiabilities = Object.values(data.balanceSheet.liabilities.currentLiabilities).reduce((a, b) => a + b, 0) + 
                           Object.values(data.balanceSheet.liabilities.nonCurrentLiabilities).reduce((a, b) => a + b, 0);
  const totalEquity = Object.values(data.balanceSheet.equity).reduce((a, b) => a + b, 0);

  const isBalanced = Math.abs(totalAssets - (totalLiabilities + totalEquity)) < 100; // Allow small rounding error

  return (
    <section className="py-24 bg-[#f8f8f8]">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="mb-8 p-6 bg-white rounded-xl shadow-sm border border-[#e6e6e6]">
          <h2 className="text-2xl font-bold text-[#1a1a1a] mb-4">校对提取数据</h2>
          <p className="text-[#666666] mb-6">我们已尝试从 PDF 中提取以下财务数据。由于自动提取可能存在误差，请在生成报告前仔细核实和调整。</p>

          {!isBalanced && (
            <div className="flex items-center gap-2 p-4 mb-6 bg-red-50 text-red-600 rounded-lg border border-red-200">
              <AlertCircle className="w-5 h-5 flex-shrink-0" />
              <p className="text-sm">资产负债表不平！当前总资产: {totalAssets.toLocaleString()}，负债+权益: {(totalLiabilities + totalEquity).toLocaleString()}，差额: {(totalAssets - (totalLiabilities + totalEquity)).toLocaleString()}</p>
            </div>
          )}
          {isBalanced && (
            <div className="flex items-center gap-2 p-4 mb-6 bg-green-50 text-green-600 rounded-lg border border-green-200">
              <CheckCircle className="w-5 h-5 flex-shrink-0" />
              <p className="text-sm">资产负债表平衡，校验通过！ (总计: {totalAssets.toLocaleString()})</p>
            </div>
          )}

          <Tabs defaultValue="balance" className="w-full">
            <TabsList className="mb-4 bg-[#f8f8f8] p-1">
              <TabsTrigger value="balance" className="data-[state=active]:bg-[#dc0c0c] data-[state=active]:text-white">资产负债表</TabsTrigger>
              <TabsTrigger value="income" className="data-[state=active]:bg-[#dc0c0c] data-[state=active]:text-white">利润表</TabsTrigger>
              <TabsTrigger value="cash" className="data-[state=active]:bg-[#dc0c0c] data-[state=active]:text-white">现金流量表</TabsTrigger>
            </TabsList>

            <TabsContent value="balance" className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-4">
                  <h3 className="font-semibold text-lg border-b pb-2">资产</h3>
                  <div>
                    <Label>货币资金</Label>
                    <Input type="number" value={data.balanceSheet.assets.currentAssets.cash} onChange={e => updateValue(['balanceSheet', 'assets', 'currentAssets', 'cash'], parseFloat(e.target.value) || 0)} />
                  </div>
                  <div>
                    <Label>应收账款</Label>
                    <Input type="number" value={data.balanceSheet.assets.currentAssets.accountsReceivable} onChange={e => updateValue(['balanceSheet', 'assets', 'currentAssets', 'accountsReceivable'], parseFloat(e.target.value) || 0)} />
                  </div>
                  <div>
                    <Label>存货</Label>
                    <Input type="number" value={data.balanceSheet.assets.currentAssets.inventory} onChange={e => updateValue(['balanceSheet', 'assets', 'currentAssets', 'inventory'], parseFloat(e.target.value) || 0)} />
                  </div>
                  <div>
                    <Label>固定资产</Label>
                    <Input type="number" value={data.balanceSheet.assets.nonCurrentAssets.propertyPlantEquipment} onChange={e => updateValue(['balanceSheet', 'assets', 'nonCurrentAssets', 'propertyPlantEquipment'], parseFloat(e.target.value) || 0)} />
                  </div>
                </div>
                
                <div className="space-y-4">
                  <h3 className="font-semibold text-lg border-b pb-2">负债与所有者权益</h3>
                  <div>
                    <Label>短期借款</Label>
                    <Input type="number" value={data.balanceSheet.liabilities.currentLiabilities.shortTermDebt} onChange={e => updateValue(['balanceSheet', 'liabilities', 'currentLiabilities', 'shortTermDebt'], parseFloat(e.target.value) || 0)} />
                  </div>
                  <div>
                    <Label>应付账款</Label>
                    <Input type="number" value={data.balanceSheet.liabilities.currentLiabilities.accountsPayable} onChange={e => updateValue(['balanceSheet', 'liabilities', 'currentLiabilities', 'accountsPayable'], parseFloat(e.target.value) || 0)} />
                  </div>
                  <div>
                    <Label>长期借款</Label>
                    <Input type="number" value={data.balanceSheet.liabilities.nonCurrentLiabilities.longTermDebt} onChange={e => updateValue(['balanceSheet', 'liabilities', 'nonCurrentLiabilities', 'longTermDebt'], parseFloat(e.target.value) || 0)} />
                  </div>
                  <div>
                    <Label>实收资本 / 股本</Label>
                    <Input type="number" value={data.balanceSheet.equity.shareCapital} onChange={e => updateValue(['balanceSheet', 'equity', 'shareCapital'], parseFloat(e.target.value) || 0)} />
                  </div>
                  <div>
                    <Label>留存收益 / 未分配利润</Label>
                    <Input type="number" value={data.balanceSheet.equity.retainedEarnings} onChange={e => updateValue(['balanceSheet', 'equity', 'retainedEarnings'], parseFloat(e.target.value) || 0)} />
                  </div>
                </div>
              </div>
            </TabsContent>

            <TabsContent value="income" className="space-y-6">
               <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-4">
                  <h3 className="font-semibold text-lg border-b pb-2">收入与成本</h3>
                  <div>
                    <Label>营业收入</Label>
                    <Input type="number" value={data.incomeStatement.revenue} onChange={e => updateValue(['incomeStatement', 'revenue'], parseFloat(e.target.value) || 0)} />
                  </div>
                  <div>
                    <Label>营业成本</Label>
                    <Input type="number" value={data.incomeStatement.costOfGoodsSold} onChange={e => updateValue(['incomeStatement', 'costOfGoodsSold'], parseFloat(e.target.value) || 0)} />
                  </div>
                  <div>
                    <Label>毛利润</Label>
                    <Input type="number" value={data.incomeStatement.grossProfit} onChange={e => updateValue(['incomeStatement', 'grossProfit'], parseFloat(e.target.value) || 0)} />
                  </div>
                </div>
                 <div className="space-y-4">
                  <h3 className="font-semibold text-lg border-b pb-2">利润</h3>
                  <div>
                    <Label>营业利润</Label>
                    <Input type="number" value={data.incomeStatement.operatingIncome} onChange={e => updateValue(['incomeStatement', 'operatingIncome'], parseFloat(e.target.value) || 0)} />
                  </div>
                  <div>
                    <Label>净利润</Label>
                    <Input type="number" value={data.incomeStatement.netIncome} onChange={e => updateValue(['incomeStatement', 'netIncome'], parseFloat(e.target.value) || 0)} />
                  </div>
                </div>
               </div>
            </TabsContent>

            <TabsContent value="cash" className="space-y-6">
               <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-4">
                  <h3 className="font-semibold text-lg border-b pb-2">现金流摘要</h3>
                  <div>
                    <Label>经营活动产生的现金流量净额（此处用净利润等模拟）</Label>
                    <Input type="number" value={data.cashFlow.operatingActivities.netIncome} onChange={e => updateValue(['cashFlow', 'operatingActivities', 'netIncome'], parseFloat(e.target.value) || 0)} />
                  </div>
                   <div>
                    <Label>投资活动产生的资本支出</Label>
                    <Input type="number" value={data.cashFlow.investingActivities.capitalExpenditure} onChange={e => updateValue(['cashFlow', 'investingActivities', 'capitalExpenditure'], parseFloat(e.target.value) || 0)} />
                  </div>
                   <div>
                    <Label>筹资活动债务发行</Label>
                    <Input type="number" value={data.cashFlow.financingActivities.debtIssuance} onChange={e => updateValue(['cashFlow', 'financingActivities', 'debtIssuance'], parseFloat(e.target.value) || 0)} />
                  </div>
                </div>
               </div>
            </TabsContent>
          </Tabs>
          
          <div className="mt-8 flex gap-4 justify-end border-t pt-6">
            <Button variant="outline" onClick={onCancel}>
              取消，重新上传
            </Button>
            <Button className="bg-[#dc0c0c] hover:bg-[#b80a0a] text-white" onClick={() => onConfirm(data)}>
              <Save className="w-4 h-4 mr-2" />
              确认无误，生成报告
            </Button>
          </div>
        </div>
      </div>
    </section>
  );
};

export default DataVerification;
