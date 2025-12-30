# Image Processing Agent for TuXun Agent
import cv2
import numpy as np
from PIL import Image
import exifread
import io
from .base_agent import BaseAgent
from typing import Dict, Any, Optional

class ImageProcessingAgent(BaseAgent):
    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        # Extract image data from task
        image_data = task.get('image_data')
        image_path = task.get('image_path')

        # Load image
        if image_data:
            image = Image.open(io.BytesIO(image_data))
        elif image_path:
            image = Image.open(image_path)
        else:
            raise ValueError("Either image_data or image_path must be provided")

        # Extract EXIF metadata
        exif_data = self.extract_exif_data(image_path if image_path else image)

        # Perform basic image analysis
        image_features = self.analyze_image(image)

        return {
            'exif_data': exif_data,
            'image_features': image_features,
            'image_dimensions': image.size
        }

    def extract_exif_data(self, image_source) -> Optional[Dict[str, Any]]:
        try:
            if isinstance(image_source, str):
                with open(image_source, 'rb') as f:
                    tags = exifread.process_file(f)
                    return self.parse_exif_gps(tags)
            else:
                # For in-memory images, we'd need to extract differently
                return None
        except Exception as e:
            print(f"Error extracting EXIF data: {e}")
            return None

    def parse_exif_gps(self, tags) -> Optional[Dict[str, Any]]:
        # Extract GPS coordinates from EXIF data
        gps_data = {}

        # Get latitude
        lat_ref = str(tags.get('GPS GPSLatitudeRef', ''))
        lat = tags.get('GPS GPSLatitude')

        # Get longitude
        lon_ref = str(tags.get('GPS GPSLongitudeRef', ''))
        lon = tags.get('GPS GPSLongitude')

        if lat and lon:
            gps_data['latitude'] = self.convert_to_degrees(lat.values)
            gps_data['longitude'] = self.convert_to_degrees(lon.values)

            if lat_ref and str(lat_ref).upper() == 'S':
                gps_data['latitude'] = -gps_data['latitude']
            if lon_ref and str(lon_ref).upper() == 'W':
                gps_data['longitude'] = -gps_data['longitude']

            return gps_data
        return None

    def convert_to_degrees(self, value) -> float:
        # Convert EXIF GPS coordinates to decimal degrees
        d = float(value[0].num) / float(value[0].den)
        m = float(value[1].num) / float(value[1].den)
        s = float(value[2].num) / float(value[2].den)
        return d + (m / 60.0) + (s / 3600.0)

    def analyze_image(self, image: Image.Image):
        # Basic image analysis to extract features
        # Convert to OpenCV format
        img_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

        # Extract basic features
        features = {
            'size': image.size,
            'mode': image.mode,
            'dominant_colors': self.get_dominant_colors(img_cv),
            'edges': len(cv2.Canny(img_cv, 100, 200)),
            'brightness': np.mean(img_cv)
        }
        return features

    def get_dominant_colors(self, img, k=5):
        # Simple dominant color extraction using k-means clustering
        data = img.reshape((-1, 3))
        data = np.float32(data)

        # For simplicity, return average color instead of clustering
        avg_color = np.mean(data, axis=0)
        return [tuple(avg_color.astype(int))]