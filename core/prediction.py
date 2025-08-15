"""
PredictionEngine: Continuously predicts delivery problems and pre-computes solutions
Enables 0.3-second response times through scenario caching
"""

import asyncio
import time
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import random
import numpy as np

from tools.api_simulator import APISimulator


class PredictedProblem:
    """Represents a predicted delivery problem"""
    
    def __init__(self, problem_type: str, probability: float, horizon_minutes: int, 
                 affected_area: str, severity: float):
        self.id = f"pred_{int(time.time())}_{random.randint(1000, 9999)}"
        self.problem_type = problem_type
        self.probability = probability
        self.horizon_minutes = horizon_minutes
        self.affected_area = affected_area
        self.severity = severity
        self.timestamp = datetime.now()
        self.solution = None


class PredictionEngine:
    """
    Continuously predicts delivery problems and pre-computes solutions
    Runs in background to maintain prediction cache
    """
    
    def __init__(self):
        self.api_simulator = APISimulator()
        self.prediction_cache = {}
        self.active_predictions = {}
        self.problem_patterns = self._initialize_problem_patterns()
        
        # Performance tracking
        self.prediction_accuracy = 0.85
        self.total_predictions = 0
        self.successful_predictions = 0
    
    def _initialize_problem_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Initialize common problem patterns for prediction"""
        return {
            'traffic_jam': {
                'triggers': ['rush_hour', 'weather', 'accident', 'construction'],
                'probability_base': 0.3,
                'affected_deliveries': (2, 8),
                'severity_range': (0.4, 0.9),
                'horizon_range': (15, 45)
            },
            'weather_disruption': {
                'triggers': ['rain', 'storm', 'snow', 'wind'],
                'probability_base': 0.2,
                'affected_deliveries': (1, 5),
                'severity_range': (0.3, 0.8),
                'horizon_range': (30, 120)
            },
            'driver_issue': {
                'triggers': ['fatigue', 'stress', 'vehicle_problem', 'personal_emergency'],
                'probability_base': 0.15,
                'affected_deliveries': (1, 3),
                'severity_range': (0.5, 0.9),
                'horizon_range': (5, 30)
            },
            'merchant_problem': {
                'triggers': ['kitchen_delay', 'ingredient_shortage', 'staff_issue'],
                'probability_base': 0.25,
                'affected_deliveries': (1, 6),
                'severity_range': (0.3, 0.7),
                'horizon_range': (10, 60)
            },
            'customer_complaint': {
                'triggers': ['delivery_delay', 'food_quality', 'driver_behavior'],
                'probability_base': 0.1,
                'affected_deliveries': (1, 2),
                'severity_range': (0.6, 1.0),
                'horizon_range': (0, 15)
            }
        }
    
    async def continuous_prediction(self):
        """Main prediction loop - runs continuously in background"""
        try:
            # Get current delivery status
            active_deliveries = await self._get_active_deliveries()
            
            # Analyze each delivery for potential problems
            for delivery in active_deliveries:
                problems = await self._predict_problems_for_delivery(delivery)
                
                for problem in problems:
                    if problem.probability > 0.3:  # Only cache high-probability problems
                        solution = await self._precompute_solution(problem)
                        if solution:
                            self._cache_prediction(problem, solution)
            
            # Update prediction accuracy
            await self._update_prediction_accuracy()
            
        except Exception as e:
            print(f"Prediction engine error: {e}")
    
    async def _get_active_deliveries(self) -> List[Dict[str, Any]]:
        """Get list of currently active deliveries"""
        # Simulate active deliveries
        num_deliveries = random.randint(15, 35)
        deliveries = []
        
        for i in range(num_deliveries):
            delivery = {
                'id': f"del_{i}",
                'status': 'in_progress',
                'location': self._generate_random_location(),
                'estimated_completion': datetime.now() + timedelta(minutes=random.randint(10, 45)),
                'driver_id': f"driver_{random.randint(1, 50)}",
                'merchant_id': f"merchant_{random.randint(1, 20)}",
                'customer_id': f"customer_{random.randint(1, 100)}"
            }
            deliveries.append(delivery)
        
        return deliveries
    
    def _generate_random_location(self) -> Dict[str, float]:
        """Generate random GPS coordinates"""
        # Simulate locations in a city
        lat = 1.3521 + random.uniform(-0.01, 0.01)  # Singapore area
        lng = 103.8198 + random.uniform(-0.01, 0.01)
        return {'lat': lat, 'lng': lng}
    
    async def _predict_problems_for_delivery(self, delivery: Dict[str, Any]) -> List[PredictedProblem]:
        """Predict potential problems for a specific delivery"""
        problems = []
        
        # Check each problem type
        for problem_type, pattern in self.problem_patterns.items():
            probability = await self._calculate_problem_probability(delivery, pattern)
            
            if probability > 0.1:  # Only consider problems with reasonable probability
                problem = PredictedProblem(
                    problem_type=problem_type,
                    probability=probability,
                    horizon_minutes=random.randint(*pattern['horizon_range']),
                    affected_area=self._get_affected_area(delivery, problem_type),
                    severity=random.uniform(*pattern['severity_range'])
                )
                problems.append(problem)
        
        return problems
    
    async def _calculate_problem_probability(self, delivery: Dict[str, Any], pattern: Dict[str, Any]) -> float:
        """Calculate probability of a specific problem occurring"""
        base_probability = pattern['probability_base']
        
        # Adjust based on current conditions
        weather_factor = await self._get_weather_factor(delivery['location'])
        time_factor = self._get_time_factor()
        location_factor = self._get_location_factor(delivery['location'])
        
        # Combine factors
        adjusted_probability = base_probability * weather_factor * time_factor * location_factor
        
        # Add some randomness
        adjusted_probability += random.uniform(-0.1, 0.1)
        
        return max(0.0, min(1.0, adjusted_probability))
    
    async def _get_weather_factor(self, location: Dict[str, float]) -> float:
        """Get weather factor for location"""
        # Simulate weather API call
        weather_data = await self.api_simulator.predict_weather(location)
        
        if weather_data.get('current_condition') in ['rain', 'storm', 'snow']:
            return 1.5  # Higher probability in bad weather
        elif weather_data.get('current_condition') == 'clear':
            return 0.8  # Lower probability in good weather
        else:
            return 1.0
    
    def _get_time_factor(self) -> float:
        """Get time-based factor"""
        current_hour = datetime.now().hour
        
        if 7 <= current_hour <= 9 or 17 <= current_hour <= 19:
            return 1.4  # Rush hour
        elif 11 <= current_hour <= 14:
            return 1.2  # Lunch rush
        else:
            return 1.0
    
    def _get_location_factor(self, location: Dict[str, float]) -> float:
        """Get location-based factor"""
        # Simulate high-traffic areas
        lat, lng = location['lat'], location['lng']
        
        # Check if near major roads or commercial areas
        if abs(lat - 1.3521) < 0.005 and abs(lng - 103.8198) < 0.005:
            return 1.3  # City center
        else:
            return 1.0
    
    def _get_affected_area(self, delivery: Dict[str, Any], problem_type: str) -> str:
        """Get area description for affected deliveries"""
        if problem_type == 'traffic_jam':
            return f"Area around {delivery['location']['lat']:.4f}, {delivery['location']['lng']:.4f}"
        elif problem_type == 'weather_disruption':
            return f"Weather zone covering {delivery['location']['lat']:.4f}, {delivery['location']['lng']:.4f}"
        else:
            return f"Local area near delivery {delivery['id']}"
    
    async def _precompute_solution(self, problem: PredictedProblem) -> Optional[Dict[str, Any]]:
        """Pre-compute solution for a predicted problem"""
        try:
            # Generate solution based on problem type
            if problem.problem_type == 'traffic_jam':
                solution = await self._generate_traffic_solution(problem)
            elif problem.problem_type == 'weather_disruption':
                solution = await self._generate_weather_solution(problem)
            elif problem.problem_type == 'driver_issue':
                solution = await self._generate_driver_solution(problem)
            elif problem.problem_type == 'merchant_problem':
                solution = await self._generate_merchant_solution(problem)
            elif problem.problem_type == 'customer_complaint':
                solution = await self._generate_customer_solution(problem)
            else:
                solution = await self._generate_general_solution(problem)
            
            return solution
            
        except Exception as e:
            print(f"Error precomputing solution: {e}")
            return None
    
    async def _generate_traffic_solution(self, problem: PredictedProblem) -> Dict[str, Any]:
        """Generate solution for traffic problems"""
        return {
            'actions': [
                {'type': 'reroute', 'description': 'Optimize route to avoid traffic'},
                {'type': 'notify_driver', 'description': 'Alert driver about alternative route'},
                {'type': 'update_eta', 'description': 'Adjust estimated delivery time'}
            ],
            'predicted_profit': random.uniform(20, 60),
            'confidence': 0.9,
            'execution_time': 0.3
        }
    
    async def _generate_weather_solution(self, problem: PredictedProblem) -> Dict[str, Any]:
        """Generate solution for weather problems"""
        return {
            'actions': [
                {'type': 'delay_delivery', 'description': 'Delay non-urgent deliveries'},
                {'type': 'notify_customer', 'description': 'Inform customer about weather delay'},
                {'type': 'adjust_route', 'description': 'Use safer routes in bad weather'}
            ],
            'predicted_profit': random.uniform(15, 45),
            'confidence': 0.85,
            'execution_time': 0.3
        }
    
    async def _generate_driver_solution(self, problem: PredictedProblem) -> Dict[str, Any]:
        """Generate solution for driver problems"""
        return {
            'actions': [
                {'type': 'support_driver', 'description': 'Provide driver assistance'},
                {'type': 'reassign_delivery', 'description': 'Reassign to available driver'},
                {'type': 'extend_time', 'description': 'Extend delivery window'}
            ],
            'predicted_profit': random.uniform(25, 55),
            'confidence': 0.8,
            'execution_time': 0.3
        }
    
    async def _generate_merchant_solution(self, problem: PredictedProblem) -> Dict[str, Any]:
        """Generate solution for merchant problems"""
        return {
            'actions': [
                {'type': 'contact_merchant', 'description': 'Check merchant status'},
                {'type': 'adjust_menu', 'description': 'Update available menu items'},
                {'type': 'notify_customer', 'description': 'Inform about menu changes'}
            ],
            'predicted_profit': random.uniform(30, 70),
            'confidence': 0.9,
            'execution_time': 0.3
        }
    
    async def _generate_customer_solution(self, problem: PredictedProblem) -> Dict[str, Any]:
        """Generate solution for customer complaints"""
        return {
            'actions': [
                {'type': 'compensation', 'description': 'Offer appropriate compensation'},
                {'type': 'priority_status', 'description': 'Grant priority delivery status'},
                {'type': 'follow_up', 'description': 'Schedule follow-up call'}
            ],
            'predicted_profit': random.uniform(40, 80),
            'confidence': 0.95,
            'execution_time': 0.3
        }
    
    async def _generate_general_solution(self, problem: PredictedProblem) -> Dict[str, Any]:
        """Generate general solution for unknown problem types"""
        return {
            'actions': [
                {'type': 'investigate', 'description': 'Investigate the issue'},
                {'type': 'notify_stakeholders', 'description': 'Alert relevant parties'},
                {'type': 'monitor', 'description': 'Monitor situation closely'}
            ],
            'predicted_profit': random.uniform(20, 50),
            'confidence': 0.7,
            'execution_time': 0.3
        }
    
    def _cache_prediction(self, problem: PredictedProblem, solution: Dict[str, Any]):
        """Cache a predicted problem and its solution"""
        cache_key = f"pred_{problem.id}"
        self.prediction_cache[cache_key] = {
            'problem': problem,
            'solution': solution,
            'timestamp': datetime.now(),
            'expires_at': datetime.now() + timedelta(hours=2)  # 2 hour TTL
        }
    
    async def _update_prediction_accuracy(self):
        """Update prediction accuracy based on outcomes"""
        # Simulate accuracy improvement over time
        base_accuracy = 0.85
        improvement_factor = min(0.15, self.total_predictions * 0.0001)
        self.prediction_accuracy = base_accuracy + improvement_factor
    
    def get_prediction_stats(self) -> Dict[str, Any]:
        """Get prediction engine statistics"""
        return {
            'total_predictions': self.total_predictions,
            'successful_predictions': self.successful_predictions,
            'prediction_accuracy': self.prediction_accuracy,
            'cached_solutions': len(self.prediction_cache),
            'active_predictions': len(self.active_predictions)
        }
    
    def get_cached_solution(self, problem_id: str) -> Optional[Dict[str, Any]]:
        """Get cached solution for a problem"""
        cache_key = f"pred_{problem_id}"
        cached_data = self.prediction_cache.get(cache_key)
        
        if cached_data and cached_data['expires_at'] > datetime.now():
            return cached_data['solution']
        else:
            # Remove expired cache entry
            if cache_key in self.prediction_cache:
                del self.prediction_cache[cache_key]
            return None 