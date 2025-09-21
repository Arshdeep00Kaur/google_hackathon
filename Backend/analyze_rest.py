#!/usr/bin/env python3
"""
REST API Analysis Tool

This script analyzes the current API routes and evaluates their compliance
with RESTful principles.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def analyze_restful_compliance():
    """Analyze API routes for RESTful compliance"""
    
    print("=== REST API Compliance Analysis ===\n")
    
    # Import the router
    try:
        from app.api.v1.router import api_router
        
        print("📋 Current API Routes:")
        print("-" * 50)
        
        routes_analysis = []
        
        for route in api_router.routes:
            if hasattr(route, 'path') and hasattr(route, 'methods'):
                methods = list(route.methods)
                if 'HEAD' in methods:
                    methods.remove('HEAD')  # Remove auto-generated HEAD
                if 'OPTIONS' in methods:
                    methods.remove('OPTIONS')  # Remove auto-generated OPTIONS
                
                route_info = {
                    'methods': methods,
                    'path': route.path,
                    'restful': True,
                    'issues': []
                }
                
                routes_analysis.append(route_info)
                print(f"{', '.join(methods):12} {route.path}")
        
        print("\n" + "=" * 80)
        print("🔍 RESTful Compliance Analysis:")
        print("=" * 80)
        
        # Analyze each route
        restful_issues = []
        
        for route in routes_analysis:
            path = route['path']
            methods = route['methods']
            issues = []
            
            # Check for RESTful violations
            
            # 1. Check for verb-like paths
            verb_violations = []
            path_parts = path.strip('/').split('/')
            for part in path_parts:
                if part in ['async', 'health-check', 'cleanup', 'stats', 'ping']:
                    verb_violations.append(part)
            
            if verb_violations:
                issues.append(f"Contains verb-like segments: {verb_violations}")
            
            # 2. Check for proper HTTP methods usage
            if 'POST' in methods and any(verb in path for verb in ['get', 'list', 'fetch']):
                issues.append("POST method with GET-like path")
            
            if 'GET' in methods and any(verb in path for verb in ['create', 'add', 'submit']):
                issues.append("GET method with POST-like path")
            
            # 3. Check for nested resources
            if path.count('{') > 1:
                issues.append("Multiple path parameters - consider resource hierarchy")
            
            if issues:
                route['restful'] = False
                route['issues'] = issues
                restful_issues.extend(issues)
        
        # Print detailed analysis
        print("\n🚨 RESTful Violations Found:")
        print("-" * 50)
        
        violation_count = 0
        for route in routes_analysis:
            if not route['restful']:
                violation_count += 1
                print(f"\n❌ {', '.join(route['methods'])} {route['path']}")
                for issue in route['issues']:
                    print(f"   • {issue}")
        
        print(f"\n📊 Summary:")
        print(f"   Total Routes: {len(routes_analysis)}")
        print(f"   RESTful Routes: {len(routes_analysis) - violation_count}")
        print(f"   Non-RESTful Routes: {violation_count}")
        print(f"   Compliance Rate: {((len(routes_analysis) - violation_count) / len(routes_analysis) * 100):.1f}%")
        
        # Provide recommendations
        print("\n💡 RESTful Improvement Recommendations:")
        print("-" * 50)
        
        recommendations = {
            '/jobs/chat': 'POST /jobs (with type: "chat" in body)',
            '/jobs/document': 'POST /jobs (with type: "document" in body)',
            '/jobs/health-check': 'POST /jobs (with type: "health-check" in body)',
            '/jobs/cleanup': 'DELETE /jobs?older_than=7days',
            '/jobs/stats': 'GET /jobs/statistics',
            '/jobs/ping': 'GET /health/jobs',
            '/queries/async': 'POST /queries (with async: true in body)',
            '/documents/async': 'POST /documents (with async: true in body)',
            '/queue/health': 'GET /health/queue'
        }
        
        for current, suggested in recommendations.items():
            if any(current in route['path'] for route in routes_analysis):
                print(f"   {current:20} → {suggested}")
        
        print("\n🎯 RESTful Principles to Follow:")
        print("-" * 50)
        print("   1. Use nouns for resources, not verbs")
        print("   2. Use HTTP methods for actions (GET, POST, PUT, DELETE)")
        print("   3. Use query parameters for filtering/options")
        print("   4. Use request body for data/configuration")
        print("   5. Maintain resource hierarchy: /parent/{id}/child")
        print("   6. Use status codes appropriately")
        
        return violation_count == 0
        
    except Exception as e:
        print(f"❌ Error analyzing routes: {e}")
        return False

if __name__ == "__main__":
    analyze_restful_compliance()