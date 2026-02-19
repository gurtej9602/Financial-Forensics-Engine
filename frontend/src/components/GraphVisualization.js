import { useEffect, useRef } from 'react';
import cytoscape from 'cytoscape';

const CYTOSCAPE_STYLESHEET = [
  {
    selector: 'node',
    style: {
      'background-color': '#475569',
      'label': 'data(label)',
      'color': '#e2e8f0',
      'text-valign': 'center',
      'text-halign': 'center',
      'font-size': '10px',
      'width': '30px',
      'height': '30px',
      'border-width': '2px',
      'border-color': '#64748b'
    }
  },
  {
    selector: 'node[suspicious=true]',
    style: {
      'background-color': '#ef4444',
      'border-color': '#fca5a5',
      'border-width': '3px',
      'width': '40px',
      'height': '40px',
      'font-weight': 'bold'
    }
  },
  {
    selector: 'edge',
    style: {
      'width': 2,
      'line-color': '#334155',
      'target-arrow-color': '#334155',
      'target-arrow-shape': 'triangle',
      'curve-style': 'bezier',
      'arrow-scale': 1
    }
  },
  {
    selector: ':selected',
    style: {
      'background-color': '#3b82f6',
      'line-color': '#3b82f6',
      'target-arrow-color': '#3b82f6',
      'border-color': '#60a5fa'
    }
  }
];

const LAYOUT_CONFIG = {
  name: 'cose',
  animate: false, // Disabling animation to prevent frame-loop issues
  nodeRepulsion: 8000,
  idealEdgeLength: 100,
  edgeElasticity: 100,
  nestingFactor: 5,
  gravity: 80,
  numIter: 1000,
  initialTemp: 200,
  coolingFactor: 0.95,
  minTemp: 1.0,
  fit: true,
  padding: 30
};

const GraphVisualization = ({ graphData }) => {
  const containerRef = useRef(null);
  const cyRef = useRef(null);

  useEffect(() => {
    if (!containerRef.current || !graphData) return;

    // Destroy existing instance if any
    if (cyRef.current) {
      cyRef.current.destroy();
      cyRef.current = null;
    }

    // Initialize Cytoscape manually
    const cy = cytoscape({
      container: containerRef.current,
      elements: [
        ...(graphData.nodes || []),
        ...(graphData.edges || [])
      ],
      style: CYTOSCAPE_STYLESHEET,
      layout: LAYOUT_CONFIG,
      minZoom: 0.1,
      maxZoom: 5,
      wheelSensitivity: 0.2
    });

    cyRef.current = cy;

    // Handle node clicks
    cy.on('tap', 'node', (event) => {
      const node = event.target;
      const data = node.data();
      let info = `Account: ${data.id}\n`;
      info += `In-degree: ${data.in_degree}\n`;
      info += `Out-degree: ${data.out_degree}\n`;
      info += `Total Transactions: ${data.total_transactions}\n`;
      
      if (data.suspicious) {
        info += `\nSUSPICIOUS ACCOUNT\n`;
        info += `Patterns: ${data.patterns?.join(', ') || 'N/A'}\n`;
        info += `Ring IDs: ${data.ring_ids?.join(', ') || 'N/A'}`;
      }
      alert(info);
    });

    // Handle edge clicks
    cy.on('tap', 'edge', (event) => {
      const edge = event.target;
      const data = edge.data();
      let info = `Transaction Flow\n`;
      info += `From: ${data.source}\n`;
      info += `To: ${data.target}\n`;
      info += `Total Amount: $${data.total_amount?.toFixed(2)}\n`;
      info += `Transaction Count: ${data.count}`;
      alert(info);
    });

    return () => {
      if (cyRef.current) {
        cyRef.current.destroy();
        cyRef.current = null;
      }
    };
  }, [graphData]);

  return (
    <div className="relative" data-testid="graph-visualization">
      <div 
        ref={containerRef}
        className="bg-slate-900 rounded-lg border-2 border-slate-700" 
        style={{ height: '600px', width: '100%' }}
      />
      
      <div className="mt-4 flex items-center justify-center gap-6 text-sm">
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 rounded-full bg-slate-600 border-2 border-slate-400"></div>
          <span className="text-slate-300">Normal Account</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-5 h-5 rounded-full bg-red-500 border-2 border-red-300"></div>
          <span className="text-slate-300">Suspicious Account</span>
        </div>
        <div className="flex items-center gap-2">
          <svg className="w-6 h-6 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14 5l7 7m0 0l-7 7m7-7H3" />
          </svg>
          <span className="text-slate-300">Transaction Flow</span>
        </div>
      </div>
      
      <div className="mt-3 text-center text-sm text-slate-400">
        <p>💡 Click on nodes or edges to view detailed information</p>
      </div>
    </div>
  );
};

export default GraphVisualization;
