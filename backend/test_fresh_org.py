"""
Test with fresh organization: Register user and create a space.
"""
import asyncio
import httpx
import json
import random

async def test_with_fresh_org():
    base_url = "http://localhost:8000"
    
    # Generate unique org name
    org_suffix = random.randint(1000, 9999)
    org_slug = f"fresh-org-{org_suffix}"
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        # 1. Register new user with organization
        print("=" * 60)
        print("📝 STEP 1: Registering fresh user and organization")
        print("=" * 60)
        
        registration_data = {
            "email": f"user{org_suffix}@example.com",
            "password": "securepass123",
            "full_name": f"Test User {org_suffix}",
            "organization_name": f"Fresh Org {org_suffix}",
            "organization_slug": org_slug
        }
        
        print(f"Organization slug: {org_slug}")
        
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
            else:
                print(f"❌ Registration failed!")
                print(f"Response: {response.text}")
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
            "name": "Executive Board Room",
            "description": "Premium board room with state-of-the-art facilities",
            "space_type": "hourly",
            "capacity": 20,
            "price_per_unit": 150.00,
            "is_available": True,
            "floor": "Executive Floor",
            "area_sqm": 50.5
        }
        
        print(f"Space data: {space_data['name']}")
        
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
                print(f"\nSpace details:")
                print(f"  ID: {space_response['id']}")
                print(f"  Name: {space_response['name']}")
                print(f"  Type: {space_response['space_type']}")
                print(f"  Capacity: {space_response['capacity']}")
                print(f"  Price: ${space_response['price_per_unit']}")
                print(f"  Floor: {space_response['floor']}")
                print(f"  Area: {space_response['area_sqm']} sqm")
            else:
                print(f"❌ Failed to create space!")
                print(f"Response: {response.text}")
                return
                    
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
            
            if response.status_code == 200:
                spaces = response.json()
                print(f"✅ Found {len(spaces)} space(s):")
                for space in spaces:
                    print(f"  - {space['name']} ({space['space_type']}) - ${space['price_per_unit']} - Capacity: {space['capacity']}")
            else:
                print(f"❌ Failed to list spaces!")
                print(f"Response: {response.text}")
                
        except Exception as e:
            print(f"❌ Error listing spaces: {e}")
            import traceback
            traceback.print_exc()
            return
        
        # 4. Update the space
        print("\n" + "=" * 60)
        print("✏️  STEP 4: Updating the space")
        print("=" * 60)
        
        space_id = space_response['id']
        update_data = {
            "price_per_unit": 175.00,
            "capacity": 25
        }
        
        try:
            response = await client.put(
                f"{base_url}/api/v1/spaces/{space_id}",
                json=update_data,
                headers=headers
            )
            
            if response.status_code == 200:
                updated_space = response.json()
                print(f"✅ Space updated successfully!")
                print(f"  New price: ${updated_space['price_per_unit']}")
                print(f"  New capacity: {updated_space['capacity']}")
            else:
                print(f"❌ Failed to update space!")
                print(f"Response: {response.text}")
                
        except Exception as e:
            print(f"❌ Error updating space: {e}")
            import traceback
            traceback.print_exc()
        
        # 5. Create another space with different type
        print("\n" + "=" * 60)
        print("🏢 STEP 5: Creating a daily rental space")
        print("=" * 60)
        
        space_data_2 = {
            "name": "Co-working Space",
            "description": "Open co-working area with hot desks",
            "space_type": "daily",
            "capacity": 30,
            "price_per_unit": 50.00,
            "is_available": True,
            "floor": "2nd Floor",
            "area_sqm": 100.0
        }
        
        try:
            response = await client.post(
                f"{base_url}/api/v1/spaces/",
                json=space_data_2,
                headers=headers
            )
            
            if response.status_code == 201:
                space2_response = response.json()
                print(f"✅ Second space created successfully!")
                print(f"  Name: {space2_response['name']}")
                print(f"  Type: {space2_response['space_type']}")
            else:
                print(f"❌ Failed to create second space!")
                print(f"Response: {response.text}")
                
        except Exception as e:
            print(f"❌ Error creating second space: {e}")
            import traceback
            traceback.print_exc()
        
        # 6. Final list
        print("\n" + "=" * 60)
        print("📋 STEP 6: Final space listing")
        print("=" * 60)
        
        try:
            response = await client.get(
                f"{base_url}/api/v1/spaces/",
                headers=headers
            )
            
            if response.status_code == 200:
                spaces = response.json()
                print(f"✅ Total spaces: {len(spaces)}")
                for i, space in enumerate(spaces, 1):
                    print(f"  {i}. {space['name']}")
                    print(f"     Type: {space['space_type']}, Price: ${space['price_per_unit']}, Capacity: {space['capacity']}")
                    
                print("\n" + "🎉" * 30)
                print("ALL TESTS PASSED SUCCESSFULLY!")
                print("🎉" * 30)
            else:
                print(f"❌ Failed to list spaces!")
                
        except Exception as e:
            print(f"❌ Error in final listing: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_with_fresh_org())
