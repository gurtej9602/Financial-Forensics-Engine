const ResultsSummary = ({ summary }) => {
  return (
    <div className="flex items-center gap-6" data-testid="results-summary">
      <div className="bg-slate-700/50 rounded-lg px-4 py-3 border border-slate-600">
        <div className="text-slate-400 text-xs font-medium uppercase tracking-wide">Total Accounts</div>
        <div className="text-white text-2xl font-bold mt-1">{summary.total_accounts_analyzed}</div>
      </div>
      
      <div className="bg-red-500/10 rounded-lg px-4 py-3 border border-red-500/30">
        <div className="text-red-300 text-xs font-medium uppercase tracking-wide">Suspicious</div>
        <div className="text-red-400 text-2xl font-bold mt-1">{summary.suspicious_accounts_flagged}</div>
      </div>
      
      <div className="bg-orange-500/10 rounded-lg px-4 py-3 border border-orange-500/30">
        <div className="text-orange-300 text-xs font-medium uppercase tracking-wide">Fraud Rings</div>
        <div className="text-orange-400 text-2xl font-bold mt-1">{summary.fraud_rings_detected}</div>
      </div>
      
      <div className="bg-blue-500/10 rounded-lg px-4 py-3 border border-blue-500/30">
        <div className="text-blue-300 text-xs font-medium uppercase tracking-wide">Processing Time</div>
        <div className="text-blue-400 text-2xl font-bold mt-1">{summary.processing_time_seconds}s</div>
      </div>
    </div>
  );
};

export default ResultsSummary;