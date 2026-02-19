import requests
import sys
import json
from datetime import datetime
import os

class FinancialForensicsAPITester:
    def __init__(self, base_url="https://doc-processor-40.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_base = f"{self.base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0

    def run_test(self, name, test_func):
        """Run a single test"""
        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        
        try:
            success, message = test_func()
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - {message}")
            else:
                print(f"❌ Failed - {message}")
            return success
        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False

    def test_api_root(self):
        """Test API root endpoint"""
        try:
            response = requests.get(f"{self.api_base}/", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if "Financial Forensics Engine" in data.get("message", ""):
                    return True, f"API root accessible - {data['message']}"
                else:
                    return False, f"Unexpected response: {data}"
            else:
                return False, f"Status code: {response.status_code}, Response: {response.text}"
        except Exception as e:
            return False, str(e)

    def test_csv_upload_with_valid_data(self):
        """Test CSV upload with valid test data"""
        try:
            # Use the test CSV file
            test_csv_path = "/app/backend/test_transactions.csv"
            if not os.path.exists(test_csv_path):
                return False, "Test CSV file not found"

            with open(test_csv_path, 'rb') as f:
                files = {'file': ('test_transactions.csv', f, 'text/csv')}
                response = requests.post(f"{self.api_base}/upload-csv", files=files, timeout=30)

            if response.status_code == 200:
                data = response.json()
                
                # Validate response structure
                required_keys = ['suspicious_accounts', 'fraud_rings', 'summary', 'graph_data']
                missing_keys = [key for key in required_keys if key not in data]
                
                if missing_keys:
                    return False, f"Missing keys in response: {missing_keys}"

                # Validate summary data
                summary = data['summary']
                expected_summary_keys = ['total_accounts_analyzed', 'suspicious_accounts_flagged', 'fraud_rings_detected', 'processing_time_seconds']
                missing_summary_keys = [key for key in expected_summary_keys if key not in summary]
                
                if missing_summary_keys:
                    return False, f"Missing summary keys: {missing_summary_keys}"

                # Check if results make sense based on test data
                total_accounts = summary['total_accounts_analyzed']
                suspicious_accounts = summary['suspicious_accounts_flagged']
                fraud_rings = summary['fraud_rings_detected']
                processing_time = summary['processing_time_seconds']

                # According to context: Expected 6+ fraud rings, 58 suspicious accounts, < 1s processing
                if total_accounts <= 0:
                    return False, f"Invalid total accounts: {total_accounts}"
                
                if processing_time < 0:
                    return False, f"Invalid processing time: {processing_time}"

                # Check suspicious accounts structure
                if suspicious_accounts > 0 and len(data['suspicious_accounts']) != suspicious_accounts:
                    return False, f"Suspicious accounts count mismatch: summary={suspicious_accounts}, actual={len(data['suspicious_accounts'])}"

                # Check fraud rings structure  
                if fraud_rings > 0 and len(data['fraud_rings']) != fraud_rings:
                    return False, f"Fraud rings count mismatch: summary={fraud_rings}, actual={len(data['fraud_rings'])}"

                # Validate fraud ring structure
                if data['fraud_rings']:
                    first_ring = data['fraud_rings'][0]
                    required_ring_keys = ['ring_id', 'member_accounts', 'pattern_type', 'risk_score']
                    missing_ring_keys = [key for key in required_ring_keys if key not in first_ring]
                    
                    if missing_ring_keys:
                        return False, f"Missing fraud ring keys: {missing_ring_keys}"

                # Validate suspicious account structure
                if data['suspicious_accounts']:
                    first_account = data['suspicious_accounts'][0]
                    required_account_keys = ['account_id', 'suspicion_score', 'detected_patterns', 'ring_id']
                    missing_account_keys = [key for key in required_account_keys if key not in first_account]
                    
                    if missing_account_keys:
                        return False, f"Missing suspicious account keys: {missing_account_keys}"

                    # Validate suspicion score range (0-100)
                    score = first_account['suspicion_score']
                    if not (0 <= score <= 100):
                        return False, f"Invalid suspicion score: {score} (should be 0-100)"

                # Validate graph data structure
                graph_data = data['graph_data']
                if 'nodes' not in graph_data or 'edges' not in graph_data:
                    return False, "Missing nodes or edges in graph_data"

                return True, f"CSV upload successful - {total_accounts} accounts, {suspicious_accounts} suspicious, {fraud_rings} rings, {processing_time}s"
            
            else:
                return False, f"Status code: {response.status_code}, Response: {response.text}"
        except Exception as e:
            return False, str(e)

    def test_csv_upload_invalid_file(self):
        """Test CSV upload with invalid file format"""
        try:
            # Create a fake non-CSV file
            files = {'file': ('test.txt', b'This is not a CSV file', 'text/plain')}
            response = requests.post(f"{self.api_base}/upload-csv", files=files, timeout=10)

            if response.status_code == 400:
                error_data = response.json()
                if "CSV" in error_data.get("detail", ""):
                    return True, f"Correctly rejected non-CSV file: {error_data['detail']}"
                else:
                    return False, f"Wrong error message: {error_data}"
            else:
                return False, f"Expected 400 status, got {response.status_code}"
        except Exception as e:
            return False, str(e)

    def test_csv_upload_invalid_columns(self):
        """Test CSV upload with missing required columns"""
        try:
            # Create CSV with wrong columns
            invalid_csv = "id,from,to,value\n1,A,B,100\n"
            files = {'file': ('invalid.csv', invalid_csv.encode(), 'text/csv')}
            response = requests.post(f"{self.api_base}/upload-csv", files=files, timeout=10)

            if response.status_code == 400:
                error_data = response.json()
                if "Missing required columns" in error_data.get("detail", ""):
                    return True, f"Correctly rejected invalid columns: {error_data['detail']}"
                else:
                    return False, f"Wrong error message: {error_data}"
            else:
                return False, f"Expected 400 status, got {response.status_code}"
        except Exception as e:
            return False, str(e)

    def test_analysis_history(self):
        """Test analysis history endpoint"""
        try:
            response = requests.get(f"{self.api_base}/analysis-history", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                # Should return a list (may be empty)
                if isinstance(data, list):
                    return True, f"Analysis history retrieved - {len(data)} records"
                else:
                    return False, f"Expected list, got {type(data)}"
            else:
                return False, f"Status code: {response.status_code}, Response: {response.text}"
        except Exception as e:
            return False, str(e)

def main():
    print("🚀 Starting Financial Forensics Engine API Tests")
    print("=" * 60)
    
    tester = FinancialForensicsAPITester()

    # Run all tests
    tests = [
        ("API Root Endpoint", tester.test_api_root),
        ("CSV Upload - Valid Data", tester.test_csv_upload_with_valid_data),
        ("CSV Upload - Invalid File Format", tester.test_csv_upload_invalid_file),
        ("CSV Upload - Invalid Columns", tester.test_csv_upload_invalid_columns),
        ("Analysis History", tester.test_analysis_history),
    ]

    for test_name, test_func in tests:
        tester.run_test(test_name, test_func)

    # Print results
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {tester.tests_passed}/{tester.tests_run} tests passed")
    
    if tester.tests_passed == tester.tests_run:
        print("🎉 All tests passed!")
        return 0
    else:
        print("⚠️ Some tests failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())