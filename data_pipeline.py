import pandas as pd
import numpy as np

def preprocess_and_engineer_features(df, is_training=True):
    """
    Data pipeline:
    1. Clean missing values
    2. Handle outliers (in training)
    3. Generate explicit time features
    4. Generate lag features for time-series forecasting capability
    """
    # 1. Clean Missing Values (Interpolate missing temperatures)
    df['Temperature_C'] = df['Temperature_C'].interpolate(method='linear')
    df['Temperature_C'] = df['Temperature_C'].fillna(method='bfill').fillna(method='ffill')
    
    # Ensure Datetime is proper format
    df['Datetime'] = pd.to_datetime(df['Datetime'])
    df = df.sort_values('Datetime')
    
    # 2. Extract Basic Time Features
    df['Hour'] = df['Datetime'].dt.hour
    df['DayOfWeek'] = df['Datetime'].dt.dayofweek
    df['DayOfYear'] = df['Datetime'].dt.dayofyear
    df['IsWeekend'] = df['DayOfWeek'].apply(lambda x: 1 if x >= 5 else 0)
    
    # 3. Create Lag Features for proper time-series dependencies
    # These features help the model understand trend and recent momentum
    df['Temp_lag1'] = df['Temperature_C'].shift(1)
    df['Temp_lag24'] = df['Temperature_C'].shift(24)
    df['Temp_rolling_mean_24'] = df['Temperature_C'].rolling(window=24).mean()
    df['Hum_lag1'] = df['Humidity_percent'].shift(1)
    
    if is_training and 'Energy_Consumption_kWh' in df.columns:
        # 4. Handle Outliers (Cap extreme energy spikes introduced maliciously)
        Q1 = df['Energy_Consumption_kWh'].quantile(0.25)
        Q3 = df['Energy_Consumption_kWh'].quantile(0.75)
        IQR = Q3 - Q1
        upper_bound = Q3 + 3 * IQR
        df['Energy_Consumption_kWh'] = np.where(
            df['Energy_Consumption_kWh'] > upper_bound,
            upper_bound,
            df['Energy_Consumption_kWh']
        )
        
        # Drop NaNs created by shifting
        df = df.dropna().reset_index(drop=True)
    else:
        # In inference mode, if target lags are missing, we backfill them or assume they're passed.
        # But in a simple REST API, we normally wouldn't have historical target lags unless passed explicitly.
        # We'll rely on time + weather lags backfilled for API inference simplicity.
        df = df.bfill()
        
    return df
