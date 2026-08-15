from src.models.flood_prediction import fetch_and_predict, run_prediction_scenario

if __name__ == "__main__":
    print("GeoGuard - Flood Risk Prediction System")
    print("=" * 50)

    fetch_and_predict(api_key="2efc6badb1e0f099f544e8e84a4fc440")

