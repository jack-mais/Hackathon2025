"""Multi-ship AIS generator - Walk version (multiple ships with realistic routes)"""

import random
import math
from datetime import datetime, timedelta
from typing import List, Dict, Generator, Tuple
from enum import Enum

from ..core.models import Position, Route, ShipState, NavigationStatus, ShipType
from .ais_generator import SimpleShipMovement


class RouteType(Enum):
    """Types of realistic maritime routes"""
    FERRY = "ferry"
    CARGO = "cargo"  
    FISHING = "fishing"
    COASTAL = "coastal"
    PATROL = "patrol"


class WorldwideRoutes:
    """Worldwide maritime routes and ports"""
    
    # Irish Sea ports (original)
    DUBLIN = Position(latitude=53.3498, longitude=-6.2603)
    HOLYHEAD = Position(latitude=53.3090, longitude=-4.6324)
    LIVERPOOL = Position(latitude=53.4084, longitude=-2.9916)
    BELFAST = Position(latitude=54.5973, longitude=-5.9301)
    CORK = Position(latitude=51.8969, longitude=-8.4863)
    SWANSEA = Position(latitude=51.6214, longitude=-3.9436)
    ISLE_OF_MAN = Position(latitude=54.1936, longitude=-4.5591)
    CARDIFF = Position(latitude=51.4816, longitude=-3.1791)
    
    # Major European ports
    ROTTERDAM = Position(latitude=51.9225, longitude=4.4792)
    HAMBURG = Position(latitude=53.5511, longitude=9.9937)
    ANTWERP = Position(latitude=51.2194, longitude=4.4025)
    LE_HAVRE = Position(latitude=49.4944, longitude=0.1079)
    BARCELONA = Position(latitude=41.3851, longitude=2.1734)
    MARSEILLE = Position(latitude=43.2965, longitude=5.3698)
    NAPLES = Position(latitude=40.8518, longitude=14.2681)
    VENICE = Position(latitude=45.4408, longitude=12.3155)
    ATHENS = Position(latitude=37.9755, longitude=23.7348)
    ISTANBUL = Position(latitude=41.0082, longitude=28.9784)
    
    # Nordic/Baltic ports
    COPENHAGEN = Position(latitude=55.6761, longitude=12.5683)
    STOCKHOLM = Position(latitude=59.3293, longitude=18.0686)
    OSLO = Position(latitude=59.9139, longitude=10.7522)
    HELSINKI = Position(latitude=60.1699, longitude=24.9384)
    GDANSK = Position(latitude=54.3520, longitude=18.6466)
    
    # Asian ports
    SINGAPORE = Position(latitude=1.2966, longitude=103.7764)
    SHANGHAI = Position(latitude=31.2304, longitude=121.4737)
    HONG_KONG = Position(latitude=22.3193, longitude=114.1694)
    TOKYO = Position(latitude=35.6762, longitude=139.6503)
    BUSAN = Position(latitude=35.1796, longitude=129.0756)
    MUMBAI = Position(latitude=19.0760, longitude=72.8777)
    DUBAI = Position(latitude=25.2048, longitude=55.2708)
    
    # North American ports
    NEW_YORK = Position(latitude=40.7128, longitude=-74.0060)
    LOS_ANGELES = Position(latitude=33.7391, longitude=-118.2668)
    MIAMI = Position(latitude=25.7617, longitude=-80.1918)
    VANCOUVER = Position(latitude=49.2827, longitude=-123.1207)
    MONTREAL = Position(latitude=45.5017, longitude=-73.5673)
    
    @classmethod
    def get_all_ports(cls) -> Dict[str, Position]:
        """Get all available ports worldwide"""
        ports = {}
        for attr_name in dir(cls):
            attr = getattr(cls, attr_name)
            if isinstance(attr, Position) and not attr_name.startswith('_'):
                ports[attr_name] = attr
        return ports
    
    @classmethod
    def get_ports_by_region(cls, region: str = "mediterranean") -> Dict[str, Position]:
        """Get ports filtered by region"""
        all_ports = cls.get_all_ports()
        
        region_filters = {
            "irish_sea": ["DUBLIN", "HOLYHEAD", "LIVERPOOL", "BELFAST", "CORK", "SWANSEA", "ISLE_OF_MAN", "CARDIFF"],
            "europe": ["ROTTERDAM", "HAMBURG", "ANTWERP", "LE_HAVRE", "BARCELONA", "MARSEILLE", "NAPLES", "VENICE"],
            "mediterranean": ["BARCELONA", "MARSEILLE", "NAPLES", "VENICE", "ATHENS", "ISTANBUL"],
            "nordic": ["COPENHAGEN", "STOCKHOLM", "OSLO", "HELSINKI", "GDANSK"],
            "asia": ["SINGAPORE", "SHANGHAI", "HONG_KONG", "TOKYO", "BUSAN", "MUMBAI", "DUBAI"],
            "north_america": ["NEW_YORK", "LOS_ANGELES", "MIAMI", "VANCOUVER", "MONTREAL"]
        }
        
        if region.lower() in region_filters:
            filtered = {name: all_ports[name] for name in region_filters[region.lower()] if name in all_ports}
            return filtered
        
        return all_ports  # Return all if region not found
    
    @classmethod
    def get_region_coordinates(cls, region: str) -> Dict[str, Position]:
        """Get typical coordinates for maritime regions - used when no specific ports mentioned"""
        
        region_coordinates = {
            # Mediterranean sub-regions
            "mediterranean": {
                "WESTERN_MED": Position(latitude=41.0, longitude=2.0),    # Near Barcelona
                "CENTRAL_MED": Position(latitude=40.0, longitude=14.0),   # Near Naples
                "EASTERN_MED": Position(latitude=36.0, longitude=28.0),   # Near Turkey/Greece
                "SICILY_AREA": Position(latitude=37.5, longitude=13.5),   # Sicily coast
                "CORSICA_AREA": Position(latitude=42.0, longitude=9.0),   # Corsica
            },
            "north_sea": {
                "SOUTHERN_NS": Position(latitude=52.0, longitude=4.0),    # Dutch waters
                "CENTRAL_NS": Position(latitude=55.0, longitude=3.0),     # Between UK/Norway
                "NORTHERN_NS": Position(latitude=58.0, longitude=1.0),    # Norwegian waters
                "DOGGER_BANK": Position(latitude=54.6, longitude=2.0),    # Fishing grounds
            },
            "atlantic": {
                "NORTH_ATLANTIC": Position(latitude=50.0, longitude=-30.0), # Mid-Atlantic
                "SOUTH_ATLANTIC": Position(latitude=-20.0, longitude=-10.0), # South Atlantic
                "WESTERN_ATLANTIC": Position(latitude=40.0, longitude=-60.0), # US coast
            },
            "caribbean": {
                "EASTERN_CARIBBEAN": Position(latitude=15.0, longitude=-60.0), # Lesser Antilles
                "WESTERN_CARIBBEAN": Position(latitude=20.0, longitude=-85.0), # Near Mexico
                "CENTRAL_CARIBBEAN": Position(latitude=18.0, longitude=-75.0), # Jamaica area
            },
            "pacific": {
                "NORTH_PACIFIC": Position(latitude=35.0, longitude=140.0),  # Japan area
                "SOUTH_PACIFIC": Position(latitude=-20.0, longitude=170.0), # Near Fiji
                "EASTERN_PACIFIC": Position(latitude=30.0, longitude=-120.0), # California
            },
            "irish_sea": {
                "CENTRAL_IRISH": Position(latitude=53.5, longitude=-5.0),   # Center Irish Sea
                "NORTHERN_IRISH": Position(latitude=54.5, longitude=-5.5),  # Near Belfast
                "SOUTHERN_IRISH": Position(latitude=52.0, longitude=-5.5),  # Near Wales
            },
            "baltic_sea": {
                "CENTRAL_BALTIC": Position(latitude=57.0, longitude=18.0),   # Central Baltic
                "SOUTHERN_BALTIC": Position(latitude=54.5, longitude=14.0),  # German/Polish coast
                "NORTHERN_BALTIC": Position(latitude=60.0, longitude=20.0),  # Finnish waters
            },
            "english_channel": {
                "DOVER_STRAIT": Position(latitude=50.9, longitude=1.4),     # Dover area
                "WESTERN_CHANNEL": Position(latitude=49.5, longitude=-3.0), # Western approach
                "CENTRAL_CHANNEL": Position(latitude=50.0, longitude=-1.0), # Central channel
            }
        }
        
        return region_coordinates.get(region.lower(), {})
    
    @classmethod
    def get_smart_coordinates_for_location(cls, location_hint: str) -> Position:
        """Intelligently determine coordinates based on location mentions"""
        
        location_lower = location_hint.lower()
        
        # Specific geographical areas
        location_mapping = {
            # Mediterranean specific areas
            'sicily': Position(latitude=37.5, longitude=13.8),      # Sicily coast
            'coast of sicily': Position(latitude=37.3, longitude=13.5),
            'off sicily': Position(latitude=37.0, longitude=13.0),
            'italian coast': Position(latitude=40.5, longitude=14.0),
            'spanish coast': Position(latitude=41.2, longitude=2.0),
            'french riviera': Position(latitude=43.5, longitude=7.0),
            'greek islands': Position(latitude=37.0, longitude=25.0),
            'turkish coast': Position(latitude=36.5, longitude=30.0),
            
            # North Sea areas
            'norwegian waters': Position(latitude=58.0, longitude=5.0),
            'danish waters': Position(latitude=56.0, longitude=10.0),  
            'dutch coast': Position(latitude=52.5, longitude=4.0),
            'german bight': Position(latitude=54.0, longitude=7.5),
            'shetland islands': Position(latitude=60.5, longitude=-1.0),
            
            # Atlantic areas  
            'azores': Position(latitude=38.0, longitude=-28.0),
            'canary islands': Position(latitude=28.0, longitude=-16.0),
            'bay of biscay': Position(latitude=44.0, longitude=-4.0),
            'newfoundland': Position(latitude=48.0, longitude=-50.0),
            
            # Caribbean areas
            'bahamas': Position(latitude=24.0, longitude=-76.0),
            'jamaica': Position(latitude=18.0, longitude=-77.0),
            'puerto rico': Position(latitude=18.2, longitude=-66.5),
            'barbados': Position(latitude=13.1, longitude=-59.6),
            
            # Pacific areas
            'hawaii': Position(latitude=21.0, longitude=-157.0),
            'california coast': Position(latitude=34.0, longitude=-120.0),
            'japan waters': Position(latitude=35.0, longitude=140.0),
            'philippines': Position(latitude=12.0, longitude=122.0),
            
            # Baltic areas
            'stockholm archipelago': Position(latitude=59.5, longitude=18.5),
            'finnish waters': Position(latitude=60.0, longitude=24.0),
            'gulf of bothnia': Position(latitude=63.0, longitude=20.0),
            
            # Other specific areas
            'gibraltar': Position(latitude=36.1, longitude=-5.3),
            'suez canal': Position(latitude=30.0, longitude=32.5),
            'bering strait': Position(latitude=65.8, longitude=-168.0),
            'panama canal': Position(latitude=9.0, longitude=-79.5),
        }
        
        # Check for specific location matches
        for location, coords in location_mapping.items():
            if location in location_lower:
                return coords
        
        # Fallback to region coordinates
        region_coords = {
            'mediterranean': Position(latitude=40.0, longitude=15.0),
            'north sea': Position(latitude=55.0, longitude=3.0),
            'atlantic': Position(latitude=45.0, longitude=-25.0),
            'pacific': Position(latitude=30.0, longitude=150.0),
            'caribbean': Position(latitude=18.0, longitude=-70.0),
            'baltic': Position(latitude=57.0, longitude=18.0),
            'irish sea': Position(latitude=53.5, longitude=-5.0),
        }
        
        for region, coords in region_coords.items():
            if region in location_lower:
                return coords
        
        # Ultimate fallback - Mediterranean (generic maritime area)
        return Position(latitude=40.0, longitude=15.0)
    
    @classmethod
    def get_ferry_routes(cls, region: str = "mediterranean") -> List[Tuple[Position, Position, str]]:
        """Get ferry routes by region"""
        if region.lower() == "irish_sea":
            return [
            (cls.DUBLIN, cls.HOLYHEAD, "Dublin-Holyhead Ferry"),
            (cls.BELFAST, cls.LIVERPOOL, "Belfast-Liverpool Ferry"),
            (cls.CORK, cls.SWANSEA, "Cork-Swansea Ferry"),
            (cls.DUBLIN, cls.ISLE_OF_MAN, "Dublin-Isle of Man"),
            (cls.HOLYHEAD, cls.DUBLIN, "Holyhead-Dublin Ferry"),
            (cls.LIVERPOOL, cls.BELFAST, "Liverpool-Belfast Ferry"),
        ]
        elif region.lower() == "mediterranean":
            return [
                (cls.BARCELONA, cls.MARSEILLE, "Barcelona-Marseille Ferry"),
                (cls.NAPLES, cls.ATHENS, "Naples-Athens Ferry"), 
                (cls.VENICE, cls.ISTANBUL, "Venice-Istanbul Ferry"),
                (cls.MARSEILLE, cls.BARCELONA, "Marseille-Barcelona Ferry"),
            ]
        elif region.lower() == "nordic":
            return [
                (cls.COPENHAGEN, cls.STOCKHOLM, "Copenhagen-Stockholm Ferry"),
                (cls.OSLO, cls.COPENHAGEN, "Oslo-Copenhagen Ferry"),
                (cls.HELSINKI, cls.STOCKHOLM, "Helsinki-Stockholm Ferry"),
            ]
        else:
            # Default to Mediterranean
            return cls.get_ferry_routes("mediterranean")
    
    @classmethod
    def get_cargo_routes(cls, region: str = "mediterranean") -> List[Tuple[Position, Position, str]]:
        """Get cargo ship routes by region"""
        if region.lower() == "irish_sea":
            return [
            (cls.DUBLIN, cls.LIVERPOOL, "Dublin-Liverpool Cargo"),
            (cls.CORK, cls.CARDIFF, "Cork-Cardiff Cargo"),
            (cls.BELFAST, cls.SWANSEA, "Belfast-Swansea Container"),
            (cls.LIVERPOOL, cls.DUBLIN, "Liverpool-Dublin Supply"),
        ]
        elif region.lower() == "europe":
            return [
                (cls.ROTTERDAM, cls.HAMBURG, "Rotterdam-Hamburg Container"),
                (cls.ANTWERP, cls.LE_HAVRE, "Antwerp-Le Havre Cargo"),
                (cls.HAMBURG, cls.ROTTERDAM, "Hamburg-Rotterdam Supply"),
                (cls.BARCELONA, cls.MARSEILLE, "Barcelona-Marseille Freight"),
            ]
        elif region.lower() == "asia":
            return [
                (cls.SINGAPORE, cls.HONG_KONG, "Singapore-Hong Kong Container"),
                (cls.SHANGHAI, cls.TOKYO, "Shanghai-Tokyo Cargo"),
                (cls.MUMBAI, cls.DUBAI, "Mumbai-Dubai Trade"),
                (cls.HONG_KONG, cls.SINGAPORE, "Hong Kong-Singapore Supply"),
            ]
        elif region.lower() == "north_america":
            return [
                (cls.LOS_ANGELES, cls.NEW_YORK, "Trans-US Container"),
                (cls.MIAMI, cls.NEW_YORK, "East Coast Cargo"),
                (cls.VANCOUVER, cls.LOS_ANGELES, "West Coast Supply"),
            ]
        else:
            # Fallback to Mediterranean cargo routes
            return [
                (cls.BARCELONA, cls.NAPLES, "Barcelona-Naples Container"),
                (cls.MARSEILLE, cls.ATHENS, "France-Greece Cargo"),
                (cls.VENICE, cls.ISTANBUL, "Adriatic-Bosphorus Supply"),
            ]
    
    @classmethod
    def get_fishing_areas(cls, region: str = "mediterranean") -> List[Tuple[Position, Position, str]]:
        """Get fishing areas (circular/patrol patterns) by region"""
        if region.lower() == "irish_sea":
            return [
            (Position(53.7, -5.5), Position(53.9, -5.3), "North Irish Sea Grounds"),
            (Position(52.5, -5.8), Position(52.7, -5.6), "Central Irish Sea Grounds"), 
            (Position(51.8, -4.5), Position(52.0, -4.3), "Bristol Channel Grounds"),
        ]
        elif region.lower() == "north_sea":
            return [
                (Position(56.0, 3.0), Position(56.2, 3.2), "Dogger Bank Grounds"),
                (Position(54.5, 2.0), Position(54.7, 2.2), "Yorkshire Fishing Grounds"),
            ]
        elif region.lower() == "mediterranean":
            return [
                (Position(42.0, 3.0), Position(42.2, 3.2), "Balearic Sea Grounds"),
                (Position(38.0, 15.0), Position(38.2, 15.2), "Tyrrhenian Sea Grounds"),
            ]
        else:
            # Fallback to Mediterranean fishing areas
            return [
                (Position(40.0, 14.0), Position(40.2, 14.2), "Mediterranean Fishing Grounds"),
                (Position(38.0, 15.0), Position(38.2, 15.2), "Sicily Fishing Grounds"),
            ]
    
    @classmethod
    def get_coastal_patrol_routes(cls, region: str = "mediterranean") -> List[Tuple[Position, Position, str]]:
        """Get coastal patrol routes by region"""
        if region.lower() == "irish_sea":
            return [
            (Position(53.4, -6.0), Position(53.6, -5.8), "Dublin Bay Patrol"),
            (Position(53.3, -4.4), Position(53.4, -4.2), "Anglesey Coast Patrol"),
            (Position(54.6, -5.8), Position(54.8, -5.6), "Belfast Lough Patrol"),
        ]
        elif region.lower() == "mediterranean":
            return [
                (Position(41.9, 2.5), Position(42.1, 2.7), "Barcelona Coast Patrol"),
                (Position(43.3, 5.2), Position(43.5, 5.4), "Marseille Harbor Patrol"),
            ]
        elif region.lower() == "north_sea":
            return [
                (Position(51.8, 4.3), Position(52.0, 4.5), "Rotterdam Harbor Patrol"),
                (Position(53.4, 9.8), Position(53.6, 10.0), "Hamburg Port Patrol"),
            ]
        else:
            # Fallback to Mediterranean patrol routes
            return [
                (Position(41.4, 2.2), Position(41.6, 2.4), "Barcelona Coast Patrol"),
                (Position(40.8, 14.2), Position(41.0, 14.4), "Naples Harbor Patrol"),
            ]


# Backward compatibility alias
IrishSeaRoutes = WorldwideRoutes


class RealisticShipMovement(SimpleShipMovement):
    """Enhanced ship movement with more realistic patterns"""
    
    def __init__(self, route: Route, mmsi: int, ship_name: str, ship_type: ShipType = ShipType.CARGO, route_type: RouteType = RouteType.FERRY):
        super().__init__(route, mmsi, ship_name)
        self.ship_type = ship_type
        self.route_type = route_type
        
        # Adjust speed based on ship type
        self._adjust_speed_for_ship_type()
        
        # Add some realistic variation to the straight-line route
        self.waypoints = self._generate_waypoints()
    
    def _adjust_speed_for_ship_type(self):
        """Adjust speed based on ship type"""
        speed_adjustments = {
            ShipType.PASSENGER: 1.0,  # Base speed (12 knots)
            ShipType.CARGO: 0.75,  # Slower cargo ships (9 knots)
            ShipType.FISHING: 0.5,  # Slower fishing vessels (6 knots)
            ShipType.PILOT_VESSEL: 1.5,  # Faster patrol boats (18 knots)
            ShipType.HIGH_SPEED_CRAFT: 2.0,  # Fast boats (24 knots)
        }
        
        adjustment = speed_adjustments.get(self.ship_type, 1.0)
        self.route.speed_knots *= adjustment
        
        # Recalculate timing
        self.total_time_hours = self.total_distance_nm / self.route.speed_knots
    
    def _generate_waypoints(self) -> List[Position]:
        """Generate realistic waypoints instead of straight line"""
        waypoints = [self.route.start_position]
        
        if self.route_type == RouteType.FISHING:
            # Fishing pattern - circular/zigzag
            waypoints.extend(self._generate_fishing_pattern())
        elif self.route_type == RouteType.PATROL:
            # Patrol pattern - back and forth
            waypoints.extend(self._generate_patrol_pattern())
        elif self.route_type in [RouteType.FERRY, RouteType.CARGO]:
            # Commercial route - add intermediate waypoints to avoid straight line
            waypoints.extend(self._generate_commercial_waypoints())
        else:
            # Coastal - follow coastline
            waypoints.extend(self._generate_coastal_waypoints())
        
        waypoints.append(self.route.end_position)
        return waypoints
    
    def _generate_commercial_waypoints(self) -> List[Position]:
        """Generate waypoints for commercial vessels (ferries, cargo)"""
        waypoints = []
        
        # Add 1-2 intermediate waypoints to make route more realistic
        start = self.route.start_position
        end = self.route.end_position
        
        # Add waypoint 1/3 of the way with slight deviation
        lat1 = start.latitude + (end.latitude - start.latitude) * 0.33
        lon1 = start.longitude + (end.longitude - start.longitude) * 0.33
        # Add small deviation to avoid straight line
        lat1 += random.uniform(-0.05, 0.05)
        lon1 += random.uniform(-0.05, 0.05)
        waypoints.append(Position(lat1, lon1))
        
        # Add waypoint 2/3 of the way
        lat2 = start.latitude + (end.latitude - start.latitude) * 0.67
        lon2 = start.longitude + (end.longitude - start.longitude) * 0.67
        lat2 += random.uniform(-0.03, 0.03)  
        lon2 += random.uniform(-0.03, 0.03)
        waypoints.append(Position(lat2, lon2))
        
        return waypoints
    
    def _generate_fishing_pattern(self) -> List[Position]:
        """Generate fishing pattern waypoints"""
        waypoints = []
        center_lat = (self.route.start_position.latitude + self.route.end_position.latitude) / 2
        center_lon = (self.route.start_position.longitude + self.route.end_position.longitude) / 2
        
        # Create circular pattern
        radius = 0.1  # degrees
        for i in range(8):  # 8 points around circle
            angle = i * (2 * math.pi / 8)
            lat = center_lat + radius * math.cos(angle)
            lon = center_lon + radius * math.sin(angle)
            waypoints.append(Position(lat, lon))
        
        return waypoints
    
    def _generate_patrol_pattern(self) -> List[Position]:
        """Generate patrol pattern waypoints"""
        waypoints = []
        start = self.route.start_position
        end = self.route.end_position
        
        # Create back-and-forth pattern
        for i in range(1, 6):  # 5 patrol legs
            ratio = i / 6.0
            lat = start.latitude + (end.latitude - start.latitude) * ratio
            lon = start.longitude + (end.longitude - start.longitude) * ratio
            
            # Add perpendicular offset for patrol pattern
            if i % 2 == 1:  # Alternate sides
                lat += 0.02
            else:
                lat -= 0.02
                
            waypoints.append(Position(lat, lon))
        
        return waypoints
    
    def _generate_coastal_waypoints(self) -> List[Position]:
        """Generate coastal following waypoints"""
        waypoints = []
        
        # Simple coastal following - add waypoints that follow rough coastline
        start = self.route.start_position  
        end = self.route.end_position
        
        # Add 3 waypoints following coast
        for i in range(1, 4):
            ratio = i / 4.0
            lat = start.latitude + (end.latitude - start.latitude) * ratio
            lon = start.longitude + (end.longitude - start.longitude) * ratio
            
            # Stay closer to coast (bias toward land)
            lon += 0.02  # Move slightly toward land
            waypoints.append(Position(lat, lon))
        
        return waypoints
    
    def _interpolate_waypoint_position(self, progress_ratio: float) -> Position:
        """Interpolate position along waypoints instead of straight line"""
        if progress_ratio >= 1.0:
            return self.route.end_position
        if progress_ratio <= 0.0:
            return self.route.start_position
        
        # Calculate which segment we're on
        total_segments = len(self.waypoints) - 1
        segment_progress = progress_ratio * total_segments
        segment_index = int(segment_progress)
        segment_ratio = segment_progress - segment_index
        
        # Handle edge case
        if segment_index >= total_segments:
            return self.waypoints[-1]
        
        # Interpolate between current waypoint and next
        current_wp = self.waypoints[segment_index]
        next_wp = self.waypoints[segment_index + 1]
        
        lat = current_wp.latitude + segment_ratio * (next_wp.latitude - current_wp.latitude)
        lon = current_wp.longitude + segment_ratio * (next_wp.longitude - current_wp.longitude)
        
        return Position(lat, lon)
    
    def generate_movement(self, duration_hours: float, report_interval_seconds: int = 30) -> Generator[ShipState, None, None]:
        """Generate ship states with realistic waypoint following"""
        
        start_time = datetime.utcnow()
        total_reports = int(duration_hours * 3600 / report_interval_seconds)
        
        for report_num in range(total_reports + 1):
            elapsed_seconds = report_num * report_interval_seconds
            elapsed_hours = elapsed_seconds / 3600
            current_time = start_time + timedelta(seconds=elapsed_seconds)
            
            # Calculate progress ratio
            if self.total_time_hours > 0:
                progress_ratio = min(elapsed_hours / self.total_time_hours, 1.0)
            else:
                progress_ratio = 1.0
            
            # Determine navigation status
            if progress_ratio >= 1.0:
                nav_status = NavigationStatus.AT_ANCHOR
                speed = 0.0
            else:
                # Different navigation status based on ship type
                if self.ship_type == ShipType.FISHING:
                    nav_status = NavigationStatus.ENGAGED_IN_FISHING
                elif self.ship_type in [ShipType.PILOT_VESSEL, ShipType.LAW_ENFORCEMENT]:
                    nav_status = NavigationStatus.RESTRICTED_MANEUVERABILITY
                else:
                    nav_status = NavigationStatus.UNDER_WAY_USING_ENGINE
                speed = self.route.speed_knots
            
            # Get position using waypoint interpolation
            current_position = self._interpolate_waypoint_position(progress_ratio)
            
            # Calculate bearing to next waypoint or destination
            if progress_ratio < 1.0:
                bearing = self._calculate_current_bearing(progress_ratio)
            else:
                bearing = self.bearing
            
            ship_state = ShipState(
                mmsi=self.mmsi,
                position=current_position,
                speed_over_ground=speed,
                course_over_ground=bearing,
                heading=bearing if speed > 0 else None,
                navigation_status=nav_status,
                timestamp=current_time,
                ship_name=self.ship_name,
                ship_type=self.ship_type,
                length=self._get_ship_length(),
                width=self._get_ship_width(),
                draught=self._get_ship_draught()
            )
            
            yield ship_state
            
            if progress_ratio >= 1.0:
                break
    
    def _calculate_current_bearing(self, progress_ratio: float) -> float:
        """Calculate bearing to next waypoint"""
        # Find current segment
        total_segments = len(self.waypoints) - 1  
        segment_progress = progress_ratio * total_segments
        segment_index = int(segment_progress)
        
        if segment_index >= total_segments:
            return self.bearing
        
        current_wp = self.waypoints[segment_index]
        next_wp = self.waypoints[segment_index + 1]
        
        return self._calculate_bearing(current_wp, next_wp)
    
    def _get_ship_length(self) -> int:
        """Get realistic ship length based on type"""
        lengths = {
            ShipType.PASSENGER: random.randint(120, 200),
            ShipType.CARGO: random.randint(150, 300),
            ShipType.FISHING: random.randint(20, 80),
            ShipType.PILOT_VESSEL: random.randint(30, 100),
            ShipType.HIGH_SPEED_CRAFT: random.randint(40, 80),
        }
        return lengths.get(self.ship_type, 150)
    
    def _get_ship_width(self) -> int:
        """Get realistic ship width based on type"""
        widths = {
            ShipType.PASSENGER: random.randint(18, 28),
            ShipType.CARGO: random.randint(20, 40),
            ShipType.FISHING: random.randint(6, 15),
            ShipType.PILOT_VESSEL: random.randint(8, 18),
            ShipType.HIGH_SPEED_CRAFT: random.randint(10, 20),
        }
        return widths.get(self.ship_type, 25)
    
    def _get_ship_draught(self) -> float:
        """Get realistic ship draught based on type"""
        draughts = {
            ShipType.PASSENGER: random.uniform(4.0, 7.0),
            ShipType.CARGO: random.uniform(8.0, 15.0),
            ShipType.FISHING: random.uniform(2.0, 5.0),
            ShipType.PILOT_VESSEL: random.uniform(2.5, 6.0),
            ShipType.HIGH_SPEED_CRAFT: random.uniform(1.5, 3.5),
        }
        return draughts.get(self.ship_type, 8.5)


class MultiShipGenerator:
    """Generator for multiple ships with realistic routes - Walk version"""
    
    def __init__(self):
        self.active_ships: List[RealisticShipMovement] = []
        self.ship_counter = 123456000  # Starting MMSI range
        self.routes_class = WorldwideRoutes
    
    def generate_irish_sea_scenario(self, num_ships: int = 3) -> List[RealisticShipMovement]:
        """Generate multiple ships in Irish Sea with realistic routes"""
        return self.generate_maritime_scenario(num_ships, region="irish_sea")
    
    def generate_maritime_scenario(self, num_ships: int = 3, region: str = "mediterranean", location_hint: str = None) -> List[RealisticShipMovement]:
        """Generate multiple ships in any maritime region with realistic routes"""
        
        ships = []
        routes_used = set()
        
        for i in range(num_ships):
            # Choose ship type
            ship_type, route_type = self._choose_ship_and_route_type(i, num_ships)
            
            # Get route based on type, region, and location hint
            route, route_name = self._get_route_for_type(route_type, routes_used, region, location_hint)
            routes_used.add(route_name)
            
            # Create ship
            mmsi = self.ship_counter + i
            ship_name = self._generate_ship_name(ship_type, i, region)
            
            ship = RealisticShipMovement(route, mmsi, ship_name, ship_type, route_type)
            ships.append(ship)
            self.active_ships.append(ship)
        
        return ships
    
    def _choose_ship_and_route_type(self, ship_index: int, total_ships: int) -> Tuple[ShipType, RouteType]:
        """Choose appropriate ship and route type for variety"""
        
        # Ensure we get good variety
        type_combinations = [
            (ShipType.PASSENGER, RouteType.FERRY),
            (ShipType.CARGO, RouteType.CARGO),
            (ShipType.FISHING, RouteType.FISHING),
            (ShipType.PILOT_VESSEL, RouteType.PATROL),
            (ShipType.HIGH_SPEED_CRAFT, RouteType.COASTAL),
        ]
        
        # Cycle through types to ensure variety
        combo_index = ship_index % len(type_combinations)
        return type_combinations[combo_index]
    
    def _get_route_for_type(self, route_type: RouteType, routes_used: set, region: str = "mediterranean", location_hint: str = None) -> Tuple[Route, str]:
        """Get a route based on the route type, region, and location hint"""
        
        # First try to get predefined routes for the region
        if route_type == RouteType.FERRY:
            routes = self.routes_class.get_ferry_routes(region)
        elif route_type == RouteType.CARGO:
            routes = self.routes_class.get_cargo_routes(region)
        elif route_type == RouteType.FISHING:
            routes = self.routes_class.get_fishing_areas(region)
        elif route_type == RouteType.PATROL:
            routes = self.routes_class.get_coastal_patrol_routes(region)
        else:  # COASTAL
            routes = self.routes_class.get_ferry_routes(region)
        
        # Try to find unused route from predefined routes
        for start_pos, end_pos, name in routes:
            if name not in routes_used:
                route = Route(start_pos, end_pos, 12.0)
                return route, name
        
        # If no predefined routes or all used, generate intelligent routes using location hint
        if location_hint:
            return self._generate_intelligent_route(route_type, region, location_hint, len(routes_used))
        else:
            # Generate route using region coordinates
            return self._generate_regional_route(route_type, region, len(routes_used))
        
        # Fallback: pick random from available routes
        if routes:
            start_pos, end_pos, name = random.choice(routes)
            route = Route(start_pos, end_pos, 12.0)
            return route, f"{name}_{len(routes_used)}"
    
        # Ultimate fallback: generate basic route
        return self._generate_basic_route(route_type, len(routes_used))
    
    def _generate_intelligent_route(self, route_type: RouteType, region: str, location_hint: str, route_index: int) -> Tuple[Route, str]:
        """Generate an intelligent route based on location hint"""
        
        # Get smart coordinates for the location
        center_pos = self.routes_class.get_smart_coordinates_for_location(location_hint)
        
        # Generate start and end positions around the center
        import random
        import math
        
        # Create routes that make sense for the area
        if route_type == RouteType.FISHING:
            # Fishing boats work in circular patterns
            radius = 0.3  # degrees (about 20 nautical miles)
            angle1 = random.uniform(0, 2 * math.pi)
            angle2 = angle1 + math.pi / 3  # 60 degrees apart
            
            start_pos = Position(
                latitude=center_pos.latitude + radius * math.cos(angle1),
                longitude=center_pos.longitude + radius * math.sin(angle1)
            )
            end_pos = Position(
                latitude=center_pos.latitude + radius * math.cos(angle2), 
                longitude=center_pos.longitude + radius * math.sin(angle2)
            )
            route_name = f"Fishing_Grounds_{location_hint.replace(' ', '_')}_{route_index}"
            
        elif route_type == RouteType.PATROL:
            # Patrol boats work back and forth
            distance = 0.5  # degrees (about 30 nautical miles)
            bearing = random.uniform(0, 2 * math.pi)
            
            start_pos = Position(
                latitude=center_pos.latitude + distance * math.cos(bearing),
                longitude=center_pos.longitude + distance * math.sin(bearing)
            )
            end_pos = Position(
                latitude=center_pos.latitude - distance * math.cos(bearing),
                longitude=center_pos.longitude - distance * math.sin(bearing)
            )
            route_name = f"Patrol_{location_hint.replace(' ', '_')}_{route_index}"
            
        else:
            # Ferry/cargo routes - point to point
            distance = 1.0  # degrees (about 60 nautical miles)
            bearing = random.uniform(0, 2 * math.pi)
            
            start_pos = Position(
                latitude=center_pos.latitude + distance * 0.5 * math.cos(bearing),
                longitude=center_pos.longitude + distance * 0.5 * math.sin(bearing)
            )
            end_pos = Position(
                latitude=center_pos.latitude - distance * 0.5 * math.cos(bearing),
                longitude=center_pos.longitude - distance * 0.5 * math.sin(bearing)
            )
            route_name = f"{route_type.value.title()}_{location_hint.replace(' ', '_')}_{route_index}"
        
        route = Route(start_pos, end_pos, 12.0)
        return route, route_name
    
    def _generate_regional_route(self, route_type: RouteType, region: str, route_index: int) -> Tuple[Route, str]:
        """Generate route using regional coordinates"""
        
        region_coords = self.routes_class.get_region_coordinates(region)
        
        if region_coords:
            # Pick a random area from the region
            area_name, center_pos = random.choice(list(region_coords.items()))
            return self._generate_intelligent_route(route_type, region, area_name.replace('_', ' '), route_index)
        
        # Fallback to basic generation
        return self._generate_basic_route(route_type, route_index)
    
    def _generate_basic_route(self, route_type: RouteType, route_index: int) -> Tuple[Route, str]:
        """Generate a basic fallback route"""
        
        # Mediterranean default positions (more generic)
        start_pos = Position(latitude=40.5, longitude=14.0)  # Near Naples
        end_pos = Position(latitude=41.0, longitude=2.0)     # Near Barcelona
        
        route = Route(start_pos, end_pos, 12.0)
        route_name = f"Default_{route_type.value}_{route_index}"
        
        return route, route_name
    
    def _generate_ship_name(self, ship_type: ShipType, index: int, region: str = "mediterranean") -> str:
        """Generate realistic ship name based on type and region"""
        
        # Region-specific name variations
        name_prefixes = {
            "irish_sea": {
                "passenger": ["CELTIC SEA", "IRISH ROVER", "EMERALD PRINCESS", "DUBLIN BAY", "WALES EXPRESS"],
                "cargo": ["ATLANTIC TRADER", "IRISH CARGO", "CELTIC CONTAINER", "MERCHANT VOYAGER", "SUPPLY MASTER"],
                "fishing": ["NEPTUNE'S CATCH", "SEA HUNTER", "ATLANTIC FISHER", "IRISH PRIDE", "OCEAN HARVEST"],
                "patrol": ["COAST GUARD", "PATROL VESSEL", "GUARDIAN", "SEA WATCH", "MARITIME PATROL"],
                "fast": ["SPEED DEMON", "FAST CAT", "SWIFT CURRENT", "RAPID TRANSIT", "QUICK SILVER"]
            },
            "mediterranean": {
                "passenger": ["MEDITERRANEAN STAR", "AZURE PRINCESS", "BLUE COAST", "RIVIERA EXPRESS", "SUNSET FERRY"],
                "cargo": ["EUROPA TRADER", "MEDITERRANEAN CARGO", "POSEIDON CONTAINER", "APOLLO FREIGHT", "TITAN SUPPLY"],
                "fishing": ["MEDITERRANEAN CATCH", "AEGEAN FISHER", "BLUE WATER", "ANCIENT MARINER", "GOLDEN NET"],
                "patrol": ["MEDITERRANEAN PATROL", "COASTAL GUARDIAN", "BLUE SHIELD", "SEA PROTECTOR", "HARBOR WATCH"],
                "fast": ["MEDITERRANEAN ARROW", "BLUE LIGHTNING", "COASTAL RACER", "AZURE SPEED", "RAPID MEDITERRANEAN"]
            },
            "north_sea": {
                "passenger": ["NORTH SEA STAR", "NORDIC PRINCESS", "BALTIC FERRY", "SCANDINAVIAN EXPRESS", "VIKING VOYAGER"],
                "cargo": ["NORTH SEA TRADER", "BALTIC CARGO", "NORDIC CONTAINER", "SCANDINAVIAN FREIGHT", "VIKING SUPPLY"],
                "fishing": ["NORTH SEA CATCH", "NORDIC FISHER", "BALTIC HUNTER", "SCANDINAVIAN NETS", "VIKING HARVEST"],
                "patrol": ["NORTH SEA PATROL", "NORDIC GUARDIAN", "BALTIC WATCH", "SCANDINAVIAN SHIELD", "VIKING PROTECTOR"],
                "fast": ["NORTH SEA ARROW", "NORDIC LIGHTNING", "BALTIC SPEED", "SCANDINAVIAN RACER", "VIKING SWIFT"]
            },
            "asia": {
                "passenger": ["PACIFIC STAR", "ASIAN PRINCESS", "ORIENT EXPRESS", "PACIFIC VOYAGER", "EASTERN FERRY"],
                "cargo": ["PACIFIC TRADER", "ASIAN CARGO", "ORIENT CONTAINER", "TRANSPACIFIC FREIGHT", "EASTERN SUPPLY"],
                "fishing": ["PACIFIC CATCH", "ASIAN FISHER", "ORIENT NETS", "DRAGON BOAT", "EASTERN HARVEST"],
                "patrol": ["PACIFIC PATROL", "ASIAN GUARDIAN", "ORIENT WATCH", "DRAGON SHIELD", "EASTERN PROTECTOR"],
                "fast": ["PACIFIC ARROW", "ASIAN LIGHTNING", "ORIENT SPEED", "DRAGON RACER", "EASTERN SWIFT"]
            }
        }
        
        # Map ship types to name categories
        type_to_category = {
            ShipType.PASSENGER: "passenger",
            ShipType.CARGO: "cargo",
            ShipType.FISHING: "fishing",
            ShipType.PILOT_VESSEL: "patrol",
            ShipType.HIGH_SPEED_CRAFT: "fast",
        }
        
        # Get names for region and type, fallback to mediterranean if region not found
        region_names = name_prefixes.get(region.lower(), name_prefixes["mediterranean"])
        category = type_to_category.get(ship_type, "cargo")
        names = region_names.get(category, region_names["cargo"])
        
        return f"{names[index % len(names)]}_{index + 1}"
