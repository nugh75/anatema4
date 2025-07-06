#!/usr/bin/env python3
"""
Test script per verificare le API delle etichette
"""
import requests
import json

# Configurazione
BASE_URL = "http://localhost:5000"
PROJECT_ID = "2efbcd28-f2ce-4f29-9819-f2079ff9fea3"

def test_api_endpoints():
    print("🔵 Testing Label Store API endpoints...")
    
    # Test 1: Get labels
    print("\n1. Testing GET /api/projects/{project_id}/labels")
    try:
        response = requests.get(f"{BASE_URL}/api/projects/{PROJECT_ID}/labels")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            labels = data.get('labels', [])
            print(f"   Found {len(labels)} labels")
            if labels:
                first_label = labels[0]
                label_id = first_label.get('id')
                print(f"   First label: {first_label.get('name')} (ID: {label_id})")
                return label_id
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"   Exception: {e}")
    
    return None

def test_label_operations(label_id):
    if not label_id:
        print("❌ No label ID to test operations")
        return
    
    print(f"\n2. Testing operations on label ID {label_id}")
    
    # Test 2: Get cell values
    print(f"\n   Testing GET /api/projects/{PROJECT_ID}/labels/{label_id}/cell-values")
    try:
        response = requests.get(f"{BASE_URL}/api/projects/{PROJECT_ID}/labels/{label_id}/cell-values")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            cell_values = data.get('cell_values', [])
            print(f"   Found {len(cell_values)} cell values")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"   Exception: {e}")

def test_auth_status(token):
    print("\n3. Testing authentication status")
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    print(f"   Using token: {token is not None}")
    try:
        response = requests.get(f"{BASE_URL}/api/auth/status", headers=headers)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Authenticated: {data.get('authenticated', False)}")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"   Exception: {e}")

if __name__ == "__main__":
    auth_token = test_auth_login()
    test_auth_status(auth_token)
    label_id = test_api_endpoints(auth_token)
    if label_id:
        test_label_operations(label_id, auth_token)
        test_batch_approve(auth_token)
        test_batch_reject(auth_token)
    print("\n✅ API testing completed")

def test_auth_login():
    print("\n1. Testing authentication login")
    login_data = {
        "username": "testuser",
        "password": "testpassword"
    }
    response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
    print(f"   Login status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print("   ✅ Authentication successful")
        return data.get('token')
    else:
        print(f"   ❌ Login failed: {response.text}")
        return None

def test_api_endpoints(token=None):
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    print("\n🔵 Testing Label Store API endpoints...")
    
    print(f"\n1. Testing GET /api/projects/{PROJECT_ID}/labels")
    try:
        response = requests.get(f"{BASE_URL}/api/projects/{PROJECT_ID}/labels", headers=headers)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            labels = data.get('labels', [])
            print(f"   Found {len(labels)} labels")
            return labels[0].get('id') if labels else None
        elif response.status_code == 401:
            print("   ⚠️  Authentication required for this endpoint")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"   Exception: {e}")
    return None

def test_batch_approve(token):
    print("\n4. Testing POST /api/projects/{project_id}/batch/approve")
    headers = {"Authorization": f"Bearer {token}"}
    # Test with valid batch
    valid_batch = {"suggestion_ids": ["valid-uuid1", "valid-uuid2"]}
    response = requests.post(f"{BASE_URL}/api/projects/{PROJECT_ID}/batch/approve", json=valid_batch, headers=headers)
    print(f"   Batch approve status: {response.status_code}")
    if response.status_code != 200:
        print(f"   Batch approve error: {response.text}")

    # Test with invalid project ID
    invalid_project_id = "invalid-uuid"
    response = requests.post(f"{BASE_URL}/api/projects/{invalid_project_id}/batch/approve", json=valid_batch, headers=headers)
    print(f"   Invalid project ID status: {response.status_code}")
    if response.status_code != 404:
        print(f"   Invalid project ID error: {response.text}")

    # Test with non-existent suggestion IDs
    non_existent_batch = {"suggestion_ids": ["non-existent-uuid1", "non-existent-uuid2"]}
    response = requests.post(f"{BASE_URL}/api/projects/{PROJECT_ID}/batch/approve", json=non_existent_batch, headers=headers)
    print(f"   Non-existent suggestions status: {response.status_code}")
    if response.status_code != 200:
        print(f"   Non-existent suggestions error: {response.text}")

def test_batch_reject(token):
    print("\n5. Testing POST /api/projects/{project_id}/batch/reject")
    headers = {"Authorization": f"Bearer {token}"}
    # Test with valid batch
    valid_batch = {"suggestion_ids": ["valid-uuid1", "valid-uuid2"]}
    response = requests.post(f"{BASE_URL}/api/projects/{PROJECT_ID}/batch/reject", json=valid_batch, headers=headers)
    print(f"   Batch reject status: {response.status_code}")
    if response.status_code != 200:
        print(f"   Batch reject error: {response.text}")

    # Test with invalid project ID
    invalid_project_id = "invalid-uuid"
    response = requests.post(f"{BASE_URL}/api/projects/{invalid_project_id}/batch/reject", json=valid_batch, headers=headers)
    print(f"   Invalid project ID status: {response.status_code}")
    if response.status_code != 404:
        print(f"   Invalid project ID error: {response.text}")

def test_auth_login():
    print("\n1. Testing authentication login")
    login_data = {
        "username": "testuser",
        "password": "testpassword"
    }
    response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
    print(f"   Login status: {response.status_code}")
    if response.status_code == 200:
        print("   ✅ Authentication successful")
    else:
        print(f"   ❌ Login failed: {response.text}")
    print("\n✅ API testing completed")

def test_batch_approve():
    print("\n4. Testing POST /api/projects/{project_id}/batch/approve")
    # Test with valid batch
    valid_batch = {"suggestion_ids": ["valid-uuid1", "valid-uuid2"]}
    response = requests.post(f"{BASE_URL}/api/projects/{PROJECT_ID}/batch/approve", json=valid_batch)
    print(f"   Batch approve status: {response.status_code}")
    if response.status_code != 200:
        print(f"   Batch approve error: {response.text}")

    # Test with invalid project ID
    invalid_project_id = "invalid-uuid"
    response = requests.post(f"{BASE_URL}/api/projects/{invalid_project_id}/batch/approve", json=valid_batch)
    print(f"   Invalid project ID status: {response.status_code}")
    if response.status_code != 404:
        print(f"   Invalid project ID error: {response.text}")

    # Test with non-existent suggestion IDs
    non_existent_batch = {"suggestion_ids": ["non-existent-uuid1", "non-existent-uuid2"]}
    response = requests.post(f"{BASE_URL}/api/projects/{PROJECT_ID}/batch/approve", json=non_existent_batch)
    print(f"   Non-existent suggestions status: {response.status_code}")
    if response.status_code != 200:
        print(f"   Non-existent suggestions error: {response.text}")

def test_batch_reject():
    print("\n5. Testing POST /api/projects/{project_id}/batch/reject")
    # Test with valid batch
    valid_batch = {"suggestion_ids": ["valid-uuid1", "valid-uuid2"]}
    response = requests.post(f"{BASE_URL}/api/projects/{PROJECT_ID}/batch/reject", json=valid_batch)
    print(f"   Batch reject status: {response.status_code}")
    if response.status_code != 200:
        print(f"   Batch reject error: {response.text}")

    # Test with invalid project ID
    invalid_project_id = "invalid-uuid"
    response = requests.post(f"{BASE_URL}/api/projects/{invalid_project_id}/batch/reject", json=valid_batch)
    print(f"   Invalid project ID status: {response.status_code}")
    if response.status_code != 404:
        print(f"   Invalid project ID error: {response.text}")
