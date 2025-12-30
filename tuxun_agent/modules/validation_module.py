"""
Validation Module for TuXun Agent
Validates geolocation results and provides confidence scoring
"""
from typing import Dict, Any, List, Tuple
import math
from geopy.distance import geodesic

class ValidationModule:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.confidence_threshold = config.get('CONFIDENCE_THRESHOLD', 0.7)
    
    def validate_location_prediction(self, prediction: Dict[str, Any], 
                                  image_features: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Validate a location prediction and adjust confidence based on various factors
        """
        validated_result = prediction.copy()
        
        # Calculate additional validation metrics
        validation_metrics = self._calculate_validation_metrics(prediction, image_features)
        
        # Update confidence based on validation
        adjusted_confidence = self._adjust_confidence(
            prediction.get('predicted_location', {}).get('confidence', 0.5),
            validation_metrics
        )
        
        # Update the prediction with validation results
        validated_result['predicted_location']['confidence'] = adjusted_confidence
        validated_result['validation_metrics'] = validation_metrics
        validated_result['is_reliable'] = adjusted_confidence >= self.confidence_threshold
        
        return validated_result
    
    def _calculate_validation_metrics(self, prediction: Dict[str, Any], 
                                   image_features: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Calculate various validation metrics for the prediction
        """
        metrics = {
            'consistency_score': 0.0,
            'feature_matching_score': 0.0,
            'confidence_calibration': 1.0,
            'outlier_detection': False,
            'validation_notes': []
        }
        
        # Check consistency between predicted location and alternative locations
        predicted_loc = prediction.get('predicted_location', {})
        alternatives = prediction.get('alternative_locations', [])
        
        if alternatives:
            # Calculate consistency with alternatives
            consistency_score = self._check_consistency_with_alternatives(
                predicted_loc, alternatives
            )
            metrics['consistency_score'] = consistency_score
        
        # If we have image features, check if they're consistent with the location
        if image_features:
            feature_score = self._check_feature_consistency(
                predicted_loc, image_features
            )
            metrics['feature_matching_score'] = feature_score
        
        # Check if the predicted location seems reasonable
        is_outlier = self._is_outlier_location(predicted_loc)
        metrics['outlier_detection'] = is_outlier
        if is_outlier:
            metrics['validation_notes'].append("Predicted location appears to be an outlier")
        
        return metrics
    
    def _check_consistency_with_alternatives(self, predicted_loc: Dict[str, Any], 
                                           alternatives: List[Dict[str, Any]]) -> float:
        """
        Check how consistent the main prediction is with alternative predictions
        """
        if not alternatives:
            return 1.0  # No alternatives to compare with
        
        predicted_coords = (predicted_loc.get('latitude', 0), 
                           predicted_loc.get('longitude', 0))
        
        # Calculate distances to alternatives
        distances = []
        for alt in alternatives:
            alt_coords = (alt.get('latitude', 0), alt.get('longitude', 0))
            try:
                distance = geodesic(predicted_coords, alt_coords).kilometers
                distances.append(distance)
            except:
                continue
        
        if not distances:
            return 1.0
        
        # Calculate consistency (inverse of average distance to alternatives)
        avg_distance = sum(distances) / len(distances)
        
        # Normalize to 0-1 scale (lower distance = higher consistency)
        # Using a sigmoid-like function to map distances to consistency scores
        consistency = 1 / (1 + avg_distance / 10)  # Adjust divisor as needed
        
        return min(consistency, 1.0)
    
    def _check_feature_consistency(self, predicted_loc: Dict[str, Any], 
                                 image_features: Dict[str, Any]) -> float:
        """
        Check if image features are consistent with the predicted location
        """
        # This is a simplified implementation
        # In a real system, this would compare image features with 
        # expected features for the predicted location
        
        # For now, return a neutral score
        return 0.5
    
    def _is_outlier_location(self, predicted_loc: Dict[str, Any]) -> bool:
        """
        Check if the predicted location is an outlier (e.g., ocean, uninhabited area)
        """
        lat = predicted_loc.get('latitude', 0)
        lon = predicted_loc.get('longitude', 0)
        
        # Basic checks for obviously wrong locations
        if abs(lat) > 90 or abs(lon) > 180:
            return True  # Invalid coordinates
        
        # Check if it's in the middle of an ocean (very simplified)
        # This would require more sophisticated geographic data in practice
        if -5 < lat < 5 and -170 < lon < -160:
            # Pacific Ocean area
            return True
        
        return False
    
    def _adjust_confidence(self, original_confidence: float, 
                          validation_metrics: Dict[str, Any]) -> float:
        """
        Adjust confidence based on validation metrics
        """
        # Start with original confidence
        adjusted_confidence = original_confidence
        
        # Apply consistency adjustment
        consistency_factor = validation_metrics.get('consistency_score', 0.5)
        adjusted_confidence *= (0.7 + 0.3 * consistency_factor)  # Weighted adjustment
        
        # Apply feature matching adjustment
        feature_factor = validation_metrics.get('feature_matching_score', 0.5)
        adjusted_confidence *= (0.8 + 0.2 * feature_factor)
        
        # Apply outlier penalty
        if validation_metrics.get('outlier_detection', False):
            adjusted_confidence *= 0.5  # Significant penalty for outliers
        
        # Ensure confidence is within bounds
        adjusted_confidence = max(0.0, min(1.0, adjusted_confidence))
        
        return adjusted_confidence
    
    def cross_validate_with_external_sources(self, prediction: Dict[str, Any], 
                                          external_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Cross-validate prediction with external data sources
        """
        validation_result = {
            'cross_validation_score': 0.0,
            'external_agreement': [],
            'discrepancies': [],
            'final_confidence': prediction.get('predicted_location', {}).get('confidence', 0.5)
        }
        
        predicted_coords = (
            prediction.get('predicted_location', {}).get('latitude', 0),
            prediction.get('predicted_location', {}).get('longitude', 0)
        )
        
        if not external_data:
            return validation_result
        
        agreements = []
        discrepancies = []
        
        for source_data in external_data:
            source_coords = (source_data.get('latitude', 0), source_data.get('longitude', 0))
            
            try:
                distance = geodesic(predicted_coords, source_coords).kilometers
                
                if distance < 1:  # Less than 1km considered agreement
                    agreements.append({
                        'source': source_data.get('source', 'unknown'),
                        'distance_km': distance,
                        'confidence': source_data.get('confidence', 0.8)
                    })
                else:
                    discrepancies.append({
                        'source': source_data.get('source', 'unknown'),
                        'distance_km': distance,
                        'predicted_coords': predicted_coords,
                        'source_coords': source_coords
                    })
            except:
                continue
        
        # Calculate cross-validation score based on agreements
        if agreements:
            avg_confidence = sum(a['confidence'] for a in agreements) / len(agreements)
            validation_result['cross_validation_score'] = min(avg_confidence, 1.0)
        else:
            validation_result['cross_validation_score'] = 0.0
        
        validation_result['external_agreement'] = agreements
        validation_result['discrepancies'] = discrepancies
        
        # Adjust final confidence based on cross-validation
        base_confidence = prediction.get('predicted_location', {}).get('confidence', 0.5)
        cv_score = validation_result['cross_validation_score']
        
        # Weighted combination of original and cross-validation confidence
        final_confidence = 0.7 * base_confidence + 0.3 * cv_score
        validation_result['final_confidence'] = min(final_confidence, 1.0)
        
        return validation_result