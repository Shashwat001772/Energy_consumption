from pydantic import BaseModel, Field
from typing import List, Optional

class HourlyWeather(BaseModel):
    Hour: int = Field(..., ge=0, le=23)
    DayOfWeek: int = Field(..., ge=0, le=6, description="0=Mon, 6=Sun")
    DayOfYear: int = Field(..., ge=1, le=366)
    IsWeekend: int = Field(..., ge=0, le=1)
    Temperature_C: float = Field(..., description="Temperature in Celsius")
    Humidity_percent: float = Field(..., description="Relative humidity percentage (20-100)")
    
    # Optional lag features, will be computed/backfilled if not provided
    Temp_lag1: Optional[float] = None
    Temp_lag24: Optional[float] = None
    Temp_rolling_mean_24: Optional[float] = None
    Hum_lag1: Optional[float] = None

class PredictionRequest(BaseModel):
    data: List[HourlyWeather]

class PredictionResult(BaseModel):
    Hour: int
    Predicted_Consumption_kWh: float

class PredictionResponse(BaseModel):
    predictions: List[PredictionResult]
    message: str
    status: str
