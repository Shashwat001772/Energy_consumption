import streamlit as st
import pandas as pd
import numpy as np
import joblib
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# Page configuration
st.set_page_config(page_title="Energy Forecaster Professional", page_icon="⚡", layout="wide")

# Custom CSS for better styling
st.markdown("""
<style>
    .reportview-container {
        background: #f0f2f6
    }
    .sidebar .sidebar-content {
        background: #ffffff
    }
    h1, h2, h3 {
        color: #1e3d59;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    try:
        df = pd.read_csv('energy_data.csv')
        df['Datetime'] = pd.to_datetime(df['Datetime'])
        return df
    except FileNotFoundError:
        return None

@st.cache_resource
def load_model():
    try:
        return joblib.load('model.joblib')
    except FileNotFoundError:
        return None

df = load_data()
model = load_model()

if df is None or model is None:
    st.error("Data or Model not found. Please run the generation and training scripts first.")
    st.stop()

# --- SIDEBAR ---
with st.sidebar:
    st.title("⚡ Settings & Filters")
    st.markdown("Configure your dashboard view.")
    
    # Global date filter
    min_date = df['Datetime'].min().date()
    max_date = df['Datetime'].max().date()
    
    date_range = st.date_input(
        "Historical Data Range", 
        value=(max_date - timedelta(days=30), max_date),
        min_value=min_date, 
        max_value=max_date
    )
    
    st.markdown("---")
    st.markdown("### System Info")
    st.info("Model: Random Forest Regressor\n\nVersion: 3.0.0 (Interactive)\n\nStatus: Online 🟢")

# Filter data based on sidebar input
if len(date_range) == 2:
    start_dt, end_dt = date_range
    mask = (df['Datetime'].dt.date >= start_dt) & (df['Datetime'].dt.date <= end_dt)
    filtered_df = df.loc[mask]
else:
    filtered_df = df

st.title("⚡ Energy Simulation Sandbox")
st.markdown("A professional interactive dashboard for predicting energy grid stress via real-time modifiers and editable weather.")

# --- TABS ---
tab1, tab2, tab3 = st.tabs(["📊 Historical Overview", "🚀 Grid Stress Simulator", "🧠 Model Insights"])

with tab1:
    st.header("Historical Energy Consumption")
    
    st.subheader("Key Performance Indicators (Selected Period)")
    col1, col2, col3, col4 = st.columns(4)
    
    current_avg = filtered_df['Energy_Consumption_kWh'].mean()
    current_max = filtered_df['Energy_Consumption_kWh'].max()
    current_total = filtered_df['Energy_Consumption_kWh'].sum()
    
    if len(date_range) == 2:
        period_days = (end_dt - start_dt).days + 1
        past_start = start_dt - timedelta(days=period_days)
        past_mask = (df['Datetime'].dt.date >= past_start) & (df['Datetime'].dt.date < start_dt)
        past_df = df.loc[past_mask]
        
        past_avg = past_df['Energy_Consumption_kWh'].mean() if not past_df.empty else current_avg
        delta_avg = current_avg - past_avg
    else:
        delta_avg = 0
        
    col1.metric("Average Hourly Usage", f"{current_avg:.1f} kWh", f"{delta_avg:.1f} kWh vs Prior Period" if delta_avg else None)
    col2.metric("Peak Usage Limit", f"{current_max:.1f} kWh")
    col3.metric("Total Period Load", f"{current_total / 1000:.1f} MWh")
    col4.metric("Data Points Analyzed", f"{len(filtered_df):,}")
    
    st.divider()
    
    st.subheader("Consumption Trends & Correlations")
    fig_ts = px.line(filtered_df, x='Datetime', y='Energy_Consumption_kWh', 
                     title='Energy Consumption Over Time',
                     labels={'Datetime': 'Date & Time', 'Energy_Consumption_kWh': 'Energy (kWh)'})
    fig_ts.update_layout(template="plotly_dark" if st.get_option("theme.base") == "dark" else "plotly_white")
    st.plotly_chart(fig_ts, use_container_width=True)
    
    col_heat, col_scatter = st.columns(2)
    
    with col_heat:
        heatmap_data = filtered_df.copy()
        heatmap_data['Day'] = heatmap_data['Datetime'].dt.day_name()
        heatmap_data['Hour'] = heatmap_data['Datetime'].dt.hour
        day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        grouped = heatmap_data.groupby(['Day', 'Hour'])['Energy_Consumption_kWh'].mean().reset_index()
        
        fig_heat = px.density_heatmap(grouped, x='Hour', y='Day', z='Energy_Consumption_kWh',
                                      category_orders={"Day": day_order},
                                      color_continuous_scale='Viridis',
                                      title="Average Load Profile (Hour vs Day)")
        st.plotly_chart(fig_heat, use_container_width=True)
        
    with col_scatter:
        fig_scatter = px.scatter(filtered_df, x='Temperature_C', y='Energy_Consumption_kWh',
                                 color='Humidity_percent', opacity=0.6,
                                 title="Impact of Weather on Consumption",
                                 labels={'Temperature_C': 'Temp (°C)', 'Energy_Consumption_kWh': 'Energy (kWh)', 'Humidity_percent': 'Humidity (%)'})
        st.plotly_chart(fig_scatter, use_container_width=True)

with tab2:
    st.header("Predict Future Grid Stress")
    st.markdown("Use this interactive sandbox to simulate how extreme weather and modern technologies affect grid capacity.")
    
    # Configuration Box
    with st.container():
        st.subheader("1. Base Scenario & Grid Modifiers")
        col_scenario, col_date = st.columns(2)
        
        with col_scenario:
            scenario = st.selectbox("Select Weather Preset", ["Custom Mode", "Summer Heatwave 🌡️", "Winter Freeze ❄️", "Mild Spring 🌸"])
            
        with col_date:
            start_date = st.date_input("Start Date for Forecast", value=max_date + timedelta(days=1))
            
        st.markdown("**What-If Grid Modifiers**")
        col_ev, col_solar = st.columns(2)
        
        with col_ev:
            add_ev = st.toggle("🔌 High EV Charging (Adds 120 kWh load artificially from 5PM-10PM)")
        with col_solar:
            add_solar = st.toggle("☀️ Regional Solar Generation (Deducts 150 kWh midday due to solar)")

    st.subheader("2. Hourly Editable Weather Data")
    st.markdown("Fine-tune the hour-by-hour temperature and humidity below. **These cells are fully editable.**")

    # Set default values based on scenario
    if scenario == "Summer Heatwave 🌡️":
        def_temp, def_hum, amp = 38.0, 40.0, 8
    elif scenario == "Winter Freeze ❄️":
        def_temp, def_hum, amp = -5.0, 60.0, 6
    elif scenario == "Mild Spring 🌸":
        def_temp, def_hum, amp = 20.0, 50.0, 4
    else:
        def_temp, def_hum, amp = 25.0, 50.0, 5
        
    # Generate 24 hours
    forecast_dates = [datetime.combine(start_date, datetime.min.time()) + timedelta(hours=i) for i in range(24)]
    hours_arr = np.array([d.hour for d in forecast_dates])
    
    # Initialize default arrays
    temp_variation = -amp * np.cos(2 * np.pi * (hours_arr - 4) / 24)
    base_temp = def_temp + temp_variation
    hum_variation = 10 * np.cos(2 * np.pi * hours_arr / 24)
    base_hum = np.clip(def_hum + hum_variation, 20, 100)
    
    weather_df = pd.DataFrame({
        'Hour': [f"{h:02d}:00" for h in hours_arr],
        'Temperature_C': base_temp,
        'Humidity_percent': base_hum
    })
    
    # Make editor interactive
    edited_weather = st.data_editor(
        weather_df,
        use_container_width=True,
        hide_index=True,
        num_rows="fixed",
        column_config={
            "Hour": st.column_config.Column("Time", disabled=True),
            "Temperature_C": st.column_config.NumberColumn("Temperature (°C)", format="%.1f", step=1.0),
            "Humidity_percent": st.column_config.NumberColumn("Humidity (%)", format="%.1f", step=1.0),
        }
    )

    if st.button("🚀 Calculate Grid Stress", type="primary", use_container_width=True):
        with st.spinner("Processing AI model and grid modifiers..."):
            
            # Reconstruct prediction dataframe
            forecast_df = pd.DataFrame({
                'Datetime': forecast_dates,
                'Hour': hours_arr,
                'DayOfWeek': [d.weekday() for d in forecast_dates],
                'DayOfYear': [d.timetuple().tm_yday for d in forecast_dates],
                'IsWeekend': [1 if d.weekday() >= 5 else 0 for d in forecast_dates],
                'Temperature_C': edited_weather['Temperature_C'],
                'Humidity_percent': edited_weather['Humidity_percent']
            })
            
            # Run Base AI prediction
            features = ['Hour', 'DayOfWeek', 'DayOfYear', 'IsWeekend', 'Temperature_C', 'Humidity_percent']
            base_predictions = model.predict(forecast_df[features])
            
            # Apply Modifiers
            if add_ev:
                ev_load = np.where((forecast_df['Hour'] >= 17) & (forecast_df['Hour'] <= 22), 120, 0)
                base_predictions += ev_load
                
            if add_solar:
                # Solar duck curve: massive dip in grid reliance mid-day
                solar_gen = np.where((forecast_df['Hour'] >= 10) & (forecast_df['Hour'] <= 15), -150, 0)
                solar_gen = np.where((forecast_df['Hour'] == 9) | (forecast_df['Hour'] == 16), -50, solar_gen)
                solar_gen = np.where((forecast_df['Hour'] == 8) | (forecast_df['Hour'] == 17), -20, solar_gen)
                base_predictions += solar_gen
                
            forecast_df['Predicted_Consumption_kWh'] = base_predictions
            
            # Determine grid overload limit (10% above historical max for test stability)
            MAX_CAPACITY = df['Energy_Consumption_kWh'].max() * 1.10
            num_overloads = (forecast_df['Predicted_Consumption_kWh'] > MAX_CAPACITY).sum()
            
            # Alert Mechanism
            if num_overloads > 0:
                st.error(f"🚨 **WARNING**: GRID OVERLOAD! System capacity exceeded ({MAX_CAPACITY:.1f} kWh) for {num_overloads} hours!")
            else:
                st.success("✅ Grid remains stable and running smoothly within constraints.")
            
            # Dual Axis Chart 
            fig_dual = go.Figure()
            
            fig_dual.add_trace(go.Scatter(
                x=forecast_df['Datetime'], y=forecast_df['Predicted_Consumption_kWh'],
                name='Simulated Energy Demand (kWh)', mode='lines+markers', line=dict(color='#ff7f0e', width=3)
            ))
            
            # Add capacity line
            fig_dual.add_trace(go.Scatter(
                x=[forecast_df['Datetime'].min(), forecast_df['Datetime'].max()], 
                y=[MAX_CAPACITY, MAX_CAPACITY],
                name='Grid Max Capacity Limit', mode='lines', line=dict(color='red', width=2, dash='dash')
            ))
            
            fig_dual.add_trace(go.Scatter(
                x=forecast_df['Datetime'], y=forecast_df['Temperature_C'],
                name='Temperature (°C)', mode='lines', line=dict(color='#1f77b4', width=2, dash='dot'),
                yaxis='y2'
            ))
            
            fig_dual.update_layout(
                title=f"Predicted Grid Simulation Results",
                yaxis=dict(title=dict(text='Energy Consumption (kWh)', font=dict(color='#ff7f0e')), tickfont=dict(color='#ff7f0e')),
                yaxis2=dict(title=dict(text='Temperature (°C)', font=dict(color='#1f77b4')), tickfont=dict(color='#1f77b4'), anchor='x', overlaying='y', side='right'),
                hovermode='x unified',
                template="plotly_dark" if st.get_option("theme.base") == "dark" else "plotly_white",
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            
            st.plotly_chart(fig_dual, use_container_width=True)
            
            # Provide CSV download
            csv_data = forecast_df[['Datetime', 'Predicted_Consumption_kWh', 'Temperature_C', 'Humidity_percent']].to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download Forecast Report (CSV)",
                data=csv_data,
                file_name=f"grid_forecast_simulation_{start_date}.csv",
                mime='text/csv'
            )

with tab3:
    st.header("Model Diagnostic Insights")
    st.markdown("Understand what features drive our Random Forest algorithm's forecasts.")
    
    col_diag1, col_diag2 = st.columns([2, 1])
    
    with col_diag1:
        st.subheader("Feature Importance")
        # Extract features from model if available
        if hasattr(model, 'feature_importances_'):
            features = ['Hour', 'DayOfWeek', 'DayOfYear', 'IsWeekend', 'Temperature_C', 'Humidity_percent']
            importances = model.feature_importances_
            feat_df = pd.DataFrame({'Feature': features, 'Importance': importances})
            feat_df = feat_df.sort_values(by='Importance', ascending=True)
            
            fig_feat = px.bar(feat_df, x='Importance', y='Feature', orientation='h', 
                              title="Relative Importance of Input Variables",
                              color='Importance', color_continuous_scale='Blues')
            fig_feat.update_layout(showlegend=False)
            st.plotly_chart(fig_feat, use_container_width=True)
        else:
            st.info("Feature importance not available for this model type.")
            
    with col_diag2:
        st.subheader("Model Meta-Data")
        st.info("**Algorithm:** Random Forest Regressor")
        if hasattr(model, 'n_estimators'):
            st.write(f"**Decision Trees:** {model.n_estimators}")
        if hasattr(model, 'max_depth'):
            st.write(f"**Max Depth:** {model.max_depth}")
            
        st.success("The algorithm heavily weights **Temperature** (for heating and cooling requirements) and **Hour of Day** (driven by daily behavioral peaks), leading to highly accurate hourly load profiles.")
