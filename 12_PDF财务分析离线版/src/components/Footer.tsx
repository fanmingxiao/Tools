import React from 'react';
import { BarChart3, Mail, Phone, MapPin } from 'lucide-react';

const Footer: React.FC = () => {
  const currentYear = new Date().getFullYear();

  const footerLinks = {
    product: [
      { label: '功能特性', href: '#features' },
      { label: '定价方案', href: '#' },
      { label: 'API 文档', href: '#' },
      { label: '更新日志', href: '#' },
    ],
    company: [
      { label: '关于我们', href: '#' },
      { label: '联系我们', href: '#' },
      { label: '加入我们', href: '#' },
      { label: '新闻动态', href: '#' },
    ],
    resources: [
      { label: '帮助中心', href: '#' },
      { label: '使用指南', href: '#' },
      { label: '案例研究', href: '#' },
      { label: '博客', href: '#' },
    ],
    legal: [
      { label: '隐私政策', href: '#' },
      { label: '服务条款', href: '#' },
      { label: '安全说明', href: '#' },
      { label: 'Cookie 政策', href: '#' },
    ],
  };

  return (
    <footer className="bg-[#1a1a1a] text-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <div className="grid md:grid-cols-2 lg:grid-cols-6 gap-12">
          {/* Brand */}
          <div className="lg:col-span-2">
            <a href="#" className="flex items-center gap-2 mb-6">
              <div className="w-10 h-10 bg-[#dc0c0c] rounded-lg flex items-center justify-center">
                <BarChart3 className="w-6 h-6 text-white" />
              </div>
              <span className="text-xl font-bold">财务分析</span>
            </a>
            <p className="text-[#999] mb-6 leading-relaxed">
              专业财务分析，为现代团队打造。<br />
              让数据驱动决策，让分析更简单。
            </p>
            <div className="space-y-3 text-sm text-[#999]">
              <div className="flex items-center gap-2">
                <Mail className="w-4 h-4" />
                <span>contact@financial-analysis.com</span>
              </div>
              <div className="flex items-center gap-2">
                <Phone className="w-4 h-4" />
                <span>400-888-8888</span>
              </div>
              <div className="flex items-center gap-2">
                <MapPin className="w-4 h-4" />
                <span>北京市朝阳区金融街</span>
              </div>
            </div>
          </div>

          {/* Links */}
          <div>
            <h4 className="font-semibold mb-4">产品</h4>
            <ul className="space-y-3">
              {footerLinks.product.map((link) => (
                <li key={link.label}>
                  <a
                    href={link.href}
                    className="text-sm text-[#999] hover:text-white transition-colors"
                  >
                    {link.label}
                  </a>
                </li>
              ))}
            </ul>
          </div>

          <div>
            <h4 className="font-semibold mb-4">公司</h4>
            <ul className="space-y-3">
              {footerLinks.company.map((link) => (
                <li key={link.label}>
                  <a
                    href={link.href}
                    className="text-sm text-[#999] hover:text-white transition-colors"
                  >
                    {link.label}
                  </a>
                </li>
              ))}
            </ul>
          </div>

          <div>
            <h4 className="font-semibold mb-4">资源</h4>
            <ul className="space-y-3">
              {footerLinks.resources.map((link) => (
                <li key={link.label}>
                  <a
                    href={link.href}
                    className="text-sm text-[#999] hover:text-white transition-colors"
                  >
                    {link.label}
                  </a>
                </li>
              ))}
            </ul>
          </div>

          <div>
            <h4 className="font-semibold mb-4">法律</h4>
            <ul className="space-y-3">
              {footerLinks.legal.map((link) => (
                <li key={link.label}>
                  <a
                    href={link.href}
                    className="text-sm text-[#999] hover:text-white transition-colors"
                  >
                    {link.label}
                  </a>
                </li>
              ))}
            </ul>
          </div>
        </div>

        {/* Bottom */}
        <div className="mt-16 pt-8 border-t border-[#333] flex flex-col md:flex-row justify-between items-center gap-4">
          <p className="text-sm text-[#999]">
            © {currentYear} 财务分析系统. 保留所有权利.
          </p>
          <div className="flex gap-6">
            <a href="#" className="text-sm text-[#999] hover:text-white transition-colors">
              隐私政策
            </a>
            <a href="#" className="text-sm text-[#999] hover:text-white transition-colors">
              服务条款
            </a>
            <a href="#" className="text-sm text-[#999] hover:text-white transition-colors">
              Cookie 设置
            </a>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
