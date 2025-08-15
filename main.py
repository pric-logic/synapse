"""
Project Synapse: FastAPI Backend
Provides REST API endpoints for the AI delivery orchestrator
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Dict, List, Any, Optional
import asyncio
import time
import json
from datetime import datetime

from core.agent import SynapseAgent, Scenario, Solution
from tools.api_simulator import APISimulator
from config import config
from utils.gemini_client import get_gemini_client


# Initialize FastAPI app
app = FastAPI(
    title="Project Synapse API",
    description="Multimodal Predictive Delivery Orchestrator API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global instances
synapse_agent: Optional[SynapseAgent] = None
api_simulator: Optional[APISimulator] = None


# Pydantic models for API requests/responses
class ScenarioRequest(BaseModel):
    description: str
    customer_id: Optional[str] = None
    driver_id: Optional[str] = None
    merchant_id: Optional[str] = None


class SolutionResponse(BaseModel):
    solution_id: str
    scenario_id: str
    actions: List[Dict[str, Any]]
    predicted_profit: float
    confidence: float
    reasoning: str
    execution_time: float
    cache_hit: bool
    timestamp: str


class PerformanceMetrics(BaseModel):
    total_scenarios: int
    cache_hits: int
    average_response_time: float
    total_profit_generated: float
    accuracy_rate: float


class CacheStatus(BaseModel):
    total_cached_solutions: int
    cache_hit_rate: float
    average_response_time: float
    prediction_accuracy: float


class MultimodalStats(BaseModel):
    visual_accuracy: float
    audio_accuracy: float
    environmental_accuracy: float
    fusion_accuracy: float
    recent_fusion_confidence: float
    recent_data_quality: float
    average_processing_time: float
    total_processed: int


class OptimizationStats(BaseModel):
    total_profit_generated: float
    average_roi: float
    successful_optimizations: int
    total_optimizations: int


class PredictionStats(BaseModel):
    total_predictions: int
    successful_predictions: int
    prediction_accuracy: float
    cached_solutions: int
    active_predictions: int


class APIStats(BaseModel):
    total_calls: int
    average_response_time: float
    min_response_time: float
    max_response_time: float


@app.on_event("startup")
async def startup_event():
    """Initialize components on startup"""
    global synapse_agent, api_simulator
    
    # Validate configuration
    if not config.validate():
        print("⚠️  Configuration validation failed. Some features may not work properly.")
    
    # Test Gemini connection
    try:
        gemini_client = get_gemini_client()
        if gemini_client.health_check():
            print("✅ Gemini API connection successful!")
        else:
            print("⚠️  Gemini API health check failed")
    except Exception as e:
        print(f"⚠️  Could not initialize Gemini client: {e}")
    
    # Initialize SynapseAgent
    synapse_agent = SynapseAgent()
    
    # Initialize API Simulator
    api_simulator = APISimulator()
    
    print("🚀 Project Synapse API started successfully!")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "🚀 Project Synapse API",
        "description": "Multimodal Predictive Delivery Orchestrator",
        "version": "1.0.0",
        "docs": "/docs",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "agent_initialized": synapse_agent is not None,
        "api_simulator_initialized": api_simulator is not None
    }


@app.post("/solve", response_model=SolutionResponse)
async def solve_disruption(scenario_request: ScenarioRequest):
    """
    Solve a delivery disruption scenario
    
    Args:
        scenario_request: Scenario description and optional IDs
    
    Returns:
        AI-generated solution with actions and profit prediction
    """
    if not synapse_agent:
        raise HTTPException(status_code=500, detail="AI agent not initialized")
    
    try:
        start_time = time.time()
        
        # Solve the disruption
        solution = synapse_agent.solve_disruption(scenario_request.description)
        
        # Convert to response model
        response = SolutionResponse(
            solution_id=solution.id,
            scenario_id=solution.scenario_id,
            actions=solution.actions,
            predicted_profit=solution.predicted_profit,
            confidence=solution.confidence,
            reasoning=solution.reasoning,
            execution_time=solution.execution_time,
            cache_hit=solution.cache_hit,
            timestamp=datetime.now().isoformat()
        )
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error solving disruption: {str(e)}")


@app.get("/metrics/performance", response_model=PerformanceMetrics)
async def get_performance_metrics():
    """Get AI agent performance metrics"""
    if not synapse_agent:
        raise HTTPException(status_code=500, detail="AI agent not initialized")
    
    try:
        metrics = synapse_agent.get_performance_metrics()
        return PerformanceMetrics(**metrics)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting metrics: {str(e)}")


@app.get("/metrics/cache", response_model=CacheStatus)
async def get_cache_status():
    """Get prediction cache status"""
    if not synapse_agent:
        raise HTTPException(status_code=500, detail="AI agent not initialized")
    
    try:
        cache_status = synapse_agent.get_prediction_cache_status()
        return CacheStatus(**cache_status)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting cache status: {str(e)}")


@app.get("/metrics/multimodal", response_model=MultimodalStats)
async def get_multimodal_stats():
    """Get multimodal processing statistics"""
    if not synapse_agent:
        raise HTTPException(status_code=500, detail="AI agent not initialized")
    
    try:
        multimodal_stats = synapse_agent.multimodal_processor.get_processing_stats()
        return MultimodalStats(**multimodal_stats)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting multimodal stats: {str(e)}")


@app.get("/metrics/optimization", response_model=OptimizationStats)
async def get_optimization_stats():
    """Get profit optimization statistics"""
    if not synapse_agent:
        raise HTTPException(status_code=500, detail="AI agent not initialized")
    
    try:
        optimizer_stats = synapse_agent.profit_optimizer.get_optimization_stats()
        return OptimizationStats(**optimizer_stats)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting optimization stats: {str(e)}")


@app.get("/metrics/prediction", response_model=PredictionStats)
async def get_prediction_stats():
    """Get prediction engine statistics"""
    if not synapse_agent:
        raise HTTPException(status_code=500, detail="AI agent not initialized")
    
    try:
        prediction_stats = synapse_agent.prediction_engine.get_prediction_stats()
        return PredictionStats(**prediction_stats)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting prediction stats: {str(e)}")


@app.get("/metrics/api", response_model=APIStats)
async def get_api_stats():
    """Get API simulator statistics"""
    if not api_simulator:
        raise HTTPException(status_code=500, detail="API simulator not initialized")
    
    try:
        api_stats = api_simulator.get_api_stats()
        return APIStats(**api_stats)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting API stats: {str(e)}")


@app.get("/cache/info")
async def get_cache_info():
    """Get detailed cache information"""
    if not synapse_agent:
        raise HTTPException(status_code=500, detail="AI agent not initialized")
    
    try:
        cache_info = synapse_agent.cache_manager.info()
        return cache_info
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting cache info: {str(e)}")


@app.delete("/cache/clear")
async def clear_cache():
    """Clear all cached solutions"""
    if not synapse_agent:
        raise HTTPException(status_code=500, detail="AI agent not initialized")
    
    try:
        success = synapse_agent.cache_manager.clear()
        if success:
            return {"message": "Cache cleared successfully", "timestamp": datetime.now().isoformat()}
        else:
            raise HTTPException(status_code=500, detail="Failed to clear cache")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error clearing cache: {str(e)}")


@app.get("/optimization/history")
async def get_optimization_history(limit: int = 50):
    """Get optimization history"""
    if not synapse_agent:
        raise HTTPException(status_code=500, detail="AI agent not initialized")
    
    try:
        history = synapse_agent.profit_optimizer.get_optimization_history(limit)
        return {
            "history": history,
            "total_records": len(history),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting optimization history: {str(e)}")


@app.get("/optimization/top-approaches")
async def get_top_approaches(limit: int = 5):
    """Get top performing optimization approaches"""
    if not synapse_agent:
        raise HTTPException(status_code=500, detail="AI agent not initialized")
    
    try:
        approaches = synapse_agent.profit_optimizer.get_top_performing_approaches(limit)
        return {
            "approaches": approaches,
            "total_approaches": len(approaches),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting top approaches: {str(e)}")


@app.post("/api/simulate")
async def simulate_api_calls(background_tasks: BackgroundTasks):
    """Simulate various API calls for demonstration"""
    if not api_simulator:
        raise HTTPException(status_code=500, detail="API simulator not initialized")
    
    try:
        # Run API simulations in background
        background_tasks.add_task(run_api_simulations)
        
        return {
            "message": "API simulations started in background",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error starting API simulations: {str(e)}")


async def run_api_simulations():
    """Run API simulations in background"""
    try:
        # Simulate various API calls
        await api_simulator.check_traffic()
        await api_simulator.predict_weather()
        await api_simulator.analyze_customer_sentiment()
        await api_simulator.calculate_driver_stress()
        await api_simulator.optimize_route(
            start_location={'lat': 1.3521, 'lng': 103.8198},
            end_location={'lat': 1.3621, 'lng': 103.8298}
        )
        
        print("✅ API simulations completed successfully")
        
    except Exception as e:
        print(f"❌ Error in API simulations: {e}")


@app.get("/demo/scenarios")
async def get_demo_scenarios():
    """Get available demo scenarios"""
    scenarios = [
        {
            "id": "traffic_jam",
            "title": "🚗 Traffic Jam Cascade",
            "description": "Major accident on Highway 1 affects 5 active deliveries",
            "type": "traffic_disruption",
            "expected_outcome": "0.3s response with rerouting solution"
        },
        {
            "id": "customer_complaint",
            "title": "😠 Customer Complaint",
            "description": "Customer angry about cold food delivery",
            "type": "customer_issue",
            "expected_outcome": "Profit optimization with LTV analysis"
        },
        {
            "id": "multimodal",
            "title": "🎤 Multi-Modal Analysis",
            "description": "Driver reports traffic, but GPS shows clear",
            "type": "driver_wellbeing",
            "expected_outcome": "Superior context understanding via multimodal fusion"
        }
    ]
    
    return {
        "scenarios": scenarios,
        "total_scenarios": len(scenarios),
        "timestamp": datetime.now().isoformat()
    }


@app.get("/gemini/info")
async def get_gemini_info():
    """Get Gemini model information and status"""
    try:
        gemini_client = get_gemini_client()
        model_info = gemini_client.get_model_info()
        health_status = gemini_client.health_check()
        
        return {
            "status": "healthy" if health_status else "unhealthy",
            "model_info": model_info,
            "configuration": {
                "model": config.GEMINI_MODEL,
                "api_key_configured": bool(config.GEMINI_API_KEY),
                "safety_settings": config.GEMINI_SAFETY_SETTINGS
            },
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting Gemini info: {str(e)}")


@app.post("/demo/run/{scenario_id}")
async def run_demo_scenario(scenario_id: str):
    """Run a specific demo scenario"""
    if not synapse_agent:
        raise HTTPException(status_code=500, detail="AI agent not initialized")
    
    # Map scenario IDs to descriptions
    scenario_map = {
        "traffic_jam": "Major accident on Highway 1 affects 5 active deliveries",
        "customer_complaint": "Customer angry about cold food delivery",
        "multimodal": "Driver reports traffic, but GPS shows clear"
    }
    
    if scenario_id not in scenario_map:
        raise HTTPException(status_code=400, detail=f"Unknown scenario ID: {scenario_id}")
    
    try:
        start_time = time.time()
        
        # Run the scenario
        solution = synapse_agent.solve_disruption(scenario_map[scenario_id])
        
        processing_time = time.time() - start_time
        
        return {
            "scenario_id": scenario_id,
            "scenario_description": scenario_map[scenario_id],
            "solution": {
                "id": solution.id,
                "actions": solution.actions,
                "predicted_profit": solution.predicted_profit,
                "confidence": solution.confidence,
                "execution_time": solution.execution_time,
                "cache_hit": solution.cache_hit
            },
            "processing_time": processing_time,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error running demo scenario: {str(e)}")


@app.get("/status")
async def get_system_status():
    """Get comprehensive system status"""
    if not synapse_agent or not api_simulator:
        raise HTTPException(status_code=500, detail="System not fully initialized")
    
    try:
        # Check Gemini status
        gemini_status = "unknown"
        try:
            gemini_client = get_gemini_client()
            gemini_status = "healthy" if gemini_client.health_check() else "unhealthy"
        except Exception as e:
            gemini_status = f"error: {str(e)}"
        
        # Gather all status information
        status = {
            "system": {
                "status": "running",
                "uptime": "active",
                "timestamp": datetime.now().isoformat()
            },
            "agent": {
                "initialized": synapse_agent is not None,
                "performance": synapse_agent.get_performance_metrics() if synapse_agent else None,
                "cache_status": synapse_agent.get_prediction_cache_status() if synapse_agent else None
            },
            "components": {
                "prediction_engine": synapse_agent.prediction_engine.get_prediction_stats() if synapse_agent else None,
                "profit_optimizer": synapse_agent.profit_optimizer.get_optimization_stats() if synapse_agent else None,
                "multimodal_processor": synapse_agent.multimodal_processor.get_processing_stats() if synapse_agent else None,
                "api_simulator": api_simulator.get_api_stats() if api_simulator else None
            },
            "gemini": {
                "status": gemini_status,
                "model": config.GEMINI_MODEL,
                "api_key_configured": bool(config.GEMINI_API_KEY)
            }
        }
        
        return status
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting system status: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    
    print("🚀 Starting Project Synapse API...")
    uvicorn.run(
        "main:app",
        host=config.API_HOST,
        port=config.API_PORT,
        reload=config.API_DEBUG,
        log_level="info"
    ) 