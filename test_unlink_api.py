import requests
import time

BASE_URL = "http://localhost:5000/api/bgg"
GAME_NAME = "蓋亞計畫"

def test_unlink():
    print(f"Testing unlink for {GAME_NAME}...")
    url = f"{BASE_URL}/games/link/{GAME_NAME}"
    
    try:
        response = requests.delete(url)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200 and response.json().get('success'):
            print("Unlink API test PASSED!")
        else:
            print("Unlink API test FAILED!")
            
    except Exception as e:
        print(f"Error testing API: {e}")

if __name__ == "__main__":
    # Wait a bit for server to be ready
    time.sleep(2)
    test_unlink()
