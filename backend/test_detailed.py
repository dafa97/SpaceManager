"""
Complete test: Register user and create a space (with file output).
"""
import asyncio
import httpx
import json
import sys

async def test_complete_flow():
    base_url = "http://localhost:8000"
    output = []
    
    def log(msg):
        print(msg)
        output.append(msg)
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        # 1. Register new user with organization
        log("=" * 60)
        log("📝 STEP 1: Registering new user and organization")
        log("=" * 60)
        
        registration_data = {
            "email": "newuser2@example.com",
            "password": "securepass123",
            "full_name": "New User 2",
            "organization_name": "Example Corp 2",
            "organization_slug": "example-corp-2"
        }
        
        try:
            response = await client.post(
                f"{base_url}/api/v1/auth/register",
                json=registration_data
            )
            log(f"Registration status: {response.status_code}")
            
            if response.status_code in [200, 201]:
                token_data = response.json()
                access_token = token_data.get("access_token")
                log(f"✅ Registration successful!")
                log(f"   Access token: {access_token[:30]}...")
            elif response.status_code == 400:
                log(f"⚠️  User might already exist, trying to login...")
                
                # Try to login instead
                login_data = {
                    "email": "newuser2@example.com",
                    "password": "securepass123"
                }
                
                response = await client.post(
                    f"{base_url}/api/v1/auth/login",
                    json=login_data
                )
                
                if response.status_code == 200:
                    token_data = response.json()
                    access_token = token_data.get("access_token")
                    log(f"✅ Login successful!")
                    log(f"   Access token: {access_token[:30]}...")
                else:
                    log(f"❌ Login failed: {response.text}")
                    return
            else:
                log(f"❌ Registration failed: {response.text}")
                return
                
        except Exception as e:
            log(f"❌ Error during registration: {e}")
            import traceback
            log(traceback.format_exc())
            return
        
        # 2. Create a space
        log("\n" + "=" * 60)
        log("🏢 STEP 2: Creating a test space")
        log("=" * 60)
        
        headers = {"Authorization": f"Bearer {access_token}"}
        space_data = {
            "name": "Conference Room B",
            "description": "Medium conference room with video conferencing",
            "space_type": "hourly",
            "capacity": 12,
            "price_per_unit": 65.00,
            "is_available": True,
            "floor": "2nd Floor",
            "area_sqm": 28.0
        }
        
        log(f"Space data:")
        log(json.dumps(space_data, indent=2))
        
        try:
            response = await client.post(
                f"{base_url}/api/v1/spaces/",
                json=space_data,
                headers=headers
            )
            
            log(f"\n📊 Response status: {response.status_code}")
            log(f"Response text: {response.text}")
            
            if response.status_code == 201:
                space_response = response.json()
                log("✅ Space created successfully!")
                log(json.dumps(space_response, indent=2))
            else:
                log(f"❌ Failed to create space!")
                try:
                    error_detail = response.json()
                    log(f"\nError details:")
                    log(json.dumps(error_detail, indent=2))
                except:
                    pass
                    
        except Exception as e:
            log(f"❌ Error creating space: {e}")
            import traceback
            log(traceback.format_exc())
            return
        
        # 3. List all spaces
        log("\n" + "=" * 60)
        log("📋 STEP 3: Listing all spaces")
        log("=" * 60)
        
        try:
            response = await client.get(
                f"{base_url}/api/v1/spaces/",
                headers=headers
            )
            
            log(f"List spaces status: {response.status_code}")
            
            if response.status_code == 200:
                spaces = response.json()
                log(f"✅ Found {len(spaces)} space(s):")
                for space in spaces:
                    log(f"   - ID: {space['id']}, Name: {space['name']} ({space['space_type']}) - ${space['price_per_unit']}")
            else:
                log(f"❌ Failed to list spaces: {response.text}")
                
        except Exception as e:
            log(f"❌ Error listing spaces: {e}")
            import traceback
            log(traceback.format_exc())
    
    # Write output to file
    with open('test_output_detailed.txt', 'w') as f:
        f.write('\n'.join(output))
    
    log("\nTest output written to test_output_detailed.txt")

if __name__ == "__main__":
    asyncio.run(test_complete_flow())
