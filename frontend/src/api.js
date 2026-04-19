import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_URL,
});

export const requestRealtimePrediction = async (dataPayload) => {
  // dataPayload is an array of objects
  try {
    const response = await api.post('/predict', { data: dataPayload });
    return response.data;
  } catch (error) {
    console.error("Prediction Error:", error.response?.data || error.message);
    throw error;
  }
};

export const requestBatchPrediction = async (file) => {
  const formData = new FormData();
  formData.append('file', file);
  try {
    const response = await api.post('/predict/batch', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  } catch (error) {
    console.error("Batch Error:", error.response?.data || error.message);
    throw error;
  }
};

export const fetchHistoricalAnalytics = async () => {
  try {
    const response = await api.get('/analytics/historical');
    return response.data;
  } catch (error) {
    console.error("Analytics Error:", error.response?.data || error.message);
    throw error;
  }
};

export const fetchFutureForecast = async () => {
  try {
    const response = await api.get('/predict/forecast');
    return response.data;
  } catch (error) {
    console.error("Forecast Error:", error.response?.data || error.message);
    throw error;
  }
};

