import unittest
import json
import os
import sys
from unittest.mock import Mock, patch
import numpy as np

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import modules to test
from ai import analyze_weather
from server import app, rule_based_recommendation

# Try to import n8n modules (optional)
try:
    from n8n import ModelLoader, WeatherService, N8NIntegration
    N8N_AVAILABLE = True
except ImportError:
    N8N_AVAILABLE = False
    print("⚠️ n8n module not available - skipping n8n tests")

# Try to import train_model functions
try:
    from train_model import train_model
    TRAIN_MODEL_AVAILABLE = True
except ImportError:
    TRAIN_MODEL_AVAILABLE = False
    print("⚠️ train_model function not available - skipping train_model tests")


# ============================================================
# TEST 1: AI ENGINE UNIT TESTS
# ============================================================

class TestAIEngineUnit(unittest.TestCase):
    """Unit tests for core recommendation engine (ai.py)"""
    
    def test_rainy_weather(self):
        """Test rainy weather returns indoor activity"""
        result = analyze_weather(
            temperature=20,
            humidity=85,
            wind_speed=5,
            weather="Rain"
        )
        self.assertEqual(result["activity"], "Indoor Games / Movies")
        self.assertEqual(result["category"], "Indoor")
        self.assertIn("Rainy", result["reason"])

    def test_thunderstorm_weather(self):
        """Test thunderstorm weather returns indoor activity"""
        result = analyze_weather(
            temperature=25,
            humidity=90,
            wind_speed=10,
            weather="Thunderstorm"
        )
        self.assertEqual(result["activity"], "Indoor Games / Movies")
        self.assertEqual(result["category"], "Indoor")

    def test_snow_weather(self):
        """Test snowy weather returns indoor activity"""
        result = analyze_weather(
            temperature=-2,
            humidity=75,
            wind_speed=4,
            weather="Snow"
        )
        self.assertEqual(result["activity"], "Indoor Activities")
        self.assertEqual(result["category"], "Indoor")
        self.assertIn("snowy", result["reason"].lower())

    def test_high_temperature(self):
        """Test high temperature returns indoor activity"""
        result = analyze_weather(
            temperature=38,
            humidity=40,
            wind_speed=2,
            weather="Clear"
        )
        self.assertEqual(result["activity"], "Indoor Activities")
        self.assertEqual(result["category"], "Indoor")
        self.assertIn("temperature is high", result["reason"].lower())

    def test_high_wind(self):
        """Test high wind speed returns indoor activity"""
        result = analyze_weather(
            temperature=25,
            humidity=60,
            wind_speed=10,
            weather="Clear"
        )
        self.assertEqual(result["activity"], "Indoor Activities")
        self.assertEqual(result["category"], "Indoor")
        self.assertIn("strong wind", result["reason"].lower())

    def test_cool_weather(self):
        """Test cool weather returns mixed activity"""
        result = analyze_weather(
            temperature=15,
            humidity=60,
            wind_speed=3,
            weather="Clear"
        )
        self.assertEqual(result["activity"], "Walking / Indoor Games")
        self.assertEqual(result["category"], "Mixed")
        self.assertIn("cool", result["reason"].lower())

    def test_perfect_outdoor_weather(self):
        """Test perfect weather returns outdoor activity"""
        result = analyze_weather(
            temperature=25,
            humidity=60,
            wind_speed=3,
            weather="Clear"
        )
        self.assertEqual(result["activity"], "Walking / Cycling / Outdoor Sports")
        self.assertEqual(result["category"], "Outdoor")
        self.assertIn("comfortable", result["reason"].lower())

    def test_high_humidity(self):
        """Test high humidity with good temperature returns light outdoor"""
        result = analyze_weather(
            temperature=25,
            humidity=80,
            wind_speed=3,
            weather="Clear"
        )
        self.assertEqual(result["activity"], "Light Outdoor Activity")
        self.assertEqual(result["category"], "Outdoor")
        self.assertIn("humidity", result["reason"].lower())

    def test_cloudy_weather(self):
        """Test cloudy weather returns outdoor activity"""
        result = analyze_weather(
            temperature=20,
            humidity=65,
            wind_speed=3,
            weather="Clouds"
        )
        self.assertEqual(result["activity"], "Walking / Photography")
        self.assertEqual(result["category"], "Outdoor")
        self.assertIn("cloudy", result["reason"].lower())

    def test_case_insensitive_weather(self):
        """Test weather condition is case insensitive"""
        result1 = analyze_weather(20, 60, 3, "rain")
        result2 = analyze_weather(20, 60, 3, "RAIN")
        result3 = analyze_weather(20, 60, 3, "Rain")
        self.assertEqual(result1["activity"], result2["activity"])
        self.assertEqual(result1["activity"], result3["activity"])

    def test_unknown_weather(self):
        """Test unknown weather conditions fall back to default"""
        result = analyze_weather(20, 50, 3, "UnknownWeatherType")
        self.assertEqual(result["activity"], "Indoor / Outdoor Activity")
        self.assertEqual(result["category"], "Mixed")
        self.assertIn("moderate", result["reason"].lower())

    def test_default_case(self):
        """Test default case when no specific conditions match"""
        result = analyze_weather(
            temperature=20,
            humidity=50,
            wind_speed=3,
            weather="Partly Cloudy"
        )
        self.assertEqual(result["activity"], "Indoor / Outdoor Activity")
        self.assertEqual(result["category"], "Mixed")
        self.assertIn("moderate", result["reason"].lower())


# ============================================================
# TEST 2: RULE-BASED ENGINE UNIT TESTS
# ============================================================

class TestRuleBasedEngineUnit(unittest.TestCase):
    """Unit tests for rule-based recommendation engine (server.py)"""
    
    def test_rain_rules(self):
        """Test rain rules"""
        activity, reason = rule_based_recommendation(20, 85, 5, "Rain")
        self.assertEqual(activity, "Indoor Games / Movies")
        self.assertIn("Rainy", reason)
        
        activity, reason = rule_based_recommendation(20, 85, 5, "Thunderstorm")
        self.assertEqual(activity, "Indoor Games / Movies")
        self.assertIn("Rainy", reason)

    def test_snow_rules(self):
        """Test snow rules"""
        activity, reason = rule_based_recommendation(-2, 75, 4, "Snow")
        self.assertEqual(activity, "Indoor Activities")
        self.assertIn("Snowy", reason)

    def test_temperature_rules(self):
        """Test temperature-based rules"""
        # Very hot
        activity, reason = rule_based_recommendation(38, 40, 2, "Clear")
        self.assertEqual(activity, "Indoor Activities")
        self.assertIn("hot", reason.lower())
        
        # Cold
        activity, reason = rule_based_recommendation(10, 60, 3, "Clear")
        self.assertEqual(activity, "Walking / Indoor Games")
        self.assertIn("Cool", reason)
        
        # Perfect
        activity, reason = rule_based_recommendation(25, 60, 3, "Clear")
        self.assertEqual(activity, "Walking / Cycling / Outdoor Sports")
        self.assertIn("Perfect", reason)

    def test_wind_rules(self):
        """Test wind-based rules"""
        activity, reason = rule_based_recommendation(25, 60, 10, "Clear")
        self.assertEqual(activity, "Indoor Activities")
        self.assertIn("Strong winds", reason)

    def test_humidity_rules(self):
        """Test humidity-based rules"""
        # High humidity
        activity, reason = rule_based_recommendation(25, 80, 3, "Clear")
        self.assertEqual(activity, "Light Outdoor Activity")
        self.assertIn("High humidity", reason)
        
        # Low humidity
        activity, reason = rule_based_recommendation(25, 60, 3, "Clear")
        self.assertEqual(activity, "Walking / Cycling / Outdoor Sports")
        self.assertIn("Perfect", reason)

    def test_cloudy_rules(self):
        """Test cloudy weather rules"""
        activity, reason = rule_based_recommendation(20, 65, 3, "Clouds")
        self.assertEqual(activity, "Walking / Photography")
        self.assertIn("Cloudy", reason)

    def test_default_case(self):
        """Test default case"""
        activity, reason = rule_based_recommendation(20, 50, 3, "Mist")
        self.assertEqual(activity, "Indoor / Outdoor Activity")
        self.assertIn("moderate", reason.lower())


# ============================================================
# TEST 3: FLASK API UNIT TESTS
# ============================================================

class TestFlaskAPIUnit(unittest.TestCase):
    """Unit tests for Flask API server"""
    
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_health_endpoint(self):
        """Test health check endpoint"""
        response = self.app.get('/health')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'healthy')
        self.assertIn('model_loaded', data)

    def test_home_endpoint(self):
        """Test home endpoint"""
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['service'], 'Weather Activity Recommendation System')
        self.assertEqual(data['status'], 'running')

    def test_weather_analysis_post(self):
        """Test weather analysis POST endpoint"""
        payload = {
            "temperature": 25,
            "humidity": 60,
            "wind_speed": 3,
            "weather": "Clear"
        }
        response = self.app.post('/webhook/weather', 
                                json=payload,
                                content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertIn('activity', data)
        self.assertEqual(data['method'], 'Rule-Based')

    def test_weather_analysis_get(self):
        """Test weather analysis GET endpoint returns info"""
        response = self.app.get('/webhook/weather')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('message', data)
        self.assertIn('example', data)

    def test_city_weather_missing_city(self):
        """Test city weather with missing city parameter"""
        response = self.app.post('/webhook/city', json={})
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertEqual(data['error'], 'City name is required')

    def test_batch_analysis_empty(self):
        """Test batch analysis with empty records"""
        payload = {"records": []}
        response = self.app.post('/webhook/batch', 
                                json=payload,
                                content_type='application/json')
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertEqual(data['error'], 'No records provided')


# ============================================================
# TEST 4: EDGE CASES AND ERROR HANDLING
# ============================================================

class TestEdgeCasesUnit(unittest.TestCase):
    """Unit tests for edge cases and error handling"""
    
    def test_extreme_temperatures(self):
        """Test extreme temperature values"""
        # Very cold
        result = analyze_weather(-50, 60, 3, "Clear")
        self.assertEqual(result["activity"], "Walking / Indoor Games")
        
        # Very hot
        result = analyze_weather(60, 60, 3, "Clear")
        self.assertEqual(result["activity"], "Indoor Activities")

    def test_extreme_humidity(self):
        """Test extreme humidity values"""
        # 0% humidity
        result = analyze_weather(25, 0, 3, "Clear")
        self.assertEqual(result["activity"], "Walking / Cycling / Outdoor Sports")
        
        # 100% humidity
        result = analyze_weather(25, 100, 3, "Clear")
        self.assertEqual(result["activity"], "Light Outdoor Activity")

    def test_extreme_wind_speed(self):
        """Test extreme wind speed values"""
        # 0 wind
        result = analyze_weather(25, 60, 0, "Clear")
        self.assertEqual(result["activity"], "Walking / Cycling / Outdoor Sports")
        
        # Very high wind
        result = analyze_weather(25, 60, 100, "Clear")
        self.assertEqual(result["activity"], "Indoor Activities")

    def test_empty_weather_string(self):
        """Test empty weather string"""
        result = analyze_weather(25, 60, 3, "")
        self.assertEqual(result["activity"], "Indoor / Outdoor Activity")
        self.assertEqual(result["category"], "Mixed")

    def test_none_weather(self):
        """Test None weather"""
        result = analyze_weather(25, 60, 3, None)
        self.assertEqual(result["activity"], "Indoor / Outdoor Activity")
        self.assertEqual(result["category"], "Mixed")


# ============================================================
# TEST 5: INTEGRATION TESTS
# ============================================================

class TestIntegrationUnit(unittest.TestCase):
    """Integration unit tests"""
    
    def test_ai_to_rule_consistency(self):
        """Test that AI engine and rule-based engine are consistent"""
        test_scenarios = [
            (20, 85, 5, "Rain"),
            (-2, 75, 4, "Snow"),
            (38, 40, 2, "Clear"),
            (25, 60, 10, "Clear"),
            (15, 60, 3, "Clear"),
            (25, 60, 3, "Clear"),
            (25, 80, 3, "Clear"),
            (20, 65, 3, "Clouds")
        ]
        
        for temp, hum, wind, weather in test_scenarios:
            with self.subTest(temp=temp, weather=weather):
                ai_result = analyze_weather(temp, hum, wind, weather)
                rule_activity, _ = rule_based_recommendation(temp, hum, wind, weather)
                self.assertEqual(ai_result['activity'], rule_activity)

    def test_full_workflow_rain(self):
        """Test full workflow with rain"""
        result = analyze_weather(20, 85, 5, "Rain")
        self.assertEqual(result["activity"], "Indoor Games / Movies")
        self.assertEqual(result["category"], "Indoor")
        self.assertIn("Rainy", result["reason"])

    def test_full_workflow_snow(self):
        """Test full workflow with snow"""
        result = analyze_weather(-2, 75, 4, "Snow")
        self.assertEqual(result["activity"], "Indoor Activities")
        self.assertEqual(result["category"], "Indoor")
        self.assertIn("snowy", result["reason"].lower())

    def test_full_workflow_perfect(self):
        """Test full workflow with perfect weather"""
        result = analyze_weather(25, 60, 3, "Clear")
        self.assertEqual(result["activity"], "Walking / Cycling / Outdoor Sports")
        self.assertEqual(result["category"], "Outdoor")
        self.assertIn("comfortable", result["reason"].lower())


# ============================================================
# TEST 6: N8N INTEGRATION TESTS (if available)
# ============================================================

if N8N_AVAILABLE:
    class TestN8NIntegrationUnit(unittest.TestCase):
        """Unit tests for N8NIntegration class"""
        
        def setUp(self):
            self.integration = N8NIntegration()

        @patch('n8n.requests.post')
        def test_get_recommendation_from_n8n_success(self, mock_post):
            """Test successful n8n recommendation"""
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                'recommendation': {
                    'activity': 'Outdoor Sports',
                    'reason': 'Perfect weather for sports',
                    'method': 'n8n-ai'
                }
            }
            mock_post.return_value = mock_response

            weather_data = {
                'temperature': 25,
                'humidity': 60,
                'wind_speed': 3,
                'weather': 'Clear'
            }
            result = self.integration.get_recommendation_from_n8n(weather_data)
            self.assertIsNotNone(result)
            self.assertEqual(result['activity'], 'Outdoor Sports')

        @patch('n8n.requests.post')
        def test_get_recommendation_from_n8n_failure(self, mock_post):
            """Test n8n failure returns None"""
            mock_post.side_effect = Exception('Connection error')
            
            weather_data = {
                'temperature': 25,
                'humidity': 60,
                'wind_speed': 3,
                'weather': 'Clear'
            }
            result = self.integration.get_recommendation_from_n8n(weather_data)
            self.assertIsNone(result)

        @patch.object(N8NIntegration, 'get_recommendation_from_n8n')
        def test_analyze_weather_without_n8n(self, mock_n8n):
            """Test analyze_weather with n8n unavailable (fallback)"""
            mock_n8n.return_value = None
            
            result = self.integration.analyze_weather(25, 60, 3, 'Clear')
            self.assertFalse(result['n8n_available'])
            self.assertIn('activity', result)


# ============================================================
# RUN TESTS
# ============================================================

def run_tests():
    """Run all unit tests"""
    # Load tests
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test cases
    suite.addTests(loader.loadTestsFromTestCase(TestAIEngineUnit))
    suite.addTests(loader.loadTestsFromTestCase(TestRuleBasedEngineUnit))
    suite.addTests(loader.loadTestsFromTestCase(TestFlaskAPIUnit))
    suite.addTests(loader.loadTestsFromTestCase(TestEdgeCasesUnit))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegrationUnit))
    
    if N8N_AVAILABLE:
        suite.addTests(loader.loadTestsFromTestCase(TestN8NIntegrationUnit))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 70)
    print("  TEST SUMMARY")
    print("=" * 70)
    print(f"  Total tests:    {result.testsRun}")
    print(f"  ✅ Passed:       {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"  ❌ Failures:     {len(result.failures)}")
    print(f"  ⚠️ Errors:       {len(result.errors)}")
    print("=" * 70)
    
    if result.wasSuccessful():
        print("  ✅ ALL TESTS PASSED!")
        print("  🎉 System is ready!")
    else:
        print("  ❌ SOME TESTS FAILED")
        print("  🔧 Please fix the issues.")
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
