"""
Test script to create a space and identify any errors.
"""
import asyncio
import httpx
import json

async def test_create_space():
    base_url = "http://localhost:8000"
    
    # First, login to get a token
    login_data = {
        "email": "admin@test.com",
        "password": "admin123"
    }
    
    print("🔐 Logging in...")
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(f"{base_url}/api/v1/auth/login", json=login_data)
            print(f"Login status: {response.status_code}")
            
            if response.status_code == 200:
                token_data = response.json()
                access_token = token_data.get("access_token")
                print(f"✅ Login successful! Token: {access_token[:20]}...")
                
                # Now try to create a space
                headers = {"Authorization": f"Bearer {access_token}"}
                space_data = {
                    "name": "Test Conference Room",
                    "description": "A test conference room for meetings",
                    "space_type": "hourly",
                    "capacity": 10,
                    "price_per_unit": 50.00,
                    "is_available": True,
                    "floor": "2nd Floor",
                    "area_sqm": 25.5
                }
                
                print("\n📦 Creating space...")
                print(f"Space data: {json.dumps(space_data, indent=2)}")
                
                response = await client.post(
                    f"{base_url}/api/v1/spaces/",
                    json=space_data,
                    headers=headers
                )
                
                print(f"\n📊 Response status: {response.status_code}")
                print(f"Response body: {response.text}")
                
                if response.status_code == 201:
                    print("✅ Space created successfully!")
                    print(json.dumps(response.json(), indent=2))
                else:
                    print(f"❌ Error creating space!")
                    try:
                        error_detail = response.json()
                        print(f"Error details: {json.dumps(error_detail, indent=2)}")
                    except:
                        print(f"Raw error: {response.text}")
            else:
                print(f"❌ Login failed!")
                print(f"Response: {response.text}")
                
        except Exception as e:
            print(f"❌ Exception occurred: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_create_space())
