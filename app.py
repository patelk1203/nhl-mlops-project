from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import xgboost as xgb
import pandas as pd
import uvicorn

# 1. Initialize the Web Application
app = FastAPI(title="NHL Game Predictor API")

# Allow web pages to request data from this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# 2. Load the trained Machine Learning Model from the file
print("Loading model...")
model = xgb.Booster()
model.load_model('model/xgboost-model')
print("Model loaded successfully!")

# 3. Team Name Mapping
# During training, we converted text like "TOR" into numbers. 
# We must use the exact same alphabetical numbering scheme here.
team_mapping = {
    'ANA': 0, 'ARI': 1, 'BOS': 2, 'BUF': 3, 'CAR': 4, 'CBJ': 5, 'CGY': 6, 'CHI': 7, 
    'COL': 8, 'DAL': 9, 'DET': 10, 'EDM': 11, 'FLA': 12, 'LAK': 13, 'MIN': 14, 'MTL': 15, 
    'NJD': 16, 'NSH': 17, 'NYI': 18, 'NYR': 19, 'OTT': 20, 'PHI': 21, 'PIT': 22, 'SEA': 23, 
    'SJS': 24, 'STL': 25, 'TBL': 26, 'TOR': 27, 'UTA': 28, 'VAN': 29, 'VGK': 30, 'WPG': 31, 'WSH': 32
}

# 4. Define the Web Endpoints
@app.get("/")
def read_root():
    return {"message": "Welcome to the NHL Prediction API! Go to /predict to use the model."}

@app.get("/predict")
def predict_game(home: str, away: str):
    # Ensure inputs are uppercase
    home = home.upper()
    away = away.upper()
    
    # Validate the teams exist
    if home not in team_mapping or away not in team_mapping:
        raise HTTPException(status_code=400, detail="Invalid team abbreviation. Use 3-letter codes like TOR, BOS, etc.")
        
    # Format the data exactly how XGBoost saw it during training: ['season', 'home_team', 'away_team']
    input_data = pd.DataFrame({
        'season': [20252026], # Assuming predictions are for the current season
        'home_team': [team_mapping[home]],
        'away_team': [team_mapping[away]]
    })
    
    # Convert to XGBoost's specific Matrix format
    dmatrix = xgb.DMatrix(input_data)
    
    # MAKE THE PREDICTION!
    prediction = model.predict(dmatrix)
    
    # The model outputs a probability between 0.0 and 1.0. We multiply by 100 for a percentage.
    win_probability = float(prediction[0]) * 100
    
    return {
        "matchup": f"{home} (Home) vs {away} (Away)",
        "home_win_probability": f"{win_probability:.2f}%",
        "away_win_probability": f"{(100 - win_probability):.2f}%"
    }

# 5. Run the Server
if __name__ == "__main__":
    # This turns on the local web server on port 8000
    uvicorn.run(app, host="0.0.0.0", port=8000)