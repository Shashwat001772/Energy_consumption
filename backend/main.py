from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import numpy as np
import joblib
import io
import os
import sys

# Add parent directory to path to import data pipeline
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
try:
    from data_pipeline import preprocess_and_engineer_features
except ImportError:
    pass # handle case if run from different dir

from schemas import PredictionRequest, PredictionResponse, PredictionResult
from logger import log_prediction, log_error

app = FastAPI(title="Energy Forecasting API", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Relative to backend/
MODEL_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "xgboost_model.joblib")
DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "energy_data.csv")
model_data = None
historical_df = None
from datetime import datetime, timedelta

@app.on_event("startup")
def load_artifacts():
    global model_data, historical_df
    try:
        model_data = joblib.load(MODEL_PATH)
        print("Model loaded successfully.")
    except Exception as e:
        log_error(f"Failed to load model: {str(e)}")
        print(f"Warning: Model not found at {MODEL_PATH}")
        
    try:
        if os.path.exists(DATA_PATH):
            historical_df = pd.read_csv(DATA_PATH)
            historical_df['Datetime'] = pd.to_datetime(historical_df['Datetime'])
            historical_df['Month'] = historical_df['Datetime'].dt.month
            historical_df['Hour'] = historical_df['Datetime'].dt.hour
            historical_df['DayOfWeek'] = historical_df['Datetime'].dt.dayofweek
            print("Historical data loaded successfully.")
    except Exception as e:
        log_error(f"Failed to load historical data: {str(e)}")
        print("Warning: Failed to load historical data")

@app.post("/predict", response_model=PredictionResponse)
def predict(request: PredictionRequest):
    if not model_data:
        raise HTTPException(status_code=500, detail="Model not loaded")
        
    try:
        # Convert request to dataframe
        dicts = [item.dict() for item in request.data]
        df = pd.DataFrame(dicts)
         
        features = model_data['features']
        
        # Dynamic gap filling for realtime inputs where previous data might be missing
        df['Temp_lag1'] = df.get('Temp_lag1', np.nan).fillna(df['Temperature_C'].shift(1).bfill())
        df['Temp_lag24'] = df.get('Temp_lag24', np.nan).fillna(df['Temperature_C'])
        df['Temp_rolling_mean_24'] = df.get('Temp_rolling_mean_24', np.nan).fillna(df['Temperature_C'].rolling(24, min_periods=1).mean().bfill())
        df['Hum_lag1'] = df.get('Hum_lag1', np.nan).fillna(df['Humidity_percent'].shift(1).bfill())
        
        # Make sure columns match features expectation
        # Specifically, bfill one last time just in case there's only 1 row
        df = df.bfill().ffill()
        
        X = df[features]
        
        predictions = model_data['model'].predict(X)
        
        results = []
        for i, pred in enumerate(predictions):
            results.append(PredictionResult(
                Hour=df.iloc[i]['Hour'],
                Predicted_Consumption_kWh=round(float(pred), 2)
            ))
            
        log_prediction(len(results), "v2_success")
        
        return PredictionResponse(
            predictions=results,
            message="Predictions computed successfully",
            status="success"
        )
        
    except Exception as e:
        log_error(str(e))
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/predict/batch")
async def predict_batch(file: UploadFile = File(...)):
    if not model_data:
        raise HTTPException(status_code=500, detail="Model not loaded")
        
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files are allowed")
        
    try:
        contents = await file.read()
        df = pd.read_csv(io.StringIO(contents.decode('utf-8')))
        
        # Use full pipeline since it's a batch CSV
        from data_pipeline import preprocess_and_engineer_features
        df_processed = preprocess_and_engineer_features(df, is_training=False)
        
        X = df_processed[model_data['features']]
        predictions = model_data['model'].predict(X)
        
        df['Predicted_Consumption_kWh'] = predictions
        
        log_prediction(len(predictions), "batch_success")
        
        return {
            "message": f"Successfully processed {len(predictions)} rows.",
            "data": df[['Datetime', 'Predicted_Consumption_kWh']].to_dict(orient='records')
        }
        
    except Exception as e:
        log_error(str(e))
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/analytics/historical")
def get_historical_analytics():
    if historical_df is None:
        raise HTTPException(status_code=404, detail="Historical data not available")
    
    # 1. Monthly Averages (Summer vs Winter)
    monthly_avg = historical_df.groupby('Month')['Energy_Consumption_kWh'].mean().reset_index()
    monthly_avg['Month_Name'] = pd.to_datetime(monthly_avg['Month'], format='%m').dt.month_name()
    
    # 2. Hourly Averages (Night vs Day)
    hourly_avg = historical_df.groupby('Hour')['Energy_Consumption_kWh'].mean().reset_index()
    
    # 3. Weekday vs Weekend
    historical_df['IsWeekend'] = historical_df['DayOfWeek'] >= 5
    weekend_avg = historical_df.groupby('IsWeekend')['Energy_Consumption_kWh'].mean().reset_index()
    weekend_avg['Type'] = weekend_avg['IsWeekend'].map({True: 'Weekend', False: 'Weekday'})
    
    return {
        "monthly": monthly_avg[['Month_Name', 'Energy_Consumption_kWh']].to_dict(orient='records'),
        "hourly": hourly_avg.to_dict(orient='records'),
        "weekend_vs_weekday": weekend_avg[['Type', 'Energy_Consumption_kWh']].to_dict(orient='records')
    }

@app.get("/predict/forecast")
def get_forecast():
    if not model_data:
        raise HTTPException(status_code=500, detail="Model not loaded")
        
    try:
        features = model_data['features']
        
        # Generate 7 days of future data
        now = datetime.now().replace(minute=0, second=0, microsecond=0)
        future_dates = [now + timedelta(hours=i) for i in range(24 * 7)]
        
        # Simulate some weather for future dates (base temp 25, varying)
        future_data = []
        for dt in future_dates:
            hour = dt.hour
            day_of_year = dt.timetuple().tm_yday
            day_of_week = dt.weekday()
            is_weekend = 1 if day_of_week >= 5 else 0
            
            # Simple simulation of temperature curve
            temp = 25 - (5 * np.cos((2 * np.pi * (hour - 4)) / 24))
            hum = 60 + (10 * np.cos((2 * np.pi * hour) / 24))
            
            future_data.append({
                'Datetime': dt.isoformat(),
                'Hour': hour,
                'DayOfWeek': day_of_week,
                'DayOfYear': day_of_year,
                'IsWeekend': is_weekend,
                'Temperature_C': temp,
                'Humidity_percent': hum,
                'Temp_lag1': temp,
                'Temp_lag24': temp,
                'Temp_rolling_mean_24': temp,
                'Hum_lag1': hum
            })
            
        df = pd.DataFrame(future_data)
        X = df[features]
        predictions = model_data['model'].predict(X)
        df['Predicted_Consumption_kWh'] = predictions
        
        # Group by day for daily trends
        df['Date'] = pd.to_datetime(df['Datetime']).dt.date
        daily_trends = df.groupby('Date')['Predicted_Consumption_kWh'].sum().reset_index()
        daily_trends['Date'] = daily_trends['Date'].astype(str)
        
        return {
            "hourly_forecast": df[['Datetime', 'Predicted_Consumption_kWh', 'Temperature_C']].to_dict(orient='records'),
            "daily_trends": daily_trends.to_dict(orient='records'),
            "next_hour": round(float(predictions[0]), 2),
            "next_day": round(float(daily_trends.iloc[0]['Predicted_Consumption_kWh']), 2),
            "next_week": round(float(df['Predicted_Consumption_kWh'].sum()), 2)
        }
    except Exception as e:
        log_error(str(e))
        raise HTTPException(status_code=400, detail=str(e))
