import {
  Document,
  Packer,
  Paragraph,
  TextRun,
  Table,
  TableRow,
  TableCell,
  HeadingLevel,
  AlignmentType,
  WidthType,
  PageBreak,
  ImageRun
} from 'docx';
import { saveAs } from 'file-saver';
import type { AnalysisResult } from '@/types/financial';

export interface ReportImages {
  balance?: string;
  profit?: string;
  radar?: string;
  cashflow?: string;
}

// 辅助方法：将 base64 字符串转化为 Uint8Array 处理 (前端通用)
const base64ToUint8Array = (base64: string) => {
  const base64Data = base64.replace(/^data:image\/\w+;base64,/, "");
  const binaryString = window.atob(base64Data);
  const len = binaryString.length;
  const bytes = new Uint8Array(len);
  for (let i = 0; i < len; i++) {
    bytes[i] = binaryString.charCodeAt(i);
  }
  return bytes;
};

// 格式化数字
function formatNumber(num: number, currency: string = 'CNY'): string {
  if (Math.abs(num) >= 100000000) {
    return `${(num / 100000000).toFixed(2)}亿 ${currency}`;
  } else if (Math.abs(num) >= 10000) {
    return `${(num / 10000).toFixed(2)}万 ${currency}`;
  }
  return `${num.toLocaleString()} ${currency}`;
}

const createHeading = (text: string) => {
  return new Paragraph({
    text: text,
    heading: HeadingLevel.HEADING_2,
    spacing: { before: 400, after: 200 },
  });
};

const createParagraph = (text: string) => {
  return new Paragraph({
    children: [new TextRun({ text, size: 24 })],
    spacing: { before: 100, after: 100, line: 360 },
  });
};

const createListItems = (items: string[]) => {
  return items.map(
    (item) =>
      new Paragraph({
        children: [new TextRun({ text: item, size: 24 })],
        bullet: { level: 0 },
        spacing: { before: 100, after: 100 },
      })
  );
};

const createEmptyLine = () => new Paragraph({ text: "" });

const createImageParagraph = (base64Str?: string, width = 600, height = 350) => {
  if (!base64Str) return createEmptyLine();
  return new Paragraph({
    alignment: AlignmentType.CENTER,
    children: [
      new ImageRun({
        data: base64ToUint8Array(base64Str),
        transformation: { width, height },
        type: "png",
      }),
    ],
    spacing: { before: 200, after: 200 },
  });
};

export async function exportToWord(data: AnalysisResult, filename?: string, images?: ReportImages): Promise<void> {
  const { data: financialData, metrics, insights, risks, recommendations } = data;

  const doc = new Document({
    sections: [
      {
        properties: {},
        children: [
          // 封面
          new Paragraph({
            children: [
              new TextRun({
                text: "财务分析报告",
                bold: true,
                size: 72,
              }),
            ],
            alignment: AlignmentType.CENTER,
            spacing: { before: 2000, after: 1000 },
          }),
          new Paragraph({
            children: [
              new TextRun({
                text: financialData.companyName,
                size: 36,
                color: "dc0c0c",
              }),
            ],
            alignment: AlignmentType.CENTER,
            spacing: { after: 2000 },
          }),
          new Paragraph({
            children: [
              new TextRun({ text: `报告日期：${financialData.reportDate}`, size: 24, color: "999999" }),
            ],
            alignment: AlignmentType.CENTER,
          }),
          new Paragraph({
            children: [
              new TextRun({ text: `货币单位：${financialData.currency}`, size: 24, color: "999999" }),
            ],
            alignment: AlignmentType.CENTER,
          }),
          new Paragraph({
            children: [
              new TextRun({ text: `编制单位：财务分析系统`, size: 24, color: "999999" }),
            ],
            alignment: AlignmentType.CENTER,
          }),

          new Paragraph({ children: [new PageBreak()] }),

          // 一、执行摘要
          createHeading("一、执行摘要"),
          createParagraph(`本报告基于${financialData.companyName}的财务报表数据，对公司的财务状况、经营成果和现金流量进行了全面分析。旨在为管理层和投资者提供决策参考。`),
          createParagraph(`从关键财务指标来看，公司净利润率为${metrics.netMargin}%，净资产收益率(ROE)为${metrics.roe}%，流动比率为${metrics.currentRatio}，整体财务状况${metrics.currentRatio > 1.5 && metrics.netMargin > 5 ? '稳健' : '需要关注'}。`),

          // 二、关键财务指标
          createHeading("二、关键财务指标"),
          new Table({
            width: { size: 100, type: WidthType.PERCENTAGE },
            margins: { top: 100, bottom: 100, left: 100, right: 100 },
            rows: [
              new TableRow({
                children: [
                  new TableCell({ children: [new Paragraph({ children: [new TextRun({ text: '指标名称', bold: true })] })] }),
                  new TableCell({ children: [new Paragraph({ children: [new TextRun({ text: '数值', bold: true })] })] }),
                  new TableCell({ children: [new Paragraph({ children: [new TextRun({ text: '指标名称', bold: true })] })] }),
                  new TableCell({ children: [new Paragraph({ children: [new TextRun({ text: '数值', bold: true })] })] }),
                ],
              }),
              new TableRow({
                children: [
                  new TableCell({ children: [new Paragraph("净利润率")] }),
                  new TableCell({ children: [new Paragraph(`${metrics.netMargin}%`)] }),
                  new TableCell({ children: [new Paragraph("净资产收益率")] }),
                  new TableCell({ children: [new Paragraph(`${metrics.roe}%`)] }),
                ],
              }),
              new TableRow({
                children: [
                  new TableCell({ children: [new Paragraph("流动比率")] }),
                  new TableCell({ children: [new Paragraph(`${metrics.currentRatio}`)] }),
                  new TableCell({ children: [new Paragraph("速动比率")] }),
                  new TableCell({ children: [new Paragraph(`${metrics.quickRatio}`)] }),
                ],
              }),
              new TableRow({
                children: [
                  new TableCell({ children: [new Paragraph("总资产收益率")] }),
                  new TableCell({ children: [new Paragraph(`${metrics.roa}%`)] }),
                  new TableCell({ children: [new Paragraph("资产负债率")] }),
                  new TableCell({ children: [new Paragraph(`${(metrics.debtToAsset * 100).toFixed(1)}%`)] }),
                ],
              }),
            ],
          }),

          createEmptyLine(),
          createHeading("三、财务图表分析"),
          createParagraph("本节提供了核心财务数据的图表化呈现，直观反映企业的经营结构和质量特征："),
          
          images?.profit ? new Paragraph({ children: [new TextRun({ text: "1. 利润瀑布图流程分析", bold: true, size: 28 })] }) : createEmptyLine(),
          createImageParagraph(images?.profit),
          
          images?.balance ? new Paragraph({ children: [new TextRun({ text: "2. 资产负债对称结构图", bold: true, size: 28 })] }) : createEmptyLine(),
          createImageParagraph(images?.balance),
          
          images?.cashflow ? new Paragraph({ children: [new TextRun({ text: "3. 现金流量分析", bold: true, size: 28 })] }) : createEmptyLine(),
          createImageParagraph(images?.cashflow),
          
          images?.radar ? new Paragraph({ children: [new TextRun({ text: "4. 财务指标雷达图", bold: true, size: 28 })] }) : createEmptyLine(),
          createImageParagraph(images?.radar),

          createEmptyLine(),
          createHeading("四、资产负债表与利润表摘要"),
          new Table({
            width: { size: 100, type: WidthType.PERCENTAGE },
            rows: [
              new TableRow({
                children: [
                  new TableCell({ children: [new Paragraph({ children: [new TextRun({ text: '核心科目', bold: true })] })] }),
                  new TableCell({ children: [new Paragraph({ children: [new TextRun({ text: '金额', bold: true })] })] }),
                ],
              }),
              new TableRow({
                children: [
                  new TableCell({ children: [new Paragraph("货币资金")] }),
                  new TableCell({ children: [new Paragraph(formatNumber(financialData.balanceSheet.assets.currentAssets.cash))] }),
                ],
              }),
              new TableRow({
                children: [
                  new TableCell({ children: [new Paragraph("应收账款")] }),
                  new TableCell({ children: [new Paragraph(formatNumber(financialData.balanceSheet.assets.currentAssets.accountsReceivable))] }),
                ],
              }),
              new TableRow({
                children: [
                  new TableCell({ children: [new Paragraph("营业收入")] }),
                  new TableCell({ children: [new Paragraph(formatNumber(financialData.incomeStatement.revenue))] }),
                ],
              }),
              new TableRow({
                children: [
                  new TableCell({ children: [new Paragraph("营业利润")] }),
                  new TableCell({ children: [new Paragraph(formatNumber(financialData.incomeStatement.operatingIncome))] }),
                ],
              }),
              new TableRow({
                children: [
                  new TableCell({ children: [new Paragraph("净利润")] }),
                  new TableCell({ children: [new Paragraph(formatNumber(financialData.incomeStatement.netIncome))] }),
                ],
              }),
            ],
          }),

          createEmptyLine(),
          createHeading("五、财务洞察"),
          ...createListItems(insights),

          createHeading("六、风险提示"),
          ...createListItems(risks),

          createHeading("七、改进建议"),
          ...createListItems(recommendations),

          createEmptyLine(),
          createEmptyLine(),
          new Paragraph({
            children: [
              new TextRun({ text: "免责声明：本报告基于提取的财务数据进行自动分析生成，仅供参考，不构成投资建议。", color: "999999", size: 20 }),
            ],
          }),
        ],
      },
    ],
  });

  const blob = await Packer.toBlob(doc);
  saveAs(blob, `${filename || financialData.companyName}_财务分析报告.docx`);
}
