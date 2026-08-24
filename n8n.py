import pandas as pd
import numpy as np
import pickle
import json
import os
from datetime import datetime
from typing import Dict, Any, Optional, Tuple
import requests
import warnings
warnings.filterwarnings('ignore')

API_KEY = "8f93b69527326e29e8f2ffd28bb6d0d1"

N8N_WEBHOOK_URL = "https://vermag.app.n8n.cloud/webhook/a59ea635-d7c4-4447-a334-95770249d05f"

MODEL_PATH = "weather_activity_model.pkl"
ENCODER_PATH = "weather_encoders.pkl"

class ModelLoader:
    """Load and manage the trained Logistic Regression model."""
    
    def __init__(self, model_path: str = MODEL_PATH, encoder_path: str = ENCODER_PATH):
        self.model = None
        self.weather_encoder = None
        self.activity_encoder = None
        self.features = None
        self.classes = None
        self.accuracy = None
        self.model_name = None
        self.use_ml = False
        
        self.load_model(model_path, encoder_path)
    
    def load_model(self, model_path: str, encoder_path: str) -> bool:
        """Load the trained model and encoders."""
        model_loaded = False
        encoder_loaded = False
        
        try:
            if os.path.exists(model_path):
                with open(model_path, 'rb') as file:
                    model_package = pickle.load(file)
                
                self.model = model_package['model']
                self.model_name = model_package.get('model_name', 'Logistic Regression')
                self.accuracy = model_package.get('accuracy', 0.0)
                self.features = model_package.get('features', [])
                self.classes = model_package.get('classes', [])
                
                print(f"✓ Model loaded: {self.model_name}")
                print(f"  Accuracy: {self.accuracy:.2%}")
                print(f"  Classes: {len(self.classes)} activities")
                model_loaded = True
            else:
                print("⚠ Model file not found. Using rule-based fallback.")
        except Exception as e:
            print(f"⚠ Error loading model: {e}. Using rule-based fallback.")
        
        try:
            if os.path.exists(encoder_path):
                with open(encoder_path, 'rb') as file:
                    encoder_package = pickle.load(file)
                
                self.weather_encoder = encoder_package['weather_encoder']
                self.activity_encoder = encoder_package['activity_encoder']
                print(f"✓ Encoders loaded successfully")
                encoder_loaded = True
            else:
                print("⚠ Encoder file not found. Using rule-based fallback.")
                if self.classes:
                    from sklearn.preprocessing import LabelEncoder
                    self.activity_encoder = LabelEncoder()
                    self.activity_encoder.classes_ = np.array(self.classes)
                    encoder_loaded = True
                    print(f"  Created fallback activity encoder with {len(self.classes)} classes")
        except Exception as e:
            print(f"⚠ Error loading encoders: {e}. Using rule-based fallback.")
        
        self.use_ml = model_loaded and encoder_loaded
        return self.use_ml
    
    def get_weather_encoding(self, weather: str) -> int:
        """Get weather encoding, with fallback."""
        if self.weather_encoder is not None:
            try:
                return self.weather_encoder.transform([weather])[0]
            except:
                pass
        
        weather_map = {
            'Clear': 0, 'Clouds': 1, 'Rain': 2, 'Thunderstorm': 3,
            'Snow': 4, 'Drizzle': 5, 'Mist': 6, 'Fog': 7
        }
        return weather_map.get(weather, 0)
    
    def predict(self, temperature: float, humidity: float, wind_speed: float, 
                weather: str) -> Dict[str, Any]:
        """Make a prediction using the trained model or rule-based fallback."""
        if not self.use_ml or self.model is None:
            return self.rule_based_predict(temperature, humidity, wind_speed, weather)
        
        try:
            weather_encoded = self.get_weather_encoding(weather)
            
            features = np.array([[
                temperature,
                humidity,
                wind_speed,
                weather_encoded,
                1 if weather in ['Rain', 'Thunderstorm', 'Drizzle'] else 0,
                1 if weather == 'Snow' else 0,
                1 if weather == 'Clear' else 0,
                1 if weather == 'Clouds' else 0,
                1 if weather in ['Mist', 'Fog'] else 0
            ]])
            
            prediction = self.model.predict(features)
            probabilities = self.model.predict_proba(features)[0]
            
            if self.activity_encoder is not None:
                activity = self.activity_encoder.inverse_transform(prediction)[0]
            else:
                activity = self.classes[prediction[0]] if prediction[0] < len(self.classes) else "Unknown"
            
            confidence = max(probabilities) * 100
            
            return {
                'activity': activity,
                'confidence': confidence,
                'probabilities': {
                    cls: prob * 100 for cls, prob in zip(self.classes, probabilities)
                } if self.classes else {},
                'method': 'ML Model'
            }
            
        except Exception as e:
            print(f"⚠ ML prediction failed: {e}. Using rule-based fallback.")
            return self.rule_based_predict(temperature, humidity, wind_speed, weather)
    
    def rule_based_predict(self, temperature: float, humidity: float, 
                          wind_speed: float, weather: str) -> Dict[str, Any]:
        """Rule-based prediction with reasons."""
        weather_lower = weather.lower()
        
        if "rain" in weather_lower or "thunderstorm" in weather_lower:
            return {
                'activity': 'Indoor Games / Movies',
                'reason': 'Rainy weather is not suitable for most outdoor activities.',
                'confidence': 95.0,
                'method': 'Rule-Based (Rain)'
            }
        
        if "snow" in weather_lower:
            return {
                'activity': 'Indoor Activities',
                'reason': 'Cold snowy conditions are better suited for indoor activities.',
                'confidence': 95.0,
                'method': 'Rule-Based (Snow)'
            }
        
        if temperature >= 35:
            return {
                'activity': 'Indoor Activities',
                'reason': 'The temperature is high. Avoid strenuous outdoor activities.',
                'confidence': 90.0,
                'method': 'Rule-Based (Hot)'
            }
        
        if wind_speed >= 8:
            return {
                'activity': 'Indoor Activities',
                'reason': 'Strong wind may make outdoor activities uncomfortable.',
                'confidence': 85.0,
                'method': 'Rule-Based (Wind)'
            }
        
        if temperature < 18:
            return {
                'activity': 'Walking / Indoor Games',
                'reason': 'The weather is cool. A short walk or indoor activity is suitable.',
                'confidence': 80.0,
                'method': 'Rule-Based (Cold)'
            }
        
        if 18 <= temperature <= 32:
            if humidity <= 75:
                return {
                    'activity': 'Walking / Cycling / Outdoor Sports',
                    'reason': 'The weather conditions are comfortable for outdoor activities.',
                    'confidence': 90.0,
                    'method': 'Rule-Based (Comfortable)'
                }
            else:
                return {
                    'activity': 'Light Outdoor Activity',
                    'reason': 'Humidity is somewhat high, so choose a light outdoor activity.',
                    'confidence': 85.0,
                    'method': 'Rule-Based (Humid)'
                }
        
        if "cloud" in weather_lower:
            return {
                'activity': 'Walking / Photography',
                'reason': 'Cloudy weather can be comfortable for a short outdoor activity.',
                'confidence': 80.0,
                'method': 'Rule-Based (Cloudy)'
            }
        
        return {
            'activity': 'Indoor / Outdoor Activity',
            'reason': 'Weather conditions are moderate.',
            'confidence': 70.0,
            'method': 'Rule-Based (Default)'
        }

class WeatherService:
    """Fetch and process weather data from OpenWeather API."""
    
    def __init__(self, api_key: str = API_KEY):
        self.api_key = api_key
        self.base_url = "https://api.openweathermap.org/data/2.5/weather"
    
    def get_weather(self, city: str) -> Dict[str, Any]:
        """Get weather data for a city."""
        if not self.api_key or self.api_key == "PASTE_YOUR_NEW_API_KEY_HERE":
            return {'error': 'API key not configured'}
        
        params = {
            'q': city,
            'appid': self.api_key,
            'units': 'metric'
        }
        
        try:
            response = requests.get(self.base_url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                return {
                    'city': data['name'],
                    'country': data.get('sys', {}).get('country', ''),
                    'temperature': data['main']['temp'],
                    'feels_like': data['main']['feels_like'],
                    'humidity': data['main']['humidity'],
                    'wind_speed': data['wind']['speed'],
                    'weather': data['weather'][0]['main'],
                    'description': data['weather'][0]['description'],
                    'icon': data['weather'][0]['icon'],
                    'pressure': data['main']['pressure'],
                    'timestamp': datetime.now().isoformat()
                }
            else:
                error_msg = response.json().get('message', 'Unknown error')
                return {'error': f'API error: {error_msg}'}
                
        except requests.exceptions.ConnectionError:
            return {'error': 'Network connection error. Please check your internet connection.'}
        except requests.exceptions.Timeout:
            return {'error': 'Request timeout. The API server took too long to respond.'}
        except requests.exceptions.RequestException as e:
            return {'error': f'API request failed: {str(e)}'}
        except Exception as e:
            return {'error': f'Unexpected error: {str(e)}'}
class N8NIntegration:
    """Main integration class for n8n workflows."""
    
    def __init__(self):
        self.model_loader = ModelLoader()
        self.weather_service = WeatherService()
        self.n8n_available = False  
    
    def get_recommendation_from_n8n(self, weather_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Call the n8n webhook and return the recommendation.
        Returns None if the call fails.
        """
        payload = {
            "city": weather_data.get("city", ""),
            "temperature": weather_data.get("temperature", 25),
            "humidity": weather_data.get("humidity", 60),
            "wind_speed": weather_data.get("wind_speed", 3),
            "weather": weather_data.get("weather", "Clear"),
            "description": weather_data.get("description", "")
        }
        
        try:
            print(f"📤 Calling n8n webhook: {N8N_WEBHOOK_URL}")
            resp = requests.post(N8N_WEBHOOK_URL, json=payload, timeout=15)
            resp.raise_for_status()
            
            data = resp.json()
            print(f"📥 n8n response: {json.dumps(data, indent=2)}")
            
            rec = None
            
            if 'recommendation' in data and isinstance(data['recommendation'], dict):
                rec = data['recommendation']
            elif 'activity' in data and 'reason' in data:
                rec = data
            elif 'result' in data:
                rec = {
                    'activity': data.get('result', 'No recommendation'),
                    'reason': data.get('message', ''),
                    'method': 'n8n'
                }
            elif isinstance(data, dict):
                for key in ['activity', 'recommendation', 'result', 'suggestion']:
                    if key in data and isinstance(data[key], (str, dict)):
                        if isinstance(data[key], str):
                            rec = {'activity': data[key], 'reason': 'From n8n', 'method': 'n8n'}
                        elif isinstance(data[key], dict) and 'activity' in data[key]:
                            rec = data[key]
                        break
            
            if rec and 'activity' in rec:
                if 'method' not in rec:
                    rec['method'] = 'n8n-ai'
                if 'reason' not in rec:
                    rec['reason'] = 'Recommendation from n8n'
                self.n8n_available = True
                return rec
            
            print("⚠ Could not parse n8n response format")
            return None
            
        except requests.exceptions.Timeout:
            print("⚠ n8n request timed out")
            return None
        except requests.exceptions.ConnectionError:
            print("⚠ Cannot connect to n8n (network error)")
            return None
        except requests.exceptions.HTTPError as e:
            print(f"⚠ n8n HTTP error: {e}")
            return None
        except Exception as e:
            print(f"⚠ n8n call failed: {e}")
            return None
    
    def analyze_weather(self, temperature: float, humidity: float, 
                        wind_speed: float, weather: str,
                        description: str = "") -> Dict[str, Any]:
        """
        Analyze weather and recommend an activity.
        Uses n8n first, falls back to local if n8n fails.
        """
        weather_data = {
            "temperature": temperature,
            "humidity": humidity,
            "wind_speed": wind_speed,
            "weather": weather,
            "description": description
        }
        
        n8n_result = self.get_recommendation_from_n8n(weather_data)
        
        if n8n_result:
            result = {
                'activity': n8n_result.get('activity', 'No recommendation'),
                'reason': n8n_result.get('reason', ''),
                'confidence': n8n_result.get('confidence', 90.0),
                'method': n8n_result.get('method', 'n8n-ai'),
                'input': weather_data,
                'timestamp': datetime.now().isoformat(),
                'n8n_available': True
            }
        else:
            local_result = self.model_loader.predict(temperature, humidity, wind_speed, weather)
            result = {
                'activity': local_result.get('activity', 'No recommendation'),
                'reason': local_result.get('reason', 'Weather conditions are moderate.'),
                'confidence': local_result.get('confidence', 70.0),
                'method': local_result.get('method', 'Rule-Based (Local)'),
                'input': weather_data,
                'timestamp': datetime.now().isoformat(),
                'n8n_available': False
            }
        
        return result
    
    def get_weather_and_recommend(self, city: str) -> Dict[str, Any]:
        """
        Fetch weather for a city and get activity recommendation.
        This is the main function for n8n workflow integration.
        """
        weather_data = self.weather_service.get_weather(city)
        
        if 'error' in weather_data:
            return weather_data
        
        recommendation = self.analyze_weather(
            temperature=weather_data['temperature'],
            humidity=weather_data['humidity'],
            wind_speed=weather_data['wind_speed'],
            weather=weather_data['weather'],
            description=weather_data['description']
        )
        
        return {
            'success': True,
            'city': weather_data['city'],
            'country': weather_data['country'],
            'weather': weather_data,
            'recommendation': recommendation,
            'n8n_available': recommendation.get('n8n_available', False),
            'timestamp': datetime.now().isoformat()
        }
    
    def batch_analyze(self, weather_records: list) -> list:
        """
        Analyze multiple weather records in batch.
        """
        results = []
        for record in weather_records:
            result = self.analyze_weather(
                temperature=record.get('temperature', 0),
                humidity=record.get('humidity', 0),
                wind_speed=record.get('wind_speed', 0),
                weather=record.get('weather', 'Clear'),
                description=record.get('description', '')
            )
            results.append({
                'input': record,
                'output': result
            })
        return results

def handle_webhook(event_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle incoming webhook events.
    """
    integration = N8NIntegration()
    
    if event_type == 'weather_analysis':
        return integration.analyze_weather(
            temperature=data.get('temperature', 0),
            humidity=data.get('humidity', 0),
            wind_speed=data.get('wind_speed', 0),
            weather=data.get('weather', 'Clear'),
            description=data.get('description', '')
        )
    
    elif event_type == 'city_weather':
        city = data.get('city', '')
        if not city:
            return {'error': 'City name is required'}
        return integration.get_weather_and_recommend(city)
    
    elif event_type == 'batch_analysis':
        records = data.get('records', [])
        return {'results': integration.batch_analyze(records)}
    
    else:
        return {'error': f'Unknown event type: {event_type}'}

def create_flask_app():
    """Create a Flask app for receiving webhook requests."""
    try:
        from flask import Flask, request, jsonify
        from flask_cors import CORS
        
        app = Flask(__name__)
        CORS(app)
        integration = N8NIntegration()
        
        @app.route('/', methods=['GET'])
        def home():
            return jsonify({
                'service': 'Weather Activity Recommendation System',
                'status': 'running',
                'n8n_webhook_url': N8N_WEBHOOK_URL,
                'endpoints': [
                    'POST /webhook/weather - Analyze weather data',
                    'POST /webhook/city - Get weather for a city',
                    'POST /webhook/batch - Batch analysis',
                    'GET /health - Health check'
                ],
                'timestamp': datetime.now().isoformat()
            })
        
        @app.route('/webhook/weather', methods=['POST'])
        def weather_webhook():
            """Handle weather analysis webhook."""
            try:
                data = request.json or {}
                result = handle_webhook('weather_analysis', data)
                return jsonify(result)
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @app.route('/webhook/city', methods=['POST'])
        def city_webhook():
            """Handle city weather webhook."""
            try:
                data = request.json or {}
                result = handle_webhook('city_weather', data)
                return jsonify(result)
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @app.route('/webhook/batch', methods=['POST'])
        def batch_webhook():
            """Handle batch analysis webhook."""
            try:
                data = request.json or {}
                result = handle_webhook('batch_analysis', data)
                return jsonify(result)
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @app.route('/health', methods=['GET'])
        def health_check():
            """Health check endpoint."""
            return jsonify({
                'status': 'healthy',
                'model_loaded': integration.model_loader.use_ml,
                'model_name': integration.model_loader.model_name,
                'accuracy': integration.model_loader.accuracy,
                'n8n_webhook_url': N8N_WEBHOOK_URL,
                'timestamp': datetime.now().isoformat()
            })
        
        return app
        
    except ImportError:
        print("Flask not installed. Install with: pip install flask flask-cors")
        return None

def test_n8n_connection():
    """Test the n8n webhook connection."""
    integration = N8NIntegration()
    
    test_weather = {
        "city": "Test",
        "temperature": 25,
        "humidity": 60,
        "wind_speed": 3,
        "weather": "Clear",
        "description": "Clear sky"
    }
    
    print("\n" + "=" * 60)
    print(" TESTING N8N CONNECTION")
    print("=" * 60)
    print(f"\nTesting webhook: {N8N_WEBHOOK_URL}")
    print(f"Payload: {json.dumps(test_weather, indent=2)}")
    
    result = integration.get_recommendation_from_n8n(test_weather)
    
    if result:
        print("\n✅ n8n is working!")
        print(f"   Activity: {result.get('activity')}")
        print(f"   Reason: {result.get('reason')}")
        print(f"   Method: {result.get('method')}")
    else:
        print("\n❌ n8n is not available (using local fallback)")
    
    print("=" * 60)

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        import argparse
        
        parser = argparse.ArgumentParser(description='Weather Activity Recommendation System')
        parser.add_argument('--city', type=str, help='City name to get weather')
        parser.add_argument('--analyze', action='store_true', help='Analyze weather data')
        parser.add_argument('--temperature', type=float, help='Temperature in Celsius')
        parser.add_argument('--humidity', type=float, help='Humidity percentage')
        parser.add_argument('--wind', type=float, help='Wind speed in m/s')
        parser.add_argument('--weather', type=str, help='Weather condition')
        parser.add_argument('--test', action='store_true', help='Test n8n connection')
        parser.add_argument('--webhook', type=str, help='Webhook event type')
        parser.add_argument('--data', type=str, help='JSON data for webhook')
        
        args = parser.parse_args()
        
        if args.test:
            test_n8n_connection()
        elif args.city:
            integration = N8NIntegration()
            result = integration.get_weather_and_recommend(args.city)
            print(json.dumps(result, indent=2))
        elif args.analyze:
            integration = N8NIntegration()
            result = integration.analyze_weather(
                temperature=args.temperature or 25,
                humidity=args.humidity or 60,
                wind_speed=args.wind or 3,
                weather=args.weather or 'Clear'
            )
            print(json.dumps(result, indent=2))
        elif args.webhook:
            data = json.loads(args.data) if args.data else {}
            result = handle_webhook(args.webhook, data)
            print(json.dumps(result, indent=2))
        else:
            print("Usage:")
            print("  python n8n.py --test                    # Test n8n connection")
            print("  python n8n.py --city London             # Get weather for London")
            print("  python n8n.py --analyze --temperature 25 --weather Clear")
    else:
        # Interactive mode
        print("=" * 60)
        print(" WEATHER ACTIVITY RECOMMENDATION SYSTEM - N8N INTEGRATION")
        print("=" * 60)
        
        integration = N8NIntegration()
        
        if integration.model_loader.use_ml:
            print(f"\n✓ Model loaded: {integration.model_loader.model_name}")
            print(f"  Accuracy: {integration.model_loader.accuracy:.2%}")
            print(f"  Classes: {len(integration.model_loader.classes)} activities")
        else:
            print("\n⚠ Using rule-based recommendation (ML model not available)")
        
        print("\n" + "=" * 60)
        print("N8N INTEGRATION READY")
        print("=" * 60)
        print(f"\nWebhook URL: {N8N_WEBHOOK_URL}")
        print("\nCommands:")
        print("  python n8n.py --test      - Test n8n connection")
        print("  python n8n.py --city London - Get recommendation for London")
        print("  python n8n.py --analyze --temperature 25 --weather Clear")
        
        print("\nTest n8n connection now? (y/n): ", end="")
