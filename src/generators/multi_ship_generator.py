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


class IrishSeaRoutes:
    """Predefined realistic routes in the Irish Sea"""
    
    # Major ports
    DUBLIN = Position(latitude=53.3498, longitude=-6.2603)
    HOLYHEAD = Position(latitude=53.3090, longitude=-4.6324)
    LIVERPOOL = Position(latitude=53.4084, longitude=-2.9916)
    BELFAST = Position(latitude=54.5973, longitude=-5.9301)
    CORK = Position(latitude=51.8969, longitude=-8.4863)
    SWANSEA = Position(latitude=51.6214, longitude=-3.9436)
    ISLE_OF_MAN = Position(latitude=54.1936, longitude=-4.5591)
    CARDIFF = Position(latitude=51.4816, longitude=-3.1791)
    
    @classmethod
    def get_ferry_routes(cls) -> List[Tuple[Position, Position, str]]:
        """Get common ferry routes with names"""
        return [
            (cls.DUBLIN, cls.HOLYHEAD, "Dublin-Holyhead Ferry"),
            (cls.BELFAST, cls.LIVERPOOL, "Belfast-Liverpool Ferry"),
            (cls.CORK, cls.SWANSEA, "Cork-Swansea Ferry"),
            (cls.DUBLIN, cls.ISLE_OF_MAN, "Dublin-Isle of Man"),
            (cls.HOLYHEAD, cls.DUBLIN, "Holyhead-Dublin Ferry"),
            (cls.LIVERPOOL, cls.BELFAST, "Liverpool-Belfast Ferry"),
        ]
    
    @classmethod 
    def get_cargo_routes(cls) -> List[Tuple[Position, Position, str]]:
        """Get cargo ship routes"""
        return [
            (cls.DUBLIN, cls.LIVERPOOL, "Dublin-Liverpool Cargo"),
            (cls.CORK, cls.CARDIFF, "Cork-Cardiff Cargo"),
            (cls.BELFAST, cls.SWANSEA, "Belfast-Swansea Container"),
            (cls.LIVERPOOL, cls.DUBLIN, "Liverpool-Dublin Supply"),
        ]
    
    @classmethod
    def get_fishing_areas(cls) -> List[Tuple[Position, Position, str]]:
        """Get fishing areas (circular/patrol patterns)"""
        # Fishing grounds in Irish Sea
        return [
            (Position(53.7, -5.5), Position(53.9, -5.3), "North Irish Sea Grounds"),
            (Position(52.5, -5.8), Position(52.7, -5.6), "Central Irish Sea Grounds"), 
            (Position(51.8, -4.5), Position(52.0, -4.3), "Bristol Channel Grounds"),
        ]
    
    @classmethod
    def get_coastal_patrol_routes(cls) -> List[Tuple[Position, Position, str]]:
        """Get coastal patrol routes"""
        return [
            (Position(53.4, -6.0), Position(53.6, -5.8), "Dublin Bay Patrol"),
            (Position(53.3, -4.4), Position(53.4, -4.2), "Anglesey Coast Patrol"),
            (Position(54.6, -5.8), Position(54.8, -5.6), "Belfast Lough Patrol"),
        ]


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
    
    def generate_irish_sea_scenario(self, num_ships: int = 3) -> List[RealisticShipMovement]:
        """Generate multiple ships in Irish Sea with realistic routes"""
        
        ships = []
        routes_used = set()
        
        for i in range(num_ships):
            # Choose ship type
            ship_type, route_type = self._choose_ship_and_route_type(i, num_ships)
            
            # Get route based on type
            route, route_name = self._get_route_for_type(route_type, routes_used)
            routes_used.add(route_name)
            
            # Create ship
            mmsi = self.ship_counter + i
            ship_name = self._generate_ship_name(ship_type, i)
            
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
    
    def _get_route_for_type(self, route_type: RouteType, routes_used: set) -> Tuple[Route, str]:
        """Get a route based on the route type"""
        
        if route_type == RouteType.FERRY:
            routes = IrishSeaRoutes.get_ferry_routes()
        elif route_type == RouteType.CARGO:
            routes = IrishSeaRoutes.get_cargo_routes()
        elif route_type == RouteType.FISHING:
            routes = IrishSeaRoutes.get_fishing_areas()
        elif route_type == RouteType.PATROL:
            routes = IrishSeaRoutes.get_coastal_patrol_routes()
        else:  # COASTAL
            routes = IrishSeaRoutes.get_ferry_routes()  # Use ferry routes but different behavior
        
        # Try to find unused route
        for start_pos, end_pos, name in routes:
            if name not in routes_used:
                route = Route(start_pos, end_pos, 12.0)  # Base speed, will be adjusted
                return route, name
        
        # If all used, pick random one
        start_pos, end_pos, name = random.choice(routes)
        route = Route(start_pos, end_pos, 12.0)
        return route, f"{name}_{len(routes_used)}"
    
    def _generate_ship_name(self, ship_type: ShipType, index: int) -> str:
        """Generate realistic ship name based on type"""
        
        ferry_names = ["CELTIC SEA", "IRISH ROVER", "EMERALD PRINCESS", "DUBLIN BAY", "WALES EXPRESS"]
        cargo_names = ["ATLANTIC TRADER", "IRISH CARGO", "CELTIC CONTAINER", "MERCHANT VOYAGER", "SUPPLY MASTER"] 
        fishing_names = ["NEPTUNE'S CATCH", "SEA HUNTER", "ATLANTIC FISHER", "IRISH PRIDE", "OCEAN HARVEST"]
        patrol_names = ["COAST GUARD 1", "PATROL VESSEL", "GUARDIAN", "SEA WATCH", "MARITIME PATROL"]
        fast_names = ["SPEED DEMON", "FAST CAT", "SWIFT CURRENT", "RAPID TRANSIT", "QUICK SILVER"]
        
        name_lists = {
            ShipType.PASSENGER: ferry_names,
            ShipType.CARGO: cargo_names,
            ShipType.FISHING: fishing_names,
            ShipType.PILOT_VESSEL: patrol_names,
            ShipType.HIGH_SPEED_CRAFT: fast_names,
        }
        
        names = name_lists.get(ship_type, cargo_names)
        return f"{names[index % len(names)]}_{index + 1}"
