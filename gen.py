import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import json

np.random.seed(42)
random.seed(42)

def generate_weather_dataset(n_samples=10000):
    """
    Generate synthetic weather dataset with activity recommendations
    """
    data = []
        weather_types = {
        'Clear': {'temp_range': (15, 35), 'humidity_range': (30, 70), 'wind_range': (0, 5)},
        'Clouds': {'temp_range': (10, 30), 'humidity_range': (50, 85), 'wind_range': (2, 7)},
        'Rain': {'temp_range': (5, 25), 'humidity_range': (70, 100), 'wind_range': (3, 10)},
        'Thunderstorm': {'temp_range': (10, 30), 'humidity_range': (80, 100), 'wind_range': (5, 15)},
        'Snow': {'temp_range': (-10, 5), 'humidity_range': (60, 90), 'wind_range': (1, 6)},
        'Drizzle': {'temp_range': (5, 20), 'humidity_range': (65, 95), 'wind_range': (2, 8)},
        'Mist': {'temp_range': (0, 25), 'humidity_range': (75, 100), 'wind_range': (0, 4)},
        'Fog': {'temp_range': (-5, 20), 'humidity_range': (80, 100), 'wind_range': (0, 3)}
    }
    
    activities = {
        'Walking / Cycling / Outdoor Sports': {
            'temp_min': 18, 'temp_max': 32,
            'humidity_max': 75,
            'wind_max': 8,
            'weather_allowed': ['Clear', 'Clouds']
        },
        'Walking / Indoor Games': {
            'temp_min': 10, 'temp_max': 18,
            'humidity_max': 90,
            'wind_max': 10,
            'weather_allowed': ['Clear', 'Clouds', 'Drizzle']
        },
        'Light Outdoor Activity': {
            'temp_min': 15, 'temp_max': 35,
            'humidity_max': 100,
            'wind_max': 12,
            'weather_allowed': ['Clear', 'Clouds', 'Drizzle', 'Mist']
        },
        'Indoor Activities': {
            'temp_min': -20, 'temp_max': 50,
            'humidity_max': 100,
            'wind_max': 50,
            'weather_allowed': ['Rain', 'Thunderstorm', 'Snow', 'Fog', 'Mist']
        },
        'Walking / Photography': {
            'temp_min': 10, 'temp_max': 28,
            'humidity_max': 85,
            'wind_max': 6,
            'weather_allowed': ['Clear', 'Clouds', 'Mist']
        },
        'Indoor Games / Movies': {
            'temp_min': -20, 'temp_max': 50,
            'humidity_max': 100,
            'wind_max': 50,
            'weather_allowed': ['Rain', 'Thunderstorm', 'Snow', 'Fog']
        },
        'Outdoor Sports': {
            'temp_min': 20, 'temp_max': 30,
            'humidity_max': 70,
            'wind_max': 6,
            'weather_allowed': ['Clear']
        },
        'Walking': {
            'temp_min': 10, 'temp_max': 35,
            'humidity_max': 85,
            'wind_max': 8,
            'weather_allowed': ['Clear', 'Clouds', 'Drizzle', 'Mist']
        }
    }
    
    for i in range(n_samples):
        weather = random.choice(list(weather_types.keys()))
        weather_params = weather_types[weather]
        
        temperature = round(random.uniform(weather_params['temp_range'][0], weather_params['temp_range'][1]), 1)
        humidity = round(random.uniform(weather_params['humidity_range'][0], weather_params['humidity_range'][1]), 1)
        wind_speed = round(random.uniform(weather_params['wind_range'][0], weather_params['wind_range'][1]), 1)
        
        recommended_activity = None
        reason = ""
        
        if weather in ['Rain', 'Thunderstorm']:
            recommended_activity = 'Indoor Games / Movies'
            reason = 'Rainy weather is not suitable for outdoor activities.'
        elif weather == 'Snow':
            recommended_activity = 'Indoor Activities'
            reason = 'Cold snowy conditions are better for indoor activities.'
        elif temperature >= 35:
            recommended_activity = 'Indoor Activities'
            reason = 'Temperature is high. Avoid strenuous outdoor activities.'
        elif wind_speed >= 8:
            recommended_activity = 'Indoor Activities'
            reason = 'Strong wind may make outdoor activities uncomfortable.'
        elif temperature < 18:
            recommended_activity = random.choice(['Walking / Indoor Games', 'Walking'])
            reason = 'The weather is cool. A short walk or indoor activity is suitable.'
        elif 18 <= temperature <= 32:
            if humidity <= 75:
                recommended_activity = random.choice([
                    'Walking / Cycling / Outdoor Sports',
                    'Outdoor Sports',
                    'Walking'
                ])
                reason = 'The weather conditions are comfortable for outdoor activities.'
            else:
                recommended_activity = 'Light Outdoor Activity'
                reason = 'Humidity is somewhat high, so choose a light outdoor activity.'
        elif 'cloud' in weather.lower():
            recommended_activity = random.choice(['Walking / Photography', 'Walking'])
            reason = 'Cloudy weather can be comfortable for a short outdoor activity.'
        else:
            recommended_activity = 'Walking'
            reason = 'Weather conditions are moderate.'
        
        if random.random() < 0.2:
            alternative_activities = [act for act in activities.keys() if act != recommended_activity]
            if alternative_activities:
                recommended_activity = random.choice(alternative_activities)
                reason = f'Alternative recommendation based on specific conditions.'
        
        if random.random() < 0.05: 
            all_activities = list(activities.keys())
            incorrect_activities = [act for act in all_activities if act != recommended_activity]
            if incorrect_activities:
                recommended_activity = random.choice(incorrect_activities)
                reason = 'Noisy data point for training robustness.'
        
        if recommended_activity not in activities:
            recommended_activity = 'Walking'
        
        data_point = {
            'temperature': temperature,
            'humidity': humidity,
            'wind_speed': wind_speed,
            'weather_condition': weather,
            'recommended_activity': recommended_activity,
            'reason': reason,
            'is_rain': 1 if weather in ['Rain', 'Thunderstorm', 'Drizzle'] else 0,
            'is_snow': 1 if weather == 'Snow' else 0,
            'is_clear': 1 if weather == 'Clear' else 0,
            'is_cloudy': 1 if weather == 'Clouds' else 0,
            'is_foggy': 1 if weather in ['Fog', 'Mist'] else 0,
            'temp_category': 'very_cold' if temperature < 0 else
                             'cold' if temperature < 10 else
                             'cool' if temperature < 18 else
                             'warm' if temperature < 25 else
                             'hot' if temperature < 35 else
                             'very_hot',
            'humidity_category': 'low' if humidity < 40 else
                                'medium' if humidity < 70 else
                                'high'
        }
        
        data.append(data_point)
    
    return pd.DataFrame(data)

print("Generating weather dataset...")
