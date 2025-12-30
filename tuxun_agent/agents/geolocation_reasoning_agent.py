# Geolocation Reasoning Agent for TuXun Agent
# Updated to work with Silicon Flow API
import requests
from .base_agent import BaseAgent
from typing import Dict, Any
import json
import re

class GeolocationReasoningAgent(BaseAgent):
    def __init__(self, name: str, config: Dict[str, Any]):
        super().__init__(name, config)
        self.api_key = config.get('SILICON_FLOW_API_KEY')
        self.base_url = config.get('SILICON_FLOW_BASE_URL', 'https://api.siliconflow.com/v1')
        self.default_model = config.get('DEFAULT_MODEL', 'qwen2.5-72b-instruct')
        self.temperature = float(config.get('MODEL_TEMPERATURE', '0.3'))

    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        # Get image analysis results from task
        image_features = task.get('image_features', {})
        exif_data = task.get('exif_data')
        user_context = task.get('user_context', '')
        
        # If we have EXIF GPS data, return it directly with high confidence
        if exif_data and 'latitude' in exif_data and 'longitude' in exif_data:
            return {
                'predicted_location': {
                    'latitude': exif_data['latitude'],
                    'longitude': exif_data['longitude'],
                    'accuracy': 'high',
                    'confidence': 0.95
                },
                'reasoning': 'Location determined from EXIF GPS data',
                'alternative_locations': []
            }
        
        # If no EXIF data, use visual analysis and context
        location_prediction = await self.analyze_visual_context(
            image_features, 
            user_context
        )
        
        return location_prediction
    
    async def analyze_visual_context(self, image_features: Dict[str, Any], user_context: str) -> Dict[str, Any]:
        # Prepare a prompt for the LLM to analyze visual features and context
        prompt = self.create_analysis_prompt(image_features, user_context)
        
        # Use Silicon Flow API to analyze the image features and context
        try:
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                'model': self.default_model,
                'messages': [
                    {
                        "role": "system", 
                        "content": "You are an expert at determining geographic locations from image features and contextual information. Provide the most likely location with coordinates, accuracy estimate, and confidence score. Respond in JSON format."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                'temperature': self.temperature,
                'max_tokens': 500,
                'response_format': {"type": "json_object"}
            }
            
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result['choices'][0]['message']['content']
                
                # Parse the response
                parsed_result = self.parse_llm_response(content)
                return parsed_result
            else:
                print(f"Error from Silicon Flow API: {response.status_code} - {response.text}")
                return self.get_fallback_prediction()
                
        except Exception as e:
            print(f"Error in Silicon Flow API geolocation reasoning: {e}")
            return self.get_fallback_prediction()
    
    def create_analysis_prompt(self, image_features: Dict[str, Any], user_context: str) -> str:
        prompt = f"""
        Analyze the following image features to determine the geographic location:
        
        Image Features:
        - Size: {image_features.get('size', 'Unknown')}
        - Mode: {image_features.get('mode', 'Unknown')}
        - Brightness: {image_features.get('brightness', 'Unknown')}
        - Number of edges: {image_features.get('edges', 'Unknown')}
        - Dominant colors: {image_features.get('dominant_colors', 'Unknown')}
        
        User Context: {user_context if user_context else 'No additional context provided'}
        
        Based on these features, please provide:
        1. Most likely geographic location (city, region, country)
        2. Estimated latitude and longitude coordinates
        3. Accuracy level (high, medium, low)
        4. Confidence score (0-1)
        5. Alternative possible locations with lower confidence
        6. Reasoning for your prediction
        
        Respond in JSON format with the following structure:
        {{
            "predicted_location": {{
                "latitude": <number>,
                "longitude": <number>,
                "accuracy": "<high|medium|low>",
                "confidence": <number>
            }},
            "reasoning": "<explanation>",
            "alternative_locations": [
                {{
                    "latitude": <number>,
                    "longitude": <number>,
                    "confidence": <number>
                }}
            ]
        }}
        """
        return prompt
    
    def parse_llm_response(self, response: str) -> Dict[str, Any]:
        try:
            # Extract JSON from response if it's wrapped in markdown
            json_match = re.search(r'```(?:json)?\s*({.*?})\s*```', response, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
            else:
                # Try to find JSON object directly
                json_start = response.find('{')
                json_end = response.rfind('}') + 1
                if json_start != -1 and json_end != 0:
                    json_str = response[json_start:json_end]
                else:
                    json_str = response.strip()
            
            # Parse the JSON response
            result = json.loads(json_str)
            
            # Validate the structure
            if 'predicted_location' not in result:
                result['predicted_location'] = {
                    'latitude': 0.0,
                    'longitude': 0.0,
                    'accuracy': 'low',
                    'confidence': 0.1
                }
            
            if 'reasoning' not in result:
                result['reasoning'] = 'Location prediction based on image features'
            
            if 'alternative_locations' not in result:
                result['alternative_locations'] = []
            
            return result
        except Exception as e:
            print(f"Error parsing LLM response: {e}")
            print(f"Response content: {response}")
            return self.get_fallback_prediction()
    
    def get_fallback_prediction(self) -> Dict[str, Any]:
        # Return a fallback prediction when analysis fails
        return {
            'predicted_location': {
                'latitude': 0.0,
                'longitude': 0.0,
                'accuracy': 'low',
                'confidence': 0.1
            },
            'reasoning': 'Unable to determine location from available data',
            'alternative_locations': []
        }