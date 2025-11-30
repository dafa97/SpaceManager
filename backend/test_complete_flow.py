"""
Complete test: Register user and create a space.
"""
import asyncio
import httpx
import json

async def test_complete_flow():
    base_url = "http://localhost:8000"
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        # 1. Register new user with organization
        print("=" * 60)
        print("📝 STEP 1: Registering new user and organization")
        print("=" * 60)
        
        registration_data = {
            "email": "newuser@example.com",
            "password": "securepass123",
            "full_name": "New User",
            "organization_name": "Example Corp",
            "organization_slug": "example-corp"
        }
        
        try:
            response = await client.post(
                f"{base_url}/api/v1/auth/register",
                json=registration_data
            )
            print(f"Registration status: {response.status_code}")
            
            if response.status_code in [200, 201]:
                token_data = response.json()
                access_token = token_data.get("access_token")
                print(f"✅ Registration successful!")
                print(f"   Access token: {access_token[:30]}...")
            elif response.status_code == 400:
                print(f"⚠️  User might already exist, trying to login...")
                
                # Try to login instead
                login_data = {
                    "email": "newuser@example.com",
                    "password": "securepass123"
                }
                
                response = await client.post(
                    f"{base_url}/api/v1/auth/login",
                    json=login_data
                )
                
                if response.status_code == 200:
                    token_data = response.json()
                    access_token = token_data.get("access_token")
                    print(f"✅ Login successful!")
                    print(f"   Access token: {access_token[:30]}...")
                else:
                    print(f"❌ Login failed: {response.text}")
                    return
            else:
                print(f"❌ Registration failed: {response.text}")
                return
                
        except Exception as e:
            print(f"❌ Error during registration: {e}")
            import traceback
            traceback.print_exc()
            return
        
        # 2. Create a space
        print("\n" + "=" * 60)
        print("🏢 STEP 2: Creating a test space")
        print("=" * 60)
        
        headers = {"Authorization": f"Bearer {access_token}"}
        space_data = {
            "name": "Conference Room A",
            "description": "Large conference room with projector and whiteboard",
            "space_type": "hourly",
            "capacity": 15,
            "price_per_unit": 75.50,
            "is_available": True,
            "floor": "3rd Floor",
            "area_sqm": 35.0
        }
        
        print(f"Space data:")
        print(json.dumps(space_data, indent=2))
        
        try:
            response = await client.post(
                f"{base_url}/api/v1/spaces/",
                json=space_data,
                headers=headers
            )
            
            print(f"\n📊 Response status: {response.status_code}")
            
            if response.status_code == 201:
                space_response = response.json()
                print("✅ Space created successfully!")
                print(json.dumps(space_response, indent=2))
            else:
                print(f"❌ Failed to create space!")
                print(f"Response text: {response.text}")
                try:
                    error_detail = response.json()
                    print(f"\nError details:")
                    print(json.dumps(error_detail, indent=2))
                except:
                    pass
                    
        except Exception as e:
            print(f"❌ Error creating space: {e}")
            import traceback
            traceback.print_exc()
            return
        
        # 3. List all spaces
        print("\n" + "=" * 60)
        print("📋 STEP 3: Listing all spaces")
        print("=" * 60)
        
        try:
            response = await client.get(
                f"{base_url}/api/v1/spaces/",
                headers=headers
            )
            
            print(f"List spaces status: {response.status_code}")
            
            if response.status_code == 200:
                spaces = response.json()
                print(f"✅ Found {len(spaces)} space(s):")
                for space in spaces:
                    print(f"   - {space['name']} ({space['space_type']}) - ${space['price_per_unit']}")
            else:
                print(f"❌ Failed to list spaces: {response.text}")
                
        except Exception as e:
            print(f"❌ Error listing spaces: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_complete_flow())
