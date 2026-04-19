import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def generate_energy_data(start_date='2021-01-01', end_date='2023-12-31', output_file='energy_data.csv'):
    # Create date range
    dates = pd.date_range(start=start_date, end=end_date, freq='H')
    n = len(dates)
    
    # Pre-calculate time features
    hours = dates.hour
    day_of_week = dates.dayofweek
    day_of_year = dates.dayofyear
    
    # Simulate weather variables
    # Temperature: seasonal sine wave + daily sine wave + noise
    annual_temp_pattern = -15 * np.cos(2 * np.pi * day_of_year / 365) + 15
    daily_temp_pattern = -5 * np.cos(2 * np.pi * (hours - 4) / 24)
    temperature = (annual_temp_pattern + daily_temp_pattern + np.random.normal(0, 3, n)).to_numpy()
    
    # Humidity
    annual_hum_pattern = 10 * np.cos(2 * np.pi * day_of_year / 365) + 60
    daily_hum_pattern = 10 * np.cos(2 * np.pi * hours / 24)
    humidity = (annual_hum_pattern + daily_hum_pattern + np.random.normal(0, 5, n)).to_numpy()
    humidity = np.clip(humidity, 20, 100)
    
    # Base energy consumption
    base_consumption = 500
    
    # Daily pattern: peaks at 9AM and 7PM
    hourly_pattern = np.zeros(n)
    hourly_pattern += np.where((hours >= 7) & (hours <= 10), 100, 0)
    hourly_pattern += np.where((hours >= 17) & (hours <= 21), 150, 0)
    hourly_pattern += np.where((hours >= 0) & (hours <= 5), -100, 0)
    
    # Weekly pattern: lower on weekends
    weekly_pattern = np.where(day_of_week >= 5, -80, 0)
    
    # Weather impact: higher consumption for heating (low temp) and cooling (high temp)
    heating_demand = np.maximum(15 - temperature, 0) * 10
    cooling_demand = np.maximum(temperature - 25, 0) * 15
    weather_impact = heating_demand + cooling_demand
    
    # Put it all together
    energy_consumption = base_consumption + hourly_pattern + weekly_pattern + weather_impact + np.random.normal(0, 20, n)
    
    # Inject anomalies for pipeline testing
    np.random.seed(42)
    # 1. Missing values: drop ~1% of temperature data
    mask_temp = np.random.rand(n) < 0.01
    temperature[mask_temp] = np.nan
    
    # 2. Outliers: add massive spikes (1.5x to 3x) to ~0.5% of energy consumption data
    mask_outlier = np.random.rand(n) < 0.005
    energy_consumption[mask_outlier] *= np.random.uniform(1.5, 3.0, size=mask_outlier.sum())

    # Create DataFrame
    df = pd.DataFrame({
        'Datetime': dates,
        'Temperature_C': temperature,
        'Humidity_percent': humidity,
        'Energy_Consumption_kWh': energy_consumption
    })
    
    df.to_csv(output_file, index=False)
    print(f"Generated {n} rows of data and saved to {output_file}")

if __name__ == '__main__':
    generate_energy_data()
