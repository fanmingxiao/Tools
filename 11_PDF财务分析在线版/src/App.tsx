import { useState } from 'react';
import type { FinancialData, AnalysisResult as AnalysisResultType } from '@/types/financial';
import { analyzeFinancialData } from '@/lib/financialAnalyzer';

// Components
import Navbar from '@/components/Navbar';
import Hero from '@/components/Hero';
import Features from '@/components/Features';
import UploadSection from '@/components/UploadSection';
import DataVerification from '@/components/DataVerification';
import AnalysisResult from '@/components/AnalysisResult';
import Footer from '@/components/Footer';

function App() {
  const [extractedData, setExtractedData] = useState<FinancialData | null>(null);
  const [analysisResult, setAnalysisResult] = useState<AnalysisResultType | null>(null);

  const handleDataExtracted = (data: FinancialData) => {
    setExtractedData(data);
    setAnalysisResult(null);
    setTimeout(() => {
      document.getElementById('verification')?.scrollIntoView({ behavior: 'smooth' });
    }, 100);
  };

  const handleVerificationConfirm = (data: FinancialData) => {
    const result = analyzeFinancialData(data);
    setAnalysisResult(result);
    // Hide verification form when confirmed
    setExtractedData(null);
    setTimeout(() => {
      document.getElementById('analysis')?.scrollIntoView({ behavior: 'smooth' });
    }, 100);
  };

  const handleVerificationCancel = () => {
    setExtractedData(null);
  };

  return (
    <div className="min-h-screen bg-white">
      <Navbar />
      
      <main>
        <Hero />
        <Features />
        <UploadSection onAnalysisComplete={handleDataExtracted} />
        {extractedData && (
          <div id="verification">
            <DataVerification 
              initialData={extractedData} 
              onConfirm={handleVerificationConfirm} 
              onCancel={handleVerificationCancel} 
            />
          </div>
        )}
        {analysisResult && <AnalysisResult data={analysisResult} />}
      </main>
      
      <Footer />
    </div>
  );
}

export default App;
