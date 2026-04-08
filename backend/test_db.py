import requests
import time

BASE_URL = "http://localhost:8000"

def test_prediction_persistence():
    print("Testing prediction persistence...")
    
    # 1. Make a prediction
    payload = {
        "lat": 23.8103,
        "lon": 90.4125,
        "date": 200,
        "elevation": 10.5,
        "slope": 0.5,
        "landcover": 11,
        "precip_1d": 50.0,
        "precip_3d": 120.0,
        "precip_7d": 200.0,
        "precip_14d": 300.0,
        "dis_last": 1500.0,
        "dis_trend_3": 100.0,
        "dayofyear": 200
    }
    
    try:
        response = requests.post(f"{BASE_URL}/predict", json=payload)
        response.raise_for_status()
        print("Prediction successful.")
        
        # 2. Check history
        response = requests.get(f"{BASE_URL}/history")
        response.raise_for_status()
        history = response.json()
        
        if len(history) > 0:
            print(f"History check successful. Found {len(history)} records.")
            print(f"Latest record: {history[0]['location']} - {history[0]['risk_level']}")
        else:
            print("History check failed: No records found.")
            
    except Exception as e:
        print(f"Test failed: {e}")

if __name__ == "__main__":
    test_prediction_persistence()
