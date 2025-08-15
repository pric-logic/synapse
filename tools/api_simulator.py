"""
APISimulator: Simulates 15+ API endpoints for Project Synapse
Provides realistic data for demonstration and testing
"""

import asyncio
import time
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import random
import json
from faker import Faker

fake = Faker()


class APISimulator:
    """
    Simulates various API endpoints for Project Synapse
    Provides realistic data for demonstration purposes
    """
    
    def __init__(self):
        self.fake = Faker()
        self.api_calls = 0
        self.response_times = []
        
        # Initialize simulated data stores
        self._initialize_data_stores()
    
    def _initialize_data_stores(self):
        """Initialize simulated data stores"""
        # Customer database
        self.customers = {}
        for i in range(1000):
            customer_id = f"customer_{i}"
            self.customers[customer_id] = {
                'id': customer_id,
                'name': fake.name(),
                'email': fake.email(),
                'phone': fake.phone_number(),
                'address': fake.address(),
                'lifetime_orders': random.randint(1, 100),
                'total_spent': random.uniform(50, 2000),
                'loyalty_tier': random.choice(['bronze', 'silver', 'gold', 'platinum']),
                'last_order': fake.date_time_between(start_date='-30d', end_date='now'),
                'preferences': random.sample(['fast_delivery', 'eco_friendly', 'premium_quality'], 
                                          random.randint(1, 3))
            }
        
        # Driver database
        self.drivers = {}
        for i in range(500):
            driver_id = f"driver_{i}"
            self.drivers[driver_id] = {
                'id': driver_id,
                'name': fake.name(),
                'vehicle_type': random.choice(['motorcycle', 'car', 'bicycle']),
                'rating': random.uniform(4.0, 5.0),
                'experience_years': random.randint(1, 10),
                'current_location': {
                    'lat': 1.3521 + random.uniform(-0.02, 0.02),
                    'lng': 103.8198 + random.uniform(-0.02, 0.02)
                },
                'status': random.choice(['available', 'busy', 'offline']),
                'last_active': fake.date_time_between(start_date='-1d', end_date='now')
            }
        
        # Merchant database
        self.merchants = {}
        for i in range(200):
            merchant_id = f"merchant_{i}"
            self.merchants[merchant_id] = {
                'id': merchant_id,
                'name': fake.company(),
                'cuisine_type': random.choice(['chinese', 'indian', 'western', 'japanese', 'thai', 'korean']),
                'rating': random.uniform(3.5, 5.0),
                'preparation_time': random.randint(15, 45),
                'status': random.choice(['open', 'busy', 'closed']),
                'location': {
                    'lat': 1.3521 + random.uniform(-0.02, 0.02),
                    'lng': 103.8198 + random.uniform(-0.02, 0.02)
                }
            }
    
    async def check_traffic(self) -> Dict[str, Any]:
        """Simulate traffic API call"""
        start_time = time.time()
        await asyncio.sleep(random.uniform(0.1, 0.3))  # Simulate API delay
        
        response = {
            'congestion_level': random.uniform(0.1, 0.9),
            'incidents': random.randint(0, 5),
            'average_speed': random.uniform(10, 40),
            'affected_areas': random.randint(1, 8),
            'timestamp': datetime.now().isoformat(),
            'data_source': 'traffic_management_system'
        }
        
        self._record_api_call('check_traffic', time.time() - start_time)
        return response
    
    async def get_merchant_status(self, merchant_id: str = None) -> Dict[str, Any]:
        """Simulate merchant status API call"""
        start_time = time.time()
        await asyncio.sleep(random.uniform(0.05, 0.2))
        
        if merchant_id is None:
            merchant_id = random.choice(list(self.merchants.keys()))
        
        merchant = self.merchants.get(merchant_id, {})
        
        response = {
            'merchant_id': merchant_id,
            'status': merchant.get('status', 'unknown'),
            'preparation_time': merchant.get('preparation_time', 30),
            'queue_length': random.randint(0, 20),
            'last_updated': datetime.now().isoformat(),
            'operational_hours': '08:00-22:00'
        }
        
        self._record_api_call('get_merchant_status', time.time() - start_time)
        return response
    
    async def analyze_customer_sentiment(self, customer_id: str = None) -> Dict[str, Any]:
        """Simulate customer sentiment analysis API call"""
        start_time = time.time()
        await asyncio.sleep(random.uniform(0.1, 0.4))
        
        if customer_id is None:
            customer_id = random.choice(list(self.customers.keys()))
        
        customer = self.customers.get(customer_id, {})
        
        # Generate sentiment based on customer data
        base_sentiment = 0.7
        if customer.get('loyalty_tier') == 'platinum':
            base_sentiment += 0.2
        elif customer.get('loyalty_tier') == 'gold':
            base_sentiment += 0.1
        
        # Add some variation
        sentiment_score = max(0.0, min(1.0, base_sentiment + random.uniform(-0.2, 0.2)))
        
        response = {
            'customer_id': customer_id,
            'sentiment_score': sentiment_score,
            'sentiment_label': self._get_sentiment_label(sentiment_score),
            'confidence': random.uniform(0.8, 0.95),
            'factors': self._get_sentiment_factors(sentiment_score),
            'last_analysis': datetime.now().isoformat()
        }
        
        self._record_api_call('analyze_customer_sentiment', time.time() - start_time)
        return response
    
    async def predict_weather(self, location: Dict[str, float] = None) -> Dict[str, Any]:
        """Simulate weather prediction API call"""
        start_time = time.time()
        await asyncio.sleep(random.uniform(0.2, 0.5))
        
        if location is None:
            location = {'lat': 1.3521, 'lng': 103.8198}
        
        weather_conditions = ['clear', 'cloudy', 'rain', 'storm', 'windy']
        current_weather = random.choice(weather_conditions)
        
        response = {
            'location': location,
            'current_condition': current_weather,
            'temperature': random.uniform(20, 35),
            'humidity': random.uniform(0.4, 0.9),
            'wind_speed': random.uniform(0, 25),
            'visibility': random.uniform(5, 20),
            'precipitation_probability': random.uniform(0, 1.0),
            'forecast_3h': self._generate_weather_forecast(3),
            'forecast_6h': self._generate_weather_forecast(6),
            'timestamp': datetime.now().isoformat()
        }
        
        self._record_api_call('predict_weather', time.time() - start_time)
        return response
    
    async def calculate_driver_stress(self, driver_id: str = None) -> Dict[str, Any]:
        """Simulate driver stress calculation API call"""
        start_time = time.time()
        await asyncio.sleep(random.uniform(0.1, 0.3))
        
        if driver_id is None:
            driver_id = random.choice(list(self.drivers.keys()))
        
        driver = self.drivers.get(driver_id, {})
        
        # Calculate stress based on various factors
        base_stress = 0.3
        if driver.get('status') == 'busy':
            base_stress += 0.2
        if driver.get('rating', 5.0) < 4.5:
            base_stress += 0.1
        
        # Add environmental factors
        current_hour = datetime.now().hour
        if 7 <= current_hour <= 9 or 17 <= current_hour <= 19:
            base_stress += 0.15  # Rush hour
        
        stress_level = min(1.0, base_stress + random.uniform(-0.1, 0.1))
        
        response = {
            'driver_id': driver_id,
            'stress_level': stress_level,
            'stress_factors': self._get_stress_factors(stress_level),
            'recommendations': self._get_stress_recommendations(stress_level),
            'last_updated': datetime.now().isoformat(),
            'confidence': random.uniform(0.8, 0.95)
        }
        
        self._record_api_call('calculate_driver_stress', time.time() - start_time)
        return response
    
    async def optimize_route(self, start_location: Dict[str, float], 
                           end_location: Dict[str, float], 
                           constraints: Dict[str, Any] = None) -> Dict[str, Any]:
        """Simulate route optimization API call"""
        start_time = time.time()
        await asyncio.sleep(random.uniform(0.3, 0.8))
        
        if constraints is None:
            constraints = {}
        
        # Calculate distance
        distance = self._calculate_distance(start_location, end_location)
        
        # Generate route options
        route_options = []
        for i in range(3):
            route = {
                'route_id': f"route_{i}",
                'distance_km': distance * (1 + random.uniform(-0.1, 0.2)),
                'estimated_time_minutes': distance * 2 + random.uniform(-5, 10),
                'traffic_level': random.uniform(0.1, 0.8),
                'toll_roads': random.randint(0, 2),
                'fuel_efficiency': random.uniform(0.7, 1.0)
            }
            route_options.append(route)
        
        # Sort by estimated time
        route_options.sort(key=lambda x: x['estimated_time_minutes'])
        
        response = {
            'start_location': start_location,
            'end_location': end_location,
            'route_options': route_options,
            'recommended_route': route_options[0]['route_id'],
            'optimization_criteria': constraints.get('criteria', 'fastest'),
            'timestamp': datetime.now().isoformat()
        }
        
        self._record_api_call('optimize_route', time.time() - start_time)
        return response
    
    async def assess_customer_ltv(self, customer_id: str = None) -> Dict[str, Any]:
        """Simulate customer lifetime value assessment API call"""
        start_time = time.time()
        await asyncio.sleep(random.uniform(0.2, 0.5))
        
        if customer_id is None:
            customer_id = random.choice(list(self.customers.keys()))
        
        customer = self.customers.get(customer_id, {})
        
        # Calculate LTV based on customer data
        base_ltv = customer.get('total_spent', 500)
        loyalty_multiplier = {'bronze': 1.0, 'silver': 1.2, 'gold': 1.5, 'platinum': 2.0}
        multiplier = loyalty_multiplier.get(customer.get('loyalty_tier', 'bronze'), 1.0)
        
        ltv = base_ltv * multiplier * random.uniform(0.8, 1.2)
        
        response = {
            'customer_id': customer_id,
            'current_ltv': ltv,
            'predicted_ltv_30d': ltv * random.uniform(0.9, 1.3),
            'predicted_ltv_90d': ltv * random.uniform(0.8, 1.5),
            'retention_probability': random.uniform(0.6, 0.95),
            'recommendations': self._get_ltv_recommendations(ltv, customer),
            'last_updated': datetime.now().isoformat()
        }
        
        self._record_api_call('assess_customer_ltv', time.time() - start_time)
        return response
    
    async def check_market_conditions(self, location: Dict[str, float] = None) -> Dict[str, Any]:
        """Simulate market conditions API call"""
        start_time = time.time()
        await asyncio.sleep(random.uniform(0.1, 0.4))
        
        if location is None:
            location = {'lat': 1.3521, 'lng': 103.8198}
        
        response = {
            'location': location,
            'demand_level': random.uniform(0.3, 1.0),
            'competition_density': random.uniform(0.2, 0.9),
            'price_sensitivity': random.uniform(0.4, 0.8),
            'market_trend': random.choice(['growing', 'stable', 'declining']),
            'peak_hours': ['11:00-14:00', '18:00-21:00'],
            'seasonal_factors': self._get_seasonal_factors(),
            'timestamp': datetime.now().isoformat()
        }
        
        self._record_api_call('check_market_conditions', time.time() - start_time)
        return response
    
    async def analyze_traffic_camera(self, camera_id: str = None) -> Dict[str, Any]:
        """Simulate traffic camera analysis API call"""
        start_time = time.time()
        await asyncio.sleep(random.uniform(0.2, 0.6))
        
        if camera_id is None:
            camera_id = f"camera_{random.randint(1, 50)}"
        
        response = {
            'camera_id': camera_id,
            'vehicle_count': random.randint(20, 150),
            'congestion_level': random.uniform(0.2, 0.9),
            'incident_detected': random.choice([True, False]),
            'road_conditions': random.choice(['clear', 'wet', 'congested']),
            'average_speed': random.uniform(5, 35),
            'image_quality': random.choice(['excellent', 'good', 'fair']),
            'analysis_confidence': random.uniform(0.85, 0.98),
            'timestamp': datetime.now().isoformat()
        }
        
        self._record_api_call('analyze_traffic_camera', time.time() - start_time)
        return response
    
    async def process_driver_voice(self, audio_data: str = None) -> Dict[str, Any]:
        """Simulate driver voice processing API call"""
        start_time = time.time()
        await asyncio.sleep(random.uniform(0.3, 0.7))
        
        if audio_data is None:
            audio_data = "base64_encoded_audio_sample"
        
        response = {
            'audio_quality': random.choice(['excellent', 'good', 'fair', 'poor']),
            'speech_clarity': random.uniform(0.6, 1.0),
            'emotion_detected': random.choice(['calm', 'concerned', 'frustrated', 'excited']),
            'stress_level': random.uniform(0.2, 0.9),
            'language': 'english',
            'confidence': random.uniform(0.8, 0.95),
            'transcription': "Driver reporting traffic conditions on main road",
            'timestamp': datetime.now().isoformat()
        }
        
        self._record_api_call('process_driver_voice', time.time() - start_time)
        return response
    
    async def predict_demand_surge(self, location: Dict[str, float] = None, 
                                  time_horizon: int = 24) -> Dict[str, Any]:
        """Simulate demand surge prediction API call"""
        start_time = time.time()
        await asyncio.sleep(random.uniform(0.4, 0.8))
        
        if location is None:
            location = {'lat': 1.3521, 'lng': 103.8198}
        
        # Generate demand prediction
        base_demand = random.uniform(0.5, 1.0)
        surge_factor = random.uniform(1.0, 2.5)
        
        response = {
            'location': location,
            'time_horizon_hours': time_horizon,
            'current_demand': base_demand,
            'predicted_demand': base_demand * surge_factor,
            'surge_probability': random.uniform(0.3, 0.8),
            'peak_time': self._predict_peak_time(),
            'factors': self._get_demand_factors(),
            'confidence': random.uniform(0.7, 0.9),
            'timestamp': datetime.now().isoformat()
        }
        
        self._record_api_call('predict_demand_surge', time.time() - start_time)
        return response
    
    async def calculate_compensation(self, incident_type: str, 
                                   severity: float, 
                                   customer_tier: str = 'standard') -> Dict[str, Any]:
        """Simulate compensation calculation API call"""
        start_time = time.time()
        await asyncio.sleep(random.uniform(0.1, 0.3))
        
        # Base compensation by incident type
        base_compensation = {
            'delivery_delay': 10,
            'food_quality': 15,
            'driver_behavior': 20,
            'technical_issue': 5,
            'weather_delay': 8
        }
        
        base_amount = base_compensation.get(incident_type, 10)
        
        # Adjust by severity
        severity_multiplier = 0.5 + (severity * 0.5)  # 0.5 to 1.0
        
        # Adjust by customer tier
        tier_multiplier = {
            'standard': 1.0,
            'silver': 1.2,
            'gold': 1.5,
            'platinum': 2.0
        }
        
        final_compensation = base_amount * severity_multiplier * tier_multiplier.get(customer_tier, 1.0)
        
        response = {
            'incident_type': incident_type,
            'severity': severity,
            'customer_tier': customer_tier,
            'base_compensation': base_amount,
            'final_compensation': round(final_compensation, 2),
            'calculation_factors': {
                'severity_multiplier': round(severity_multiplier, 2),
                'tier_multiplier': tier_multiplier.get(customer_tier, 1.0)
            },
            'timestamp': datetime.now().isoformat()
        }
        
        self._record_api_call('calculate_compensation', time.time() - start_time)
        return response
    
    async def assess_brand_impact(self, action_type: str, 
                                 customer_tier: str = 'standard',
                                 incident_severity: float = 0.5) -> Dict[str, Any]:
        """Simulate brand impact assessment API call"""
        start_time = time.time()
        await asyncio.sleep(random.uniform(0.2, 0.5))
        
        # Base brand impact scores
        base_impact = {
            'compensation': 0.3,
            'apology': 0.2,
            'priority_service': 0.4,
            'loyalty_rewards': 0.5,
            'quality_improvement': 0.6
        }
        
        base_score = base_impact.get(action_type, 0.3)
        
        # Adjust by customer tier
        tier_impact = {
            'standard': 1.0,
            'silver': 1.3,
            'gold': 1.6,
            'platinum': 2.0
        }
        
        # Adjust by severity (higher severity = higher impact)
        severity_impact = 0.5 + (incident_severity * 0.5)
        
        final_impact = base_score * tier_impact.get(customer_tier, 1.0) * severity_impact
        
        response = {
            'action_type': action_type,
            'customer_tier': customer_tier,
            'incident_severity': incident_severity,
            'brand_impact_score': round(final_impact, 3),
            'impact_category': self._categorize_brand_impact(final_impact),
            'recommendations': self._get_brand_impact_recommendations(final_impact),
            'timestamp': datetime.now().isoformat()
        }
        
        self._record_api_call('assess_brand_impact', time.time() - start_time)
        return response
    
    async def optimize_fleet_position(self, current_deliveries: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Simulate fleet optimization API call"""
        start_time = time.time()
        await asyncio.sleep(random.uniform(0.5, 1.0))
        
        if current_deliveries is None:
            current_deliveries = []
        
        num_deliveries = len(current_deliveries) if current_deliveries else random.randint(5, 20)
        
        response = {
            'total_deliveries': num_deliveries,
            'optimization_score': random.uniform(0.6, 0.95),
            'recommended_repositioning': random.randint(0, 5),
            'estimated_efficiency_gain': random.uniform(0.1, 0.3),
            'fuel_savings_km': random.uniform(5, 25),
            'time_savings_minutes': random.uniform(10, 45),
            'optimization_algorithm': 'genetic_algorithm_v3',
            'timestamp': datetime.now().isoformat()
        }
        
        self._record_api_call('optimize_fleet_position', time.time() - start_time)
        return response
    
    async def generate_alternatives(self, scenario_type: str, 
                                  current_solution: Dict[str, Any] = None) -> Dict[str, Any]:
        """Simulate alternative solution generation API call"""
        start_time = time.time()
        await asyncio.sleep(random.uniform(0.3, 0.7))
        
        alternatives = []
        for i in range(random.randint(2, 5)):
            alternative = {
                'alternative_id': f"alt_{i}",
                'approach': f"alternative_approach_{i}",
                'estimated_cost': random.uniform(10, 100),
                'estimated_benefit': random.uniform(20, 150),
                'implementation_time': random.randint(1, 7),
                'risk_level': random.choice(['low', 'medium', 'high']),
                'confidence': random.uniform(0.6, 0.9)
            }
            alternatives.append(alternative)
        
        response = {
            'scenario_type': scenario_type,
            'alternatives_generated': len(alternatives),
            'alternatives': alternatives,
            'recommended_alternative': alternatives[0]['alternative_id'] if alternatives else None,
            'generation_algorithm': 'multi_objective_optimization',
            'timestamp': datetime.now().isoformat()
        }
        
        self._record_api_call('generate_alternatives', time.time() - start_time)
        return response
    
    def _record_api_call(self, api_name: str, response_time: float):
        """Record API call statistics"""
        self.api_calls += 1
        self.response_times.append(response_time)
        
        # Keep only last 1000 response times
        if len(self.response_times) > 1000:
            self.response_times = self.response_times[-1000:]
    
    def get_api_stats(self) -> Dict[str, Any]:
        """Get API simulation statistics"""
        if not self.response_times:
            return {
                'total_calls': 0, 
                'average_response_time': 0,
                'min_response_time': 0,
                'max_response_time': 0
            }
        
        return {
            'total_calls': self.api_calls,
            'average_response_time': sum(self.response_times) / len(self.response_times),
            'min_response_time': min(self.response_times),
            'max_response_time': max(self.response_times)
        }
    
    # Helper methods for generating realistic data
    def _get_sentiment_label(self, score: float) -> str:
        if score >= 0.8:
            return 'very_positive'
        elif score >= 0.6:
            return 'positive'
        elif score >= 0.4:
            return 'neutral'
        elif score >= 0.2:
            return 'negative'
        else:
            return 'very_negative'
    
    def _get_sentiment_factors(self, score: float) -> List[str]:
        factors = []
        if score > 0.7:
            factors.extend(['high_loyalty', 'frequent_orders', 'positive_feedback'])
        elif score < 0.3:
            factors.extend(['recent_complaints', 'delivery_issues', 'service_quality'])
        else:
            factors.extend(['mixed_experience', 'moderate_engagement'])
        return factors
    
    def _generate_weather_forecast(self, hours: int) -> List[Dict[str, Any]]:
        forecast = []
        for i in range(hours):
            forecast.append({
                'hour': i + 1,
                'condition': random.choice(['clear', 'cloudy', 'rain', 'windy']),
                'temperature': random.uniform(20, 35),
                'precipitation_probability': random.uniform(0, 0.8)
            })
        return forecast
    
    def _get_stress_factors(self, stress_level: float) -> List[str]:
        factors = []
        if stress_level > 0.7:
            factors.extend(['high_traffic', 'time_pressure', 'customer_demands'])
        elif stress_level > 0.5:
            factors.extend(['moderate_congestion', 'schedule_tightness'])
        else:
            factors.extend(['smooth_operations', 'good_conditions'])
        return factors
    
    def _get_stress_recommendations(self, stress_level: float) -> List[str]:
        recommendations = []
        if stress_level > 0.8:
            recommendations.extend(['immediate_break', 'route_change', 'support_call'])
        elif stress_level > 0.6:
            recommendations.extend(['short_break', 'stress_management', 'peer_support'])
        else:
            recommendations.extend(['maintain_current_pace', 'regular_check_ins'])
        return recommendations
    
    def _calculate_distance(self, start: Dict[str, float], end: Dict[str, float]) -> float:
        """Calculate approximate distance between two points"""
        import math
        lat1, lng1 = start['lat'], start['lng']
        lat2, lng2 = end['lat'], end['lng']
        
        # Simple distance calculation (not accurate for real-world use)
        return math.sqrt((lat2 - lat1)**2 + (lng2 - lng1)**2) * 111000  # Rough km conversion
    
    def _get_ltv_recommendations(self, ltv: float, customer: Dict[str, Any]) -> List[str]:
        recommendations = []
        if ltv > 1000:
            recommendations.extend(['premium_service', 'exclusive_offers', 'priority_support'])
        elif ltv > 500:
            recommendations.extend(['loyalty_program', 'personalized_offers', 'early_access'])
        else:
            recommendations.extend(['engagement_campaigns', 'referral_programs', 'value_offers'])
        return recommendations
    
    def _get_seasonal_factors(self) -> List[str]:
        current_month = datetime.now().month
        if current_month in [12, 1, 2]:
            return ['holiday_season', 'increased_demand', 'weather_impact']
        elif current_month in [6, 7, 8]:
            return ['summer_peak', 'outdoor_activities', 'vacation_season']
        else:
            return ['regular_season', 'stable_demand']
    
    def _predict_peak_time(self) -> str:
        peak_times = ['11:00-13:00', '18:00-20:00', '12:00-14:00', '19:00-21:00']
        return random.choice(peak_times)
    
    def _get_demand_factors(self) -> List[str]:
        factors = ['weather_conditions', 'local_events', 'promotional_offers', 'competitor_activity']
        return random.sample(factors, random.randint(2, 4))
    
    def _categorize_brand_impact(self, impact_score: float) -> str:
        if impact_score >= 0.8:
            return 'very_positive'
        elif impact_score >= 0.6:
            return 'positive'
        elif impact_score >= 0.4:
            return 'neutral'
        elif impact_score >= 0.2:
            return 'negative'
        else:
            return 'very_negative'
    
    def _get_brand_impact_recommendations(self, impact_score: float) -> List[str]:
        recommendations = []
        if impact_score > 0.7:
            recommendations.extend(['amplify_positive_actions', 'share_success_stories', 'reward_team'])
        elif impact_score < 0.3:
            recommendations.extend(['immediate_damage_control', 'customer_outreach', 'process_improvement'])
        else:
            recommendations.extend(['monitor_impact', 'gather_feedback', 'continuous_improvement'])
        return recommendations 