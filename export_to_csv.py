import psycopg2
import pandas as pd
import os

# 1. Database connection parameters
DB_PARAMS = {
    "host": "localhost",
    "database": "nhl_predictions_db",
    "user": "nhl_analytics_user",
    "password": "nhl_secure_password",
    "port": "5432"
}

def export_data_for_ml():
    print("Connecting to local PostgreSQL database...")
    
    try:
        conn = psycopg2.connect(**DB_PARAMS)
        
        # 2. Extract the data using a SQL query
        query = "SELECT * FROM nhl_games;"
        
        # Load the SQL query directly into a Pandas DataFrame
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        print(f"Successfully extracted {len(df)} rows.")
        
        # 3. Feature Engineering: Create the Target Variable
        # Machine learning models need a clear "answer key" to learn from. 
        # We will create a column called 'home_win'. If home_score > away_score, it equals 1. Else, 0.
        df['home_win'] = (df['home_score'] > df['away_score']).astype(int)
        
        # 4. Save to CSV
        output_path = os.path.join("data", "model_ready_data.csv")
        
        # We drop the raw scores because if the model has the final scores, 
        # predicting the winner is cheating (data leakage). We only want it to learn from pre-game data.
        df_for_training = df[['season', 'home_team', 'away_team', 'home_win']]
        
        df_for_training.to_csv(output_path, index=False)
        print(f"Success! Model-ready data saved to: {output_path}")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    export_data_for_ml()