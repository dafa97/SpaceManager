import json
import urllib.request
import urllib.error
import sys

BASE_URL = "http://localhost:8000/api/v1"

def make_request(url, method="GET", data=None, headers=None):
    if headers is None:
        headers = {}
    
    if data:
        data = json.dumps(data).encode("utf-8")
        headers["Content-Type"] = "application/json"
    
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as response:
            return response.status, json.loads(response.read().decode())
    except urllib.error.HTTPError as e:
        content = e.read().decode()
        try:
            return e.code, json.loads(content)
        except:
            return e.code, content
    except Exception as e:
        print(f"Error: {e}")
        return 500, str(e)

def run_test():
    print("1. Registering new user...")
    register_data = {
        "email": "test_auth_v4@example.com",
        "password": "password123",
        "full_name": "Test User",
        "organization_name": "Test Org V4",
        "organization_slug": "test-org-v4"
    }
    
    status, response = make_request(f"{BASE_URL}/auth/register", "POST", register_data)
    
    if status == 400 and "already registered" in str(response):
        print("   User already exists, trying login...")
        login_data = {
            "email": register_data["email"],
            "password": register_data["password"]
        }
        status, response = make_request(f"{BASE_URL}/auth/login", "POST", login_data)
    
    if status not in [200, 201]:
        print(f"   Failed: {status} - {response}")
        return

    tokens = response
    access_token = tokens["access_token"]
    refresh_token = tokens["refresh_token"]
    print(f"   Success! Got tokens.")
    print(f"   Access Token: {access_token[:20]}...")
    
    print("\n2. Verifying /me endpoint...")
    headers = {"Authorization": f"Bearer {access_token}"}
    status, user = make_request(f"{BASE_URL}/auth/me", "GET", headers=headers)
    
    if status != 200:
        print(f"   Failed: {status} - {user}")
        return
    print(f"   Success! User: {user['email']}")

    print("\n3. Testing Token Refresh...")
    # Refresh token endpoint expects query param 'refresh_token'
    refresh_url = f"{BASE_URL}/auth/refresh?refresh_token={refresh_token}"
    status, new_tokens = make_request(refresh_url, "POST")
    
    if status != 200:
        print(f"   Failed: {status} - {new_tokens}")
        return
        
    new_access_token = new_tokens["access_token"]
    print(f"   Success! Got new access token: {new_access_token[:20]}...")
    
    # Update access token
    access_token = new_access_token
    headers = {"Authorization": f"Bearer {access_token}"}

    print("\n4. Creating a second organization...")
    org_data = {
        "name": "Second Org V4",
        "slug": "second-org-v4"
    }
    status, org = make_request(f"{BASE_URL}/orgs/", "POST", org_data, headers)
    
    if status == 400 and "already taken" in str(org):
        print("   Org already exists, skipping creation.")
    elif status != 201:
        print(f"   Failed: {status} - {org}")
    else:
        print(f"   Success! Created Org: {org['organization']['name']}")

    print("\n5. Listing organizations...")
    status, orgs = make_request(f"{BASE_URL}/orgs/", "GET", headers=headers)
    
    if status != 200:
        print(f"   Failed: {status} - {orgs}")
        return
        
    print(f"   Success! Found {len(orgs)} organizations:")
    for membership in orgs:
        print(f"   - {membership['organization']['name']} ({membership['role']})")

if __name__ == "__main__":
    run_test()
