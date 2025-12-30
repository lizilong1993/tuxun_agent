"""
API endpoints for TuXun Agent geolocation service
"""
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
from typing import Optional
import os
import uuid
from ..config import Config
from ..agents.image_processing_agent import ImageProcessingAgent
from ..agents.geolocation_reasoning_agent import GeolocationReasoningAgent
from ..modules.validation_module import ValidationModule

router = APIRouter()

# Initialize agents and modules
config = Config()
image_agent = ImageProcessingAgent("ImageProcessingAgent", config.__dict__)
reasoning_agent = GeolocationReasoningAgent("GeolocationReasoningAgent", config.__dict__)
validation_module = ValidationModule(config.__dict__)

@router.post("/geolocate")
async def geolocate_image(
    image: UploadFile = File(...),
    context: Optional[str] = Form(None)
):
    """
    Upload an image for geolocation analysis
    """
    try:
        # Validate file type
        file_ext = image.filename.split('.')[-1].lower()
        if file_ext not in config.ALLOWED_IMAGE_FORMATS:
            raise HTTPException(status_code=400, detail=f"File format not supported. Allowed formats: {config.ALLOWED_IMAGE_FORMATS}")
        
        # Check file size
        contents = await image.read()
        if len(contents) > config.MAX_IMAGE_SIZE:
            raise HTTPException(status_code=400, detail=f"File too large. Maximum size: {config.MAX_IMAGE_SIZE} bytes")
        
        # Save uploaded image temporarily
        os.makedirs(config.UPLOAD_FOLDER, exist_ok=True)
        unique_filename = f"{uuid.uuid4()}_{image.filename}"
        image_path = os.path.join(config.UPLOAD_FOLDER, unique_filename)
        
        with open(image_path, "wb") as f:
            f.write(contents)
        
        # Create task for image processing agent
        image_task = {
            'image_path': image_path
        }
        
        # Process image to extract features and EXIF data
        image_result = await image_agent.execute(image_task)
        
        # Create task for geolocation reasoning agent
        reasoning_task = {
            'image_features': image_result['image_features'],
            'exif_data': image_result['exif_data'],
            'user_context': context or ''
        }
        
        # Perform geolocation reasoning
        geolocation_result = await reasoning_agent.execute(reasoning_task)
        
        # Validate the result
        validated_result = validation_module.validate_location_prediction(
            geolocation_result,
            image_result['image_features']
        )
        
        # Clean up temporary file
        os.remove(image_path)
        
        return {
            "status": "success",
            "result": validated_result
        }
        
    except Exception as e:
        # Clean up temporary file if it exists
        if 'image_path' in locals() and os.path.exists(image_path):
            os.remove(image_path)
        
        raise HTTPException(status_code=500, detail=f"Error processing image: {str(e)}")

@router.get("/health")
async def health_check():
    """
    Health check endpoint
    """
    return {"status": "healthy", "service": "TuXun Agent Geolocation API"}

# Additional endpoints can be added here