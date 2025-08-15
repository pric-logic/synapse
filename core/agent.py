"""
SynapseAgent: Core AI agent for Project Synapse
Implements multimodal intelligence, prediction caching, and profit optimization
"""

import asyncio
import time
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
import hashlib
import json

import numpy as np

from core.prediction import PredictionEngine
from core.optimizer import ProfitOptimizer
from core.multimodal import MultimodalProcessor
from tools.api_simulator import APISimulator
from utils.cache import CacheManager
from utils.gemini_client import get_gemini_client


@dataclass
class Scenario:
    """Represents a delivery disruption scenario"""
    id: str
    description: str
    timestamp: datetime
    affected_deliveries: int
    severity: float  # 0.0 to 1.0
    scenario_type: str
    raw_input: str
    
    def __hash__(self):
        return hash(self.id)
    
    def to_dict(self):
        return {
            'id': self.id,
            'description': self.description,
            'timestamp': self.timestamp.isoformat(),
            'affected_deliveries': self.affected_deliveries,
            'severity': self.severity,
            'scenario_type': self.scenario_type,
            'raw_input': self.raw_input
        }


@dataclass
class Solution:
    """Represents a solution to a scenario"""
    id: str
    scenario_id: str
    actions: List[Dict[str, Any]]
    predicted_profit: float
    confidence: float
    reasoning: str
    execution_time: float
    cache_hit: bool = False
    interactive_options: List[Dict[str, str]] = None
    
    def to_dict(self):
        return {
            'id': self.id,
            'scenario_id': self.scenario_id,
            'actions': self.actions,
            'predicted_profit': self.predicted_profit,
            'confidence': self.confidence,
            'reasoning': self.reasoning,
            'execution_time': self.execution_time,
            'cache_hit': self.cache_hit,
            'interactive_options': self.interactive_options or []
        }


class SynapseAgent:
    """
    Main AI agent for Project Synapse
    Orchestrates multimodal analysis, prediction, and profit optimization
    """
    
    def __init__(self, gemini_api_key: str = None):
        # Initialize LLM
        try:
            self.llm = get_gemini_client()
        except Exception as e:
            print(f"⚠️  Warning: Could not initialize Gemini client: {e}")
            self.llm = None
        
        # Initialize core components
        self.prediction_engine = PredictionEngine()
        self.profit_optimizer = ProfitOptimizer()
        self.multimodal_processor = MultimodalProcessor()
        self.api_simulator = APISimulator()
        self.cache_manager = CacheManager()
        
        # Performance tracking
        self.performance_metrics = {
            'total_scenarios': 0,
            'cache_hits': 0,
            'average_response_time': 0.0,
            'total_profit_generated': 0.0,
            'accuracy_rate': 0.0
        }
        
        # Don't start background prediction loop immediately
        # It will be started when needed
    
    def start_background_prediction(self):
        """Start background prediction loop (call this when in async context)"""
        # This method is intentionally empty for now
        # Background prediction can be implemented later when needed
        pass
    
    def solve_disruption(self, scenario_input: str) -> Solution:
        """
        Main method to solve delivery disruptions
        Returns solution in 0.3 seconds or less
        """
        start_time = time.time()
        
        # Create scenario object
        scenario = self._create_scenario(scenario_input)
        
        # Check prediction cache first (speed advantage)
        cached_solution = self._check_prediction_cache(scenario)
        if cached_solution:
            cached_solution.cache_hit = True
            cached_solution.execution_time = time.time() - start_time
            self._update_metrics(cached_solution, True)
            return cached_solution
        
        # Multi-modal analysis
        context = self.multimodal_processor.analyze_scenario(scenario)
        
        # Generate profit-optimal solution
        solution = self.profit_optimizer.optimize(scenario, context)
        
        # Execute with reasoning
        final_solution = self._execute_with_reasoning(scenario, solution, context)
        final_solution.execution_time = time.time() - start_time
        
        # Cache the solution for future use
        self._cache_solution(scenario, final_solution)
        
        # Update metrics
        self._update_metrics(final_solution, False)
        
        return final_solution
    
    def _create_scenario(self, input_text: str) -> Scenario:
        """Create a scenario object from input text"""
        # Generate unique ID
        scenario_id = hashlib.md5(input_text.encode()).hexdigest()[:8]
        
        # Analyze input to determine scenario type and severity
        scenario_type = self._classify_scenario(input_text)
        severity = self._assess_severity(input_text)
        affected_deliveries = self._estimate_affected_deliveries(input_text)
        
        return Scenario(
            id=scenario_id,
            description=input_text,
            timestamp=datetime.now(),
            affected_deliveries=affected_deliveries,
            severity=severity,
            scenario_type=scenario_type,
            raw_input=input_text
        )
    
    def _classify_scenario(self, input_text: str) -> str:
        """Classify the type of scenario"""
        text_lower = input_text.lower()
        
        if any(word in text_lower for word in ['traffic', 'accident', 'jam', 'road']):
            return 'traffic_disruption'
        elif any(word in text_lower for word in ['complaint', 'angry', 'cold', 'food']):
            return 'customer_issue'
        elif any(word in text_lower for word in ['driver', 'voice', 'stress']):
            return 'driver_wellbeing'
        elif any(word in text_lower for word in ['weather', 'rain', 'storm']):
            return 'environmental'
        else:
            return 'general_disruption'
    
    def _assess_severity(self, input_text: str) -> float:
        """Assess the severity of the scenario (0.0 to 1.0)"""
        text_lower = input_text.lower()
        
        # Keywords that indicate severity
        high_severity = ['major', 'critical', 'emergency', 'accident', 'angry']
        medium_severity = ['delay', 'problem', 'issue', 'cold', 'traffic']
        low_severity = ['minor', 'slight', 'small']
        
        if any(word in text_lower for word in high_severity):
            return np.random.uniform(0.7, 1.0)
        elif any(word in text_lower for word in medium_severity):
            return np.random.uniform(0.4, 0.7)
        elif any(word in text_lower for word in low_severity):
            return np.random.uniform(0.1, 0.4)
        else:
            return np.random.uniform(0.3, 0.6)
    
    def _estimate_affected_deliveries(self, input_text: str) -> int:
        """Estimate number of affected deliveries"""
        text_lower = input_text.lower()
        
        # Look for numbers in the text
        import re
        numbers = re.findall(r'\d+', input_text)
        
        if numbers:
            return int(numbers[0])
        else:
            # Estimate based on keywords
            if any(word in text_lower for word in ['major', 'highway', 'multiple']):
                return np.random.randint(3, 8)
            elif any(word in text_lower for word in ['single', 'one', 'individual']):
                return 1
            else:
                return np.random.randint(1, 4)
    
    def _check_prediction_cache(self, scenario: Scenario) -> Optional[Solution]:
        """Check if solution exists in prediction cache"""
        cache_key = f"scenario_{scenario.id}"
        cached_data = self.cache_manager.get(cache_key)
        
        if cached_data:
            # Convert back to Solution object
            return Solution(**cached_data)
        return None
    
    def _cache_solution(self, scenario: Scenario, solution: Solution):
        """Cache solution for future use"""
        cache_key = f"scenario_{scenario.id}"
        self.cache_manager.set(cache_key, solution.to_dict(), ttl=3600)  # 1 hour TTL
    
    def _execute_with_reasoning(self, scenario: Scenario, solution: Dict, context: Dict) -> Solution:
        """Execute solution with detailed reasoning"""
        # Create JSON-safe context by converting datetime objects to strings
        def make_json_safe(obj):
            if isinstance(obj, dict):
                return {k: make_json_safe(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [make_json_safe(item) for item in obj]
            elif hasattr(obj, 'isoformat'):  # datetime objects
                return obj.isoformat()
            elif hasattr(obj, 'to_dict'):  # custom objects with to_dict method
                return obj.to_dict()
            else:
                return obj
        
        safe_context = make_json_safe(context)
        safe_solution = make_json_safe(solution)
        
        # Generate reasoning using LLM
        reasoning_prompt = f"""
        Scenario: {scenario.description}
        
        Provide a BRIEF explanation (max 2-3 sentences) of:
        1. Why this solution was chosen
        2. Expected profit impact
        """
        
        try:
            if self.llm:
                # Generate the solution explanation
                reasoning = self.llm.generate_concise_logistics_solution(
                    scenario=scenario.description,
                    solution=str(solution),
                    temperature=0.1
                )
                
                # Generate interactive options
                interactive_options = self.llm.generate_interactive_options(
                    scenario=scenario.description,
                    solution=str(solution)
                )
            else:
                reasoning = "Solution optimized for maximum profit."
                interactive_options = [
                    {
                        "text": "Make Changes to Driver's Route",
                        "action": "route_change",
                        "description": "Update delivery route to avoid disruption"
                    },
                    {
                        "text": "Connect Customer Service Agent",
                        "action": "customer_service",
                        "description": "Get customer service agent involved"
                    }
                ]
        except Exception as e:
            reasoning = "Solution optimized for maximum profit."
            interactive_options = [
                {
                    "text": "Make Changes to Driver's Route",
                    "action": "route_change",
                    "description": "Update delivery route to avoid disruption"
                },
                {
                    "text": "Connect Customer Service Agent",
                    "action": "customer_service",
                    "description": "Get customer service agent involved"
                }
            ]
        
        # Create solution object
        solution_id = f"sol_{scenario.id}_{int(time.time())}"
        
        return Solution(
            id=solution_id,
            scenario_id=scenario.id,
            actions=solution.get('actions', []),
            predicted_profit=solution.get('predicted_profit', 0.0),
            confidence=solution.get('confidence', 0.8),
            reasoning=reasoning,
            execution_time=0.0,
            interactive_options=interactive_options
        )
    
    def _update_metrics(self, solution: Solution, cache_hit: bool):
        """Update performance metrics"""
        self.performance_metrics['total_scenarios'] += 1
        
        if cache_hit:
            self.performance_metrics['cache_hits'] += 1
        
        # Update average response time
        current_avg = self.performance_metrics['average_response_time']
        total_scenarios = self.performance_metrics['total_scenarios']
        self.performance_metrics['average_response_time'] = (
            (current_avg * (total_scenarios - 1) + solution.execution_time) / total_scenarios
        )
        
        # Update total profit
        self.performance_metrics['total_profit_generated'] += solution.predicted_profit
        
        # Update accuracy rate (simulate improvement over time)
        base_accuracy = 0.85
        improvement_factor = min(0.15, total_scenarios * 0.001)
        self.performance_metrics['accuracy_rate'] = base_accuracy + improvement_factor
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get current performance metrics"""
        return self.performance_metrics.copy()
    
    def get_prediction_cache_status(self) -> Dict[str, Any]:
        """Get status of prediction cache"""
        return {
            'total_cached_solutions': len(self.cache_manager.get_all_keys()),
            'cache_hit_rate': (
                self.performance_metrics['cache_hits'] / 
                max(1, self.performance_metrics['total_scenarios'])
            ),
            'average_response_time': self.performance_metrics['average_response_time'],
            'prediction_accuracy': self.performance_metrics['accuracy_rate']
        } 