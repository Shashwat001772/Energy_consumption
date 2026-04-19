import pandas as pd
import numpy as np
import joblib
from xgboost import XGBRegressor
from sklearn.model_selection import train_test_split, RandomizedSearchCV
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from data_pipeline import preprocess_and_engineer_features

def train_and_save_model(data_path='energy_data.csv', model_path='xgboost_model.joblib'):
    print(f"Loading data from {data_path}...")
    try:
        df = pd.read_csv(data_path)
    except FileNotFoundError:
        print(f"Error: {data_path} not found. Please run generate_data.py first.")
        return

    print("Running Data Pipeline (Preprocessing & Feature Engineering)...")
    df = preprocess_and_engineer_features(df, is_training=True)
    
    # Define features and target
    features = [
        'Hour', 'DayOfWeek', 'DayOfYear', 'IsWeekend', 
        'Temperature_C', 'Humidity_percent',
        'Temp_lag1', 'Temp_lag24', 'Temp_rolling_mean_24', 'Hum_lag1'
    ]
    target = 'Energy_Consumption_kWh'
    
    X = df[features]
    y = df[target]
    
    print("Splitting dataset (Time-Series Split style)...")
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, shuffle=False)
    
    print("Training XGBoost Regressor with Hyperparameter Tuning...")
    xgb = XGBRegressor(random_state=42, n_jobs=-1)
    
    param_grid = {
        'n_estimators': [100, 200],
        'max_depth': [4, 6, 8],
        'learning_rate': [0.05, 0.1]
    }
    
    search = RandomizedSearchCV(xgb, param_distributions=param_grid, n_iter=5, cv=3, scoring='neg_mean_squared_error', random_state=42, verbose=1)
    search.fit(X_train, y_train)
    
    best_model = search.best_estimator_
    
    print("Evaluating Best Model...")
    predictions = best_model.predict(X_test)
    mse = mean_squared_error(y_test, predictions)
    rmse = np.sqrt(mse)
    mae = mean_absolute_error(y_test, predictions)
    r2 = r2_score(y_test, predictions)
    
    print("-" * 30)
    print("XGBoost Model Performance:")
    print(f"Best Params: {search.best_params_}")
    print(f"RMSE: {rmse:.2f} kWh")
    print(f"MAE:  {mae:.2f} kWh")
    print(f"R2:   {r2:.4f}")
    print("-" * 30)
    
    print(f"Saving model to {model_path}...")
    joblib.dump({
        'model': best_model,
        'features': features
    }, model_path)
    print("Done!")

if __name__ == '__main__':
    train_and_save_model()
