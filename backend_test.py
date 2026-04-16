#!/usr/bin/env python3
"""
CloudDoctor Backend API Testing
Tests all backend endpoints for the AI-powered cloud diagnostics application.
"""

import requests
import sys
import json
import time
from datetime import datetime

class CloudDoctorAPITester:
    def __init__(self, base_url="https://llama-diagnostics.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []

    def log_test(self, name, success, details=""):
        """Log test result"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name}")
        else:
            print(f"❌ {name} - {details}")
        
        self.test_results.append({
            "test": name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })

    def test_health_endpoint(self):
        """Test GET /api/health"""
        try:
            response = requests.get(f"{self.api_url}/health", timeout=10)
            if response.status_code == 200:
                data = response.json()
                required_services = ["mongodb", "llm", "betterstack", "sample_app"]
                
                # Check all services are present
                missing_services = [svc for svc in required_services if svc not in data]
                if missing_services:
                    self.log_test("Health endpoint - service coverage", False, f"Missing services: {missing_services}")
                    return False
                
                # Check MongoDB status
                mongodb_status = data.get("mongodb", {}).get("status")
                if mongodb_status != "connected":
                    self.log_test("Health endpoint - MongoDB", False, f"MongoDB status: {mongodb_status}")
                else:
                    self.log_test("Health endpoint - MongoDB", True)
                
                # Check LLM status
                llm_status = data.get("llm", {}).get("status")
                if llm_status != "connected":
                    self.log_test("Health endpoint - LLM", False, f"LLM status: {llm_status}")
                else:
                    self.log_test("Health endpoint - LLM", True)
                
                # Check sample app status
                sample_app = data.get("sample_app", {})
                self.log_test("Health endpoint - Sample App", True, f"Status: {sample_app.get('status', 'unknown')}")
                
                self.log_test("Health endpoint - overall", True)
                return True
            else:
                self.log_test("Health endpoint", False, f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Health endpoint", False, str(e))
            return False

    def test_scenarios_endpoint(self):
        """Test GET /api/scenarios"""
        try:
            response = requests.get(f"{self.api_url}/scenarios", timeout=10)
            if response.status_code == 200:
                data = response.json()
                expected_scenarios = ["db-crash", "memory-leak", "high-latency", "crash"]
                
                # Check all scenarios are present
                missing_scenarios = [scenario for scenario in expected_scenarios if scenario not in data]
                if missing_scenarios:
                    self.log_test("Scenarios endpoint", False, f"Missing scenarios: {missing_scenarios}")
                    return False
                
                # Check scenario structure
                for scenario, details in data.items():
                    if "description" not in details or "service" not in details:
                        self.log_test("Scenarios endpoint", False, f"Invalid structure for {scenario}")
                        return False
                
                self.log_test("Scenarios endpoint", True, f"Found {len(data)} scenarios")
                return True
            else:
                self.log_test("Scenarios endpoint", False, f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Scenarios endpoint", False, str(e))
            return False

    def test_trigger_incident(self):
        """Test POST /api/incidents/trigger"""
        try:
            # Test with db-crash scenario
            payload = {"scenario": "db-crash"}
            response = requests.post(f"{self.api_url}/incidents/trigger", json=payload, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ["id", "anomaly_type", "service", "status", "timestamp"]
                
                # Check response structure
                missing_fields = [field for field in required_fields if field not in data]
                if missing_fields:
                    self.log_test("Trigger incident", False, f"Missing fields: {missing_fields}")
                    return False, None
                
                # Verify scenario was set correctly
                if data.get("anomaly_type") != "db-crash":
                    self.log_test("Trigger incident", False, f"Wrong anomaly_type: {data.get('anomaly_type')}")
                    return False, None
                
                self.log_test("Trigger incident", True, f"Created incident: {data['id']}")
                return True, data["id"]
            else:
                self.log_test("Trigger incident", False, f"Status code: {response.status_code}")
                return False, None
        except Exception as e:
            self.log_test("Trigger incident", False, str(e))
            return False, None

    def test_get_incidents(self):
        """Test GET /api/incidents"""
        try:
            response = requests.get(f"{self.api_url}/incidents", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    self.log_test("Get incidents", True, f"Found {len(data)} incidents")
                    return True, data
                else:
                    self.log_test("Get incidents", False, "Response is not a list")
                    return False, []
            else:
                self.log_test("Get incidents", False, f"Status code: {response.status_code}")
                return False, []
        except Exception as e:
            self.log_test("Get incidents", False, str(e))
            return False, []

    def test_resolve_incident(self, incident_id):
        """Test POST /api/incidents/{id}/resolve"""
        if not incident_id:
            self.log_test("Resolve incident", False, "No incident ID provided")
            return False
        
        try:
            response = requests.post(f"{self.api_url}/incidents/{incident_id}/resolve", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "resolved":
                    self.log_test("Resolve incident", True)
                    return True
                else:
                    self.log_test("Resolve incident", False, f"Status not updated: {data.get('status')}")
                    return False
            else:
                self.log_test("Resolve incident", False, f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Resolve incident", False, str(e))
            return False

    def test_logs_endpoint(self):
        """Test GET /api/logs"""
        try:
            # Test basic logs endpoint
            response = requests.get(f"{self.api_url}/logs", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if "logs" in data and "count" in data:
                    self.log_test("Logs endpoint - basic", True, f"Found {data['count']} logs")
                else:
                    self.log_test("Logs endpoint - basic", False, "Invalid response structure")
                    return False
            else:
                self.log_test("Logs endpoint - basic", False, f"Status code: {response.status_code}")
                return False
            
            # Test with level filter
            response = requests.get(f"{self.api_url}/logs?levels=ERROR", timeout=10)
            if response.status_code == 200:
                data = response.json()
                self.log_test("Logs endpoint - ERROR filter", True, f"Found {data['count']} error logs")
            else:
                self.log_test("Logs endpoint - ERROR filter", False, f"Status code: {response.status_code}")
                return False
            
            return True
        except Exception as e:
            self.log_test("Logs endpoint", False, str(e))
            return False

    def test_log_stats_endpoint(self):
        """Test GET /api/logs/stats"""
        try:
            response = requests.get(f"{self.api_url}/logs/stats", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if "stats" in data and "total" in data:
                    stats = data["stats"]
                    expected_levels = ["DEBUG", "INFO", "WARN", "ERROR", "FATAL"]
                    
                    # Check all severity levels are present
                    missing_levels = [level for level in expected_levels if level not in stats]
                    if missing_levels:
                        self.log_test("Log stats endpoint", False, f"Missing levels: {missing_levels}")
                        return False
                    
                    self.log_test("Log stats endpoint", True, f"Total logs: {data['total']}")
                    return True
                else:
                    self.log_test("Log stats endpoint", False, "Invalid response structure")
                    return False
            else:
                self.log_test("Log stats endpoint", False, f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Log stats endpoint", False, str(e))
            return False

    def test_simulator_endpoints(self):
        """Test simulator control endpoints"""
        try:
            # Test get state
            response = requests.get(f"{self.api_url}/simulator/state", timeout=10)
            if response.status_code == 200:
                data = response.json()
                required_fields = ["current_scenario", "is_healthy", "description"]
                missing_fields = [field for field in required_fields if field not in data]
                if missing_fields:
                    self.log_test("Simulator state", False, f"Missing fields: {missing_fields}")
                    return False
                
                self.log_test("Simulator state", True, f"Healthy: {data['is_healthy']}")
            else:
                self.log_test("Simulator state", False, f"Status code: {response.status_code}")
                return False
            
            # Test stop simulator
            response = requests.post(f"{self.api_url}/simulator/stop", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get("is_healthy") == True:
                    self.log_test("Simulator stop", True)
                else:
                    self.log_test("Simulator stop", False, f"System not healthy after stop: {data}")
                    return False
            else:
                self.log_test("Simulator stop", False, f"Status code: {response.status_code}")
                return False
            
            return True
        except Exception as e:
            self.log_test("Simulator endpoints", False, str(e))
            return False

    def run_all_tests(self):
        """Run all backend tests"""
        print(f"🧪 Starting CloudDoctor Backend API Tests")
        print(f"🔗 Testing against: {self.api_url}")
        print("=" * 60)
        
        # Test health endpoint first
        if not self.test_health_endpoint():
            print("❌ Health check failed - stopping tests")
            return False
        
        # Test scenarios
        self.test_scenarios_endpoint()
        
        # Test incident management
        success, incident_id = self.test_trigger_incident()
        if success:
            # Wait a moment for logs to be generated
            time.sleep(2)
            
            # Test logs after incident
            self.test_logs_endpoint()
            self.test_log_stats_endpoint()
            
            # Test incident listing
            self.test_get_incidents()
            
            # Test incident resolution
            self.test_resolve_incident(incident_id)
        
        # Test simulator control
        self.test_simulator_endpoints()
        
        # Print summary
        print("=" * 60)
        print(f"📊 Test Summary: {self.tests_passed}/{self.tests_run} passed")
        
        if self.tests_passed == self.tests_run:
            print("🎉 All tests passed!")
            return True
        else:
            print(f"⚠️  {self.tests_run - self.tests_passed} tests failed")
            return False

def main():
    tester = CloudDoctorAPITester()
    success = tester.run_all_tests()
    
    # Save test results
    with open("/app/backend_test_results.json", "w") as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "total_tests": tester.tests_run,
            "passed_tests": tester.tests_passed,
            "success_rate": tester.tests_passed / tester.tests_run if tester.tests_run > 0 else 0,
            "results": tester.test_results
        }, f, indent=2)
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())