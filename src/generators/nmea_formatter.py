"""NMEA message formatter for AIS data"""

import math
from datetime import datetime
from typing import List

from ..core.models import ShipState


class NMEAFormatter:
    """Formats AIS data into NMEA 0183 sentences"""
    
    @staticmethod
    def _encode_6bit(value: int, width: int) -> str:
        """Encode integer value as 6-bit ASCII armoring"""
        # AIS uses 6-bit encoding with character offset
        chars = "0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuvwxyz{|}~"
        
        result = ""
        for i in range(width):
            char_val = (value >> (6 * (width - 1 - i))) & 0x3F
            result += chars[char_val]
        
        return result
    
    @staticmethod
    def _latitude_to_ais(lat: float) -> int:
        """Convert latitude in degrees to AIS format (1/10000 arc minutes)"""
        return int(lat * 600000)  # Convert to 1/10000 arc minutes
    
    @staticmethod
    def _longitude_to_ais(lon: float) -> int:
        """Convert longitude in degrees to AIS format (1/10000 arc minutes)"""
        return int(lon * 600000)  # Convert to 1/10000 arc minutes
    
    @staticmethod
    def _speed_to_ais(speed_knots: float) -> int:
        """Convert speed in knots to AIS format (1/10 knots)"""
        return int(speed_knots * 10)
    
    @staticmethod
    def _course_to_ais(course_degrees: float) -> int:
        """Convert course in degrees to AIS format (1/10 degrees)"""
        return int(course_degrees * 10)
    
    @staticmethod
    def _calculate_checksum(sentence: str) -> str:
        """Calculate NMEA checksum"""
        checksum = 0
        for char in sentence:
            checksum ^= ord(char)
        return f"{checksum:02X}"
    
    def format_position_report(self, ship_state: ShipState, sequence_id: int = 0) -> str:
        """
        Format AIS message type 1 (Position Report Class A) as NMEA sentence
        
        This is a simplified version for demonstration purposes.
        A production implementation would need full AIS bit-level encoding.
        """
        
        # Create a simplified AIVDM sentence
        # In reality, this would involve complex bit-level encoding
        
        # Convert position to AIS format
        lat_ais = self._latitude_to_ais(ship_state.position.latitude)
        lon_ais = self._longitude_to_ais(ship_state.position.longitude)
        speed_ais = self._speed_to_ais(ship_state.speed_over_ground)
        course_ais = self._course_to_ais(ship_state.course_over_ground)
        
        # Simplified payload (in practice this would be properly bit-encoded)
        # This is a mock payload for demonstration
        payload = f"15MvEPH000G?tO`K>RA1wUbN0TKH"
        
        # Create AIVDM sentence parts
        total_sentences = 1
        sentence_number = 1
        message_id = sequence_id % 10
        channel = "A"
        
        # Build sentence without checksum
        sentence_core = f"AIVDM,{total_sentences},{sentence_number},{message_id},{channel},{payload},0"
        
        # Calculate checksum
        checksum = self._calculate_checksum(sentence_core)
        
        # Complete NMEA sentence
        nmea_sentence = f"!{sentence_core}*{checksum}"
        
        return nmea_sentence
    
    def format_realistic_position_report(self, ship_state: ShipState) -> str:
        """
        Format a more realistic NMEA sentence with actual position data
        (Still simplified, but includes real coordinates)
        """
        timestamp = ship_state.timestamp.strftime("%H%M%S")
        date = ship_state.timestamp.strftime("%d%m%y")
        
        # Create GPS-style position sentences that would accompany AIS
        gga_sentence = self._create_gga_sentence(ship_state, timestamp)
        rmc_sentence = self._create_rmc_sentence(ship_state, timestamp, date)
        
        return f"{gga_sentence}\\r\\n{rmc_sentence}"
    
    def _create_gga_sentence(self, ship_state: ShipState, timestamp: str) -> str:
        """Create GPGGA sentence (GPS Fix Data)"""
        lat = ship_state.position.latitude
        lon = ship_state.position.longitude
        
        # Convert to degrees and minutes
        lat_deg = int(abs(lat))
        lat_min = (abs(lat) - lat_deg) * 60
        lat_dir = "N" if lat >= 0 else "S"
        
        lon_deg = int(abs(lon))
        lon_min = (abs(lon) - lon_deg) * 60
        lon_dir = "E" if lon >= 0 else "W"
        
        sentence_core = f"GPGGA,{timestamp},{lat_deg:02d}{lat_min:07.4f},{lat_dir},{lon_deg:03d}{lon_min:07.4f},{lon_dir},1,08,1.0,10.0,M,0.0,M,,"
        checksum = self._calculate_checksum(sentence_core)
        
        return f"${sentence_core}*{checksum}"
    
    def _create_rmc_sentence(self, ship_state: ShipState, timestamp: str, date: str) -> str:
        """Create GPRMC sentence (Recommended Minimum Navigation Information)"""
        lat = ship_state.position.latitude
        lon = ship_state.position.longitude
        speed = ship_state.speed_over_ground
        course = ship_state.course_over_ground
        
        # Convert to degrees and minutes
        lat_deg = int(abs(lat))
        lat_min = (abs(lat) - lat_deg) * 60
        lat_dir = "N" if lat >= 0 else "S"
        
        lon_deg = int(abs(lon))
        lon_min = (abs(lon) - lon_deg) * 60
        lon_dir = "E" if lon >= 0 else "W"
        
        sentence_core = f"GPRMC,{timestamp},A,{lat_deg:02d}{lat_min:07.4f},{lat_dir},{lon_deg:03d}{lon_min:07.4f},{lon_dir},{speed:.1f},{course:.1f},{date},,"
        checksum = self._calculate_checksum(sentence_core)
        
        return f"${sentence_core}*{checksum}"
    
    def create_ais_summary(self, ship_state: ShipState) -> dict:
        """Create a JSON summary of AIS data for easy consumption"""
        return {
            "mmsi": ship_state.mmsi,
            "ship_name": ship_state.ship_name,
            "position": {
                "latitude": ship_state.position.latitude,
                "longitude": ship_state.position.longitude
            },
            "speed_knots": ship_state.speed_over_ground,
            "course_degrees": ship_state.course_over_ground,
            "heading_degrees": ship_state.heading,
            "navigation_status": ship_state.navigation_status.name,
            "ship_type": ship_state.ship_type.name,
            "dimensions": {
                "length": ship_state.length,
                "width": ship_state.width,
                "draught": ship_state.draught
            },
            "timestamp": ship_state.timestamp.isoformat()
        }
