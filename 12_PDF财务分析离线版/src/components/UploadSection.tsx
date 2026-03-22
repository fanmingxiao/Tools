import React, { useState, useRef } from 'react';
import { Upload, FileText, X, Loader2, CheckCircle } from 'lucide-react';
import { Button } from '@/components/ui/button';
import type { FinancialData } from '@/types/financial';
import { generateMockFinancialData } from '@/lib/mockDataGenerator';
import { parsePDFEngine } from '@/lib/pdfParser';

interface UploadSectionProps {
  onAnalysisComplete: (data: FinancialData) => void;
}

const UploadSection: React.FC<UploadSectionProps> = ({ onAnalysisComplete }) => {
  const [isDragging, setIsDragging] = useState(false);
  const [file, setFile] = useState<File | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    
    const droppedFile = e.dataTransfer.files[0];
    if (droppedFile && droppedFile.type === 'application/pdf') {
      setFile(droppedFile);
      setError(null);
    } else {
      setError('请上传 PDF 格式的文件');
    }
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (selectedFile) {
      setFile(selectedFile);
      setError(null);
    }
  };

  const handleAnalyze = async () => {
    if (!file) return;
    
    setIsAnalyzing(true);
    setError(null);
    
    try {
      const data = await parsePDFEngine(file);
      onAnalysisComplete(data);
    } catch (err) {
      console.error(err);
      setError(`分析出错：${err instanceof Error ? err.message : String(err)}`);
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleClear = () => {
    setFile(null);
    setError(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  return (
    <section id="upload" className="py-24 bg-white">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section Header */}
        <div className="text-center mb-12">
          <h2 className="text-3xl md:text-4xl font-bold text-[#1a1a1a] mb-4">
            上传财务报告
          </h2>
          <p className="text-lg text-[#666666]">
            支持 PDF 格式的资产负债表、现金流量表和利润表
          </p>
        </div>

        {/* Upload Area */}
        <div
          className={`relative border-2 border-dashed rounded-2xl p-12 text-center transition-all duration-300 ${
            isDragging
              ? 'border-[#dc0c0c] bg-[#fff8f8]'
              : 'border-[#e6e6e6] bg-[#f8f8f8] hover:border-[#999]'
          }`}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          onClick={() => fileInputRef.current?.click()}
        >
          <input
            ref={fileInputRef}
            type="file"
            accept=".pdf"
            className="hidden"
            onChange={handleFileSelect}
          />

          {!file ? (
            <div className="space-y-4">
              <div className="w-20 h-20 bg-white rounded-full flex items-center justify-center mx-auto shadow-sm">
                <Upload className="w-10 h-10 text-[#dc0c0c]" />
              </div>
              <div>
                <p className="text-lg font-medium text-[#1a1a1a] mb-2">
                  点击或拖拽上传 PDF 文件
                </p>
                <p className="text-sm text-[#666666]">
                  支持格式：.pdf（最大 10MB）
                </p>
              </div>
            </div>
          ) : (
            <div className="space-y-6">
              <div className="flex items-center justify-center gap-4">
                <div className="w-16 h-16 bg-[#dc0c0c]/10 rounded-xl flex items-center justify-center">
                  <FileText className="w-8 h-8 text-[#dc0c0c]" />
                </div>
                <div className="text-left">
                  <p className="font-medium text-[#1a1a1a]">{file.name}</p>
                  <p className="text-sm text-[#666666]">
                    {(file.size / 1024 / 1024).toFixed(2)} MB
                  </p>
                </div>
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    handleClear();
                  }}
                  className="p-2 hover:bg-[#e6e6e6] rounded-full transition-colors"
                >
                  <X className="w-5 h-5 text-[#666666]" />
                </button>
              </div>

              <div className="flex gap-4 justify-center">
                <Button
                  onClick={(e) => {
                    e.stopPropagation();
                    handleAnalyze();
                  }}
                  disabled={isAnalyzing}
                  className="bg-[#dc0c0c] hover:bg-[#b80a0a] text-white px-8"
                >
                  {isAnalyzing ? (
                    <>
                      <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                      分析中...
                    </>
                  ) : (
                    <>
                      <CheckCircle className="w-4 h-4 mr-2" />
                      开始分析
                    </>
                  )}
                </Button>
              </div>
            </div>
          )}
        </div>

        {/* Error Message */}
        {error && (
          <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg text-red-600 text-sm">
            {error}
          </div>
        )}

        {/* Demo Note */}
        <div className="mt-8 text-center">
          <p className="text-sm text-[#999]">
            没有 PDF 文件？
            <button
              onClick={() => {
                const mockData = generateMockFinancialData('示例科技有限公司');
                onAnalysisComplete(mockData);
              }}
              className="text-[#dc0c0c] hover:underline ml-1"
            >
              使用示例数据体验
            </button>
          </p>
        </div>
      </div>
    </section>
  );
};

export default UploadSection;
