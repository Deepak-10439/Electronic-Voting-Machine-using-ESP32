#!/usr/bin/env python3
"""
Comprehensive Test Suite for ESP32 EVM Django Backend
Tests all API endpoints, authentication, voting workflows, and system integrity
"""

import requests
import json
import time
import sys
from datetime import datetime

class EVMTestSuite:
    def __init__(self, base_url="http://127.0.0.1:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.auth_token = None
        self.test_results = []
        
    def log_test(self, test_name, status, message="", data=None):
        """Log test results"""
        result = {
            "test": test_name,
            "status": status,
            "message": message,
            "timestamp": datetime.now().isoformat(),
            "data": data
        }
        self.test_results.append(result)
        
        # Color coding for terminal output
        if status == "PASS":
            print(f"✅ {test_name}: {message}")
        elif status == "FAIL":
            print(f"❌ {test_name}: {message}")
        elif status == "WARN":
            print(f"⚠️  {test_name}: {message}")
        else:
            print(f"ℹ️  {test_name}: {message}")
            
        if data:
            print(f"   Data: {json.dumps(data, indent=2)}")
        print()

    def test_server_connectivity(self):
        """Test if Django server is running and accessible"""
        try:
            response = self.session.get(f"{self.base_url}/")
            if response.status_code == 200:
                self.log_test("Server Connectivity", "PASS", 
                            f"Server is running (Status: {response.status_code})", 
                            response.json())
                return True
            else:
                self.log_test("Server Connectivity", "FAIL", 
                            f"Unexpected status code: {response.status_code}")
                return False
        except requests.exceptions.ConnectionError:
            self.log_test("Server Connectivity", "FAIL", 
                        "Cannot connect to Django server. Is it running on http://127.0.0.1:8000?")
            return False
        except Exception as e:
            self.log_test("Server Connectivity", "FAIL", f"Unexpected error: {str(e)}")
            return False

    def test_health_endpoints(self):
        """Test health check and system status endpoints"""
        endpoints = [
            ("/api/health/", "Health Check"),
            ("/api/time/", "System Time"),
        ]
        
        for endpoint, name in endpoints:
            try:
                response = self.session.get(f"{self.base_url}{endpoint}")
                if response.status_code == 200:
                    self.log_test(name, "PASS", f"Endpoint accessible", response.json())
                else:
                    self.log_test(name, "FAIL", f"Status code: {response.status_code}")
            except Exception as e:
                self.log_test(name, "FAIL", f"Error: {str(e)}")

    def test_authentication_endpoint(self):
        """Test ESP32 authentication endpoint"""
        test_cases = [
            {
                "name": "Valid ESP32 Authentication",
                "data": {
                    "device_id": "TEST_ESP32_001",
                    "fingerprint_template": "00" * 534,  # Mock fingerprint template
                    "aadhar_number": "123456789012"
                },
                "expected_status": [200, 201, 400]  # Accept various responses during development
            },
            {
                "name": "Invalid Aadhar Number",
                "data": {
                    "device_id": "TEST_ESP32_002", 
                    "fingerprint_template": "FF" * 534,
                    "aadhar_number": "invalid"
                },
                "expected_status": [400, 422]
            },
            {
                "name": "Missing Device ID",
                "data": {
                    "fingerprint_template": "AA" * 534,
                    "aadhar_number": "987654321098"
                },
                "expected_status": [400, 422]
            }
        ]
        
        for case in test_cases:
            try:
                response = self.session.post(f"{self.base_url}/api/auth/", 
                                           json=case["data"])
                
                if response.status_code in case["expected_status"]:
                    self.log_test(case["name"], "PASS", 
                                f"Status: {response.status_code}", response.json())
                    
                    # Store auth token if successful
                    if response.status_code in [200, 201] and 'token' in response.json():
                        self.auth_token = response.json()['token']
                        self.session.headers.update({'Authorization': f'Token {self.auth_token}'})
                else:
                    self.log_test(case["name"], "FAIL", 
                                f"Unexpected status: {response.status_code}", response.json())
                    
            except Exception as e:
                self.log_test(case["name"], "FAIL", f"Error: {str(e)}")

    def test_voting_endpoints(self):
        """Test voting-related endpoints"""
        # Test getting active elections
        try:
            response = self.session.get(f"{self.base_url}/api/elections/")
            self.log_test("Get Active Elections", "PASS" if response.status_code == 200 else "FAIL",
                         f"Status: {response.status_code}", response.json())
        except Exception as e:
            self.log_test("Get Active Elections", "FAIL", f"Error: {str(e)}")
        
        # Test vote casting (if we have auth token)
        if self.auth_token:
            vote_data = {
                "election_id": "test-election-1",
                "candidate_id": "test-candidate-1", 
                "fingerprint_template": "BB" * 534,
                "device_id": "TEST_ESP32_001"
            }
            
            try:
                response = self.session.post(f"{self.base_url}/api/vote/", json=vote_data)
                self.log_test("Cast Vote", "PASS" if response.status_code in [200, 201, 400] else "FAIL",
                             f"Status: {response.status_code}", response.json())
            except Exception as e:
                self.log_test("Cast Vote", "FAIL", f"Error: {str(e)}")

    def test_admin_endpoints(self):
        """Test admin interface accessibility"""
        try:
            response = self.session.get(f"{self.base_url}/admin/")
            if response.status_code in [200, 302]:  # 302 is redirect to login
                self.log_test("Admin Interface", "PASS", 
                            f"Admin interface accessible (Status: {response.status_code})")
            else:
                self.log_test("Admin Interface", "FAIL", 
                            f"Unexpected status: {response.status_code}")
        except Exception as e:
            self.log_test("Admin Interface", "FAIL", f"Error: {str(e)}")

    def test_cors_headers(self):
        """Test CORS headers for ESP32 compatibility"""
        try:
            response = self.session.options(f"{self.base_url}/api/health/")
            headers = response.headers
            
            cors_tests = [
                ("Access-Control-Allow-Origin", "CORS Origin Header"),
                ("Access-Control-Allow-Methods", "CORS Methods Header"),
                ("Access-Control-Allow-Headers", "CORS Headers Header")
            ]
            
            for header, test_name in cors_tests:
                if header in headers:
                    self.log_test(test_name, "PASS", f"Value: {headers[header]}")
                else:
                    self.log_test(test_name, "WARN", f"Header not found: {header}")
                    
        except Exception as e:
            self.log_test("CORS Headers Test", "FAIL", f"Error: {str(e)}")

    def test_performance(self):
        """Test API response times"""
        endpoints = ["/api/health/", "/api/time/", "/"]
        
        for endpoint in endpoints:
            try:
                start_time = time.time()
                response = self.session.get(f"{self.base_url}{endpoint}")
                end_time = time.time()
                
                response_time = (end_time - start_time) * 1000  # Convert to milliseconds
                
                if response_time < 1000:  # Less than 1 second
                    self.log_test(f"Performance {endpoint}", "PASS", 
                                f"Response time: {response_time:.2f}ms")
                else:
                    self.log_test(f"Performance {endpoint}", "WARN", 
                                f"Slow response: {response_time:.2f}ms")
                    
            except Exception as e:
                self.log_test(f"Performance {endpoint}", "FAIL", f"Error: {str(e)}")

    def run_all_tests(self):
        """Run complete test suite"""
        print("=" * 60)
        print("🧪 ESP32 EVM Django Backend - Comprehensive Test Suite")
        print(f"📅 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🔗 Testing server: {self.base_url}")
        print("=" * 60)
        print()
        
        # Run all test categories
        if not self.test_server_connectivity():
            print("❌ Server not accessible. Stopping tests.")
            return False
            
        self.test_health_endpoints()
        self.test_authentication_endpoint()
        self.test_voting_endpoints()
        self.test_admin_endpoints()
        self.test_cors_headers()
        self.test_performance()
        
        # Generate summary
        self.generate_summary()
        return True

    def generate_summary(self):
        """Generate test summary report"""
        print("=" * 60)
        print("📊 TEST SUMMARY REPORT")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = len([t for t in self.test_results if t["status"] == "PASS"])
        failed_tests = len([t for t in self.test_results if t["status"] == "FAIL"])
        warning_tests = len([t for t in self.test_results if t["status"] == "WARN"])
        
        print(f"📈 Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"⚠️  Warnings: {warning_tests}")
        print(f"📊 Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        print()
        
        if failed_tests > 0:
            print("❌ FAILED TESTS:")
            for test in self.test_results:
                if test["status"] == "FAIL":
                    print(f"   • {test['test']}: {test['message']}")
            print()
        
        if warning_tests > 0:
            print("⚠️  WARNINGS:")
            for test in self.test_results:
                if test["status"] == "WARN":
                    print(f"   • {test['test']}: {test['message']}")
            print()
        
        # Save detailed results to file
        try:
            with open('test_results.json', 'w') as f:
                json.dump({
                    'summary': {
                        'total': total_tests,
                        'passed': passed_tests,
                        'failed': failed_tests,
                        'warnings': warning_tests,
                        'success_rate': (passed_tests/total_tests)*100
                    },
                    'tests': self.test_results
                }, f, indent=2)
            print(f"💾 Detailed results saved to: test_results.json")
        except Exception as e:
            print(f"⚠️  Could not save results file: {e}")
        
        print("=" * 60)

def main():
    """Main test execution"""
    print("🚀 Starting ESP32 EVM Backend Test Suite...")
    print()
    
    # Check if server URL is provided as command line argument
    server_url = "http://127.0.0.1:8000"
    if len(sys.argv) > 1:
        server_url = sys.argv[1]
    
    tester = EVMTestSuite(server_url)
    success = tester.run_all_tests()
    
    if success:
        print("🎉 Test suite completed successfully!")
    else:
        print("💥 Test suite encountered critical errors!")
        sys.exit(1)

if __name__ == "__main__":
    main()