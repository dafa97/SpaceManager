import httpx
import asyncio
import json

BASE_URL = "http://localhost:8000/api/v1"

async def reproduce():
    # 1. Login
    login_data = {
        "email": "testuser@test.com",
        "password": "testpass123"
    }
    print(f"Logging in with {login_data['email']}...")
    async with httpx.AsyncClient() as client:
        try:
            # Login endpoint expects JSON with email/password
            response = await client.post(f"{BASE_URL}/auth/login", json=login_data)
            if response.status_code != 200:
                print(f"Login failed: {response.status_code} {response.text}")
                return
            
            token_data = response.json()
            access_token = token_data["access_token"]
            print("Login successful. Token received.")
        except Exception as e:
            print(f"Login failed with exception: {e}")
            return

        # 2. Access /spaces
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        print(f"Accessing {BASE_URL}/spaces...")
        try:
            response = await client.get(f"{BASE_URL}/spaces", headers=headers)
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text}")
            print(f"Headers: {response.headers}")
        except Exception as e:
            print(f"Request failed with exception: {e}")

if __name__ == "__main__":
    asyncio.run(reproduce())
