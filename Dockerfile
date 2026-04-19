FROM python:3.10-slim

WORKDIR /app

# Copy the trained model
COPY xgboost_model.joblib .

# Copy data pipeline code (required by joblib/backend)
COPY data_pipeline.py .

WORKDIR /app/backend

# Copy requirements
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY backend/ .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
