import logging
import os

# Create logs directory if it doesn't exist
os.makedirs("logs", exist_ok=True)

# Configure the logger
logging.basicConfig(
    filename='logs/predictions.log',
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger("energy_forecaster")

def log_prediction(size: int, status: str):
    logger.info(f"Prediction requested: Size={size}, Status={status}")

def log_error(error_msg: str):
    logger.error(f"Error during prediction: {error_msg}")
