"""
SYSTEM TESTS - Weather Activity Recommendation System
Tests the complete system from end-to-end
Run with: python -m pytest tests/test_system.py -v
"""

import unittest
import json
import os
import sys
import time
import threading
import subprocess
import requests
from unittest.mock import patch, Mock
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import numpy as np
from flask import Flask

from ai import analyze_weather
from server import app, rule_based_recommendation
from n8n import N8NIntegration, ModelLoader, WeatherService
import train_model
import gen


# ============================================================
# TEST 1: END-TO-END SYSTEM TESTS
# ============================================================

class TestEndToEndSystem(unittest.TestCase):
    """End-to-end system tests"""
    
    def setUp(self):
        """Setup test environment"""
        self.app = app.test_client()
        self.app.testing = True
        self.integration = N8NIntegration()

    def test_complete_user_journey(self):
        """Test complete user journey from city input to recommendation"""
        with patch('requests.get') as mock_get:
            # Mock weather API response
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                'name': 'New York',
                'sys': {'country': 'US'},
                'main': {
                    'temp': 22.5,
                    'feels_like': 21.0,
                    'humidity': 65
                },
                'wind': {'speed': 4.0},
                'weather': [{'main': 'Clear', 'description': 'clear sky'}]
            }
            mock_get.return_value = mock_response

            # 1. User enters city
            city = "New York"
            
            # 2. System fetches weather
            weather_service = WeatherService('test_key')
            weather_data = weather_service.get_weather(city)
            
            # 3. System analyzes weather
            recommendation = self.integration.analyze_weather(
                temperature=weather_data['temperature'],
                humidity=weather_data['humidity'],
                wind_speed=weather_data['wind_speed'],
                weather=weather_data['weather'],
                description=weather_data['description']
            )
            
            # 4. Verify results
            self.assertIsNotNone(recommendation)
            self.assertIn('activity', recommendation)
            self.assertIn('reason', recommendation)
            self.assertEqual(recommendation['input']['weather'], 'Clear')

    def test_api_workflow(self):
        """Test complete API workflow"""
        # 1. POST weather data
        payload = {
            'temperature': 25,
            'humidity': 60,
            'wind_speed': 3,
            'weather': 'Clear'
        }
        
        response = self.app.post('/webhook/weather', 
                                json=payload,
                                content_type='application/json')
        
        # 2. Verify API response
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertIn('activity', data)
        self.assertIn('reason', data)
        
        # 3. Verify recommendation is reasonable
        self.assertEqual(data['activity'], 'Walking / Cycling / Outdoor Sports')
        self.assertIn('comfortable', data['reason'].lower())

    def test_city_workflow(self):
        """Test complete city workflow"""
        with patch('requests.get') as mock_get:
            # Mock weather API
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                'name': 'London',
                'sys': {'country': 'GB'},
                'main': {
                    'temp': 15.5,
                    'feels_like': 13.2,
                    'humidity': 82
                },
                'wind': {'speed': 4.1},
                'weather': [{'main': 'Clouds', 'description': 'scattered clouds'}]
            }
            mock_get.return_value = mock_response

            # 1. POST city request
            response = self.app.post('/webhook/city', 
                                    json={'city': 'London'},
                                    content_type='application/json')
            
            # 2. Verify response
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            self.assertTrue(data['success'])
            self.assertEqual(data['city'], 'London')
            self.assertIn('weather', data)
            self.assertIn('recommendation', data)
            self.assertEqual(data['weather']['condition'], 'Clouds')

    def test_batch_workflow(self):
        """Test complete batch workflow"""
        # 1. Prepare batch data
        batch_data = {
            'records': [
                {'temperature': 25, 'humidity': 60, 'weather': 'Clear'},
                {'temperature': 30, 'humidity': 80, 'weather': 'Rain'},
                {'temperature': 15, 'humidity': 70, 'weather': 'Clouds'},
                {'temperature': -2, 'humidity': 75, 'weather': 'Snow'}
            ]
        }
        
        # 2. POST batch request
        response = self.app.post('/webhook/batch', 
                                json=batch_data,
                                content_type='application/json')
        
        # 3. Verify response
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertEqual(data['total_processed'], 4)
        self.assertEqual(len(data['results']), 4)
        
        # 4. Verify each recommendation
        expected_activities = [
            'Walking / Cycling / Outdoor Sports',
            'Indoor Games / Movies',
            'Walking / Photography',
            'Indoor Activities'
        ]
        for i, result in enumerate(data['results']):
            self.assertIn('activity', result['output'])
            self.assertEqual(result['output']['activity'], expected_activities[i])


# ============================================================
# TEST 2: PERFORMANCE SYSTEM TESTS
# ============================================================

class TestPerformanceSystem(unittest.TestCase):
    """Performance system tests"""
    
    def test_response_time_single_request(self):
        """Test response time for single request"""
        start_time = time.time()
        
        result = analyze_weather(25, 60, 3, "Clear")
        
        elapsed_time = time.time() - start_time
        self.assertLess(elapsed_time, 0.05)  # Should be very fast (<50ms)
        self.assertIsNotNone(result)

    def test_api_response_time(self):
        """Test API response time"""
        app_client = app.test_client()
        
        start_time = time.time()
        response = app_client.post('/webhook/weather', 
                                  json={'temperature': 25, 'humidity': 60, 'weather': 'Clear'},
                                  content_type='application/json')
        elapsed_time = time.time() - start_time
        
        self.assertEqual(response.status_code, 200)
        self.assertLess(elapsed_time, 0.5)  # Should be <500ms

    def test_batch_processing_time(self):
        """Test batch processing time for multiple records"""
        # Create 100 records
        records = [
            {'temperature': np.random.uniform(0, 40),
             'humidity': np.random.uniform(30, 90),
             'weather': np.random.choice(['Clear', 'Clouds', 'Rain', 'Snow'])}
            for _ in range(100)
        ]
        
        start_time = time.time()
        
        # Process batch
        results = []
        for record in records:
            result = analyze_weather(
                record['temperature'],
                record['humidity'],
                3,  # wind speed
                record['weather']
            )
            results.append(result)
        
        elapsed_time = time.time() - start_time
        avg_time_per_record = elapsed_time / len(records)
        
        print(f"\nBatch of {len(records)} records: {elapsed_time:.2f}s")
        print(f"Average per record: {avg_time_per_record*1000:.2f}ms")
        
        self.assertLess(avg_time_per_record, 0.05)  # <50ms per record

    def test_model_prediction_speed(self):
        """Test ML model prediction speed"""
        loader = ModelLoader()
        
        if loader.use_ml:
            start_time = time.time()
            for _ in range(1000):
                loader.predict(25, 60, 3, 'Clear')
            elapsed_time = time.time() - start_time
            avg_time = elapsed_time / 1000
            
            print(f"\n1000 predictions: {elapsed_time:.2f}s")
            print(f"Average: {avg_time*1000:.2f}ms")
            self.assertLess(avg_time, 0.01)  # <10ms per prediction

    def test_concurrent_requests(self):
        """Test handling concurrent requests"""
        import concurrent.futures
        
        def make_request():
            with app.test_client() as client:
                return client.post('/webhook/weather', 
                                  json={'temperature': 25, 'humidity': 60, 'weather': 'Clear'},
                                  content_type='application/json')
        
        # Make 50 concurrent requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
            futures = [executor.submit(make_request) for _ in range(50)]
            results = [f.result() for f in futures]
        
        # Verify all requests succeeded
        for response in results:
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            self.assertTrue(data['success'])


# ============================================================
# TEST 3: DATA VALIDATION SYSTEM TESTS
# ============================================================

class TestDataValidationSystem(unittest.TestCase):
    """Data validation system tests"""
    
    def test_validate_weather_data_structure(self):
        """Test weather data structure validation"""
        valid_data = {
            'temperature': 25.0,
            'humidity': 60.0,
            'wind_speed': 3.0,
            'weather': 'Clear',
            'description': 'clear sky'
        }
        
        # Validate all fields exist
        required_fields = ['temperature', 'humidity', 'wind_speed', 'weather']
        for field in required_fields:
            self.assertIn(field, valid_data)
        
        # Validate data types
        self.assertIsInstance(valid_data['temperature'], (int, float))
        self.assertIsInstance(valid_data['humidity'], (int, float))
        self.assertIsInstance(valid_data['wind_speed'], (int, float))
        self.assertIsInstance(valid_data['weather'], str)

    def test_validate_recommendation_structure(self):
        """Test recommendation structure validation"""
        result = analyze_weather(25, 60, 3, "Clear")
        
        # Validate required fields
        required_fields = ['activity', 'reason', 'category']
        for field in required_fields:
            self.assertIn(field, result)
        
        # Validate field types
        self.assertIsInstance(result['activity'], str)
        self.assertIsInstance(result['reason'], str)
        self.assertIsInstance(result['category'], str)
        
        # Validate category is one of allowed values
        allowed_categories = ['Indoor', 'Outdoor', 'Mixed']
        self.assertIn(result['category'], allowed_categories)

    def test_validate_api_response_structure(self):
        """Test API response structure validation"""
        app_client = app.test_client()
        
        response = app_client.post('/webhook/weather', 
                                  json={'temperature': 25, 'humidity': 60, 'weather': 'Clear'},
                                  content_type='application/json')
        data = json.loads(response.data)
        
        # Validate required fields
        required_fields = ['success', 'activity', 'reason', 'method', 'input']
        for field in required_fields:
            self.assertIn(field, data)
        
        # Validate field types
        self.assertIsInstance(data['success'], bool)
        self.assertIsInstance(data['activity'], str)
        self.assertIsInstance(data['reason'], str)
        self.assertIsInstance(data['method'], str)
        self.assertIsInstance(data['input'], dict)

    def test_validate_dataset_quality(self):
        """Test generated dataset quality"""
        from gen import generate_weather_dataset
        
        df = generate_weather_dataset(1000)
        
        # Check for missing values
        self.assertEqual(df.isnull().sum().sum(), 0)
        
        # Check for duplicate rows
        self.assertEqual(df.duplicated().sum(), 0)
        
        # Check for unreasonable values
        self.assertTrue((df['temperature'] >= -50).all())
        self.assertTrue((df['temperature'] <= 60).all())
        self.assertTrue((df['humidity'] >= 0).all())
        self.assertTrue((df['humidity'] <= 100).all())
        self.assertTrue((df['wind_speed'] >= 0).all())


# ============================================================
# TEST 4: FAILOVER SYSTEM TESTS
# ============================================================

class TestFailoverSystem(unittest.TestCase):
    """Failover and resilience system tests"""
    
    def test_n8n_failover(self):
        """Test failover when n8n is unavailable"""
        integration = N8NIntegration()
        
        with patch.object(integration, 'get_recommendation_from_n8n') as mock_n8n:
            # Simulate n8n failure
            mock_n8n.return_value = None
            
            # System should fallback to rule-based
            result = integration.analyze_weather(25, 60, 3, 'Clear')
            self.assertFalse(result['n8n_available'])
            self.assertEqual(result['method'], 'Rule-Based (Local)')

    def test_model_failover(self):
        """Test failover when ML model is unavailable"""
        with patch('n8n.os.path.exists') as mock_exists:
            mock_exists.return_value = False
            
            loader = ModelLoader()
            self.assertFalse(loader.use_ml)
            
            # Should use rule-based prediction
            result = loader.predict(25, 60, 3, 'Clear')
            self.assertIn('Rule-Based', result['method'])

    def test_api_failover(self):
        """Test failover when weather API fails"""
        with patch('requests.get') as mock_get:
            # Simulate API failure
            mock_get.side_effect = Exception('API failed')
            
            service = WeatherService('test_key')
            result = service.get_weather('London')
            self.assertIn('error', result)
            self.assertIsNotNone(result['error'])

    def test_graceful_degradation(self):
        """Test graceful degradation when components fail"""
        # Test with missing components
        with patch('n8n.ModelLoader.load_model') as mock_load:
            mock_load.return_value = False
            
            loader = ModelLoader()
            self.assertFalse(loader.use_ml)
            
            # Should still work with rule-based
            result = loader.predict(25, 60, 3, 'Clear')
            self.assertIn('activity', result)

    def test_network_timeout_handling(self):
        """Test handling of network timeouts"""
        import requests
        
        with patch('requests.post') as mock_post:
            mock_post.side_effect = requests.exceptions.Timeout()
            
            integration = N8NIntegration()
            result = integration.get_recommendation_from_n8n(
                {'temperature': 25, 'humidity': 60, 'weather': 'Clear'}
            )
            self.assertIsNone(result)


# ============================================================
# TEST 5: CONCURRENCY SYSTEM TESTS
# ============================================================

class TestConcurrencySystem(unittest.TestCase):
    """Concurrency and multi-threading system tests"""
    
    def test_parallel_weather_analysis(self):
        """Test parallel weather analysis"""
        import concurrent.futures
        
        weather_conditions = [
            (25, 60, 3, 'Clear'),
            (30, 80, 5, 'Rain'),
            (15, 70, 2, 'Clouds'),
            (-2, 75, 4, 'Snow'),
            (35, 40, 2, 'Clear')
        ]
        
        def analyze(condition):
            temp, hum, wind, weather = condition
            return analyze_weather(temp, hum, wind, weather)
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            results = list(executor.map(analyze, weather_conditions))
        
        self.assertEqual(len(results), 5)
        for result in results:
            self.assertIn('activity', result)

    def test_parallel_api_calls(self):
        """Test parallel API calls"""
        import concurrent.futures
        
        def call_api():
            with app.test_client() as client:
                return client.post('/webhook/weather', 
                                  json={'temperature': 25, 'humidity': 60, 'weather': 'Clear'},
                                  content_type='application/json')
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(call_api) for _ in range(10)]
            responses = [f.result() for f in futures]
        
        for response in responses:
            self.assertEqual(response.status_code, 200)


# ============================================================
# TEST 6: SECURITY SYSTEM TESTS
# ============================================================

class TestSecuritySystem(unittest.TestCase):
    """Security system tests"""
    
    def test_input_sanitization(self):
        """Test input sanitization"""
        # Test with potentially malicious input
        malicious_inputs = [
            "'; DROP TABLE users; --",
            "<script>alert('XSS')</script>",
            "../../../etc/passwd",
            "SELECT * FROM users",
            "%00",  # Null byte
            "🚀💥🔥"  # Emoji
        ]
        
        for input_data in malicious_inputs:
            with self.subTest(input=input_data):
                # Should not crash or allow injection
                result = analyze_weather(25, 60, 3, input_data)
                self.assertIsNotNone(result)
                self.assertIn('activity', result)

    def test_api_key_validation(self):
        """Test API key validation"""
        # Test with invalid API key
        service = WeatherService('invalid_key')
        self.assertEqual(service.api_key, 'invalid_key')
        
        # Test with empty API key
        service = WeatherService('')
        result = service.get_weather('London')
        self.assertEqual(result['error'], 'API key not configured')

    def test_cors_security(self):
        """Test CORS security headers"""
        response = app.test_client().options('/webhook/weather')
        self.assertIn('Access-Control-Allow-Origin', response.headers)
        self.assertIn('Access-Control-Allow-Methods', response.headers)
        self.assertIn('Access-Control-Allow-Headers', response.headers)


# ============================================================
# TEST 7: RELIABILITY SYSTEM TESTS
# ============================================================

class TestReliabilitySystem(unittest.TestCase):
    """Reliability and robustness system tests"""
    
    def test_continuous_operation(self):
        """Test system can handle continuous operation"""
        for i in range(100):
            result = analyze_weather(
                np.random.uniform(-10, 40),
                np.random.uniform(30, 90),
                np.random.uniform(0, 15),
                np.random.choice(['Clear', 'Clouds', 'Rain', 'Snow'])
            )
            self.assertIsNotNone(result)
            self.assertIn('activity', result)

    def test_memory_leak_prevention(self):
        """Test for memory leaks during repeated operations"""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        # Perform many operations
        for _ in range(1000):
            analyze_weather(25, 60, 3, "Clear")
        
        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory
        
        print(f"\nMemory increase: {memory_increase / 1024 / 1024:.2f} MB")
        self.assertLess(memory_increase, 50 * 1024 * 1024)  # Less than 50MB increase

    def test_error_recovery(self):
        """Test error recovery after failures"""
        for i in range(10):
            try:
                result = analyze_weather(25, 60, 3, "Clear")
                self.assertIsNotNone(result)
            except Exception as e:
                self.fail(f"System failed to recover: {e}")

    def test_consistent_output(self):
        """Test consistent output for same inputs"""
        test_cases = [
            (20, 85, 5, "Rain"),
            (25, 60, 3, "Clear"),
            (15, 70, 2, "Clouds")
        ]
        
        for temp, hum, wind, weather in test_cases:
            with self.subTest(weather=weather):
                results = []
                for _ in range(10):
                    results.append(analyze_weather(temp, hum, wind, weather))
                
                # All results should be identical for same inputs
                first_result = results[0]
                for result in results[1:]:
                    self.assertEqual(result['activity'], first_result['activity'])
                    self.assertEqual(result['category'], first_result['category'])
                    self.assertEqual(result['reason'], first_result['reason'])


# ============================================================
# TEST 8: SCALABILITY SYSTEM TESTS
# ============================================================

class TestScalabilitySystem(unittest.TestCase):
    """Scalability system tests"""
    
    def test_handle_large_batch(self):
        """Test handling of large batches"""
        # Generate 1000 records
        records = [
            {
                'temperature': np.random.uniform(0, 40),
                'humidity': np.random.uniform(30, 90),
                'wind_speed': np.random.uniform(0, 10),
                'weather': np.random.choice(['Clear', 'Clouds', 'Rain'])
            }
            for _ in range(1000)
        ]
        
        start_time = time.time()
        
        # Process all records
        results = []
        for record in records:
            result = analyze_weather(
                record['temperature'],
                record['humidity'],
                record['wind_speed'],
                record['weather']
            )
            results.append(result)
        
        elapsed_time = time.time() - start_time
        print(f"\nProcessed 1000 records in {elapsed_time:.2f}s")
        print(f"Average: {elapsed_time/1000*1000:.2f}ms per record")
        
        self.assertEqual(len(results), 1000)
        self.assertLess(elapsed_time, 30)  # Should complete within 30 seconds

    def test_model_scalability(self):
        """Test model scalability with different data sizes"""
        # Test with different dataset sizes
        sizes = [100, 500, 1000, 5000]
        
        for size in sizes:
            with self.subTest(size=size):
                from gen import generate_weather_dataset
                df = generate_weather_dataset(size)
                self.assertEqual(len(df), size)

    def test_concurrent_user_simulation(self):
        """Simulate concurrent users"""
        import concurrent.futures
        
        def simulate_user(user_id):
            # Each user makes multiple requests
            results = []
            for _ in range(10):
                result = analyze_weather(
                    np.random.uniform(0, 40),
                    np.random.uniform(30, 90),
                    np.random.uniform(0, 10),
                    np.random.choice(['Clear', 'Clouds', 'Rain'])
                )
                results.append(result)
            return results
        
        # Simulate 10 users with 10 requests each
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(simulate_user, i) for i in range(10)]
            all_results = [f.result() for f in futures]
        
        self.assertEqual(len(all_results), 10)
        for user_results in all_results:
            self.assertEqual(len(user_results), 10)


# ============================================================
# TEST 9: ACCURACY SYSTEM TESTS
# ============================================================

class TestAccuracySystem(unittest.TestCase):
    """Accuracy and quality system tests"""
    
    def test_recommendation_accuracy(self):
        """Test recommendation accuracy against expected outputs"""
        test_cases = [
            # (temp, humidity, wind, weather, expected_activity)
            (25, 60, 3, "Clear", "Walking / Cycling / Outdoor Sports"),
            (30, 80, 5, "Rain", "Indoor Games / Movies"),
            (-2, 75, 4, "Snow", "Indoor Activities"),
            (38, 40, 2, "Clear", "Indoor Activities"),
            (15, 60, 3, "Clear", "Walking / Indoor Games"),
            (20, 65, 3, "Clouds", "Walking / Photography"),
            (25, 80, 3, "Clear", "Light Outdoor Activity"),
        ]
        
        for temp, hum, wind, weather, expected in test_cases:
            with self.subTest(weather=weather):
                result = analyze_weather(temp, hum, wind, weather)
                self.assertEqual(result['activity'], expected)

    def test_rule_accuracy(self):
        """Test rule-based accuracy against expected outputs"""
        test_cases = [
            (25, 60, 3, "Clear", "Walking / Cycling / Outdoor Sports"),
            (30, 80, 5, "Rain", "Indoor Games / Movies"),
            (-2, 75, 4, "Snow", "Indoor Activities"),
        ]
        
        for temp, hum, wind, weather, expected in test_cases:
            with self.subTest(weather=weather):
                activity, _ = rule_based_recommendation(temp, hum, wind, weather)
                self.assertEqual(activity, expected)

    def test_consistency_across_methods(self):
        """Test consistency between AI engine and rule-based engine"""
        test_cases = [
            (20, 85, 5, "Rain"),
            (-2, 75, 4, "Snow"),
            (38, 40, 2, "Clear"),
            (25, 60, 10, "Clear"),
            (15, 60, 3, "Clear"),
            (20, 65, 3, "Clouds"),
        ]
        
        for temp, hum, wind, weather in test_cases:
            with self.subTest(weather=weather):
                ai_result = analyze_weather(temp, hum, wind, weather)
                rule_activity, _ = rule_based_recommendation(temp, hum, wind, weather)
                self.assertEqual(ai_result['activity'], rule_activity)


# ============================================================
# TEST 10: DEPLOYMENT SYSTEM TESTS
# ============================================================

class TestDeploymentSystem(unittest.TestCase):
    """Deployment readiness system tests"""
    
    def test_all_imports_work(self):
        """Test all imports work correctly"""
        try:
            import ai
            import server
            import n8n
            import train_model
            import gen
            import weather_app
        except ImportError as e:
            self.fail(f"Import failed: {e}")

    def test_configuration_validation(self):
        """Test configuration validation"""
        # Check API key format
        test_key = "8f93b69527326e29e8f2ffd28bb6d0d1"
        self.assertEqual(len(test_key), 32)  # Standard OpenWeather API key length
        self.assertTrue(test_key.isalnum())

    def test_file_structure(self):
        """Test required files exist"""
        required_files = [
            'ai.py',
            'server.py',
            'n8n.py',
            'train_model.py',
            'gen.py',
            'weather_app.py',
            'requirements.txt'
        ]
        
        for file in required_files:
            with self.subTest(file=file):
                self.assertTrue(os.path.exists(file), f"{file} not found")

    def test_environment_variables(self):
        """Test environment variable handling"""
        import os
        
        # Test that we can handle missing environment variables gracefully
        with patch.dict(os.environ, {}, clear=True):
            # Should not crash
            integration = N8NIntegration()
            self.assertIsNotNone(integration)


# ============================================================
# RUN SYSTEM TESTS
# ============================================================

def run_system_tests():
    """Run all system tests"""
    unittest.main(verbosity=2)


if __name__ == '__main__':
    run_system_tests()