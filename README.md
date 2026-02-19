# Financial Forensics Engine - Money Muling Detection

A web-based financial forensics engine that leverages graph theory to detect money muling networks from transaction data.

## 🚀 Live Demo

**Live Application URL:** [Your deployed URL here]

## 📋 Overview

This application processes transaction data and uses advanced graph analysis to identify three types of money muling patterns:
- **Circular Fund Routing** (Cycles of 3-5 accounts)
- **Smurfing Patterns** (Fan-in/Fan-out with 10+ connections)
- **Layered Shell Networks** (Chains through low-activity intermediary accounts)

## 🛠️ Tech Stack

### Backend
- **FastAPI** - High-performance Python web framework
- **NetworkX** - Graph analysis and algorithm implementation
- **Pandas** - Data processing and CSV handling
- **Motor** - Async MongoDB driver
- **Python 3.11+**

### Frontend
- **React 19** - UI framework
- **Cytoscape.js** - Interactive graph visualization
- **Tailwind CSS** - Styling
- **Axios** - HTTP client

### Database
- **MongoDB** - Document storage for analysis results

## 🏗️ System Architecture

```
┌─────────────────────┐
│   React Frontend    │
│  (Cytoscape.js)     │
└──────────┬──────────┘
           │ HTTP/REST
           │
┌──────────▼──────────┐
│   FastAPI Backend   │
│  - CSV Upload       │
│  - Graph Analysis   │
│  - Pattern Detection│
└──────────┬──────────┘
           │
┌──────────▼──────────┐
│  NetworkX Engine    │
│  - Cycle Detection  │
│  - Smurfing Analysis│
│  - Shell Detection  │
└──────────┬──────────┘
           │
┌──────────▼──────────┐
│   MongoDB Database  │
│  (Analysis History) │
└─────────────────────┘
```

## 🧮 Algorithm Approach

### 1. Graph Construction
- **Time Complexity:** O(E) where E = number of transactions
- Creates a directed graph with accounts as nodes and transactions as edges
- Aggregates multiple transactions between same sender-receiver pairs

### 2. Cycle Detection
- **Algorithm:** Depth-First Search (DFS) with cycle tracking
- **Time Complexity:** O(V + E) where V = vertices, E = edges
- **Implementation:** Uses NetworkX's `simple_cycles()` function
- Detects circular fund routing patterns of length 3-5
- All accounts in a cycle are grouped into the same fraud ring

### 3. Smurfing Detection (Fan-in/Fan-out)
- **Time Complexity:** O(V × D) where D = average degree
- **Fan-in:** Identifies accounts receiving from 10+ senders
- **Fan-out:** Identifies accounts sending to 10+ receivers
- **Temporal Analysis:** Applies 1.5× multiplier for transactions within 72-hour window
- Filters out legitimate high-volume accounts based on transaction patterns

### 4. Layered Shell Network Detection
- **Algorithm:** All simple paths with intermediary filtering
- **Time Complexity:** O(V × E) with cutoff optimization
- Finds chains of 3+ hops through low-activity accounts
- Shell criteria: Intermediate accounts with only 2-3 total transactions
- Uses cutoff of 6 to prevent exponential path explosion

### 5. False Positive Reduction
- **Legitimate Account Filtering:**
  - Excludes accounts with consistent, regular transaction patterns
  - Distinguishes between merchant/payroll accounts and mule accounts
  - Considers transaction amount variance and temporal distribution

## 📊 Suspicion Score Methodology

Weighted scoring system (0-100):

| Pattern | Base Score | Notes |
|---------|-----------|-------|
| **Cycle Member** | 85 | High risk - circular routing is strong indicator |
| **Smurfing (Fan-in)** | 65 | Multiplied by temporal factor (1.0-1.5x) |
| **Smurfing (Fan-out)** | 65 | Multiplied by temporal factor (1.0-1.5x) |
| **Shell Account** | 75 | Intermediate nodes in layering chains |
| **Multiple Patterns** | Additive | Accounts matching multiple patterns get combined scores |

**Temporal Factor:**
- 1.5× multiplier if transactions occur within 72-hour window
- 1.0× for transactions spread over longer periods

**Final Score:** `min(sum(base_scores × temporal_factors), 100)`

## 📥 Installation & Setup

### Prerequisites
- Python 3.11+
- Node.js 18+
- MongoDB 4.4+
- Yarn package manager

### Backend Setup
```bash
cd backend
pip install -r requirements.txt

# Create .env file
echo "MONGO_URL=mongodb://localhost:27017" > .env
echo "DB_NAME=forensics_db" >> .env
echo "CORS_ORIGINS=*" >> .env
```

### Frontend Setup
```bash
cd frontend
yarn install

# Create .env file
echo "REACT_APP_BACKEND_URL=http://localhost:8001" > .env
```

### Running the Application

**Backend:**
```bash
cd backend
uvicorn server:app --host 0.0.0.0 --port 8001 --reload
```

**Frontend:**
```bash
cd frontend
yarn start
```

Access the application at `http://localhost:3000`

## 📖 Usage Instructions

### 1. Upload CSV File
- Navigate to the homepage
- Click "Upload" or drag-and-drop a CSV file
- Required CSV format:

```csv
transaction_id,sender_id,receiver_id,amount,timestamp
TX_001,ACC_001,ACC_002,5000.00,2024-01-01 10:00:00
```

### 2. View Analysis Results
- **Graph Visualization:** Interactive network showing all accounts and transaction flows
  - Red nodes = Suspicious accounts
  - Gray nodes = Normal accounts
  - Arrows = Transaction direction
  - Click nodes/edges for detailed information

- **Fraud Ring Table:** Summary of detected rings with:
  - Ring ID
  - Pattern Type
  - Member Count
  - Risk Score
  - Member Account IDs

- **Summary Statistics:**
  - Total accounts analyzed
  - Suspicious accounts flagged
  - Fraud rings detected
  - Processing time

### 3. Download Results
- Click "Download JSON" to export results in the required format:
  - `suspicious_accounts` array
  - `fraud_rings` array
  - `summary` object

## 🧪 Testing

### Generate Test Data
```bash
cd backend
python generate_test_data.py
```

This creates `test_transactions.csv` with known fraud patterns:
- 2 cycles (3-node and 4-node)
- 1 fan-in pattern (15→1)
- 1 fan-out pattern (1→12)
- 1 shell chain (5-hop)
- 30 legitimate transactions

### API Testing
```bash
# Test health endpoint
curl http://localhost:8001/api/

# Test CSV upload
curl -X POST http://localhost:8001/api/upload-csv \
  -F "file=@test_transactions.csv"
```

## ⚠️ Known Limitations

1. **Scalability:**
   - Current implementation optimal for datasets up to 50K transactions
   - Path detection (shell networks) can be computationally expensive for very dense graphs
   - Recommend using Spark/GraphX for datasets > 100K transactions

2. **False Positives:**
   - Legitimate payroll systems with regular fan-out patterns may trigger alerts
   - High-frequency trading accounts might be flagged as smurfing
   - Mitigation: Manual review recommended for risk scores < 75

3. **Temporal Analysis:**
   - Currently uses fixed 72-hour window for smurfing detection
   - May miss patterns spread over longer periods
   - Future enhancement: Adaptive time window based on transaction velocity

4. **Graph Algorithms:**
   - All simple paths algorithm has exponential worst-case complexity
   - Cutoff of 6 hops may miss longer shell chains
   - Cycle detection limited to length 5 (may miss larger circular networks)

5. **Data Quality:**
   - Requires clean, well-formatted CSV input
   - Missing timestamps or malformed data will cause processing errors
   - No automatic data cleaning or imputation

## 👥 Team Members

- [Your Name] - Full Stack Development, Algorithm Design
- [Team Member 2] - Graph Analysis, Backend Development
- [Team Member 3] - UI/UX Design, Frontend Development

## 📄 License

This project is developed for the RIFT 2026 Hackathon.

## 🔗 Links

- **GitHub Repository:** [Repository URL]
- **Live Demo:** [Deployment URL]
- **Demo Video:** [LinkedIn Post URL]

## 🎯 Evaluation Criteria Coverage

✅ **Problem Clarity:** Graph-based detection for multi-hop money muling networks  
✅ **Solution Accuracy:** Three detection algorithms with exact JSON output  
✅ **Technical Depth:** NetworkX algorithms with complexity analysis  
✅ **Innovation:** Temporal analysis, weighted suspicion scoring  
✅ **Live Deployment:** Web application with CSV upload  
✅ **Documentation:** Complete README with methodology  

---

Built with ❤️ for RIFT 2026 Hackathon
