"""
Track A/B Data Format Converter
===============================

Provides conversion layer between Track A and Track B data formats
to ensure compatibility during integration.

Key Features:
- Converts between Track A 'result' and Track B 'data' response fields
- Maintains backward compatibility
- Transparent conversion during runtime
- Preserves all data integrity

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary - See LICENSE file for terms
"""

from typing import Dict, Any, Union, Optional
import logging
from datetime import datetime


class FormatConverter:
    """
    Converts data formats between Track A and Track B for compatibility.
    
    Track A Format: {"status": str, "result": Any, ...}
    Track B Format: {"status": str, "data": Any, ...}
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.conversion_stats = {
            "a_to_b_conversions": 0,
            "b_to_a_conversions": 0,
            "errors": 0,
            "last_conversion": None
        }
    
    def convert_track_a_to_track_b(self, track_a_response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert Track A response format to Track B format.
        
        Converts 'result' field to 'data' field while preserving all other fields.
        
        Args:
            track_a_response: Response in Track A format {"status": ..., "result": ...}
            
        Returns:
            Response in Track B format {"status": ..., "data": ...}
        """
        try:
            if not isinstance(track_a_response, dict):
                raise ValueError("Response must be a dictionary")
            
            # Create copy to avoid modifying original
            track_b_response = track_a_response.copy()
            
            # Convert 'result' to 'data'
            if "result" in track_b_response:
                track_b_response["data"] = track_b_response.pop("result")
            
            # Add conversion metadata if not present
            if "_format_version" not in track_b_response:
                track_b_response["_format_version"] = "track_b"
            
            self._update_stats("a_to_b")
            self.logger.debug("Successfully converted Track A response to Track B format")
            
            return track_b_response
            
        except Exception as e:
            self._update_stats("error")
            self.logger.error(f"Failed to convert Track A to Track B response: {e}")
            raise
    
    def convert_track_b_to_track_a(self, track_b_response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert Track B response format to Track A format.
        
        Converts 'data' field to 'result' field while preserving all other fields.
        
        Args:
            track_b_response: Response in Track B format {"status": ..., "data": ...}
            
        Returns:
            Response in Track A format {"status": ..., "result": ...}
        """
        try:
            if not isinstance(track_b_response, dict):
                raise ValueError("Response must be a dictionary")
            
            # Create copy to avoid modifying original
            track_a_response = track_b_response.copy()
            
            # Convert 'data' to 'result'
            if "data" in track_a_response:
                track_a_response["result"] = track_a_response.pop("data")
            
            # Add conversion metadata if not present
            if "_format_version" not in track_a_response:
                track_a_response["_format_version"] = "track_a"
            
            # Remove Track B specific metadata
            track_a_response.pop("_track_b_metadata", None)
            
            self._update_stats("b_to_a")
            self.logger.debug("Successfully converted Track B response to Track A format")
            
            return track_a_response
            
        except Exception as e:
            self._update_stats("error")
            self.logger.error(f"Failed to convert Track B to Track A response: {e}")
            raise
    
    def auto_convert_response(self, response: Dict[str, Any], target_format: str) -> Dict[str, Any]:
        """
        Automatically convert response to target format.
        
        Args:
            response: Response dictionary in any format
            target_format: 'track_a' or 'track_b'
            
        Returns:
            Response converted to target format
        """
        if not isinstance(response, dict):
            return response
        
        current_format = self.detect_response_format(response)
        
        if current_format == target_format:
            return response  # Already in correct format
        
        if target_format == "track_a":
            return self.convert_track_b_to_track_a(response)
        elif target_format == "track_b":
            return self.convert_track_a_to_track_b(response)
        else:
            raise ValueError(f"Unknown target format: {target_format}")
    
    def detect_response_format(self, response: Dict[str, Any]) -> str:
        """
        Detect whether response is in Track A or Track B format.
        
        Args:
            response: Response dictionary
            
        Returns:
            'track_a', 'track_b', or 'unknown'
        """
        if not isinstance(response, dict):
            return "unknown"
        
        # Check explicit format version
        format_version = response.get("_format_version")
        if format_version in ["track_a", "track_b"]:
            return format_version
        
        # Detect by field presence
        has_result = "result" in response
        has_data = "data" in response
        
        if has_result and not has_data:
            return "track_a"
        elif has_data and not has_result:
            return "track_b"
        elif has_result and has_data:
            # Both present - check which is primary
            self.logger.warning("Response has both 'result' and 'data' fields - using 'result' as primary")
            return "track_a"
        else:
            # Neither present - likely a different format
            return "unknown"
    
    def is_conversion_needed(self, response: Dict[str, Any], target_format: str) -> bool:
        """
        Check if conversion is needed for the response.
        
        Args:
            response: Response dictionary
            target_format: 'track_a' or 'track_b'
            
        Returns:
            True if conversion is needed, False otherwise
        """
        current_format = self.detect_response_format(response)
        return current_format != target_format and current_format != "unknown"
    
    def create_compatible_response(self, 
                                 status: str, 
                                 data: Any, 
                                 format_type: str = "universal",
                                 **kwargs) -> Dict[str, Any]:
        """
        Create a response compatible with both Track A and Track B.
        
        Args:
            status: Response status
            data: Response data/result
            format_type: 'track_a', 'track_b', or 'universal'
            **kwargs: Additional response fields
            
        Returns:
            Response dictionary in specified format
        """
        base_response = {
            "status": status,
            "timestamp": datetime.now().isoformat(),
            **kwargs
        }
        
        if format_type == "track_a":
            base_response["result"] = data
            base_response["_format_version"] = "track_a"
        elif format_type == "track_b":
            base_response["data"] = data
            base_response["_format_version"] = "track_b"
        else:  # universal
            # Include both for maximum compatibility
            base_response["result"] = data
            base_response["data"] = data
            base_response["_format_version"] = "universal"
        
        return base_response
    
    def _update_stats(self, operation_type: str):
        """Update conversion statistics."""
        if operation_type == "a_to_b":
            self.conversion_stats["a_to_b_conversions"] += 1
        elif operation_type == "b_to_a":
            self.conversion_stats["b_to_a_conversions"] += 1
        elif operation_type == "error":
            self.conversion_stats["errors"] += 1
        
        self.conversion_stats["last_conversion"] = datetime.now().isoformat()
    
    def get_conversion_stats(self) -> Dict[str, Any]:
        """Get conversion statistics."""
        return self.conversion_stats.copy()
    
    def clear_stats(self):
        """Clear conversion statistics."""
        self.conversion_stats = {
            "a_to_b_conversions": 0,
            "b_to_a_conversions": 0,
            "errors": 0,
            "last_conversion": None
        }


# Global converter instance for easy access
_format_converter = FormatConverter()

def convert_to_track_a(response: Dict[str, Any]) -> Dict[str, Any]:
    """Convenience function to convert response to Track A format."""
    return _format_converter.convert_track_b_to_track_a(response)

def convert_to_track_b(response: Dict[str, Any]) -> Dict[str, Any]:
    """Convenience function to convert response to Track B format."""
    return _format_converter.convert_track_a_to_track_b(response)

def auto_convert(response: Dict[str, Any], target_format: str) -> Dict[str, Any]:
    """Convenience function to auto-convert response to target format."""
    return _format_converter.auto_convert_response(response, target_format)

def create_universal_response(status: str, data: Any, **kwargs) -> Dict[str, Any]:
    """Convenience function to create universally compatible response."""
    return _format_converter.create_compatible_response(status, data, "universal", **kwargs)