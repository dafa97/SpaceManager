"""
Setup test data: Create organization and user for testing.
"""
import asyncio
import httpx
import json

async def setup_test_data():
    base_url = "http://localhost:8000"
    
    async with httpx.AsyncClient() as client:
        # 1. Create organization
        print("🏢 Creating organization...")
        org_data = {
            "name": "Test Company",
            "slug": "test-company",
            "email": "info@testcompany.com",
            "phone": "+1234567890"
        }
        
        try:
            response = await client.post(f"{base_url}/api/v1/orgs/", json=org_data)
            print(f"Organization creation status: {response.status_code}")
            
            if response.status_code in [200, 201]:
                org_response = response.json()
                print(f"✅ Organization created: {json.dumps(org_response, indent=2)}")
                org_id = org_response.get("id")
            elif response.status_code == 400:
                # Organization might already exist
                print(f"⚠️  Organization might already exist: {response.text}")
                # Try to get it
                response = await client.get(f"{base_url}/api/v1/orgs/")
                if response.status_code == 200:
                    orgs = response.json()
                    if orgs:
                        org_id = orgs[0]["id"]
                        print(f"Using existing organization: {orgs[0]}")
                    else:
                        print("❌ No organizations found")
                        return
                else:
                    print(f"❌ Failed to get organizations: {response.text}")
                    return
            else:
                print(f"❌ Failed to create organization: {response.text}")
                return
        except Exception as e:
            print(f"❌ Error creating organization: {e}")
            import traceback
            traceback.print_exc()
            return
        
        # 2. Register user
        print("\n👤 Registering user...")
        user_data = {
            "email": "testuser@test.com",
            "password": "testpass123",
            "full_name": "Test User",
            "organization_id": org_id
        }
        
        try:
            response = await client.post(f"{base_url}/api/v1/auth/register", json=user_data)
            print(f"User registration status: {response.status_code}")
            
            if response.status_code in [200, 201]:
                user_response = response.json()
                print(f"✅ User registered: {json.dumps(user_response, indent=2)}")
            else:
                print(f"⚠️  User registration response: {response.text}")
        except Exception as e:
            print(f"❌ Error registering user: {e}")
            import traceback
            traceback.print_exc()
            return
        
        # 3. Try to login
        print("\n🔐 Testing login...")
        login_data = {
            "email": "testuser@test.com",
            "password": "testpass123"
        }
        
        try:
            response = await client.post(f"{base_url}/api/v1/auth/login", json=login_data)
            print(f"Login status: {response.status_code}")
            
            if response.status_code == 200:
                token_data = response.json()
                print(f"✅ Login successful!")
                print(f"Access token: {token_data.get('access_token')[:30]}...")
            else:
                print(f"❌ Login failed: {response.text}")
        except Exception as e:
            print(f"❌ Error during login: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(setup_test_data())
