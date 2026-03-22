import React, { useState, useEffect } from 'react';
import { BarChart3, Menu, X } from 'lucide-react';
import { Button } from '@/components/ui/button';

const Navbar: React.FC = () => {
  const [isScrolled, setIsScrolled] = useState(false);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 50);
    };

    window.addEventListener('scroll', handleScroll, { passive: true });
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const navLinks = [
    { label: '功能特性', href: '#features' },
    { label: '财务分析', href: '#analysis' },
    { label: '数据可视化', href: '#charts' },
    { label: '关于我们', href: '#about' },
  ];

  return (
    <nav
      className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${
        isScrolled
          ? 'bg-white/95 backdrop-blur-md shadow-sm'
          : 'bg-transparent'
      }`}
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <a href="#" className="flex items-center gap-2 group">
            <div className="w-8 h-8 bg-[#dc0c0c] rounded-lg flex items-center justify-center transition-transform duration-300 group-hover:scale-110">
              <BarChart3 className="w-5 h-5 text-white" />
            </div>
            <span className="text-lg font-bold text-[#1a1a1a]">财务分析</span>
          </a>

          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center gap-8">
            {navLinks.map((link) => (
              <a
                key={link.href}
                href={link.href}
                className="text-sm text-[#666666] hover:text-[#1a1a1a] transition-colors duration-200 relative group"
              >
                {link.label}
                <span className="absolute -bottom-1 left-1/2 w-0 h-0.5 bg-[#dc0c0c] transition-all duration-300 group-hover:w-full group-hover:left-0" />
              </a>
            ))}
          </div>

          {/* CTA Button */}
          <div className="hidden md:block">
            <Button
              className="bg-[#1a1a1a] hover:bg-[#333] text-white text-sm px-6 transition-all duration-300 hover:scale-105"
              onClick={() => document.getElementById('upload')?.scrollIntoView({ behavior: 'smooth' })}
            >
              开始分析
            </Button>
          </div>

          {/* Mobile Menu Button */}
          <button
            className="md:hidden p-2"
            onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
          >
            {isMobileMenuOpen ? (
              <X className="w-6 h-6 text-[#1a1a1a]" />
            ) : (
              <Menu className="w-6 h-6 text-[#1a1a1a]" />
            )}
          </button>
        </div>

        {/* Mobile Menu */}
        {isMobileMenuOpen && (
          <div className="md:hidden bg-white border-t border-[#e6e6e6] py-4">
            <div className="flex flex-col gap-4">
              {navLinks.map((link) => (
                <a
                  key={link.href}
                  href={link.href}
                  className="text-sm text-[#666666] hover:text-[#1a1a1a] px-4 py-2"
                  onClick={() => setIsMobileMenuOpen(false)}
                >
                  {link.label}
                </a>
              ))}
              <div className="px-4 pt-2">
                <Button
                  className="w-full bg-[#1a1a1a] hover:bg-[#333] text-white"
                  onClick={() => {
                    setIsMobileMenuOpen(false);
                    document.getElementById('upload')?.scrollIntoView({ behavior: 'smooth' });
                  }}
                >
                  开始分析
                </Button>
              </div>
            </div>
          </div>
        )}
      </div>
    </nav>
  );
};

export default Navbar;
