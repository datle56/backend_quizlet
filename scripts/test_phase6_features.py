#!/usr/bin/env python3
"""
Test script for Phase 6 Advanced Features
Tests notifications, reports, and analytics endpoints
"""

import requests
import json
from typing import Dict, Any

# Configuration
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api/v1"

# Test data
test_user_credentials = {
    "username": "string",
    "password": "string"
}

test_study_set_data = {
    "title": "Test Study Set for Phase 6",
    "description": "A test study set for testing Phase 6 features",
    "is_public": True,
    "language_from": "en",
    "language_to": "es"
}

test_notification_data = {
    "type": "test_notification",
    "message": "This is a test notification",
    "related_entity_type": "study_set",
    "related_entity_id": 1
}

test_report_data = {
    "reported_entity_type": "study_set",
    "reported_entity_id": 1,
    "reason": "Test report for Phase 6 features"
}


class Phase6Tester:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        self.test_user_id = None
        self.test_study_set_id = None
    
    def login(self) -> bool:
        """Login and get authentication token"""
        try:
            response = self.session.post(
                f"{API_BASE}/auth/login",
                json=test_user_credentials
            )
            
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data.get("access_token")
                self.session.headers.update({
                    "Authorization": f"Bearer {self.auth_token}"
                })
                print("✅ Login successful")
                return True
            else:
                print(f"❌ Login failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Login error: {e}")
            return False
    
    def test_notifications(self) -> bool:
        """Test notifications endpoints"""
        print("\n🔔 Testing Notifications System...")
        
        try:
            # Get notifications
            response = self.session.get(f"{API_BASE}/notifications/")
            if response.status_code == 200:
                print("✅ GET /notifications/ - Success")
                notifications = response.json()
                print(f"   Found {notifications.get('total', 0)} notifications")
            else:
                print(f"❌ GET /notifications/ - Failed: {response.status_code}")
                return False
            
            # Get notification stats
            response = self.session.get(f"{API_BASE}/notifications/stats")
            if response.status_code == 200:
                print("✅ GET /notifications/stats - Success")
                stats = response.json()
                print(f"   Total: {stats.get('total_notifications', 0)}, Unread: {stats.get('unread_notifications', 0)}")
            else:
                print(f"❌ GET /notifications/stats - Failed: {response.status_code}")
                return False
            
            # Test email notification
            response = self.session.post(f"{API_BASE}/notifications/test-email")
            if response.status_code == 200:
                print("✅ POST /notifications/test-email - Success")
            else:
                print(f"❌ POST /notifications/test-email - Failed: {response.status_code}")
            
            # Test push notification
            response = self.session.post(f"{API_BASE}/notifications/test-push")
            if response.status_code == 200:
                print("✅ POST /notifications/test-push - Success")
            else:
                print(f"❌ POST /notifications/test-push - Failed: {response.status_code}")
            
            return True
            
        except Exception as e:
            print(f"❌ Notifications test error: {e}")
            return False
    
    def test_reports(self) -> bool:
        """Test reports endpoints"""
        print("\n📋 Testing Reports System...")
        
        try:
            # Create a report
            response = self.session.post(
                f"{API_BASE}/reports/",
                json=test_report_data
            )
            if response.status_code == 200:
                print("✅ POST /reports/ - Success")
                report_data = response.json()
                report_id = report_data.get("id")
            else:
                print(f"❌ POST /reports/ - Failed: {response.status_code} - {response.text}")
                return False
            
            # Get my reports
            response = self.session.get(f"{API_BASE}/reports/my-reports")
            if response.status_code == 200:
                print("✅ GET /reports/my-reports - Success")
                reports = response.json()
                print(f"   Found {len(reports)} reports")
            else:
                print(f"❌ GET /reports/my-reports - Failed: {response.status_code}")
                return False
            
            # Get report stats (admin only, might fail for regular user)
            response = self.session.get(f"{API_BASE}/reports/stats")
            if response.status_code == 200:
                print("✅ GET /reports/stats - Success")
                stats = response.json()
                print(f"   Total reports: {stats.get('total_reports', 0)}")
            else:
                print(f"⚠️  GET /reports/stats - Expected failure (admin only): {response.status_code}")
            
            return True
            
        except Exception as e:
            print(f"❌ Reports test error: {e}")
            return False
    
    def test_analytics(self) -> bool:
        """Test analytics endpoints"""
        print("\n📊 Testing Analytics System...")
        
        try:
            # Get user stats
            response = self.session.get(f"{API_BASE}/analytics/user-stats")
            if response.status_code == 200:
                print("✅ GET /analytics/user-stats - Success")
                stats = response.json()
                print(f"   Study sets created: {stats.get('total_study_sets_created', 0)}")
                print(f"   Terms learned: {stats.get('total_terms_learned', 0)}")
                print(f"   Study sessions: {stats.get('total_study_sessions', 0)}")
            else:
                print(f"❌ GET /analytics/user-stats - Failed: {response.status_code}")
                return False
            
            # Get study session stats
            response = self.session.get(f"{API_BASE}/analytics/study-session-stats")
            if response.status_code == 200:
                print("✅ GET /analytics/study-session-stats - Success")
                stats = response.json()
                print(f"   Total sessions: {stats.get('total_sessions', 0)}")
                print(f"   Total time: {stats.get('total_time_minutes', 0)} minutes")
            else:
                print(f"❌ GET /analytics/study-session-stats - Failed: {response.status_code}")
                return False
            
            # Get dashboard stats
            response = self.session.get(f"{API_BASE}/analytics/dashboard")
            if response.status_code == 200:
                print("✅ GET /analytics/dashboard - Success")
                dashboard = response.json()
                print(f"   Recent sessions: {len(dashboard.get('recent_sessions', []))}")
                print(f"   Unread notifications: {dashboard.get('unread_notifications_count', 0)}")
            else:
                print(f"❌ GET /analytics/dashboard - Failed: {response.status_code}")
                return False
            
            return True
            
        except Exception as e:
            print(f"❌ Analytics test error: {e}")
            return False
    
    def test_comprehensive_analytics(self) -> bool:
        """Test comprehensive analytics endpoint"""
        print("\n📈 Testing Comprehensive Analytics...")
        
        try:
            # Get comprehensive analytics
            response = self.session.get(f"{API_BASE}/analytics/comprehensive")
            if response.status_code == 200:
                print("✅ GET /analytics/comprehensive - Success")
                analytics = response.json()
                
                if analytics.get("user_stats"):
                    print("   ✅ User stats included")
                if analytics.get("study_session_stats"):
                    print("   ✅ Study session stats included")
                    
            else:
                print(f"❌ GET /analytics/comprehensive - Failed: {response.status_code}")
                return False
            
            return True
            
        except Exception as e:
            print(f"❌ Comprehensive analytics test error: {e}")
            return False
    
    def run_all_tests(self):
        """Run all Phase 6 feature tests"""
        print("🚀 Starting Phase 6 Advanced Features Testing")
        print("=" * 50)
        
        # Login first
        if not self.login():
            print("❌ Cannot proceed without authentication")
            return False
        
        # Test each feature
        notifications_ok = self.test_notifications()
        reports_ok = self.test_reports()
        analytics_ok = self.test_analytics()
        comprehensive_ok = self.test_comprehensive_analytics()
        
        # Summary
        print("\n" + "=" * 50)
        print("📋 Phase 6 Test Results:")
        print(f"   Notifications: {'✅ PASS' if notifications_ok else '❌ FAIL'}")
        print(f"   Reports: {'✅ PASS' if reports_ok else '❌ FAIL'}")
        print(f"   Analytics: {'✅ PASS' if analytics_ok else '❌ FAIL'}")
        print(f"   Comprehensive Analytics: {'✅ PASS' if comprehensive_ok else '❌ FAIL'}")
        
        all_passed = notifications_ok and reports_ok and analytics_ok and comprehensive_ok
        print(f"\nOverall Result: {'🎉 ALL TESTS PASSED' if all_passed else '❌ SOME TESTS FAILED'}")
        
        return all_passed


def main():
    """Main test function"""
    tester = Phase6Tester()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎉 Phase 6 Advanced Features are working correctly!")
        print("\n📚 Available Endpoints:")
        print("   Notifications:")
        print("     GET    /api/v1/notifications/")
        print("     PUT    /api/v1/notifications/{id}/read")
        print("     PUT    /api/v1/notifications/mark-all-read")
        print("     GET    /api/v1/notifications/stats")
        print("     POST   /api/v1/notifications/test-email")
        print("     POST   /api/v1/notifications/test-push")
        print("\n   Reports:")
        print("     POST   /api/v1/reports/")
        print("     GET    /api/v1/reports/")
        print("     PUT    /api/v1/reports/{id}/resolve")
        print("     GET    /api/v1/reports/stats")
        print("     GET    /api/v1/reports/my-reports")
        print("\n   Analytics:")
        print("     GET    /api/v1/analytics/user-stats")
        print("     GET    /api/v1/analytics/study-set-stats/{id}")
        print("     GET    /api/v1/analytics/class-stats/{id}")
        print("     GET    /api/v1/analytics/study-session-stats")
        print("     GET    /api/v1/analytics/comprehensive")
        print("     GET    /api/v1/analytics/dashboard")
        print("     GET    /api/v1/analytics/progress/{study_set_id}")
    else:
        print("\n❌ Some Phase 6 features are not working correctly.")
        print("Please check the server logs and ensure all endpoints are properly configured.")


if __name__ == "__main__":
    main() 