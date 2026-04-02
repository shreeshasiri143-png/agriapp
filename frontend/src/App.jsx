import { useState, useEffect } from 'react'
import './App.css'

function App() {
  const [metrics, setMetrics] = useState(null)
  const [formData, setFormData] = useState({
    N: 50,
    P: 50,
    K: 50,
    temperature: 25.0,
    humidity: 50.0,
    ph: 6.5
  })
  const [prediction, setPrediction] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  
  const INTS = ['N', 'P', 'K'];

  const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || (import.meta.env.PROD ? '/api' : 'http://127.0.0.1:8000');

  useEffect(() => {
    fetch(`${API_BASE_URL}/model-metrics`)
      .then(res => res.json())
      .then(data => setMetrics(data))
      .catch(err => console.error("Could not fetch metrics. Is backend running?", err))
  }, [])

  const handleSliderChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: parseFloat(value)
    }))
  }

  const handlePredict = async () => {
    setLoading(true)
    setError(null)
    setPrediction(null)
    try {
      const response = await fetch(`${API_BASE_URL}/predict`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      });
      if (!response.ok) {
        throw new Error("Prediction failed: " + response.statusText);
      }
      const data = await response.json();
      setPrediction(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="container">
      <header className="app-header">
        <h1>🌾 Smart Fertilizer Recommendation system</h1>
        <p>AI-driven insights for experiential learning and optimal yield</p>
      </header>

      <div className="main-content">
        <aside className="sliders-panel card">
          <h2>Soil Parameters</h2>
          <p className="subtitle">Move sliders to see how environmental metrics impact recommendations (NEP 2020: Experiential Learning)</p>
          
          <div className="sliders-grid">
            {Object.keys(formData).map((key) => {
              let max = 100;
              let step = 1;
              if (key === 'temperature') { max = 50; step = 0.5; }
              else if (key === 'ph') { max = 10; step = 0.1; }
              else if (key === 'humidity') { max = 100; step = 0.5; }
              else if (key === 'N') { max = 140; }
              else if (key === 'P') { max = 145; }
              else if (key === 'K') { max = 205; }
              
              const isInt = INTS.includes(key);

              return (
                <div key={key} className="slider-group">
                  <div className="slider-label">
                    <span className="key-name">{key.toUpperCase()}</span>
                    <span className="key-value">{isInt ? Math.round(formData[key]) : formData[key].toFixed(1)}</span>
                  </div>
                  <input
                    type="range"
                    name={key}
                    min="0"
                    max={max}
                    step={step}
                    value={formData[key]}
                    onChange={handleSliderChange}
                    className="styled-slider"
                  />
                </div>
              )
            })}
          </div>

          <button onClick={handlePredict} disabled={loading} className="predict-btn">
            {loading ? 'Analyzing Soil...' : 'Get Recommendation'}
          </button>
        </aside>

        <main className="results-panel">
          {error && <div className="error-box">{error}</div>}
          
          {prediction ? (
            <div className="recommendation-card card slide-in">
              <div className="rec-header">
                <h2>Recommended Fertilizer</h2>
                <div className="confidence-badge">
                  {(prediction.confidence_score * 100).toFixed(1)}% Confidence
                </div>
              </div>
              
              <div className="rec-main">
                <div className="fert-name">{prediction.recommendation}</div>
                <div className="fert-qty">{prediction.quantity_kg_per_hectare} kg / hectare</div>
              </div>
              
              <div className="explanation-section">
                <h3>Why this recommendation?</h3>
                <p>{prediction.explanation}</p>
              </div>
              
            </div>
          ) : (
             <div className="placeholder-card card">
               <span className="icon">🌱</span>
               <p>Adjust the sliders and click 'Get Recommendation' to see AI predictions.</p>
             </div>
          )}

          {metrics && (
            <div className="metrics-card card">
               <h3>Model Effectiveness & Metrics</h3>
               <p className="subtitle">Comparing Base vs Tuned Models (NEP 2020: Critical Thinking)</p>
               <div className="metrics-grid">
                 {Object.entries(metrics.metrics).map(([modelName, data]) => (
                   <div key={modelName} className={`metric-box ${metrics.best_model === modelName ? 'best-model' : ''}`}>
                      <h4>{modelName}</h4>
                      <p>Untuned Acc: {(data.untuned.accuracy * 100).toFixed(1)}%</p>
                      <p>Tuned Acc: {(data.tuned.accuracy * 100).toFixed(1)}%</p>
                   </div>
                 ))}
               </div>
            </div>
          )}
        </main>
      </div>
    </div>
  )
}

export default App
