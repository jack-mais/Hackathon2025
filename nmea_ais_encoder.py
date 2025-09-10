#!/usr/bin/env python3
"""
NMEA AIS Message Encoder

This module provides functionality to encode vessel track data into NMEA AIS messages
for types 1, 2, 3 (Position Reports) and type 5 (Static and Voyage Related Data).

AIS Message Types:
- Type 1: Position Report Class A (assigned schedule)
- Type 2: Position Report Class A (assigned schedule) 
- Type 3: Position Report Class A (special position indicator, MMSI polled)
- Type 5: Static and Voyage Related Data

NMEA 0183 Format:
!AIVDM,1,1,,A,message_payload,0*checksum
"""

import math
import json
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone


class NMEAAISEncoder:
    """Encoder for NMEA AIS messages from vessel track data"""
    
    def __init__(self):
        # AIS message type definitions
        self.message_types = {
            1: "Position Report Class A (assigned schedule)",
            2: "Position Report Class A (assigned schedule)", 
            3: "Position Report Class A (special position indicator, MMSI polled)",
            5: "Static and Voyage Related Data"
        }
    
    def encode_tracks_to_nmea(self, tracks_data: Dict[str, Any], message_types: List[int] = [1, 2, 3, 5]) -> Dict[str, Any]:
        """
        Convert vessel tracks JSON to NMEA AIS messages
        
        Args:
            tracks_data: JSON data containing vessel tracks
            message_types: List of AIS message types to generate (1, 2, 3, 5)
            
        Returns:
            Dictionary containing NMEA messages organized by vessel and message type
        """
        result = {
            "metadata": {
                "total_vessels": 0,
                "total_messages": 0,
                "message_types_generated": message_types,
                "generated_at": datetime.now(timezone.utc).isoformat()
            },
            "vessels": {}
        }
        
        if 'tracks' not in tracks_data:
            raise ValueError("Invalid tracks data: missing 'tracks' key")
        
        tracks = tracks_data['tracks']
        result["metadata"]["total_vessels"] = len(tracks)
        
        for track in tracks:
            mmsi = track.get('mmsi')
            if not mmsi:
                continue
                
            vessel_messages = self._encode_vessel_track(track, message_types)
            result["vessels"][str(mmsi)] = vessel_messages
            result["metadata"]["total_messages"] += sum(len(msgs) for msgs in vessel_messages.values())
        
        return result
    
    def _encode_vessel_track(self, track: Dict[str, Any], message_types: List[int]) -> Dict[str, List[str]]:
        """Encode a single vessel track into NMEA messages"""
        vessel_messages = {}
        
        # Generate static data (Type 5) - only once per vessel
        if 5 in message_types:
            vessel_messages["type_5"] = [self._encode_type_5(track)]
        
        # Generate position reports (Types 1, 2, 3) for each track point
        position_messages = []
        for point in track.get('points', []):
            if 1 in message_types:
                position_messages.append(self._encode_type_1(point, track))
            if 2 in message_types:
                position_messages.append(self._encode_type_2(point, track))
            if 3 in message_types:
                position_messages.append(self._encode_type_3(point, track))
        
        if position_messages:
            vessel_messages["position_reports"] = position_messages
        
        return vessel_messages
    
    def _encode_type_1(self, point: Dict[str, Any], track: Dict[str, Any]) -> str:
        """Encode Type 1: Position Report Class A (assigned schedule)"""
        return self._encode_position_report(point, track, message_type=1)
    
    def _encode_type_2(self, point: Dict[str, Any], track: Dict[str, Any]) -> str:
        """Encode Type 2: Position Report Class A (assigned schedule)"""
        return self._encode_position_report(point, track, message_type=2)
    
    def _encode_type_3(self, point: Dict[str, Any], track: Dict[str, Any]) -> str:
        """Encode Type 3: Position Report Class A (special position indicator, MMSI polled)"""
        return self._encode_position_report(point, track, message_type=3)
    
    def _encode_position_report(self, point: Dict[str, Any], track: Dict[str, Any], message_type: int) -> str:
        """Encode position report messages (Types 1, 2, 3)"""
        mmsi = int(track.get('mmsi', 0))
        lat = float(point.get('latitude', 0.0))
        lon = float(point.get('longitude', 0.0))
        speed = float(point.get('speed_over_ground', 0.0))
        course = float(point.get('course_over_ground', 0.0))
        heading = float(point.get('true_heading', 0.0))
        # Handle timestamp - could be ISO string or Unix timestamp
        timestamp_raw = point.get('timestamp', 0)
        if isinstance(timestamp_raw, str):
            # If it's an ISO string, convert to Unix timestamp
            from datetime import datetime
            try:
                dt = datetime.fromisoformat(timestamp_raw.replace('Z', '+00:00'))
                timestamp = int(dt.timestamp()) % 60  # Use seconds part for AIS timestamp
            except:
                timestamp = 0
        else:
            timestamp = int(timestamp_raw) % 60  # Use seconds part for AIS timestamp
        
        # Convert to AIS format
        ais_lat = int((lat + 90) * 600000)  # Convert to 1/60000 minutes
        ais_lon = int((lon + 180) * 600000)  # Convert to 1/60000 minutes
        ais_speed = int(speed * 10)  # Convert to 1/10 knots
        ais_course = int(course * 10)  # Convert to 1/10 degrees
        ais_heading = int(heading)  # Convert to degrees
        
        # Navigation status (0 = under way using engine)
        nav_status = 0
        
        # Rate of turn (0 = not available)
        rot = 0
        
        # Position accuracy (0 = low, 1 = high)
        pos_acc = 1
        
        # RAIM flag (0 = not in use, 1 = in use)
        raim = 0
        
        # Radio status (0 = default)
        radio_status = 0
        
        # Build the 6-bit encoded message
        # This is a simplified encoding - real AIS uses complex bit packing
        message_bits = self._build_position_message_bits(
            message_type, mmsi, nav_status, rot, ais_speed, pos_acc, 
            ais_lon, ais_lat, ais_course, ais_heading, timestamp, 
            raim, radio_status
        )
        
        # Convert to NMEA format
        return self._bits_to_nmea(message_bits)
    
    def _encode_type_5(self, track: Dict[str, Any]) -> str:
        """Encode Type 5: Static and Voyage Related Data"""
        mmsi = int(track.get('mmsi', 0))
        vessel_class = track.get('vessel_class', 'Unknown')
        
        # Vessel name (max 20 characters, padded with @)
        vessel_name = self._get_vessel_name(vessel_class)
        vessel_name = vessel_name[:20].ljust(20, '@')
        
        # Ship type (simplified mapping)
        ship_type = self._get_ship_type_code(vessel_class)
        
        # Call sign (8 characters, padded with @)
        call_sign = f"MMSI{int(mmsi):04d}"[:8].ljust(8, '@')
        
        # IMO number (0 = not available)
        imo = 0
        
        # Destination (max 20 characters, padded with @)
        destination = "UNKNOWN"[:20].ljust(20, '@')
        
        # ETA (estimated time of arrival)
        eta_month = 0
        eta_day = 0
        eta_hour = 0
        eta_minute = 0
        
        # Draught (1/10 meters)
        draught = 0
        
        # DTE (data terminal equipment ready)
        dte = 0
        
        # Spare
        spare = 0
        
        # Build the 6-bit encoded message
        message_bits = self._build_static_message_bits(
            5, mmsi, vessel_name, ship_type, call_sign, imo, 
            destination, eta_month, eta_day, eta_hour, eta_minute, 
            draught, dte, spare
        )
        
        # Convert to NMEA format
        return self._bits_to_nmea(message_bits)
    
    def _build_position_message_bits(self, msg_type: int, mmsi: int, nav_status: int, 
                                   rot: int, speed: int, pos_acc: int, lon: int, 
                                   lat: int, course: int, heading: int, timestamp: int,
                                   raim: int, radio_status: int) -> str:
        """Build 6-bit encoded message for position reports"""
        # This is a simplified implementation
        # Real AIS uses complex bit packing with specific field sizes
        
        # Convert to binary strings (simplified)
        bits = f"{msg_type:06b}"  # Message type (6 bits)
        bits += f"{mmsi:030b}"    # MMSI (30 bits)
        bits += f"{nav_status:04b}"  # Navigation status (4 bits)
        bits += f"{rot:08b}"      # Rate of turn (8 bits)
        bits += f"{speed:010b}"   # Speed over ground (10 bits)
        bits += f"{pos_acc:01b}"  # Position accuracy (1 bit)
        bits += f"{lon:028b}"     # Longitude (28 bits)
        bits += f"{lat:027b}"     # Latitude (27 bits)
        bits += f"{course:012b}"  # Course over ground (12 bits)
        bits += f"{heading:09b}"  # True heading (9 bits)
        bits += f"{timestamp:06b}"  # Time stamp (6 bits)
        bits += f"{raim:01b}"     # RAIM flag (1 bit)
        bits += f"{radio_status:019b}"  # Radio status (19 bits)
        
        return bits
    
    def _build_static_message_bits(self, msg_type: int, mmsi: int, vessel_name: str,
                                 ship_type: int, call_sign: str, imo: int,
                                 destination: str, eta_month: int, eta_day: int,
                                 eta_hour: int, eta_minute: int, draught: int,
                                 dte: int, spare: int) -> str:
        """Build 6-bit encoded message for static data"""
        # This is a simplified implementation
        bits = f"{msg_type:06b}"  # Message type (6 bits)
        bits += f"{mmsi:030b}"    # MMSI (30 bits)
        
        # Vessel name (120 bits = 20 chars * 6 bits)
        for char in vessel_name:
            ascii_val = ord(char) if char != '@' else 0
            bits += f"{ascii_val:06b}"
        
        bits += f"{ship_type:08b}"  # Ship type (8 bits)
        
        # Call sign (48 bits = 8 chars * 6 bits)
        for char in call_sign:
            ascii_val = ord(char) if char != '@' else 0
            bits += f"{ascii_val:06b}"
        
        bits += f"{imo:030b}"     # IMO number (30 bits)
        
        # Destination (120 bits = 20 chars * 6 bits)
        for char in destination:
            ascii_val = ord(char) if char != '@' else 0
            bits += f"{ascii_val:06b}"
        
        bits += f"{eta_month:04b}"   # ETA month (4 bits)
        bits += f"{eta_day:05b}"     # ETA day (5 bits)
        bits += f"{eta_hour:05b}"    # ETA hour (5 bits)
        bits += f"{eta_minute:06b}"  # ETA minute (6 bits)
        bits += f"{draught:08b}"     # Draught (8 bits)
        bits += f"{dte:01b}"         # DTE (1 bit)
        bits += f"{spare:01b}"       # Spare (1 bit)
        
        return bits
    
    def _bits_to_nmea(self, bits: str) -> str:
        """Convert 6-bit encoded message to NMEA format"""
        # Pad bits to multiple of 6
        while len(bits) % 6 != 0:
            bits += "0"
        
        # Convert 6-bit groups to ASCII
        payload = ""
        for i in range(0, len(bits), 6):
            six_bits = bits[i:i+6]
            ascii_val = int(six_bits, 2)
            if ascii_val < 40:
                ascii_val += 48  # Convert to printable ASCII
            else:
                ascii_val += 56
            payload += chr(ascii_val)
        
        # Calculate checksum
        checksum = 0
        for char in payload:
            checksum ^= ord(char)
        
        # Format as NMEA message
        nmea = f"!AIVDM,1,1,,A,{payload},0*{checksum:02X}"
        return nmea
    
    def _get_vessel_name(self, vessel_class: str) -> str:
        """Get vessel name based on class"""
        name_mapping = {
            'Class A': 'VESSEL_A',
            'Class B': 'VESSEL_B', 
            'Cargo': 'CARGO_SHIP',
            'Tanker': 'TANKER',
            'Fishing': 'FISHING_VSL',
            'Passenger': 'PASSENGER',
            'Pleasure': 'PLEASURE',
            'Unknown': 'UNKNOWN_VSL'
        }
        return name_mapping.get(vessel_class, 'UNKNOWN_VSL')
    
    def _get_ship_type_code(self, vessel_class: str) -> int:
        """Get AIS ship type code based on vessel class"""
        type_mapping = {
            'Class A': 70,      # Cargo, all ships of this type
            'Class B': 70,      # Cargo, all ships of this type
            'Cargo': 70,        # Cargo, all ships of this type
            'Tanker': 80,       # Tanker, all ships of this type
            'Fishing': 30,      # Fishing
            'Passenger': 60,    # Passenger, all ships of this type
            'Pleasure': 37,     # Pleasure craft
            'Unknown': 0        # Not available
        }
        return type_mapping.get(vessel_class, 0)
    
    def format_nmea_output(self, nmea_data: Dict[str, Any], format_type: str = "detailed") -> str:
        """Format NMEA data for output"""
        if format_type == "simple":
            return self._format_simple(nmea_data)
        elif format_type == "by_vessel":
            return self._format_by_vessel(nmea_data)
        else:
            return self._format_detailed(nmea_data)
    
    def _format_simple(self, nmea_data: Dict[str, Any]) -> str:
        """Format as simple list of NMEA messages"""
        messages = []
        for vessel_id, vessel_data in nmea_data.get("vessels", {}).items():
            for msg_type, msg_list in vessel_data.items():
                messages.extend(msg_list)
        
        return "\n".join(messages)
    
    def _format_by_vessel(self, nmea_data: Dict[str, Any]) -> str:
        """Format grouped by vessel"""
        output = []
        output.append("NMEA AIS Messages by Vessel:")
        output.append("=" * 50)
        
        for vessel_id, vessel_data in nmea_data.get("vessels", {}).items():
            output.append(f"\nVessel MMSI: {vessel_id}")
            output.append("-" * 30)
            
            for msg_type, msg_list in vessel_data.items():
                output.append(f"\n{msg_type.upper()}:")
                for msg in msg_list:
                    output.append(f"  {msg}")
        
        return "\n".join(output)
    
    def _format_detailed(self, nmea_data: Dict[str, Any]) -> str:
        """Format with detailed metadata"""
        output = []
        metadata = nmea_data.get("metadata", {})
        
        output.append("NMEA AIS Message Export")
        output.append("=" * 50)
        output.append(f"Generated: {metadata.get('generated_at', 'Unknown')}")
        output.append(f"Total Vessels: {metadata.get('total_vessels', 0)}")
        output.append(f"Total Messages: {metadata.get('total_messages', 0)}")
        output.append(f"Message Types: {', '.join(map(str, metadata.get('message_types_generated', [])))}")
        output.append("\n" + "=" * 50)
        
        for vessel_id, vessel_data in nmea_data.get("vessels", {}).items():
            output.append(f"\nVessel MMSI: {vessel_id}")
            output.append("-" * 30)
            
            for msg_type, msg_list in vessel_data.items():
                output.append(f"\n{msg_type.upper()} ({len(msg_list)} messages):")
                for i, msg in enumerate(msg_list, 1):
                    output.append(f"  {i:3d}: {msg}")
        
        return "\n".join(output)
