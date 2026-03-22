import React from 'react';
import { ArrowRight, FileText, TrendingUp, Shield } from 'lucide-react';
import { Button } from '@/components/ui/button';

const Hero: React.FC = () => {
  return (
    <section className="min-h-screen flex items-center pt-16 bg-gradient-to-br from-white via-white to-[#f8f8f8]">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 w-full">
        <div className="grid lg:grid-cols-2 gap-12 items-center">
          {/* Left Content */}
          <div className="space-y-8">
            <div className="inline-flex items-center gap-2 px-4 py-2 bg-[#fff8f8] rounded-full border border-[#dc0c0c]/20">
              <span className="w-2 h-2 bg-[#dc0c0c] rounded-full animate-pulse" />
              <span className="text-sm text-[#dc0c0c] font-medium">智能财务分析系统</span>
            </div>
            
            <h1 className="text-4xl md:text-5xl lg:text-6xl font-bold text-[#1a1a1a] leading-tight">
              像专业会计师一样
              <span className="text-[#dc0c0c]">分析财务</span>
            </h1>
            
            <p className="text-lg text-[#666666] max-w-xl leading-relaxed">
              轻松从您的财务 PDF 中提取洞察。上传文档，让我们的智能系统完成其余工作。
              支持资产负债表、现金流量表和利润表的全面分析。
            </p>
            
            <div className="flex flex-wrap gap-4">
              <Button
                size="lg"
                className="bg-[#dc0c0c] hover:bg-[#b80a0a] text-white px-8 transition-all duration-300 hover:scale-105 hover:shadow-lg"
                onClick={() => document.getElementById('upload')?.scrollIntoView({ behavior: 'smooth' })}
              >
                开始免费试用
                <ArrowRight className="w-4 h-4 ml-2" />
              </Button>
              <Button
                size="lg"
                variant="outline"
                className="border-[#1a1a1a] text-[#1a1a1a] hover:bg-[#1a1a1a] hover:text-white px-8 transition-all duration-300"
                onClick={() => document.getElementById('features')?.scrollIntoView({ behavior: 'smooth' })}
              >
                了解更多
              </Button>
            </div>
            
            {/* Stats */}
            <div className="flex gap-8 pt-4">
              <div>
                <p className="text-2xl font-bold text-[#1a1a1a]">2.5分钟</p>
                <p className="text-sm text-[#666666]">平均分析时间</p>
              </div>
              <div className="w-px bg-[#e6e6e6]" />
              <div>
                <p className="text-2xl font-bold text-[#1a1a1a]">99.7%</p>
                <p className="text-sm text-[#666666]">数据准确度</p>
              </div>
              <div className="w-px bg-[#e6e6e6]" />
              <div>
                <p className="text-2xl font-bold text-[#1a1a1a]">50+</p>
                <p className="text-sm text-[#666666]">支持货币</p>
              </div>
            </div>
          </div>
          
          {/* Right Content - 3D Chart Illustration */}
          <div className="relative hidden lg:block">
            <div className="relative w-full aspect-square max-w-lg mx-auto">
              {/* Background Circle */}
              <div className="absolute inset-0 bg-gradient-to-br from-[#f5f5f5] to-white rounded-full" />
              
              {/* Floating Elements */}
              <div className="absolute top-1/4 left-1/4 w-32 h-32 bg-white rounded-2xl shadow-xl flex flex-col items-center justify-center transform -rotate-6 hover:rotate-0 transition-transform duration-500">
                <TrendingUp className="w-10 h-10 text-[#dc0c0c] mb-2" />
                <span className="text-xs text-[#666666]">营收增长</span>
                <span className="text-lg font-bold text-[#1a1a1a]">+24%</span>
              </div>
              
              <div className="absolute top-1/3 right-1/4 w-28 h-28 bg-white rounded-2xl shadow-xl flex flex-col items-center justify-center transform rotate-6 hover:rotate-0 transition-transform duration-500">
                <FileText className="w-8 h-8 text-[#1a1a1a] mb-2" />
                <span className="text-xs text-[#666666]">报表</span>
                <span className="text-sm font-bold text-[#1a1a1a]">PDF</span>
              </div>
              
              <div className="absolute bottom-1/4 left-1/3 w-36 h-36 bg-white rounded-2xl shadow-xl flex flex-col items-center justify-center transform rotate-3 hover:rotate-0 transition-transform duration-500">
                <Shield className="w-10 h-10 text-[#dc0c0c] mb-2" />
                <span className="text-xs text-[#666666]">数据安全</span>
                <span className="text-lg font-bold text-[#1a1a1a]">加密</span>
              </div>
              
              {/* Center Chart */}
              <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-40 h-40 bg-gradient-to-br from-[#dc0c0c] to-[#e03000] rounded-2xl shadow-2xl flex flex-col items-center justify-center">
                <div className="text-white text-center">
                  <p className="text-3xl font-bold">AI</p>
                  <p className="text-xs opacity-80">智能分析</p>
                </div>
              </div>
              
              {/* Decorative Dots */}
              <div className="absolute top-10 right-10 w-3 h-3 bg-[#dc0c0c] rounded-full animate-bounce" />
              <div className="absolute bottom-20 left-10 w-2 h-2 bg-[#1a1a1a] rounded-full animate-pulse" />
              <div className="absolute top-1/2 right-5 w-2 h-2 bg-[#666666] rounded-full" />
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default Hero;
