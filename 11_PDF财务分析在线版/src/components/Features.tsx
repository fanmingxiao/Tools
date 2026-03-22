import React from 'react';
import { FileBarChart, ArrowRightLeft, TrendingUp, FileSearch, Shield, Brain } from 'lucide-react';

interface FeatureCardProps {
  icon: React.ReactNode;
  title: string;
  description: string;
}

const FeatureCard: React.FC<FeatureCardProps> = ({ icon, title, description }) => (
  <div className="group bg-white rounded-xl border border-[#e6e6e6] p-8 hover:shadow-xl transition-all duration-500 hover:-translate-y-1">
    <div className="w-14 h-14 bg-[#f5f5f5] rounded-xl flex items-center justify-center mb-6 group-hover:bg-[#dc0c0c] transition-colors duration-300">
      <div className="text-[#dc0c0c] group-hover:text-white transition-colors duration-300">
        {icon}
      </div>
    </div>
    <h3 className="text-xl font-bold text-[#1a1a1a] mb-3">{title}</h3>
    <p className="text-[#666666] leading-relaxed">{description}</p>
  </div>
);

const Features: React.FC = () => {
  const features = [
    {
      icon: <FileBarChart className="w-7 h-7" />,
      title: '资产负债表分析',
      description: '全面了解公司的财务状况、资产构成和负债结构。深入分析流动资产、固定资产、短期负债和长期负债的分布情况。',
    },
    {
      icon: <ArrowRightLeft className="w-7 h-7" />,
      title: '现金流量表洞察',
      description: '追踪资金流动，识别运营、投资和融资活动中的趋势。分析自由现金流和经营现金流质量。',
    },
    {
      icon: <TrendingUp className="w-7 h-7" />,
      title: '利润表解读',
      description: '分析收入、成本和盈利能力，随时间变化的详细分解。计算毛利率、净利率等关键盈利指标。',
    },
  ];

  const additionalFeatures = [
    {
      icon: <FileSearch className="w-6 h-6" />,
      title: '即时 PDF 解析',
      description: '在几秒钟内从财务 PDF 中提取数据。支持所有主要格式，自动识别表格和关键数据。',
    },
    {
      icon: <Shield className="w-6 h-6" />,
      title: '安全处理',
      description: '企业级加密保护您的财务数据。本地处理，数据不会上传到云端，确保信息安全。',
    },
    {
      icon: <Brain className="w-6 h-6" />,
      title: '智能洞察',
      description: 'AI 驱动的分析，在数据中发现模式和异常。自动生成专业的财务分析报告。',
    },
  ];

  return (
    <section id="features" className="py-24 bg-[#f8f8f8]">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section Header */}
        <div className="text-center mb-16">
          <h2 className="text-3xl md:text-4xl font-bold text-[#1a1a1a] mb-4">
            强大的财务分析工具
          </h2>
          <p className="text-lg text-[#666666] max-w-2xl mx-auto">
            您需要的一切，用于理解财务数据。从三大报表到关键指标，全面覆盖。
          </p>
        </div>

        {/* Main Features Grid */}
        <div className="grid md:grid-cols-3 gap-8 mb-16">
          {features.map((feature, index) => (
            <FeatureCard key={index} {...feature} />
          ))}
        </div>

        {/* Additional Features */}
        <div className="grid md:grid-cols-3 gap-6">
          {additionalFeatures.map((feature, index) => (
            <div
              key={index}
              className="flex items-start gap-4 p-6 bg-white rounded-lg border border-[#e6e6e6] hover:border-[#dc0c0c] transition-colors duration-300"
            >
              <div className="w-10 h-10 bg-[#f5f5f5] rounded-lg flex items-center justify-center flex-shrink-0 text-[#dc0c0c]">
                {feature.icon}
              </div>
              <div>
                <h4 className="font-semibold text-[#1a1a1a] mb-1">{feature.title}</h4>
                <p className="text-sm text-[#666666]">{feature.description}</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default Features;
