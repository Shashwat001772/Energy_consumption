# ⚡ Energy Consumption Forecasting System

An interactive, machine-learning-powered web dashboard designed to simulate and forecast electrical grid loads based on historical energy data, extreme weather scenarios, and modern grid-disruption technologies (like EVs and Solar power).

## 📖 Project Overview
This project simulates an end-to-end data science pipeline. It synthesizes a realistic energy usage dataset, trains a Machine Learning model (**Random Forest Regressor**) to learn consumption patterns, and serves up a powerful **Streamlit** web dashboard. Users can explore historical trends and utilize an interactive "Sandbox" to predict future grid stress when subjected to extreme weather or technological shifts.

## ✨ Key Pros & Advantages
- **Deep Interactivity (Grid Sandbox)**: Instead of passive static charts, users can manipulate grid behavior in real-time. You can manually edit hour-by-hour temperatures via an editable data table to instantly visualize grid strain.
- **"What-If" Game-Theoretic Analysis**: Built-in toggle switches allow users to mathematically impose grid strains, such as adding 10,000 Electric Vehicles (evening load surge) or integrating Regional Solar Generation (daytime load drops, creating the famous "Duck Curve" effect).
- **Dynamic Grid Overload Warnings**: The system evaluates historical capacity limits and automatically redlines grid failure conditions if simulated user consumption dangerously exceeds the limits.
- **Explainable AI (XAI) Insights**: The dashboard actively highlights relative **Feature Importances**, giving total transparency into how the Random Forest algorithm weights inputs like time-of-day versus atmospheric conditions.
- **Fast, Local Architecture**: The app seamlessly combines data ingestion, model processing, and the front-end interface into a single, highly performant Python project without requiring heavy external database dependencies.

## ⚙️ How It Works (Technical Architecture)

The project is split into three main operational modules:

1. **`generate_data.py` (Data Synthesis)**:
   - Synthesizes several years of hourly historical data into a local `energy_data.csv`.
   - Programmatically embeds realistic correlations into the data points: Higher consumption during extreme heat/cold (HVAC usage), lower consumption on weekends, and distinct daily behavioral peaks (mornings and evenings).

2. **`train_model.py` (AI Training Pipeline)**:
   - Ingests the historical dataset and executes Feature Engineering (e.g., parsing raw 'Datetimes' into variables a model can understand like 'Hour', 'Day of Year', 'Is Weekend').
   - Trains a `scikit-learn` **Random Forest Regressor** to predict energy usage with high accuracy (R² typically > 0.95), dumping the trained parameters to a lightweight `model.joblib` file.

3. **`app.py` (Streamlit Frontend Data-App)**:
   - Serves an interactive **Streamlit** frontend accessible in any web browser.
   - Loads the compiled dataset and AI model into cache memory to enable instantaneous grid simulation metrics and Plotly graphic renderings based entirely on real-time user sliding/editing actions.

## 🚀 Getting Started

Follow these steps to run the application on your local machine:

### 1. Install Dependencies
Ensure you have Python installed, then install the required packages:
```bash
pip install -r requirements.txt
```

### 2. Generate Historical Data
Run the data synthesizer to physically create the `energy_data.csv` database:
```bash
python generate_data.py
```

### 3. Train the AI Model
Train the Random Forest model to lock in your algorithm and output `model.joblib`:
```bash
python train_model.py
```

### 4. Launch the Dashboard
Start the Streamlit web application:
```bash
streamlit run app.py
```
*The Streamlit server will actively output a URL. Navigate to `http://localhost:8501` in your web browser to play with the interactive dashboard.*

## 🛠️ Built With Built With modern Python Stack
* [Python](https://www.python.org/) - Core programming logic
* [Streamlit](https://streamlit.io/) - Web framework & dashboard UI
* [Scikit-Learn](https://scikit-learn.org/) - Machine Learning Regressor Models
* [Plotly](https://plotly.com/) - Advanced interactive charting and heatmaps
* [Pandas & NumPy](https://pandas.pydata.org/) - Data Structuring, Filtering, and Mathematics
