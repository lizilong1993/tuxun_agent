"""
Main application file for TuXun Agent
A Manus-like tool for image geolocation
"""
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import os
from .api.geolocation_api import router as geolocation_router
from .config import Config

# Create FastAPI app
app = FastAPI(
    title="TuXun Agent",
    description="A Manus-like tool for image geolocation",
    version="1.0.0"
)

# Include API routes
app.include_router(geolocation_router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "Welcome to TuXun Agent - Image Geolocation Service"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "TuXun Agent"}

# Mount UI if it exists
ui_path = os.path.join(os.path.dirname(__file__), "ui")
if os.path.exists(ui_path):
    app.mount("/ui", StaticFiles(directory=ui_path, html=True), name="ui")

# Additional configuration can be added here
config = Config()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=config.API_HOST, port=config.API_PORT)