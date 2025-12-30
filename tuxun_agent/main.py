# Main application file for TuXun Agent  
from fastapi import FastAPI  
  
app = FastAPI(  
    title="TuXun Agent",  
    description="A Manus-like tool for image geolocation",  
    version="1.0.0"  
)  
  
@app.get("/")  
async def root():  
    return {"message": "Welcome to TuXun Agent - Image Geolocation Service"} 
