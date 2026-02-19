from fastapi import FastAPI, APIRouter, UploadFile, File, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
try:
    from mongomock_motor import AsyncMongoMockClient
except ImportError:
    AsyncMongoMockClient = None
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Dict, Any, Set, Tuple
import uuid
from datetime import datetime, timezone, timedelta
import pandas as pd
import networkx as nx
from io import StringIO
import time
from collections import defaultdict
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection with fallback
mongo_url = os.environ.get('MONGO_URL')
db_name = os.environ.get('DB_NAME', 'forensics_db')

if not mongo_url or mongo_url.lower() == 'mock':
    print("⚠️ MONGO_URL not provided or set to 'mock'. Using in-memory database fallback.")
    if AsyncMongoMockClient:
        client = AsyncMongoMockClient()
    else:
        print("❌ mongomock-motor not available. Using real client with dummy URL.")
        client = AsyncIOMotorClient("mongodb://localhost:27017")
else:
    client = AsyncIOMotorClient(mongo_url)

db = client[db_name]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")


# Define Models
class StatusCheck(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_name: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class StatusCheckCreate(BaseModel):
    client_name: str

class SuspiciousAccount(BaseModel):
    account_id: str
    suspicion_score: float
    detected_patterns: List[str]
    ring_id: str

class FraudRing(BaseModel):
    ring_id: str
    member_accounts: List[str]
    pattern_type: str
    risk_score: float

class AnalysisSummary(BaseModel):
    total_accounts_analyzed: int
    suspicious_accounts_flagged: int
    fraud_rings_detected: int
    processing_time_seconds: float

class AnalysisResult(BaseModel):
    suspicious_accounts: List[SuspiciousAccount]
    fraud_rings: List[FraudRing]
    summary: AnalysisSummary
    graph_data: Dict[str, Any]  # For visualization


class MoneyMulingDetector:
    """Graph-based money muling detection engine"""
    
    def __init__(self):
        self.graph = nx.DiGraph()
        self.transactions = []
        self.suspicious_accounts = {}
        self.fraud_rings = []
        self.account_metadata = defaultdict(lambda: {
            'total_transactions': 0,
            'in_degree': 0,
            'out_degree': 0,
            'patterns': set(),
            'ring_ids': set()
        })
        
    def load_transactions(self, df: pd.DataFrame):
        """Load transaction data into graph"""
        self.transactions = df.to_dict('records')
        
        # Build directed graph
        for _, row in df.iterrows():
            sender = row['sender_id']
            receiver = row['receiver_id']
            amount = row['amount']
            timestamp = pd.to_datetime(row['timestamp'])
            
            # Add edge with transaction metadata
            if self.graph.has_edge(sender, receiver):
                # Update existing edge
                self.graph[sender][receiver]['transactions'].append({
                    'amount': amount,
                    'timestamp': timestamp,
                    'transaction_id': row['transaction_id']
                })
                self.graph[sender][receiver]['total_amount'] += amount
                self.graph[sender][receiver]['count'] += 1
            else:
                # Create new edge
                self.graph.add_edge(sender, receiver, 
                                  transactions=[{
                                      'amount': amount,
                                      'timestamp': timestamp,
                                      'transaction_id': row['transaction_id']
                                  }],
                                  total_amount=amount,
                                  count=1)
            
            # Track account metadata
            if sender not in self.graph.nodes:
                self.graph.add_node(sender)
            if receiver not in self.graph.nodes:
                self.graph.add_node(receiver)
                
            self.account_metadata[sender]['total_transactions'] += 1
            self.account_metadata[sender]['out_degree'] = self.graph.out_degree(sender)
            self.account_metadata[receiver]['total_transactions'] += 1
            self.account_metadata[receiver]['in_degree'] = self.graph.in_degree(receiver)
    
    def detect_cycles(self) -> List[List[str]]:
        """Detect circular fund routing (cycles of length 3-5)"""
        detected_cycles = []
        
        try:
            # Find all simple cycles
            all_cycles = list(nx.simple_cycles(self.graph))
            
            # Filter cycles of length 3-5
            for cycle in all_cycles:
                if 3 <= len(cycle) <= 5:
                    detected_cycles.append(cycle)
                    
        except Exception as e:
            logging.error(f"Error in cycle detection: {e}")
        
        return detected_cycles
    
    def detect_smurfing(self, min_connections: int = 10) -> Tuple[List[Dict], List[Dict]]:
        """Detect smurfing patterns (fan-in and fan-out)"""
        fan_in_patterns = []
        fan_out_patterns = []
        
        for node in self.graph.nodes():
            in_degree = self.graph.in_degree(node)
            out_degree = self.graph.out_degree(node)
            
            # Fan-in: Multiple accounts send to one aggregator
            if in_degree >= min_connections:
                senders = list(self.graph.predecessors(node))
                
                # Check temporal clustering (72-hour window)
                timestamps = []
                for sender in senders:
                    if self.graph.has_edge(sender, node):
                        edge_data = self.graph[sender][node]
                        for tx in edge_data['transactions']:
                            timestamps.append(tx['timestamp'])
                
                if timestamps:
                    timestamps.sort()
                    time_span = (timestamps[-1] - timestamps[0]).total_seconds() / 3600
                    
                    # If transactions happen within 72 hours, higher suspicion
                    temporal_factor = 1.5 if time_span <= 72 else 1.0
                    
                    fan_in_patterns.append({
                        'aggregator': node,
                        'senders': senders,
                        'count': in_degree,
                        'temporal_factor': temporal_factor,
                        'pattern_type': 'fan_in'
                    })
            
            # Fan-out: One account disperses to many receivers
            if out_degree >= min_connections:
                receivers = list(self.graph.successors(node))
                
                # Check temporal clustering
                timestamps = []
                for receiver in receivers:
                    if self.graph.has_edge(node, receiver):
                        edge_data = self.graph[node][receiver]
                        for tx in edge_data['transactions']:
                            timestamps.append(tx['timestamp'])
                
                if timestamps:
                    timestamps.sort()
                    time_span = (timestamps[-1] - timestamps[0]).total_seconds() / 3600
                    
                    temporal_factor = 1.5 if time_span <= 72 else 1.0
                    
                    fan_out_patterns.append({
                        'disperser': node,
                        'receivers': receivers,
                        'count': out_degree,
                        'temporal_factor': temporal_factor,
                        'pattern_type': 'fan_out'
                    })
        
        return fan_in_patterns, fan_out_patterns
    
    def detect_layered_shells(self, min_hops: int = 3) -> List[List[str]]:
        """Detect layered shell networks (chains through low-activity accounts)"""
        shell_chains = []
        
        # Find all simple paths up to length 6 (to capture 3+ hops)
        for source in self.graph.nodes():
            for target in self.graph.nodes():
                if source == target:
                    continue
                
                try:
                    # Get all simple paths between source and target
                    paths = list(nx.all_simple_paths(self.graph, source, target, cutoff=6))
                    
                    for path in paths:
                        if len(path) >= min_hops + 1:  # min_hops + 1 nodes = min_hops edges
                            # Check if intermediate nodes are low-activity (shell accounts)
                            is_shell_chain = True
                            for i in range(1, len(path) - 1):  # Check intermediate nodes only
                                intermediate = path[i]
                                total_tx = self.account_metadata[intermediate]['total_transactions']
                                
                                # Shell account: only 2-3 total transactions
                                if total_tx < 2 or total_tx > 3:
                                    is_shell_chain = False
                                    break
                            
                            if is_shell_chain and path not in shell_chains:
                                shell_chains.append(path)
                                
                except nx.NetworkXNoPath:
                    continue
                except Exception as e:
                    logging.error(f"Error finding paths: {e}")
                    continue
        
        return shell_chains
    
    def calculate_suspicion_score(self, account: str, patterns: List[str], 
                                 temporal_factor: float = 1.0) -> float:
        """Calculate suspicion score (0-100) based on detected patterns"""
        base_scores = {
            'cycle': 85,
            'fan_in': 65,
            'fan_out': 65,
            'smurfing': 70,
            'shell': 75
        }
        
        score = 0.0
        
        for pattern in patterns:
            if pattern in base_scores:
                score += base_scores[pattern]
        
        # Apply temporal factor for smurfing
        score *= temporal_factor
        
        # Cap at 100
        score = min(score, 100.0)
        
        # Round to 2 decimal places
        return round(score, 2)
    
    def analyze(self) -> Dict[str, Any]:
        """Run complete analysis and return results"""
        start_time = time.time()
        
        # 1. Detect cycles
        cycles = self.detect_cycles()
        
        # 2. Detect smurfing
        fan_in_patterns, fan_out_patterns = self.detect_smurfing()
        
        # 3. Detect layered shells
        shell_chains = self.detect_layered_shells()
        
        # 4. Build suspicious accounts and fraud rings
        ring_counter = 1
        
        # Process cycles
        for cycle in cycles:
            ring_id = f"RING_{ring_counter:03d}"
            ring_counter += 1
            
            for account in cycle:
                if account not in self.suspicious_accounts:
                    self.suspicious_accounts[account] = {
                        'patterns': set(),
                        'ring_ids': set(),
                        'temporal_factor': 1.0
                    }
                
                self.suspicious_accounts[account]['patterns'].add('cycle')
                self.suspicious_accounts[account]['ring_ids'].add(ring_id)
            
            # Create fraud ring
            risk_score = 90.0  # Cycles are high risk
            self.fraud_rings.append({
                'ring_id': ring_id,
                'member_accounts': cycle,
                'pattern_type': 'Circular Fund Routing',
                'risk_score': risk_score
            })
        
        # Process fan-in patterns
        for pattern in fan_in_patterns:
            ring_id = f"RING_{ring_counter:03d}"
            ring_counter += 1
            
            aggregator = pattern['aggregator']
            senders = pattern['senders']
            temporal_factor = pattern['temporal_factor']
            
            # Mark all participants as suspicious
            all_members = [aggregator] + senders
            
            for account in all_members:
                if account not in self.suspicious_accounts:
                    self.suspicious_accounts[account] = {
                        'patterns': set(),
                        'ring_ids': set(),
                        'temporal_factor': 1.0
                    }
                
                self.suspicious_accounts[account]['patterns'].add('fan_in')
                self.suspicious_accounts[account]['ring_ids'].add(ring_id)
                self.suspicious_accounts[account]['temporal_factor'] = max(
                    self.suspicious_accounts[account]['temporal_factor'],
                    temporal_factor
                )
            
            risk_score = 70.0 * temporal_factor
            self.fraud_rings.append({
                'ring_id': ring_id,
                'member_accounts': all_members,
                'pattern_type': 'Smurfing (Fan-In)',
                'risk_score': round(risk_score, 2)
            })
        
        # Process fan-out patterns
        for pattern in fan_out_patterns:
            ring_id = f"RING_{ring_counter:03d}"
            ring_counter += 1
            
            disperser = pattern['disperser']
            receivers = pattern['receivers']
            temporal_factor = pattern['temporal_factor']
            
            all_members = [disperser] + receivers
            
            for account in all_members:
                if account not in self.suspicious_accounts:
                    self.suspicious_accounts[account] = {
                        'patterns': set(),
                        'ring_ids': set(),
                        'temporal_factor': 1.0
                    }
                
                self.suspicious_accounts[account]['patterns'].add('fan_out')
                self.suspicious_accounts[account]['ring_ids'].add(ring_id)
                self.suspicious_accounts[account]['temporal_factor'] = max(
                    self.suspicious_accounts[account]['temporal_factor'],
                    temporal_factor
                )
            
            risk_score = 70.0 * temporal_factor
            self.fraud_rings.append({
                'ring_id': ring_id,
                'member_accounts': all_members,
                'pattern_type': 'Smurfing (Fan-Out)',
                'risk_score': round(risk_score, 2)
            })
        
        # Process shell chains
        for chain in shell_chains:
            ring_id = f"RING_{ring_counter:03d}"
            ring_counter += 1
            
            for account in chain:
                if account not in self.suspicious_accounts:
                    self.suspicious_accounts[account] = {
                        'patterns': set(),
                        'ring_ids': set(),
                        'temporal_factor': 1.0
                    }
                
                self.suspicious_accounts[account]['patterns'].add('shell')
                self.suspicious_accounts[account]['ring_ids'].add(ring_id)
            
            risk_score = 80.0  # Shell networks are high risk
            self.fraud_rings.append({
                'ring_id': ring_id,
                'member_accounts': chain,
                'pattern_type': 'Layered Shell Network',
                'risk_score': risk_score
            })
        
        # 5. Calculate suspicion scores
        suspicious_accounts_list = []
        
        for account, data in self.suspicious_accounts.items():
            patterns = list(data['patterns'])
            temporal_factor = data['temporal_factor']
            suspicion_score = self.calculate_suspicion_score(
                account, patterns, temporal_factor
            )
            
            # Use the first ring_id for the account
            ring_id = sorted(list(data['ring_ids']))[0] if data['ring_ids'] else "RING_000"
            
            suspicious_accounts_list.append({
                'account_id': account,
                'suspicion_score': suspicion_score,
                'detected_patterns': patterns,
                'ring_id': ring_id
            })
        
        # Sort by suspicion score (descending)
        suspicious_accounts_list.sort(key=lambda x: x['suspicion_score'], reverse=True)
        
        # 6. Calculate processing time
        processing_time = time.time() - start_time
        
        # 7. Prepare graph data for visualization
        graph_data = self.prepare_graph_data()
        
        # 8. Build summary
        summary = {
            'total_accounts_analyzed': len(self.graph.nodes()),
            'suspicious_accounts_flagged': len(suspicious_accounts_list),
            'fraud_rings_detected': len(self.fraud_rings),
            'processing_time_seconds': round(processing_time, 2)
        }
        
        return {
            'suspicious_accounts': suspicious_accounts_list,
            'fraud_rings': self.fraud_rings,
            'summary': summary,
            'graph_data': graph_data
        }
    
    def prepare_graph_data(self) -> Dict[str, Any]:
        """Prepare graph data for Cytoscape.js visualization"""
        nodes = []
        edges = []
        
        # Get suspicious account IDs
        suspicious_ids = set(self.suspicious_accounts.keys())
        
        # Add nodes
        for node in self.graph.nodes():
            is_suspicious = node in suspicious_ids
            node_data = {
                'data': {
                    'id': node,
                    'label': node,
                    'suspicious': is_suspicious,
                    'in_degree': self.graph.in_degree(node),
                    'out_degree': self.graph.out_degree(node),
                    'total_transactions': self.account_metadata[node]['total_transactions']
                }
            }
            
            if is_suspicious:
                account_data = self.suspicious_accounts[node]
                node_data['data']['patterns'] = list(account_data['patterns'])
                node_data['data']['ring_ids'] = list(account_data['ring_ids'])
            
            nodes.append(node_data)
        
        # Add edges
        for source, target, data in self.graph.edges(data=True):
            edge_data = {
                'data': {
                    'id': f"{source}-{target}",
                    'source': source,
                    'target': target,
                    'total_amount': data['total_amount'],
                    'count': data['count']
                }
            }
            edges.append(edge_data)
        
        return {
            'nodes': nodes,
            'edges': edges
        }


# API Routes
@api_router.get("/")
async def root():
    return {"message": "Financial Forensics Engine API - Money Muling Detection"}

@api_router.post("/upload-csv")
async def upload_csv(file: UploadFile = File(...)):
    """Upload CSV file and analyze for money muling patterns"""
    
    try:
        # Validate file type
        if not file.filename.endswith('.csv'):
            raise HTTPException(status_code=400, detail="Only CSV files are accepted")
        
        # Read CSV content
        content = await file.read()
        csv_string = content.decode('utf-8')
        
        # Parse CSV
        df = pd.read_csv(StringIO(csv_string))
        
        # Validate required columns
        required_columns = ['transaction_id', 'sender_id', 'receiver_id', 'amount', 'timestamp']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            raise HTTPException(
                status_code=400,
                detail=f"Missing required columns: {', '.join(missing_columns)}"
            )
        
        # Initialize detector
        detector = MoneyMulingDetector()
        detector.load_transactions(df)
        
        # Run analysis
        results = detector.analyze()
        
        # Store results in database for later retrieval
        results_doc = {
            'id': str(uuid.uuid4()),
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'filename': file.filename,
            'results': results
        }
        await db.analysis_results.insert_one(results_doc)
        
        return results
        
    except HTTPException:
        raise
    except pd.errors.ParserError as e:
        raise HTTPException(status_code=400, detail=f"CSV parsing error: {str(e)}")
    except UnicodeDecodeError as e:
        raise HTTPException(status_code=400, detail=f"File encoding error: {str(e)}")
    except KeyError as e:
        raise HTTPException(status_code=400, detail=f"Missing required data: {str(e)}")
    except Exception as e:
        logging.error(f"Error processing CSV: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

@api_router.get("/analysis-history")
async def get_analysis_history():
    """Get history of past analyses"""
    try:
        history = await db.analysis_results.find(
            {}, 
            {"_id": 0, "id": 1, "timestamp": 1, "filename": 1, "results.summary": 1}
        ).sort("timestamp", -1).limit(10).to_list(10)
        return history
    except Exception as e:
        logging.error(f"Error fetching history: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/status", response_model=StatusCheck)
async def create_status_check(input: StatusCheckCreate):
    status_dict = input.model_dump()
    status_obj = StatusCheck(**status_dict)
    
    doc = status_obj.model_dump()
    doc['timestamp'] = doc['timestamp'].isoformat()
    
    _ = await db.status_checks.insert_one(doc)
    return status_obj

@api_router.get("/status", response_model=List[StatusCheck])
async def get_status_checks():
    status_checks = await db.status_checks.find({}, {"_id": 0}).to_list(1000)
    
    for check in status_checks:
        if isinstance(check['timestamp'], str):
            check['timestamp'] = datetime.fromisoformat(check['timestamp'])
    
    return status_checks


# Include the router in the main app
app.include_router(api_router)

# Serve frontend build static files if directory exists
frontend_path = ROOT_DIR.parent / "frontend" / "build"
if frontend_path.exists():
    app.mount("/", StaticFiles(directory=str(frontend_path), html=True), name="frontend")
    
    # Catch-all for SPA routing
    @app.exception_handler(404)
    async def not_found_handler(request, exc):
        if not request.url.path.startswith("/api"):
            return FileResponse(frontend_path / "index.html")
        return await request.app.default_exception_handler(request, exc)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
