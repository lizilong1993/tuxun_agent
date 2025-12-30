"""
Geolocation Database Module for TuXun Agent
Handles storage and retrieval of geotagged images and location data
"""
import sqlite3
import os
from typing import List, Dict, Any, Optional
import numpy as np
import faiss
import pickle
from dataclasses import dataclass

@dataclass
class LocationData:
    id: int
    latitude: float
    longitude: float
    image_path: str
    features: Optional[np.ndarray] = None
    description: Optional[str] = None

class GeolocationDB:
    def __init__(self, db_path: str = "geolocation.db", vector_db_path: str = "vector_db.faiss"):
        self.db_path = db_path
        self.vector_db_path = vector_db_path
        self.conn = None
        self.index = None
        self._initialize_database()
        self._initialize_vector_db()
    
    def _initialize_database(self):
        """Initialize the SQLite database with required tables"""
        self.conn = sqlite3.connect(self.db_path)
        cursor = self.conn.cursor()
        
        # Create locations table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS locations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                latitude REAL NOT NULL,
                longitude REAL NOT NULL,
                image_path TEXT,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create image features table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS image_features (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                location_id INTEGER,
                feature_vector BLOB,
                feature_type TEXT,
                FOREIGN KEY (location_id) REFERENCES locations (id)
            )
        ''')
        
        self.conn.commit()
    
    def _initialize_vector_db(self):
        """Initialize the FAISS vector database for similarity search"""
        # Create a simple FAISS index for image feature vectors (128 dimensions as example)
        dimension = 128  # This would match the size of our feature vectors
        self.index = faiss.IndexFlatL2(dimension)
        
        # Load existing index if it exists
        if os.path.exists(self.vector_db_path):
            self.index = faiss.read_index(self.vector_db_path)
    
    def add_location(self, latitude: float, longitude: float, image_path: str, 
                    description: Optional[str] = None) -> int:
        """Add a new geotagged location to the database"""
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO locations (latitude, longitude, image_path, description)
            VALUES (?, ?, ?, ?)
        ''', (latitude, longitude, image_path, description))
        
        location_id = cursor.lastrowid
        self.conn.commit()
        
        return location_id
    
    def add_image_features(self, location_id: int, feature_vector: np.ndarray, 
                         feature_type: str = "visual"):
        """Add image features for a location"""
        cursor = self.conn.cursor()
        
        # Serialize the feature vector
        feature_blob = pickle.dumps(feature_vector)
        
        cursor.execute('''
            INSERT INTO image_features (location_id, feature_vector, feature_type)
            VALUES (?, ?, ?)
        ''', (location_id, feature_blob, feature_type))
        
        self.conn.commit()
        
        # Add to FAISS index
        feature_vector = feature_vector.astype('float32').reshape(1, -1)
        self.index.add(feature_vector)
        
        # Save the updated index
        faiss.write_index(self.index, self.vector_db_path)
    
    def get_location_by_id(self, location_id: int) -> Optional[LocationData]:
        """Retrieve a location by its ID"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT id, latitude, longitude, image_path, description
            FROM locations
            WHERE id = ?
        ''', (location_id,))
        
        row = cursor.fetchone()
        if row:
            return LocationData(
                id=row[0],
                latitude=row[1],
                longitude=row[2],
                image_path=row[3],
                description=row[4]
            )
        return None
    
    def find_similar_locations(self, query_features: np.ndarray, k: int = 5) -> List[LocationData]:
        """Find locations with similar image features using FAISS"""
        if query_features.size != self.index.d:
            # Resize or handle dimension mismatch
            if query_features.size > self.index.d:
                query_features = query_features[:self.index.d]
            else:
                # Pad with zeros
                padded = np.zeros(self.index.d)
                padded[:query_features.size] = query_features
                query_features = padded
        
        query_features = query_features.astype('float32').reshape(1, -1)
        
        # Search for similar vectors
        distances, indices = self.index.search(query_features, k)
        
        # Retrieve location data for the similar indices
        similar_locations = []
        for idx in indices[0]:
            if idx != -1:  # FAISS returns -1 for empty slots
                # In a real implementation, we'd map the FAISS index to our database ID
                # For now, we'll return empty location data
                similar_locations.append(LocationData(
                    id=idx,
                    latitude=0.0,
                    longitude=0.0,
                    image_path="",
                    description="Similar location"
                ))
        
        return similar_locations
    
    def search_by_coordinates(self, latitude: float, longitude: float, 
                           radius_km: float = 10.0) -> List[LocationData]:
        """Search for locations within a radius of the given coordinates"""
        # Simple implementation using haversine formula
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT id, latitude, longitude, image_path, description
            FROM locations
            WHERE 6371 * acos(
                cos(radians(?)) * 
                cos(radians(latitude)) * 
                cos(radians(longitude) - radians(?)) + 
                sin(radians(?)) * 
                sin(radians(latitude))
            ) <= ?
        ''', (latitude, longitude, latitude, radius_km))
        
        rows = cursor.fetchall()
        locations = []
        for row in rows:
            locations.append(LocationData(
                id=row[0],
                latitude=row[1],
                longitude=row[2],
                image_path=row[3],
                description=row[4]
            ))
        
        return locations
    
    def close(self):
        """Close database connections"""
        if self.conn:
            self.conn.close()