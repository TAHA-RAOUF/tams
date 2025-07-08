#!/usr/bin/env python3
"""
Test script to ensure the new structure works properly
"""
import os
import sys
import subprocess
import requests
import time
import signal
from datetime import datetime

# Constants
API_BASE_URL = "http://localhost:5000/api/v1"
USERNAME = "testuser"
EMAIL = "testuser@example.com"
PASSWORD = "password123"

# Function to start the API server
def start_server():
    """Start the Flask server in a subprocess"""
    process = subprocess.Popen(
        ['python', 'run.py'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        preexec_fn=os.setsid  # Allow killing the process group
    )
    
    # Give the server time to start
    print("Starting server...")
    time.sleep(3)
    return process

# Function to stop the server
def stop_server(process):
    """Stop the Flask server"""
    if process:
        os.killpg(os.getpgid(process.pid), signal.SIGTERM)
        print("Server stopped.")

# Test user registration and login
def test_authentication():
    """Test user registration and login endpoints"""
    print("\nTesting authentication endpoints...")
    
    # Test registration
    register_data = {
        "username": USERNAME,
        "email": EMAIL,
        "password": PASSWORD
    }
    
    try:
        response = requests.post(f"{API_BASE_URL}/auth/register", json=register_data)
        if response.status_code == 201:
            print("✅ User registration successful")
        elif response.status_code == 409:
            print("✅ User already exists (registration attempted before)")
        else:
            print(f"❌ Registration failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error during registration: {str(e)}")
        return None
    
    # Test login
    login_data = {
        "username": USERNAME,
        "password": PASSWORD
    }
    
    try:
        response = requests.post(f"{API_BASE_URL}/auth/login", json=login_data)
        if response.status_code == 200:
            token = response.json().get('access_token')
            print("✅ Login successful")
            return token
        else:
            print(f"❌ Login failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error during login: {str(e)}")
        return None

# Test creating and fetching anomalies
def test_anomalies(token):
    """Test anomaly creation and retrieval"""
    print("\nTesting anomaly endpoints...")
    
    if not token:
        print("❌ Skipping anomaly tests (no token)")
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create an anomaly
    anomaly_data = {
        "title": "Test Anomaly",
        "description": "This is a test anomaly",
        "num_equipement": "TEST-001",
        "systeme": "TEST-SYS",
        "description_equipement": "Test Equipment",
        "section_proprietaire": "TEST",
        "date_detection": datetime.now().isoformat()
    }
    
    try:
        response = requests.post(f"{API_BASE_URL}/anomalies", json=anomaly_data, headers=headers)
        if response.status_code in (201, 200):
            anomaly_id = response.json().get('id')
            print(f"✅ Anomaly created with ID: {anomaly_id}")
            
            # Test retrieving the anomaly
            response = requests.get(f"{API_BASE_URL}/anomalies/{anomaly_id}", headers=headers)
            if response.status_code == 200:
                print("✅ Anomaly retrieved successfully")
            else:
                print(f"❌ Failed to retrieve anomaly: {response.status_code} - {response.text}")
        else:
            print(f"❌ Failed to create anomaly: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Error during anomaly tests: {str(e)}")

# Test the dashboard API
def test_dashboard(token):
    """Test dashboard endpoints"""
    print("\nTesting dashboard endpoints...")
    
    if not token:
        print("❌ Skipping dashboard tests (no token)")
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{API_BASE_URL}/dashboard/metrics", headers=headers)
        if response.status_code == 200:
            print("✅ Dashboard metrics retrieved successfully")
        else:
            print(f"❌ Failed to retrieve dashboard metrics: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Error during dashboard tests: {str(e)}")

# Main test function
def main():
    """Run all tests"""
    print("=" * 60)
    print("TAMS API Test Suite")
    print("=" * 60)
    
    # Start the server
    server_process = start_server()
    
    try:
        # Run tests
        token = test_authentication()
        test_anomalies(token)
        test_dashboard(token)
        
        print("\n" + "=" * 60)
        print("Tests completed.")
        print("=" * 60)
    finally:
        # Stop the server
        stop_server(server_process)

if __name__ == "__main__":
    main()
