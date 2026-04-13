import pandas as pd
import numpy as np
import joblib
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

def engineer_features(df):
    """Extract features from datetime"""
    df['Datetime'] = pd.to_datetime(df['Datetime'])
    df['Hour'] = df['Datetime'].dt.hour
    df['DayOfWeek'] = df['Datetime'].dt.dayofweek
    df['DayOfYear'] = df['Datetime'].dt.dayofyear
    df['IsWeekend'] = df['DayOfWeek'].apply(lambda x: 1 if x >= 5 else 0)
    return df

def train_and_save_model(data_path='energy_data.csv', model_path='model.joblib'):
    print(f"Loading data from {data_path}...")
    try:
        df = pd.read_csv(data_path)
    except FileNotFoundError:
        print(f"Error: {data_path} not found. Please run generate_data.py first.")
        return

    print("Engineering features...")
    df = engineer_features(df)
    
    # Define features and target
    features = ['Hour', 'DayOfWeek', 'DayOfYear', 'IsWeekend', 'Temperature_C', 'Humidity_percent']
    target = 'Energy_Consumption_kWh'
    
    X = df[features]
    y = df[target]
    
    print("Splitting dataset...")
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    print("Training Random Forest model (this may take a moment)...")
    model = RandomForestRegressor(n_estimators=100, max_depth=10, random_state=42, n_jobs=-1)
    model.fit(X_train, y_train)
    
    print("Evaluating model...")
    predictions = model.predict(X_test)
    mse = mean_squared_error(y_test, predictions)
    rmse = np.sqrt(mse)
    mae = mean_absolute_error(y_test, predictions)
    r2 = r2_score(y_test, predictions)
    
    print("-" * 30)
    print("Model Performance:")
    print(f"RMSE: {rmse:.2f} kWh")
    print(f"MAE:  {mae:.2f} kWh")
    print(f"R2:   {r2:.4f}")
    print("-" * 30)
    
    print(f"Saving model to {model_path}...")
    joblib.dump(model, model_path)
    print("Done!")

if __name__ == '__main__':
    train_and_save_model()
