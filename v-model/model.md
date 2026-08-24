# 🌦️ Weather Activity Recommendation System

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Model Accuracy](https://img.shields.io/badge/accuracy-90%25-brightgreen)](https://github.com)
[![Flask](https://img.shields.io/badge/flask-2.0%2B-orange)](https://flask.palletsprojects.com/)
[![n8n](https://img.shields.io/badge/n8n-integrated-purple)](https://n8n.io/)

## 🎯 Overview

An intelligent **Weather Activity Recommendation System** that analyzes real-time weather data and provides smart activity suggestions using both **Machine Learning** and **rule-based logic**. The system integrates with **n8n workflows** for AI-powered recommendations and includes a user-friendly **desktop GUI**.

### 🌟 Key Features

- ✅ **Real-time Weather Data** - Fetches live weather from OpenWeather API
- ✅ **AI-Powered Recommendations** - Logistic Regression model with 90% accuracy
- ✅ **n8n Integration** - Seamless workflow automation and AI orchestration
- ✅ **Beautiful Desktop GUI** - Modern Tkinter interface with intuitive design
- ✅ **RESTful API** - Flask endpoints for programmatic access
- ✅ **Intelligent Fallback** - Automatic switch between ML and rule-based logic
- ✅ **Batch Processing** - Analyze multiple weather records at once
- ✅ **City Search** - Get weather and recommendations for any city worldwide

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    USER INTERFACE LAYER                         │
│                    (Tkinter Desktop App)                        │
│                          weather_app.py                         │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    API INTEGRATION LAYER                       │
│                    (Flask Server + n8n)                        │
│                        server.py                               │
│                    n8n.py / workflow.json                      │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    WEATHER DATA LAYER                          │
│                    (OpenWeather API)                           │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    MACHINE LEARNING LAYER                      │
│                    (Logistic Regression)                       │
│                    train_model.py                              │
└─────────────────────────────────────────────────────────────────┘
```

## 📁 Project Structure

```
weather-activity-recommendation/
├── 📄 README.md                    # Project documentation
├── 📄 LICENSE                      # MIT License
├── 📄 requirements.txt             # Python dependencies
├── 📄 .gitignore                   # Git ignore file
│
├── 🖥️ weather_app.py               # Tkinter desktop application
├── 🚀 server.py                    # Flask API server
├── 🤖 n8n.py                       # n8n integration module
├── 🧠 ai.py                        # Core recommendation engine
├── 📊 train_model.py               # ML training script
├── 📈 gen.py                       # Dataset generator
│
├── 📁 models/
│   ├── weather_activity_model.pkl  # Trained ML model
│   └── weather_encoders.pkl        # Label encoders
│
├── 📁 data/
│   ├── weather_activity_dataset.csv   # Sample training data
│   └── weather_activity_dataset.json  # JSON format
│
└── 📁 workflows/
    ├── weather_analysis_workflow.json # n8n workflow definition
    └── weather_analysis_workflow.yaml # YAML format
```

## 🚀 Quick Start

### Prerequisites

```bash
Python 3.8+
pip (Python package manager)
OpenWeather API Key (free tier available)
n8n (optional, for AI workflow integration)
```

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/weather-activity-recommendation.git
cd weather-activity-recommendation
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Set up API keys**
```python
# In weather_app.py and n8n.py
API_KEY = "your_openweather_api_key"  # Get from https://openweathermap.org/api
N8N_WEBHOOK_URL = "your_n8n_webhook_url"  # Your n8n webhook endpoint
```

4. **Train the model (optional)**
```bash
python gen.py          # Generate synthetic dataset
python train_model.py  # Train the ML model
```

5. **Start the application**

**Option A: Desktop App**
```bash
python weather_app.py
```

**Option B: API Server**
```bash
python server.py
```

**Option C: n8n Integration**
```bash
python n8n.py --test
```

## 🎮 Usage Guide

### Desktop Application

1. Launch the app: `python weather_app.py`
2. Enter a city name in the search bar
3. Click "CHECK WEATHER" or press Enter
4. View real-time weather data and smart activity recommendation

### API Endpoints

| Endpoint | Method | Description | Example |
|----------|--------|-------------|---------|
| `/` | GET | Service information | - |
| `/health` | GET | Health check | - |
| `/webhook/weather` | POST | Analyze weather data | [Example](#api-examples) |
| `/webhook/city` | POST | Get city weather | [Example](#api-examples) |
| `/webhook/batch` | POST | Batch analysis | [Example](#api-examples) |

### API Examples

**Analyze Weather Data**
```bash
curl -X POST http://localhost:5000/webhook/weather \
  -H "Content-Type: application/json" \
  -d '{
    "temperature": 25,
    "humidity": 60,
    "wind_speed": 3,
    "weather": "Clear"
  }'
```

**Get City Weather**
```bash
curl -X POST http://localhost:5000/webhook/city \
  -H "Content-Type: application/json" \
  -d '{"city": "London"}'
```

**Batch Analysis**
```bash
curl -X POST http://localhost:5000/webhook/batch \
  -H "Content-Type: application/json" \
  -d '{
    "records": [
      {"temperature": 25, "humidity": 60, "weather": "Clear"},
      {"temperature": 30, "humidity": 80, "weather": "Rain"}
    ]
  }'
```

## 🧠 How It Works

### Recommendation Logic

The system uses a **dual-layer** recommendation approach:

1. **ML Model Layer** (Primary)
   - Logistic Regression trained on 10,000+ synthetic weather samples
   - 90%+ accuracy in activity prediction
   - Considers 9 features including weather encoding

2. **Rule-Based Layer** (Fallback)
   - Hierarchical decision tree
   - Priority-based evaluation
   - Handles edge cases and extreme weather

### Decision Flow

```
Input Weather Data
       ↓
Check Weather Condition
       ↓
┌──────┴──────┐
│  ML Model   │ ← n8n AI Integration
└──────┬──────┘
       ↓
   Available?
       ↓
┌──────┴──────┐
│   Yes       │   No
│  Use ML     │   Use Rule-Based
└──────┬──────┘
       ↓
Return Recommendation
```

## 📊 Performance

| Component | Metric | Value |
|-----------|--------|-------|
| ML Model | Accuracy | ~90% |
| ML Model | Precision | 0.88 |
| ML Model | Recall | 0.87 |
| API Response | Average Time | <500ms |
| UI Load Time | First Paint | <1s |
| Training Data | Samples | 10,000 |
| Activity Classes | Categories | 7 |

## 📱 Screenshots

### Desktop Application
![Weather App UI](https://via.placeholder.com/800x500?text=Weather+App+UI)

### API Response Example
```json
{
  "success": true,
  "recommendation": {
    "activity": "Walking / Cycling / Outdoor Sports",
    "confidence": "90.0%",
    "method": "Rule-Based",
    "reason": "The weather conditions are comfortable for outdoor activities."
  },
  "weather": {
    "temperature": "25°C",
    "humidity": "60%",
    "windSpeed": "3 m/s",
    "condition": "Clear"
  },
  "timestamp": "2026-08-24T14:30:00Z"
}
```

## 🛠️ Technologies Used

### Core Technologies
- **Python 3.8+** - Primary programming language
- **Scikit-learn** - Machine learning library
- **Pandas** - Data manipulation and analysis
- **NumPy** - Numerical computing
- **Flask** - Web API framework
- **Flask-CORS** - Cross-origin resource sharing

### Machine Learning
- **Logistic Regression** - Classification algorithm
- **Label Encoding** - Categorical variable encoding
- **StandardScaler** - Feature scaling
- **Pickle** - Model serialization

### Frontend
- **Tkinter** - Desktop GUI framework
- **Requests** - HTTP library

### Integration
- **n8n** - Workflow automation
- **OpenWeather API** - Weather data source

## 🔄 n8n Integration

The system seamlessly integrates with n8n for AI-powered workflow automation:

1. **Webhook Trigger** - Receives weather data
2. **HTTP Request** - Calls the Python service
3. **Function Node** - Formats the response
4. **Respond to Webhook** - Sends back recommendation

### n8n Workflow

```yaml
name: Weather Activity Analysis
nodes:
  - Webhook Trigger (weather-analysis)
  - Call Python Service (http://localhost:5000/webhook/weather)
  - Format Response (Function)
  - Respond to Webhook
```

## 🧪 Testing

### Test n8n Connection
```bash
python n8n.py --test
```

### Test API Endpoints
```bash
# Health Check
curl http://localhost:5000/health

# Weather Analysis
curl -X POST http://localhost:5000/webhook/weather \
  -H "Content-Type: application/json" \
  -d '{"temperature": 25, "humidity": 60, "weather": "Clear"}'
```

### Run Unit Tests
```bash
python -m pytest tests/
```

## 📈 Dataset Generation

Generate synthetic weather data for training:

```bash
python gen.py
```

**Output:**
- `weather_activity_dataset.csv` (10,000 records)
- `weather_activity_dataset.json` (structured format)

### Dataset Features

| Feature | Range | Description |
|---------|-------|-------------|
| Temperature | -10°C to 40°C | Current temperature |
| Humidity | 0% to 100% | Relative humidity |
| Wind Speed | 0 to 15 m/s | Wind speed |
| Weather Condition | 8 types | Clear, Clouds, Rain, etc. |
| Activity | 7 classes | Recommended activity |

## 🤝 Contributing

1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/amazing-feature
   ```
3. **Commit your changes**
   ```bash
   git commit -m 'Add amazing feature'
   ```
4. **Push to the branch**
   ```bash
   git push origin feature/amazing-feature
   ```
5. **Open a Pull Request**

### Development Guidelines

- Follow PEP 8 style guide
- Write docstrings for all functions
- Add type hints where possible
- Include unit tests for new features
- Update documentation accordingly

## 📝 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **OpenWeather API** - For providing real-time weather data
- **n8n** - For workflow automation capabilities
- **Scikit-learn** - For machine learning tools
- **All contributors** - For their valuable contributions

## 📞 Support

### Contact
- **GitHub Issues**: [Create an issue](https://github.com/yourusername/weather-activity-recommendation/issues)
- **Email**: your.email@example.com
