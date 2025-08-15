"""
Gemini Client Utility
Provides a clean interface for interacting with Google's Gemini API
"""

import google.generativeai as genai
from typing import Dict, List, Any, Optional, Union
import base64
import io
from PIL import Image
import time
import logging

from config import config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GeminiClient:
    """Client for interacting with Google's Gemini API"""
    
    def __init__(self):
        """Initialize Gemini client"""
        if not config.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY not configured")
        
        # Configure Gemini
        genai.configure(api_key=config.GEMINI_API_KEY)
        
        # Initialize models
        self.text_model = genai.GenerativeModel(
            model_name=config.GEMINI_MODEL,
            safety_settings=config.GEMINI_SAFETY_SETTINGS
        )
        
        # For multimodal tasks, use the configured model
        try:
            self.multimodal_model = genai.GenerativeModel(
                model_name="gemini-2.5-flash",
                safety_settings=config.GEMINI_SAFETY_SETTINGS
            )
        except Exception as e:
            logger.warning(f"Could not initialize multimodal model: {e}")
            self.multimodal_model = self.text_model
        
        logger.info(f"✅ Gemini client initialized with model: {config.GEMINI_MODEL}")
    
    def generate_text(self, prompt: str, temperature: float = 0.1, max_tokens: int = 200) -> str:
        """
        Generate text using Gemini
        
        Args:
            prompt: Text prompt
            temperature: Creativity level (0.0 to 1.0)
            max_tokens: Maximum tokens to generate
            
        Returns:
            Generated text
        """
        try:
            start_time = time.time()
            
            response = self.text_model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=temperature,
                    max_output_tokens=max_tokens,
                )
            )
            
            generation_time = time.time() - start_time
            logger.info(f"Text generation completed in {generation_time:.3f}s")
            
            if response.text:
                return response.text.strip()
            else:
                logger.warning("Empty response from Gemini")
                return "No response generated"
                
        except Exception as e:
            logger.error(f"Error generating text: {e}")
            return f"Error in text generation: {str(e)}"
    
    def generate_text_with_system_prompt(self, system_prompt: str, user_prompt: str, 
                                       temperature: float = 0.1, max_tokens: int = 150) -> str:
        """
        Generate text with system and user prompts
        
        Args:
            system_prompt: System instruction
            user_prompt: User request
            temperature: Creativity level
            max_tokens: Maximum tokens to generate
            
        Returns:
            Generated text
        """
        full_prompt = f"{system_prompt}\n\nUser: {user_prompt}\n\nAssistant:"
        return self.generate_text(full_prompt, temperature, max_tokens)
    
    def analyze_image(self, image_path: str, prompt: str, temperature: float = 0.1) -> str:
        """
        Analyze image using Gemini multimodal capabilities
        
        Args:
            image_path: Path to image file
            prompt: Analysis prompt
            temperature: Creativity level
            
        Returns:
            Analysis result
        """
        try:
            # Load and prepare image
            image = Image.open(image_path)
            
            # Convert to bytes for Gemini
            img_byte_arr = io.BytesIO()
            image.save(img_byte_arr, format='PNG')
            img_byte_arr = img_byte_arr.getvalue()
            
            # Generate content with image
            response = self.multimodal_model.generate_content(
                [prompt, {"mime_type": "image/png", "data": img_byte_arr}],
                generation_config=genai.types.GenerationConfig(
                    temperature=temperature,
                    max_output_tokens=150,
                )
            )
            
            if response.text:
                return response.text.strip()
            else:
                return "No analysis generated"
                
        except Exception as e:
            logger.error(f"Error analyzing image: {e}")
            return f"Error in image analysis: {str(e)}"
    
    def analyze_image_from_base64(self, base64_image: str, prompt: str, 
                                 temperature: float = 0.1) -> str:
        """
        Analyze image from base64 string
        
        Args:
            base64_image: Base64 encoded image
            prompt: Analysis prompt
            temperature: Creativity level
            
        Returns:
            Analysis result
        """
        try:
            # Decode base64 image
            image_data = base64.b64decode(base64_image)
            
            # Generate content with image
            response = self.multimodal_model.generate_content(
                [prompt, {"mime_type": "image/png", "data": image_data}],
                generation_config=genai.types.GenerationConfig(
                    temperature=temperature,
                    max_output_tokens=150,
                )
            )
            
            if response.text:
                return response.text.strip()
            else:
                return "No analysis generated"
                
        except Exception as e:
            logger.error(f"Error analyzing base64 image: {e}")
            return f"Error in image analysis: {str(e)}"
    
    def chat_conversation(self, messages: List[Dict[str, str]], 
                         temperature: float = 0.1, max_tokens: int = 200) -> str:
        """
        Have a conversation with Gemini
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            temperature: Creativity level
            max_tokens: Maximum tokens to generate
            
        Returns:
            Response from Gemini
        """
        try:
            # Convert messages to Gemini format
            gemini_messages = []
            for msg in messages:
                if msg['role'] == 'user':
                    gemini_messages.append(msg['content'])
                elif msg['role'] == 'assistant':
                    gemini_messages.append(msg['content'])
            
            # Generate response
            response = self.text_model.generate_content(
                gemini_messages,
                generation_config=genai.types.GenerationConfig(
                    temperature=temperature,
                    max_output_tokens=max_tokens,
                )
            )
            
            if response.text:
                return response.text.strip()
            else:
                return "No response generated"
                
        except Exception as e:
            logger.error(f"Error in chat conversation: {e}")
            return f"Error in conversation: {str(e)}"
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about available models"""
        try:
            models = genai.list_models()
            return {
                "available_models": [model.name for model in models],
                "current_model": config.GEMINI_MODEL,
                "multimodal_support": self.multimodal_model != self.text_model
            }
        except Exception as e:
            logger.error(f"Error getting model info: {e}")
            return {"error": str(e)}
    
    def generate_concise_logistics_solution(self, scenario: str, solution: str, 
                                          temperature: float = 0.1) -> str:
        """
        Generate an actionable logistics solution
        
        Args:
            scenario: The delivery disruption scenario
            solution: The proposed solution
            temperature: Creativity level
            
        Returns:
            Actionable solution with specific recommendations (~100 words)
        """
        try:
            prompt = f"""
            Scenario: {scenario}
            Solution: {solution}
            
            Provide an actionable solution in ~100 words with this structure:
            
            1. SPECIFIC ACTION: What exactly to do to solve this issue uniquely
            2. WHY: Brief explanation of why this approach is best
            
            Make it conversational and actionable. Focus on immediate next steps.
            Do NOT include interactive options or questions - just the solution explanation.
            """
            
            response = self.text_model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=temperature,
                    max_output_tokens=150,  # Allow for ~100 word responses
                )
            )
            
            if response.text:
                # Post-process to ensure appropriate length
                text = response.text.strip()
                
                # Limit to reasonable length (around 100 words)
                if len(text) > 500:
                    # Truncate to ~100 words
                    words = text.split()
                    if len(words) > 100:
                        text = ' '.join(words[:100]) + '...'
                
                return text
            else:
                return "I recommend rerouting the driver to avoid the disruption. This minimizes delays and maintains customer satisfaction while ensuring timely delivery."
                
        except Exception as e:
            logger.error(f"Error generating concise solution: {e}")
            return "I recommend rerouting the driver to avoid the disruption. This minimizes delays and maintains customer satisfaction while ensuring timely delivery."
    
    def generate_interactive_options(self, scenario: str, solution: str) -> List[Dict[str, str]]:
        """
        Generate interactive button options for the user
        
        Args:
            scenario: The delivery disruption scenario
            solution: The proposed solution
            
        Returns:
            List of button options with text and action
        """
        try:
            # Analyze scenario type to provide relevant options
            scenario_lower = scenario.lower()
            
            # Default options
            default_options = [
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
            
            # Add scenario-specific options
            if any(word in scenario_lower for word in ['traffic', 'accident', 'jam', 'road']):
                options = [
                    {
                        "text": "Reroute via Alternative Path",
                        "action": "reroute_alternative",
                        "description": "Use backup route to avoid traffic"
                    },
                    {
                        "text": "Notify Customers of Delay",
                        "action": "notify_customers",
                        "description": "Send delay notifications to affected customers"
                    },
                    {
                        "text": "Activate Emergency Protocol",
                        "action": "emergency_protocol",
                        "description": "Implement emergency delivery procedures"
                    }
                ]
            elif any(word in scenario_lower for word in ['complaint', 'angry', 'cold', 'food']):
                options = [
                    {
                        "text": "Offer Refund/Credit",
                        "action": "offer_compensation",
                        "description": "Provide customer compensation"
                    },
                    {
                        "text": "Send Replacement Order",
                        "action": "replacement_order",
                        "description": "Prepare and send fresh order"
                    },
                    {
                        "text": "Escalate to Manager",
                        "action": "escalate_manager",
                        "description": "Get manager involved in resolution"
                    }
                ]
            elif any(word in scenario_lower for word in ['driver', 'unwell', 'sick', 'replacement']):
                options = [
                     {
                         "text": "🚗 Show Live Driver Map",
                         "action": "show_live_map",
                         "description": "Display real-time driver location on Bangalore map"
                     },
                     {
                         "text": "🔄 Reroute to Best Path",
                         "action": "reroute_best_path",
                         "description": "Calculate and apply optimal route using Bangalore traffic data"
                     },
                     {
                         "text": "🚨 Dispatch Backup Driver",
                         "action": "backup_driver",
                         "description": "Send replacement driver immediately"
                     }
                 ]
            elif any(word in scenario_lower for word in ['weather', 'rain', 'storm', 'delay']):
                options = [
                    {
                        "text": "Activate Weather Protocol",
                        "action": "weather_protocol",
                        "description": "Implement weather-safe delivery procedures"
                    },
                    {
                        "text": "Provide Weather Updates",
                        "action": "weather_updates",
                        "description": "Keep customers informed of weather delays"
                    },
                    {
                        "text": "Use Weather-Protected Routes",
                        "action": "protected_routes",
                        "description": "Route through covered/indoor areas"
                    }
                ]
            else:
                # Generic options for unknown scenarios
                options = [
                    {
                        "text": "Implement Solution",
                        "action": "implement_solution",
                        "description": "Execute the recommended solution"
                    },
                    {
                        "text": "Get More Details",
                        "action": "get_details",
                        "description": "Request additional information"
                    },
                    {
                        "text": "Escalate Issue",
                        "action": "escalate",
                        "description": "Escalate to higher management"
                    }
                ]
            
            # Always include at least 2 options
            if len(options) < 2:
                options.extend(default_options[:2-len(options)])
            
            return options[:3]  # Return maximum 3 options
            
        except Exception as e:
            logger.error(f"Error generating interactive options: {e}")
            # Return default options if there's an error
            return [
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
    
    def health_check(self) -> bool:
        """Check if Gemini API is accessible"""
        try:
            # Simple test generation
            response = self.text_model.generate_content("Hello", max_tokens=10)
            return response.text is not None
        except Exception as e:
            logger.error(f"Gemini health check failed: {e}")
            return False

# Global Gemini client instance
gemini_client: Optional[GeminiClient] = None

def get_gemini_client() -> GeminiClient:
    """Get or create Gemini client instance"""
    global gemini_client
    if gemini_client is None:
        gemini_client = GeminiClient()
    return gemini_client
