import { useCallback, useState } from 'react';

const FileUpload = ({ onFileUpload, loading, error }) => {
  const [dragActive, setDragActive] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);

  const handleDrag = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  }, []);

  const handleDrop = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const file = e.dataTransfer.files[0];
      if (file.name.endsWith('.csv')) {
        setSelectedFile(file);
      }
    }
  }, []);

  const handleChange = (e) => {
    e.preventDefault();
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      if (file.name.endsWith('.csv')) {
        setSelectedFile(file);
      }
    }
  };

  const handleUpload = () => {
    if (selectedFile) {
      onFileUpload(selectedFile);
    }
  };

  return (
    <div className="space-y-6">
      {/* Upload Area */}
      <div className="bg-slate-800/50 rounded-xl border border-slate-700 p-8">
        <div className="text-center mb-6">
          <h2 className="text-2xl font-bold text-white mb-2" data-testid="upload-title">
            Upload Transaction Data
          </h2>
          <p className="text-slate-400">
            Upload a CSV file containing transaction data to detect money muling patterns
          </p>
        </div>

        <div
          className={`relative border-2 border-dashed rounded-lg p-12 transition-all ${
            dragActive
              ? 'border-blue-400 bg-blue-500/10'
              : 'border-slate-600 hover:border-slate-500'
          }`}
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
          data-testid="file-upload-area"
        >
          <input
            type="file"
            id="file-input"
            accept=".csv"
            onChange={handleChange}
            className="hidden"
            disabled={loading}
          />
          
          <div className="text-center">
            <svg
              className="mx-auto h-12 w-12 text-slate-400"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
              />
            </svg>
            
            <div className="mt-4">
              {selectedFile ? (
                <div className="space-y-3">
                  <div className="flex items-center justify-center gap-2 text-green-400">
                    <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                    </svg>
                    <span className="font-medium">{selectedFile.name}</span>
                  </div>
                  <button
                    onClick={handleUpload}
                    disabled={loading}
                    className="px-6 py-2.5 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                    data-testid="analyze-button"
                  >
                    {loading ? (
                      <span className="flex items-center gap-2">
                        <svg className="animate-spin h-5 w-5" fill="none" viewBox="0 0 24 24">
                          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                        </svg>
                        Analyzing...
                      </span>
                    ) : (
                      'Analyze Transactions'
                    )}
                  </button>
                </div>
              ) : (
                <label htmlFor="file-input" className="cursor-pointer">
                  <span className="text-blue-400 hover:text-blue-300 font-medium">
                    Click to upload
                  </span>
                  <span className="text-slate-400"> or drag and drop</span>
                </label>
              )}
            </div>
            
            {!selectedFile && (
              <p className="mt-2 text-sm text-slate-500">
                CSV file with transaction data (max 10MB)
              </p>
            )}
          </div>
        </div>

        {error && (
          <div className="mt-4 p-4 bg-red-500/10 border border-red-500/50 rounded-lg" data-testid="error-message">
            <div className="flex items-start gap-3">
              <svg className="w-5 h-5 text-red-400 flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
              </svg>
              <div>
                <h4 className="text-red-400 font-medium">Error</h4>
                <p className="text-red-300 text-sm mt-1">{error}</p>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* CSV Format Info */}
      <div className="bg-slate-800/50 rounded-xl border border-slate-700 p-6">
        <h3 className="text-lg font-semibold text-white mb-3">Required CSV Format</h3>
        <div className="overflow-x-auto">
          <table className="min-w-full text-sm">
            <thead>
              <tr className="border-b border-slate-700">
                <th className="text-left py-2 px-3 text-slate-300 font-medium">Column</th>
                <th className="text-left py-2 px-3 text-slate-300 font-medium">Type</th>
                <th className="text-left py-2 px-3 text-slate-300 font-medium">Description</th>
              </tr>
            </thead>
            <tbody className="text-slate-400">
              <tr className="border-b border-slate-700/50">
                <td className="py-2 px-3 font-mono text-blue-300">transaction_id</td>
                <td className="py-2 px-3">String</td>
                <td className="py-2 px-3">Unique transaction identifier</td>
              </tr>
              <tr className="border-b border-slate-700/50">
                <td className="py-2 px-3 font-mono text-blue-300">sender_id</td>
                <td className="py-2 px-3">String</td>
                <td className="py-2 px-3">Account ID of sender</td>
              </tr>
              <tr className="border-b border-slate-700/50">
                <td className="py-2 px-3 font-mono text-blue-300">receiver_id</td>
                <td className="py-2 px-3">String</td>
                <td className="py-2 px-3">Account ID of receiver</td>
              </tr>
              <tr className="border-b border-slate-700/50">
                <td className="py-2 px-3 font-mono text-blue-300">amount</td>
                <td className="py-2 px-3">Float</td>
                <td className="py-2 px-3">Transaction amount</td>
              </tr>
              <tr>
                <td className="py-2 px-3 font-mono text-blue-300">timestamp</td>
                <td className="py-2 px-3">DateTime</td>
                <td className="py-2 px-3">Format: YYYY-MM-DD HH:MM:SS</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default FileUpload;