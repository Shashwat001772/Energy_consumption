import React, { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, AreaChart, Area, BarChart, Bar } from 'recharts';
import { Activity, Upload, Zap, AlertTriangle, CheckCircle, BarChart3, Database, Home, TrendingUp, Lightbulb } from 'lucide-react';
import { requestRealtimePrediction, requestBatchPrediction, fetchHistoricalAnalytics, fetchFutureForecast } from './api';
import './index.css';

function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  
  // Data State
  const [historicalData, setHistoricalData] = useState(null);
  const [forecastData, setForecastData] = useState(null);

  // Realtime Simulator State
  const [simDate, setSimDate] = useState('2024-06-15');
  const [simTemp, setSimTemp] = useState(35);
  const [simHum, setSimHum] = useState(65);
  const [simResult, setSimResult] = useState(null);

  // Load Initial Data
  useEffect(() => {
    const loadData = async () => {
      setLoading(true);
      try {
        const [hist, forecast] = await Promise.all([
          fetchHistoricalAnalytics(),
          fetchFutureForecast()
        ]);
        setHistoricalData(hist);
        setForecastData(forecast);
      } catch (err) {
        setError('Failed to load dashboard data. Is the backend running?');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    loadData();
  }, []);

  // ---- Handlers ----
  const handleSimulate = async () => {
    setLoading(true);
    setError('');
    try {
      const dateObj = new Date(simDate);
      const payload = [];
      const adjustedDay = (dateObj.getDay() + 6) % 7;
      const dayOfYear = Math.floor((dateObj - new Date(dateObj.getFullYear(), 0, 0)) / 1000 / 60 / 60 / 24);
      const isWeekend = adjustedDay >= 5 ? 1 : 0;
      
      for(let i=0; i<24; i++) {
        const tempVar = simTemp - (5 * Math.cos((2 * Math.PI * (i - 4)) / 24));
        const humVar = Math.min(100, Math.max(20, simHum + (10 * Math.cos((2 * Math.PI * i) / 24))));
        
        payload.push({
          Hour: i,
          DayOfWeek: adjustedDay,
          DayOfYear: dayOfYear,
          IsWeekend: isWeekend,
          Temperature_C: parseFloat(tempVar.toFixed(1)),
          Humidity_percent: parseFloat(humVar.toFixed(1))
        });
      }

      const data = await requestRealtimePrediction(payload);
      setSimResult({
        predictions: data.predictions,
        weather: payload
      });
    } catch (err) {
      setError('Failed to simulate: ' + (err.response?.data?.detail || err.message));
    } finally {
      setLoading(false);
    }
  };

  // ---- Render Tabs ----
  const renderDashboard = () => {
    if (!forecastData) return <div className="animate-fade-in"><p>Loading forecast...</p></div>;
    
    // Format forecast data for chart
    const chartData = forecastData.hourly_forecast.slice(0, 24).map(d => ({
      hour: new Date(d.Datetime).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      consumption: Math.round(d.Predicted_Consumption_kWh),
      temp: Math.round(d.Temperature_C)
    }));

    return (
      <div className="animate-fade-in delay-100">
        <h2 className="flex-row"><Home size={24} /> General Overview</h2>
        
        <div className="grid-3" style={{ marginTop: '24px' }}>
          <div className="metric-card">
            <span className="metric-label">Next Hour Forecast</span>
            <span className="metric-value">{forecastData.next_hour} kWh</span>
          </div>
          <div className="metric-card">
            <span className="metric-label">Tomorrow Forecast</span>
            <span className="metric-value">{forecastData.next_day} kWh</span>
          </div>
          <div className="metric-card">
            <span className="metric-label">Next 7 Days</span>
            <span className="metric-value">{forecastData.next_week} kWh</span>
          </div>
        </div>

        <div className="glass-panel" style={{ marginTop: '32px' }}>
          <h3>Next 24 Hours Load Profile</h3>
          <div style={{ height: '350px', marginTop: '16px' }}>
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={chartData}>
                <defs>
                  <linearGradient id="colorCons" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="var(--primary)" stopOpacity={0.8}/>
                    <stop offset="95%" stopColor="var(--primary)" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                <XAxis dataKey="hour" stroke="#94a3b8" />
                <YAxis yAxisId="left" stroke="#94a3b8" />
                <YAxis yAxisId="right" orientation="right" stroke="#ef4444" domain={[0, 50]} />
                <Tooltip contentStyle={{ backgroundColor: 'rgba(15,23,42,0.9)', border: 'none', borderRadius: '8px' }} />
                <Legend />
                <Area yAxisId="left" type="monotone" dataKey="consumption" stroke="var(--primary)" fillOpacity={1} fill="url(#colorCons)" name="Load (kWh)" />
                <Line yAxisId="right" type="monotone" dataKey="temp" stroke="#ef4444" strokeDasharray="5 5" name="Temp (°C)" dot={false} />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    );
  };

  const renderHistorical = () => {
    if (!historicalData) return <div className="animate-fade-in"><p>Loading historical data...</p></div>;

    return (
      <div className="animate-fade-in delay-100">
        <h2 className="flex-row"><TrendingUp size={24} /> Historical Patterns & Trends</h2>
        
        <div className="grid-2" style={{ marginTop: '24px' }}>
          <div className="glass-panel">
            <h3>Summer vs Winter (Monthly Average)</h3>
            <div style={{ height: '250px', marginTop: '16px' }}>
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={historicalData.monthly}>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                  <XAxis dataKey="Month_Name" stroke="#94a3b8" tick={{fontSize: 12}} />
                  <YAxis stroke="#94a3b8" />
                  <Tooltip contentStyle={{ backgroundColor: 'rgba(15,23,42,0.9)', border: 'none', borderRadius: '8px' }} />
                  <Bar dataKey="Energy_Consumption_kWh" fill="var(--secondary)" name="Avg Load (kWh)" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="glass-panel">
            <h3>Night vs Day (Hourly Average)</h3>
            <div style={{ height: '250px', marginTop: '16px' }}>
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={historicalData.hourly}>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                  <XAxis dataKey="Hour" stroke="#94a3b8" />
                  <YAxis stroke="#94a3b8" />
                  <Tooltip contentStyle={{ backgroundColor: 'rgba(15,23,42,0.9)', border: 'none', borderRadius: '8px' }} />
                  <Line type="monotone" dataKey="Energy_Consumption_kWh" stroke="var(--success)" strokeWidth={3} dot={false} name="Avg Load (kWh)" />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>

        <div className="glass-panel" style={{ marginTop: '24px' }}>
          <h3>Weekday vs Weekend Average</h3>
          <div style={{ display: 'flex', gap: '24px', marginTop: '16px' }}>
            {historicalData.weekend_vs_weekday.map((item, idx) => (
              <div key={idx} className="metric-card" style={{ flex: 1 }}>
                <span className="metric-label">{item.Type} Average</span>
                <span className="metric-value">{Math.round(item.Energy_Consumption_kWh)} kWh</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  };

  const renderSimulator = () => {
    const chartData = simResult ? simResult.predictions.map((p, idx) => ({
      hour: `${p.Hour}:00`,
      consumption: p.Predicted_Consumption_kWh,
      temperature: simResult.weather[idx].Temperature_C
    })) : [];

    const maxLimit = 1500;
    const overloads = chartData.filter(d => d.consumption > maxLimit).length;

    return (
      <div className="animate-fade-in delay-100">
        <div className="grid-2">
          <div className="glass-panel">
            <h2 className="flex-row gradient-text"><Zap size={24} /> Grid Sandbox</h2>
            <p>Simulate grid stress by manipulating extreme weather conditions.</p>
            
            <div style={{ marginTop: '24px' }}>
              <label>Target Date</label>
              <input type="date" className="input-field" value={simDate} onChange={(e) => setSimDate(e.target.value)} />
            </div>

            <div style={{ marginTop: '16px' }}>
              <label>Base Temperature (°C): {simTemp}</label>
              <input type="range" min="-20" max="50" value={simTemp} onChange={(e) => setSimTemp(parseInt(e.target.value))} style={{ width: '100%' }} />
            </div>

            <div style={{ marginTop: '16px' }}>
              <label>Base Humidity (%): {simHum}</label>
              <input type="range" min="10" max="100" value={simHum} onChange={(e) => setSimHum(parseInt(e.target.value))} style={{ width: '100%' }} />
            </div>

            <button className="btn" style={{ marginTop: '24px', width: '100%' }} onClick={handleSimulate} disabled={loading}>
              {loading ? 'Simulating AI...' : 'Run Simulation'}
            </button>
          </div>

          {simResult && (
            <div className="glass-panel">
              <h2 className="flex-row">Simulation Report</h2>
              {overloads > 0 ? (
                <div className="badge danger flex-row" style={{ marginTop: '16px', padding: '12px', fontSize: '1rem' }}>
                  <AlertTriangle /> WARNING: Grid Overload ({overloads} hours over limit)
                </div>
              ) : (
                <div className="badge success flex-row" style={{ marginTop: '16px', padding: '12px', fontSize: '1rem' }}>
                  <CheckCircle /> SYSTEM STABLE: No overloads detected
                </div>
              )}

              <div className="grid-2" style={{ marginTop: '24px' }}>
                <div style={{ background: 'rgba(0,0,0,0.2)', padding: '16px', borderRadius: '8px' }}>
                  <label>Max Peak Load</label>
                  <h1 style={{ fontSize: '2rem', margin: 0, color: 'var(--primary)' }}>
                    {Math.max(...chartData.map(d => d.consumption)).toFixed(0)} <span style={{fontSize: '1rem'}}>kWh</span>
                  </h1>
                </div>
                <div style={{ background: 'rgba(0,0,0,0.2)', padding: '16px', borderRadius: '8px' }}>
                  <label>Grid Limit</label>
                  <h1 style={{ fontSize: '2rem', margin: 0, color: '#ef4444' }}>
                    {maxLimit} <span style={{fontSize: '1rem'}}>kWh</span>
                  </h1>
                </div>
              </div>
            </div>
          )}
        </div>

        {simResult && (
          <div className="glass-panel" style={{ marginTop: '24px' }}>
            <h2 className="flex-row"><Activity size={24} /> 24-Hour Forecast Profile</h2>
            <div style={{ height: '400px', marginTop: '24px' }}>
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={chartData} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
                  <defs>
                    <linearGradient id="colorConsumption" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="var(--primary)" stopOpacity={0.8}/>
                      <stop offset="95%" stopColor="var(--primary)" stopOpacity={0}/>
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                  <XAxis dataKey="hour" stroke="#94a3b8" />
                  <YAxis yAxisId="left" stroke="#94a3b8" />
                  <YAxis yAxisId="right" orientation="right" stroke="#ef4444" domain={[0, 60]} />
                  <Tooltip contentStyle={{ backgroundColor: 'rgba(15,23,42,0.9)', border: 'none', borderRadius: '8px' }} />
                  <Legend />
                  <Area yAxisId="left" type="monotone" dataKey="consumption" stroke="var(--primary)" fillOpacity={1} fill="url(#colorConsumption)" name="Load (kWh)" />
                  <Line yAxisId="right" type="monotone" dataKey="temperature" stroke="#ef4444" strokeDasharray="5 5" name="Temp (°C)" dot={false} />
                  <Line yAxisId="left" type="step" dataKey={() => maxLimit} stroke="#ef4444" strokeWidth={2} name="Grid Limit" dot={false} />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </div>
        )}
      </div>
    );
  };

  const renderSavings = () => {
    if (!forecastData) return null;

    // Find peak hour in next 24 hours
    const next24 = forecastData.hourly_forecast.slice(0, 24);
    let peak = next24[0];
    let min = next24[0];
    
    next24.forEach(d => {
      if (d.Predicted_Consumption_kWh > peak.Predicted_Consumption_kWh) peak = d;
      if (d.Predicted_Consumption_kWh < min.Predicted_Consumption_kWh) min = d;
    });

    const peakTime = new Date(peak.Datetime).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    const minTime = new Date(min.Datetime).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

    return (
      <div className="animate-fade-in delay-100">
        <h2 className="flex-row"><Lightbulb size={24} color="var(--primary)" /> Energy Savings & Insights</h2>
        
        <div className="grid-2" style={{ marginTop: '24px' }}>
          <div className="glass-panel" style={{ borderLeft: '4px solid #ef4444' }}>
            <h3><AlertTriangle size={18} style={{ display: 'inline', marginRight: '8px' }}/> Peak Usage Detected</h3>
            <p style={{ marginTop: '12px' }}>
              Your energy consumption is forecasted to peak at <strong>{Math.round(peak.Predicted_Consumption_kWh)} kWh</strong> around <strong>{peakTime}</strong> today.
            </p>
            <div className="badge danger" style={{ marginTop: '8px' }}>Action Required</div>
            <p style={{ fontSize: '0.9rem', marginTop: '12px', color: 'var(--text-main)' }}>
              <strong>Tip:</strong> Delay running heavy appliances like Washing Machines, Dishwashers, or EV charging until after this peak to avoid high demand charges and reduce grid stress.
            </p>
          </div>

          <div className="glass-panel" style={{ borderLeft: '4px solid #10b981' }}>
            <h3><CheckCircle size={18} style={{ display: 'inline', marginRight: '8px' }}/> Optimal Usage Window</h3>
            <p style={{ marginTop: '12px' }}>
              The grid is forecasted to be under lowest stress at <strong>{minTime}</strong> with a load of <strong>{Math.round(min.Predicted_Consumption_kWh)} kWh</strong>.
            </p>
            <div className="badge success" style={{ marginTop: '8px' }}>Best Time to Use</div>
            <p style={{ fontSize: '0.9rem', marginTop: '12px', color: 'var(--text-main)' }}>
              <strong>Tip:</strong> Schedule your smart thermostats, EV charging, and heavy appliances during this time window to maximize energy efficiency and reduce your bill.
            </p>
          </div>
        </div>

        <div className="glass-panel" style={{ marginTop: '24px' }}>
           <h3>Detecting Wastage (Vampire Draw)</h3>
           <p>
            Based on historical data analysis, your baseline night usage averages around <strong>{historicalData ? Math.round(historicalData.hourly.find(h => h.Hour === 3)?.Energy_Consumption_kWh) : '...'} kWh</strong>.
           </p>
           <p style={{ fontSize: '0.9rem', color: 'var(--text-main)' }}>
            <strong>Recommendation:</strong> Ensure desktop computers, TVs, and entertainment systems are fully powered down or on smart strips. This simple change can reduce your bill by up to 10% annually.
           </p>
        </div>
      </div>
    );
  };

  return (
    <div className="app-container">
      <header style={{ marginBottom: '40px', textAlign: 'center' }}>
        <h1 className="gradient-text animate-fade-in">Energy Forecaster Pro</h1>
        <p className="animate-fade-in delay-100">AI-Powered Grid Analytics & Forecasting</p>
      </header>

      {error && <div className="badge danger" style={{ marginBottom: '24px', display: 'block', textAlign: 'center', padding: '12px' }}>{error}</div>}

      <div className="tabs animate-fade-in delay-200">
        <button className={`tab ${activeTab === 'dashboard' ? 'active' : ''}`} onClick={() => setActiveTab('dashboard')}>
          <Home size={18} style={{ display: 'inline', verticalAlign: 'text-bottom', marginRight: '8px' }} />
          Dashboard
        </button>
        <button className={`tab ${activeTab === 'historical' ? 'active' : ''}`} onClick={() => setActiveTab('historical')}>
          <TrendingUp size={18} style={{ display: 'inline', verticalAlign: 'text-bottom', marginRight: '8px' }} />
          Historical Patterns
        </button>
        <button className={`tab ${activeTab === 'simulator' ? 'active' : ''}`} onClick={() => setActiveTab('simulator')}>
          <Zap size={18} style={{ display: 'inline', verticalAlign: 'text-bottom', marginRight: '8px' }} />
          Grid Simulator
        </button>
        <button className={`tab ${activeTab === 'savings' ? 'active' : ''}`} onClick={() => setActiveTab('savings')}>
          <Lightbulb size={18} style={{ display: 'inline', verticalAlign: 'text-bottom', marginRight: '8px' }} />
          Energy Savings
        </button>
      </div>

      <main>
        {activeTab === 'dashboard' && renderDashboard()}
        {activeTab === 'historical' && renderHistorical()}
        {activeTab === 'simulator' && renderSimulator()}
        {activeTab === 'savings' && renderSavings()}
      </main>
    </div>
  );
}

export default App;
