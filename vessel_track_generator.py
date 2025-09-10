#!/usr/bin/env python3
"""
Vessel Track Generator - Core Implementation

This module provides the core functionality for generating realistic vessel tracks
based on natural language prompts.
"""

import re
import random
import math
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass
class VesselParameters:
    """Parameters extracted from user prompt"""
    vessel_count: int = 10
    vessel_classes: List[str] = None
    voyage_type: str = "random"
    duration_hours: int = 24
    start_region: Optional[str] = None
    end_region: Optional[str] = None
    speed_range: Tuple[float, float] = (5.0, 25.0)  # knots
    point_interval_minutes: int = 15

    def __post_init__(self):
        if self.vessel_classes is None:
            self.vessel_classes = ["A", "B"]

@dataclass
class TrackPoint:
    """Single point in a vessel track"""
    latitude: float
    longitude: float
    timestamp: str
    speed_over_ground: float
    course_over_ground: float
    heading: float

@dataclass
class VesselTrack:
    """Complete track for a single vessel"""
    mmsi: str
    vessel_class: str
    points: List[TrackPoint]

class VesselPromptParser:
    """Parses natural language prompts to extract vessel track parameters"""
    
    # Common vessel classes and their characteristics
    VESSEL_CLASSES = {
        "A": {"name": "Class A", "speed_range": (8.0, 20.0), "typical_routes": "coastal"},
        "B": {"name": "Class B", "speed_range": (5.0, 15.0), "typical_routes": "coastal"},
        "cargo": {"name": "Cargo Ship", "speed_range": (10.0, 25.0), "typical_routes": "international"},
        "tanker": {"name": "Tanker", "speed_range": (8.0, 20.0), "typical_routes": "international"},
        "fishing": {"name": "Fishing Vessel", "speed_range": (3.0, 12.0), "typical_routes": "coastal"},
        "passenger": {"name": "Passenger Ship", "speed_range": (15.0, 30.0), "typical_routes": "coastal"},
        "yacht": {"name": "Yacht", "speed_range": (5.0, 35.0), "typical_routes": "coastal"}
    }
    
    # Common voyage types
    VOYAGE_TYPES = {
        "point to point": "point_to_point",
        "point-to-point": "point_to_point", 
        "random": "random",
        "circular": "circular",
        "patrol": "patrol",
        "fishing": "fishing_pattern"
    }
    
    # Common regions and their coordinates
    REGIONS = {
        "rotterdam": (51.9244, 4.4777),
        "singapore": (1.3521, 103.8198),
        "hamburg": (53.5511, 9.9937),
        "antwerp": (51.2194, 4.4025),
        "london": (51.5074, -0.1278),
        "new york": (40.7128, -74.0060),
        "los angeles": (34.0522, -118.2437),
        "tokyo": (35.6762, 139.6503),
        "shanghai": (31.2304, 121.4737),
        "dubai": (25.2048, 55.2708),
        "sydney": (-33.8688, 151.2093),
        "cape town": (-33.9249, 18.4241)
    }

    def parse_prompt(self, prompt: str) -> VesselParameters:
        """Parse natural language prompt and extract parameters"""
        prompt_lower = prompt.lower()
        
        # Extract vessel count
        vessel_count = self._extract_vessel_count(prompt_lower)
        
        # Extract vessel classes
        vessel_classes = self._extract_vessel_classes(prompt_lower)
        
        # Extract voyage type
        voyage_type = self._extract_voyage_type(prompt_lower)
        
        # Extract duration
        duration_hours = self._extract_duration(prompt_lower)
        
        # Extract regions
        start_region, end_region = self._extract_regions(prompt_lower)
        
        # Determine speed range based on vessel classes
        speed_range = self._determine_speed_range(vessel_classes)
        
        return VesselParameters(
            vessel_count=vessel_count,
            vessel_classes=vessel_classes,
            voyage_type=voyage_type,
            duration_hours=duration_hours,
            start_region=start_region,
            end_region=end_region,
            speed_range=speed_range
        )

    def _extract_vessel_count(self, prompt: str) -> int:
        """Extract number of vessels from prompt"""
        # Look for patterns like "20 vessels", "5 ships", "10 boats"
        patterns = [
            r'(\d+)\s+(?:vessels?|ships?|boats?)',
            r'(?:vessels?|ships?|boats?)\s+(\d+)',
            r'(\d+)\s+(?:class|vessel)',
            r'(\d+)\s+(?:cargo|tanker|fishing|passenger|yacht)',
            r'(\d+)\s+(?:cargo ships?|tanker ships?|fishing vessels?)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, prompt)
            if match:
                return int(match.group(1))
        
        # Default to 10 if not specified
        return 10

    def _extract_vessel_classes(self, prompt: str) -> List[str]:
        """Extract vessel classes from prompt"""
        classes = []
        
        # Look for class designations
        class_patterns = [
            r'class\s+([a-z]+)',
            r'([a-z]+)\s+class',
        ]
        
        for pattern in class_patterns:
            matches = re.findall(pattern, prompt)
            for match in matches:
                if match.upper() in self.VESSEL_CLASSES:
                    classes.append(match.upper())
        
        # Look for vessel type keywords
        for vessel_type, info in self.VESSEL_CLASSES.items():
            if vessel_type in prompt:
                classes.append(vessel_type)
        
        # If no classes found, default to A and B
        if not classes:
            classes = ["A", "B"]
        
        return list(set(classes))  # Remove duplicates

    def _extract_voyage_type(self, prompt: str) -> str:
        """Extract voyage type from prompt"""
        # Check for "point to point" in the prompt first
        if "point to point" in prompt or "point-to-point" in prompt:
            return "point_to_point"
        
        # Check for "from X to Y" pattern (implies point-to-point)
        if re.search(r'from\s+\w+\s+to\s+\w+', prompt):
            return "point_to_point"
        
        # Check other voyage types
        for voyage_key, voyage_value in self.VOYAGE_TYPES.items():
            if voyage_key in prompt:
                return voyage_value
        
        return "random"

    def _extract_duration(self, prompt: str) -> int:
        """Extract duration from prompt"""
        # Look for time patterns
        patterns = [
            r'(\d+)\s+hours?',
            r'(\d+)\s+hrs?',
            r'for\s+(\d+)\s+hours?',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, prompt)
            if match:
                return int(match.group(1))
        
        return 24  # Default 24 hours

    def _extract_regions(self, prompt: str) -> Tuple[Optional[str], Optional[str]]:
        """Extract start and end regions from prompt"""
        start_region = None
        end_region = None
        
        # Look for "from X to Y" patterns
        from_to_pattern = r'from\s+([a-z\s]+?)\s+to\s+([a-z\s]+)'
        match = re.search(from_to_pattern, prompt)
        if match:
            start_region = match.group(1).strip()
            end_region = match.group(2).strip()
        
        # Look for individual region mentions
        regions_found = []
        for region in self.REGIONS.keys():
            if region in prompt:
                regions_found.append(region)
        
        if regions_found:
            if len(regions_found) >= 2:
                start_region = regions_found[0]
                end_region = regions_found[1]
            else:
                start_region = regions_found[0]
        
        return start_region, end_region

    def _determine_speed_range(self, vessel_classes: List[str]) -> Tuple[float, float]:
        """Determine speed range based on vessel classes"""
        if not vessel_classes:
            return (5.0, 25.0)
        
        min_speeds = []
        max_speeds = []
        
        for vessel_class in vessel_classes:
            if vessel_class in self.VESSEL_CLASSES:
                speed_range = self.VESSEL_CLASSES[vessel_class]["speed_range"]
                min_speeds.append(speed_range[0])
                max_speeds.append(speed_range[1])
        
        if min_speeds and max_speeds:
            return (min(min_speeds), max(max_speeds))
        
        return (5.0, 25.0)

class VesselTrackGenerator:
    """Generates realistic vessel tracks based on parameters"""
    
    def __init__(self):
        self.parser = VesselPromptParser()
    
    def generate_tracks(self, parameters: VesselParameters) -> List[VesselTrack]:
        """Generate vessel tracks based on parameters"""
        tracks = []
        
        for i in range(parameters.vessel_count):
            # Select vessel class
            vessel_class = random.choice(parameters.vessel_classes)
            
            # Generate MMSI
            mmsi = self._generate_mmsi(vessel_class)
            
            # Generate track based on voyage type
            if parameters.voyage_type == "point_to_point":
                track = self._generate_point_to_point_track(
                    mmsi, vessel_class, parameters
                )
            elif parameters.voyage_type == "circular":
                track = self._generate_circular_track(
                    mmsi, vessel_class, parameters
                )
            elif parameters.voyage_type == "patrol":
                track = self._generate_patrol_track(
                    mmsi, vessel_class, parameters
                )
            elif parameters.voyage_type == "fishing_pattern":
                track = self._generate_fishing_track(
                    mmsi, vessel_class, parameters
                )
            else:  # random
                track = self._generate_random_track(
                    mmsi, vessel_class, parameters
                )
            
            tracks.append(track)
        
        return tracks
    
    def _generate_mmsi(self, vessel_class: str) -> str:
        """Generate realistic MMSI number"""
        # Different vessel classes have different MMSI ranges
        if vessel_class.upper() in ["A", "B"]:
            # Class A/B vessels typically have MMSIs starting with 2 (Europe)
            base = random.randint(200000000, 299999999)
        elif vessel_class == "cargo":
            base = random.randint(300000000, 399999999)
        elif vessel_class == "tanker":
            base = random.randint(400000000, 499999999)
        elif vessel_class == "fishing":
            base = random.randint(100000000, 199999999)
        else:
            base = random.randint(200000000, 999999999)
        
        return str(base)
    
    def _generate_point_to_point_track(
        self, mmsi: str, vessel_class: str, params: VesselParameters
    ) -> VesselTrack:
        """Generate point-to-point voyage track"""
        # Get start and end coordinates
        if params.start_region and params.start_region in self.parser.REGIONS:
            start_lat, start_lon = self.parser.REGIONS[params.start_region]
        else:
            start_lat, start_lon = self._random_coastal_coordinates()
        
        if params.end_region and params.end_region in self.parser.REGIONS:
            end_lat, end_lon = self.parser.REGIONS[params.end_region]
        else:
            end_lat, end_lon = self._random_coastal_coordinates()
        
        # Calculate route
        points = self._calculate_route_points(
            start_lat, start_lon, end_lat, end_lon, params
        )
        
        return VesselTrack(mmsi=mmsi, vessel_class=vessel_class, points=points)
    
    def _generate_random_track(
        self, mmsi: str, vessel_class: str, params: VesselParameters
    ) -> VesselTrack:
        """Generate random wandering track"""
        # Start from random coastal location
        start_lat, start_lon = self._random_coastal_coordinates()
        
        points = []
        current_lat, current_lon = start_lat, start_lon
        current_time = datetime.now()
        
        total_points = (params.duration_hours * 60) // params.point_interval_minutes
        
        for i in range(total_points):
            # Random movement
            speed = random.uniform(*params.speed_range)
            course = random.uniform(0, 360)
            
            # Calculate new position
            new_lat, new_lon = self._move_position(
                current_lat, current_lon, speed, course, params.point_interval_minutes
            )
            
            # Keep within reasonable bounds
            new_lat = max(-85, min(85, new_lat))
            new_lon = self._normalize_longitude(new_lon)
            
            point = TrackPoint(
                latitude=new_lat,
                longitude=new_lon,
                timestamp=current_time.isoformat(),
                speed_over_ground=speed,
                course_over_ground=course,
                heading=course
            )
            points.append(point)
            
            current_lat, current_lon = new_lat, new_lon
            current_time += timedelta(minutes=params.point_interval_minutes)
        
        return VesselTrack(mmsi=mmsi, vessel_class=vessel_class, points=points)
    
    def _generate_circular_track(
        self, mmsi: str, vessel_class: str, params: VesselParameters
    ) -> VesselTrack:
        """Generate circular patrol track"""
        center_lat, center_lon = self._random_coastal_coordinates()
        radius_nm = random.uniform(5, 20)  # 5-20 nautical miles
        
        points = []
        current_time = datetime.now()
        
        total_points = (params.duration_hours * 60) // params.point_interval_minutes
        
        for i in range(total_points):
            angle = (i / total_points) * 2 * math.pi
            
            # Calculate position on circle
            lat_offset = (radius_nm / 60) * math.cos(angle)
            lon_offset = (radius_nm / 60) * math.sin(angle) / math.cos(math.radians(center_lat))
            
            new_lat = center_lat + lat_offset
            new_lon = center_lon + lon_offset
            
            # Calculate speed and course
            speed = random.uniform(*params.speed_range)
            course = (angle * 180 / math.pi + 90) % 360
            
            point = TrackPoint(
                latitude=new_lat,
                longitude=new_lon,
                timestamp=current_time.isoformat(),
                speed_over_ground=speed,
                course_over_ground=course,
                heading=course
            )
            points.append(point)
            
            current_time += timedelta(minutes=params.point_interval_minutes)
        
        return VesselTrack(mmsi=mmsi, vessel_class=vessel_class, points=points)
    
    def _generate_patrol_track(
        self, mmsi: str, vessel_class: str, params: VesselParameters
    ) -> VesselTrack:
        """Generate patrol track (back and forth)"""
        start_lat, start_lon = self._random_coastal_coordinates()
        
        points = []
        current_lat, current_lon = start_lat, start_lon
        current_time = datetime.now()
        
        # Patrol parameters
        patrol_length_nm = random.uniform(10, 30)
        patrol_direction = random.uniform(0, 360)
        
        total_points = (params.duration_hours * 60) // params.point_interval_minutes
        
        for i in range(total_points):
            # Alternate direction every quarter of the track
            quarter = (i // (total_points // 4)) % 2
            direction = patrol_direction if quarter == 0 else (patrol_direction + 180) % 360
            
            speed = random.uniform(*params.speed_range)
            
            new_lat, new_lon = self._move_position(
                current_lat, current_lon, speed, direction, params.point_interval_minutes
            )
            
            point = TrackPoint(
                latitude=new_lat,
                longitude=new_lon,
                timestamp=current_time.isoformat(),
                speed_over_ground=speed,
                course_over_ground=direction,
                heading=direction
            )
            points.append(point)
            
            current_lat, current_lon = new_lat, new_lon
            current_time += timedelta(minutes=params.point_interval_minutes)
        
        return VesselTrack(mmsi=mmsi, vessel_class=vessel_class, points=points)
    
    def _generate_fishing_track(
        self, mmsi: str, vessel_class: str, params: VesselParameters
    ) -> VesselTrack:
        """Generate fishing pattern track"""
        start_lat, start_lon = self._random_coastal_coordinates()
        
        points = []
        current_lat, current_lon = start_lat, start_lon
        current_time = datetime.now()
        
        total_points = (params.duration_hours * 60) // params.point_interval_minutes
        
        for i in range(total_points):
            # Fishing vessels move slowly and erratically
            if i % 10 < 3:  # 30% of time stationary or very slow
                speed = random.uniform(0, 3)
                course = random.uniform(0, 360)
            else:
                speed = random.uniform(3, 8)
                course = random.uniform(0, 360)
            
            new_lat, new_lon = self._move_position(
                current_lat, current_lon, speed, course, params.point_interval_minutes
            )
            
            point = TrackPoint(
                latitude=new_lat,
                longitude=new_lon,
                timestamp=current_time.isoformat(),
                speed_over_ground=speed,
                course_over_ground=course,
                heading=course
            )
            points.append(point)
            
            current_lat, current_lon = new_lat, new_lon
            current_time += timedelta(minutes=params.point_interval_minutes)
        
        return VesselTrack(mmsi=mmsi, vessel_class=vessel_class, points=points)
    
    def _calculate_route_points(
        self, start_lat: float, start_lon: float, end_lat: float, end_lon: float, 
        params: VesselParameters
    ) -> List[TrackPoint]:
        """Calculate route points between two locations"""
        points = []
        current_time = datetime.now()
        
        # Calculate distance and bearing
        distance_nm = self._calculate_distance(start_lat, start_lon, end_lat, end_lon)
        bearing = self._calculate_bearing(start_lat, start_lon, end_lat, end_lon)
        
        # Calculate number of points needed
        avg_speed = sum(params.speed_range) / 2
        travel_time_hours = distance_nm / avg_speed
        total_points = int((travel_time_hours * 60) // params.point_interval_minutes)
        
        if total_points < 2:
            total_points = 2
        
        # Generate intermediate points
        for i in range(total_points):
            progress = i / (total_points - 1)
            
            # Interpolate position
            current_lat = start_lat + (end_lat - start_lat) * progress
            current_lon = start_lon + (end_lon - start_lon) * progress
            
            # Add some realistic variation (smaller for point-to-point)
            variation_lat = random.uniform(-0.001, 0.001)
            variation_lon = random.uniform(-0.001, 0.001)
            
            current_lat += variation_lat
            current_lon += variation_lon
            
            # Normalize longitude
            current_lon = self._normalize_longitude(current_lon)
            
            # Calculate speed (faster in middle, slower at start/end)
            if progress < 0.1 or progress > 0.9:
                speed = random.uniform(params.speed_range[0], params.speed_range[0] + 2)
            else:
                speed = random.uniform(*params.speed_range)
            
            point = TrackPoint(
                latitude=current_lat,
                longitude=current_lon,
                timestamp=current_time.isoformat(),
                speed_over_ground=speed,
                course_over_ground=bearing,
                heading=bearing
            )
            points.append(point)
            
            current_time += timedelta(minutes=params.point_interval_minutes)
        
        return points
    
    def _random_coastal_coordinates(self) -> Tuple[float, float]:
        """Generate random coastal coordinates"""
        # Common coastal areas
        coastal_areas = [
            (51.9244, 4.4777),   # Rotterdam
            (53.5511, 9.9937),   # Hamburg
            (51.2194, 4.4025),   # Antwerp
            (51.5074, -0.1278),  # London
            (40.7128, -74.0060), # New York
            (34.0522, -118.2437), # Los Angeles
            (35.6762, 139.6503), # Tokyo
            (31.2304, 121.4737), # Shanghai
        ]
        
        base_lat, base_lon = random.choice(coastal_areas)
        
        # Add random offset
        lat_offset = random.uniform(-2, 2)
        lon_offset = random.uniform(-2, 2)
        
        return base_lat + lat_offset, base_lon + lon_offset
    
    def _move_position(
        self, lat: float, lon: float, speed_knots: float, 
        course_deg: float, time_minutes: int
    ) -> Tuple[float, float]:
        """Move position based on speed, course, and time"""
        # Convert speed from knots to degrees per minute
        # 1 knot ≈ 1 nautical mile per hour
        # 1 nautical mile ≈ 1/60 degree of latitude
        speed_deg_per_min = (speed_knots / 60) * (time_minutes / 60)
        
        # Calculate new latitude
        new_lat = lat + speed_deg_per_min * math.cos(math.radians(course_deg))
        
        # Calculate new longitude (adjust for latitude)
        new_lon = lon + (speed_deg_per_min * math.sin(math.radians(course_deg)) / 
                        math.cos(math.radians(lat)))
        
        return new_lat, new_lon
    
    def _calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance between two points in nautical miles"""
        # Haversine formula
        R = 3440.065  # Earth's radius in nautical miles
        
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        
        a = (math.sin(dlat/2) * math.sin(dlat/2) + 
             math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * 
             math.sin(dlon/2) * math.sin(dlon/2))
        
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        distance = R * c
        
        return distance
    
    def _calculate_bearing(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate bearing between two points"""
        dlon = math.radians(lon2 - lon1)
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        
        y = math.sin(dlon) * math.cos(lat2_rad)
        x = (math.cos(lat1_rad) * math.sin(lat2_rad) - 
             math.sin(lat1_rad) * math.cos(lat2_rad) * math.cos(dlon))
        
        bearing = math.degrees(math.atan2(y, x))
        return (bearing + 360) % 360
    
    def _normalize_longitude(self, lon: float) -> float:
        """Normalize longitude to [-180, 180]"""
        while lon > 180:
            lon -= 360
        while lon < -180:
            lon += 360
        return lon

class VesselTrackMCPServer:
    """Main service class for the MCP server"""
    
    def __init__(self):
        self.parser = VesselPromptParser()
        self.generator = VesselTrackGenerator()
    
    def generate_tracks_from_prompt(self, prompt: str) -> Dict[str, Any]:
        """Generate vessel tracks from natural language prompt"""
        try:
            # Parse the prompt
            parameters = self.parser.parse_prompt(prompt)
            
            # Generate tracks
            tracks = self.generator.generate_tracks(parameters)
            
            # Convert tracks to serializable format
            serializable_tracks = []
            for track in tracks:
                track_dict = {
                    "mmsi": track.mmsi,
                    "vessel_class": track.vessel_class,
                    "points": [
                        {
                            "latitude": point.latitude,
                            "longitude": point.longitude,
                            "timestamp": point.timestamp,
                            "speed_over_ground": point.speed_over_ground,
                            "course_over_ground": point.course_over_ground,
                            "heading": point.heading
                        }
                        for point in track.points
                    ]
                }
                serializable_tracks.append(track_dict)
            
            return {
                "success": True,
                "tracks": serializable_tracks,
                "parameters_used": {
                    "vessel_count": parameters.vessel_count,
                    "vessel_classes": parameters.vessel_classes,
                    "voyage_type": parameters.voyage_type,
                    "duration_hours": parameters.duration_hours,
                    "start_region": parameters.start_region,
                    "end_region": parameters.end_region,
                    "speed_range": parameters.speed_range
                }
            }
            
        except Exception as e:
            logger.error(f"Error generating tracks: {e}")
            return {
                "success": False,
                "error": str(e),
                "tracks": [],
                "parameters_used": {}
            }
