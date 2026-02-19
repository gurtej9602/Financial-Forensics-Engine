import { useState } from "react";
import "@/App.css";
import axios from "axios";
import GraphVisualization from "./components/GraphVisualization";
import FraudRingTable from "./components/FraudRingTable";
import FileUpload from "./components/FileUpload";
import ResultsSummary from "./components/ResultsSummary";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || "";
const API = `${BACKEND_URL}/api`;

function App() {
  const [analysisResults, setAnalysisResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleFileUpload = async (file) => {
    // Clear previous results to unmount graph before starting new analysis
    setAnalysisResults(null);
    setLoading(true);
    setError(null);
    
    try {
      const formData = new FormData();
      formData.append('file', file);
      
      const response = await axios.post(`${API}/upload-csv`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });
      
      // Delay setting results slightly to ensure clean unmount/remount
      setTimeout(() => {
        setAnalysisResults(response.data);
      }, 50);
    } catch (err) {
      console.error('Upload error:', err);
      setError(err.response?.data?.detail || 'Error uploading file. Please check the CSV format.');
    } finally {
      setLoading(false);
    }
  };

  const downloadJSON = () => {
    if (!analysisResults) return;
    
    // Prepare JSON in exact format required
    const outputData = {
      suspicious_accounts: analysisResults.suspicious_accounts,
      fraud_rings: analysisResults.fraud_rings,
      summary: analysisResults.summary
    };
    
    const blob = new Blob([JSON.stringify(outputData, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `fraud_detection_results_${new Date().getTime()}.json`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
      {/* Header */}
      <div className="bg-slate-800/50 border-b border-slate-700 backdrop-blur-sm">
        <div className="container mx-auto px-6 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-white flex items-center gap-3" data-testid="app-title">
                <svg className="w-8 h-8 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                </svg>
                Financial Forensics Engine
              </h1>
              <p className="text-slate-400 mt-1">Money Muling Detection using Graph Analysis</p>
            </div>
            <div className="text-slate-400 text-sm">
              <span className="bg-blue-500/20 text-blue-300 px-3 py-1 rounded-full">RIFT 2026 Hackathon</span>
            </div>
          </div>
        </div>
      </div>

      <div className="container mx-auto px-6 py-8">
        {/* File Upload Section */}
        {!analysisResults && (
          <div className="max-w-2xl mx-auto">
            <FileUpload 
              onFileUpload={handleFileUpload} 
              loading={loading}
              error={error}
            />
          </div>
        )}

        {/* Results Section */}
        {analysisResults && (
          <div className="space-y-6">
            {/* Summary and Actions */}
            <div className="flex items-center justify-between">
              <ResultsSummary summary={analysisResults.summary} />
              <div className="flex gap-3">
                <button
                  onClick={downloadJSON}
                  className="px-6 py-2.5 bg-green-600 hover:bg-green-700 text-white rounded-lg font-medium transition-colors flex items-center gap-2"
                  data-testid="download-json-button"
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                  Download JSON
                </button>
                <button
                  onClick={() => {
                    setAnalysisResults(null);
                    setError(null);
                  }}
                  className="px-6 py-2.5 bg-slate-700 hover:bg-slate-600 text-white rounded-lg font-medium transition-colors"
                  data-testid="upload-new-button"
                >
                  Upload New File
                </button>
              </div>
            </div>

            {/* Graph Visualization */}
            <div className="bg-slate-800/50 rounded-xl border border-slate-700 p-6">
              <h2 className="text-xl font-bold text-white mb-4 flex items-center gap-2" data-testid="graph-section-title">
                <svg className="w-6 h-6 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7" />
                </svg>
                Transaction Network Graph
              </h2>
              <GraphVisualization graphData={analysisResults.graph_data} />
            </div>

            {/* Fraud Rings Table */}
            <div className="bg-slate-800/50 rounded-xl border border-slate-700 p-6">
              <h2 className="text-xl font-bold text-white mb-4 flex items-center gap-2" data-testid="fraud-rings-section-title">
                <svg className="w-6 h-6 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                </svg>
                Detected Fraud Rings
              </h2>
              <FraudRingTable rings={analysisResults.fraud_rings} />
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;