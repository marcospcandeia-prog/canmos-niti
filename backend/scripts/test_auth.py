"""
Manual test script for authentication API
Run: python scripts/test_auth.py
"""

import asyncio
import httpx


BASE_URL = "http://localhost:8000"


async def test_auth_flow():
    """Test complete authentication flow"""
    
    async with httpx.AsyncClient() as client:
        print("=" * 60)
        print("TESTING AUTHENTICATION FLOW")
        print("=" * 60)
        
        # Test 1: Register
        print("\n1. Testing POST /auth/register")
        print("-" * 60)
        
        register_data = {
            "nome": "Teste Usuário",
            "cpf": "12345678901",
            "email": "teste@example.com",
            "telefone": "11999999999",
            "senha": "senhaSegura123",
            "lgpd_consent": True
        }
        
        try:
            response = await client.post(f"{BASE_URL}/auth/register", json=register_data)
            if response.status_code == 201:
                print("✓ Register successful")
                user = response.json()
                print(f"  User ID: {user['id']}")
                print(f"  UUID: {user['uuid']}")
                print(f"  Email: {user['email']}")
            elif response.status_code == 400:
                print("✗ User already exists (expected if running multiple times)")
            else:
                print(f"✗ Register failed: {response.status_code}")
                print(f"  {response.text}")
        except Exception as e:
            print(f"✗ Error: {e}")
        
        # Test 2: Login
        print("\n2. Testing POST /auth/login")
        print("-" * 60)
        
        login_data = {
            "email": "teste@example.com",
            "senha": "senhaSegura123"
        }
        
        try:
            response = await client.post(f"{BASE_URL}/auth/login", json=login_data)
            if response.status_code == 200:
                print("✓ Login successful")
                tokens = response.json()
                access_token = tokens["access_token"]
                refresh_token = tokens["refresh_token"]
                print(f"  Access Token: {access_token[:50]}...")
                print(f"  Refresh Token: {refresh_token[:50]}...")
                print(f"  Expires in: {tokens['expires_in']} seconds")
            else:
                print(f"✗ Login failed: {response.status_code}")
                print(f"  {response.text}")
                return
        except Exception as e:
            print(f"✗ Error: {e}")
            return
        
        # Test 3: Access protected route (when implemented)
        print("\n3. Testing protected route with access token")
        print("-" * 60)
        
        headers = {"Authorization": f"Bearer {access_token}"}
        
        try:
            response = await client.get(f"{BASE_URL}/users/me", headers=headers)
            if response.status_code == 200:
                print("✓ Protected route accessed successfully")
                user = response.json()
                print(f"  Current user: {user.get('email', 'N/A')}")
            elif response.status_code == 404:
                print("⚠ Route /users/me not implemented yet (expected)")
            else:
                print(f"✗ Failed: {response.status_code}")
                print(f"  {response.text}")
        except Exception as e:
            print(f"✗ Error: {e}")
        
        # Test 4: Refresh token
        print("\n4. Testing POST /auth/refresh")
        print("-" * 60)
        
        refresh_data = {"refresh_token": refresh_token}
        
        try:
            response = await client.post(f"{BASE_URL}/auth/refresh", json=refresh_data)
            if response.status_code == 200:
                print("✓ Token refresh successful")
                new_tokens = response.json()
                new_access_token = new_tokens["access_token"]
                print(f"  New Access Token: {new_access_token[:50]}...")
                print(f"  Expires in: {new_tokens['expires_in']} seconds")
            else:
                print(f"✗ Refresh failed: {response.status_code}")
                print(f"  {response.text}")
        except Exception as e:
            print(f"✗ Error: {e}")
        
        # Test 5: Logout
        print("\n5. Testing POST /auth/logout")
        print("-" * 60)
        
        try:
            response = await client.post(f"{BASE_URL}/auth/logout")
            if response.status_code == 200:
                print("✓ Logout successful")
                result = response.json()
                print(f"  Message: {result['message']}")
            else:
                print(f"✗ Logout failed: {response.status_code}")
                print(f"  {response.text}")
        except Exception as e:
            print(f"✗ Error: {e}")
        
        # Test 6: Invalid credentials
        print("\n6. Testing invalid credentials")
        print("-" * 60)
        
        invalid_login = {
            "email": "teste@example.com",
            "senha": "senhaERRADA"
        }
        
        try:
            response = await client.post(f"{BASE_URL}/auth/login", json=invalid_login)
            if response.status_code == 401:
                print("✓ Invalid credentials correctly rejected")
            else:
                print(f"✗ Expected 401, got: {response.status_code}")
        except Exception as e:
            print(f"✗ Error: {e}")
        
        print("\n" + "=" * 60)
        print("TESTS COMPLETED")
        print("=" * 60)


if __name__ == "__main__":
    print("\nMake sure backend is running on http://localhost:8000")
    print("Run: uvicorn app.main:app --reload\n")
    
    try:
        asyncio.run(test_auth_flow())
    except KeyboardInterrupt:
        print("\n\nTests interrupted by user")
    except Exception as e:
        print(f"\n\nError running tests: {e}")
