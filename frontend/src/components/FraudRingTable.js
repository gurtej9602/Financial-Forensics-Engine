const FraudRingTable = ({ rings }) => {
  if (!rings || rings.length === 0) {
    return (
      <div className="text-center py-12" data-testid="no-rings-message">
        <svg className="mx-auto h-12 w-12 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <p className="mt-4 text-lg text-slate-300 font-medium">No fraud rings detected</p>
        <p className="mt-2 text-sm text-slate-400">All transactions appear legitimate</p>
      </div>
    );
  }

  const getRiskBadgeColor = (score) => {
    if (score >= 85) return 'bg-red-500/20 text-red-300 border-red-500/50';
    if (score >= 70) return 'bg-orange-500/20 text-orange-300 border-orange-500/50';
    return 'bg-yellow-500/20 text-yellow-300 border-yellow-500/50';
  };

  return (
    <div className="overflow-x-auto" data-testid="fraud-rings-table">
      <table className="min-w-full">
        <thead>
          <tr className="border-b border-slate-700">
            <th className="text-left py-3 px-4 text-slate-300 font-semibold">Ring ID</th>
            <th className="text-left py-3 px-4 text-slate-300 font-semibold">Pattern Type</th>
            <th className="text-left py-3 px-4 text-slate-300 font-semibold">Member Count</th>
            <th className="text-left py-3 px-4 text-slate-300 font-semibold">Risk Score</th>
            <th className="text-left py-3 px-4 text-slate-300 font-semibold">Member Account IDs</th>
          </tr>
        </thead>
        <tbody>
          {rings.map((ring, index) => (
            <tr 
              key={ring.ring_id} 
              className="border-b border-slate-700/50 hover:bg-slate-700/30 transition-colors"
              data-testid={`fraud-ring-row-${index}`}
            >
              <td className="py-3 px-4">
                <span className="font-mono text-blue-400 font-medium">{ring.ring_id}</span>
              </td>
              <td className="py-3 px-4">
                <span className="text-slate-300">{ring.pattern_type}</span>
              </td>
              <td className="py-3 px-4">
                <span className="text-slate-300">{ring.member_accounts.length}</span>
              </td>
              <td className="py-3 px-4">
                <span className={`px-3 py-1 rounded-full text-sm font-semibold border ${getRiskBadgeColor(ring.risk_score)}`}>
                  {ring.risk_score.toFixed(1)}
                </span>
              </td>
              <td className="py-3 px-4">
                <div className="max-w-md">
                  <span className="text-slate-400 text-sm font-mono break-all">
                    {ring.member_accounts.join(', ')}
                  </span>
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default FraudRingTable;