"""AIS data generator - Crawl version (single ship point-to-point)"""

import math
from datetime import datetime, timedelta
from typing import Generator, List

from ..core.models import Position, Route, ShipState, NavigationStatus, ShipType


class SimpleShipMovement:
    """Generates simple point-to-point ship movement"""
    
    def __init__(self, route: Route, mmsi: int, ship_name: str = "TEST_VESSEL"):
        self.route = route
        self.mmsi = mmsi
        self.ship_name = ship_name
        self.current_position = route.start_position
        
        # Calculate total distance and time
        self.total_distance_nm = self._calculate_distance_nautical_miles(
            route.start_position, route.end_position
        )
        self.total_time_hours = self.total_distance_nm / route.speed_knots
        self.bearing = self._calculate_bearing(
            route.start_position, route.end_position
        )
        
    def _calculate_distance_nautical_miles(self, pos1: Position, pos2: Position) -> float:
        """Calculate distance between two positions in nautical miles using Haversine formula"""
        # Convert to radians
        lat1_rad = math.radians(pos1.latitude)
        lon1_rad = math.radians(pos1.longitude)
        lat2_rad = math.radians(pos2.latitude)
        lon2_rad = math.radians(pos2.longitude)
        
        # Haversine formula
        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad
        
        a = math.sin(dlat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        
        # Radius of Earth in nautical miles
        earth_radius_nm = 3440.065
        
        return earth_radius_nm * c
    
    def _calculate_bearing(self, pos1: Position, pos2: Position) -> float:
        """Calculate initial bearing from pos1 to pos2"""
        lat1_rad = math.radians(pos1.latitude)
        lat2_rad = math.radians(pos2.latitude)
        dlon_rad = math.radians(pos2.longitude - pos1.longitude)
        
        y = math.sin(dlon_rad) * math.cos(lat2_rad)
        x = (math.cos(lat1_rad) * math.sin(lat2_rad) - 
             math.sin(lat1_rad) * math.cos(lat2_rad) * math.cos(dlon_rad))
        
        bearing_rad = math.atan2(y, x)
        bearing_deg = math.degrees(bearing_rad)
        
        # Normalize to 0-360
        return (bearing_deg + 360) % 360
    
    def _interpolate_position(self, progress_ratio: float) -> Position:
        """Interpolate position along the route"""
        if progress_ratio >= 1.0:
            return self.route.end_position
        if progress_ratio <= 0.0:
            return self.route.start_position
            
        # Simple linear interpolation
        lat = (self.route.start_position.latitude + 
               progress_ratio * (self.route.end_position.latitude - self.route.start_position.latitude))
        lon = (self.route.start_position.longitude + 
               progress_ratio * (self.route.end_position.longitude - self.route.start_position.longitude))
        
        return Position(latitude=lat, longitude=lon)
    
    def generate_movement(self, 
                         duration_hours: float, 
                         report_interval_seconds: int = 30) -> Generator[ShipState, None, None]:
        """Generate ship states over time"""
        
        start_time = datetime.utcnow()
        total_reports = int(duration_hours * 3600 / report_interval_seconds)
        
        for report_num in range(total_reports + 1):
            # Calculate elapsed time
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
                nav_status = NavigationStatus.UNDER_WAY_USING_ENGINE
                speed = self.route.speed_knots
            
            # Generate ship state
            current_position = self._interpolate_position(progress_ratio)
            
            ship_state = ShipState(
                mmsi=self.mmsi,
                position=current_position,
                speed_over_ground=speed,
                course_over_ground=self.bearing if speed > 0 else 0.0,
                heading=self.bearing if speed > 0 else None,
                navigation_status=nav_status,
                timestamp=current_time,
                ship_name=self.ship_name,
                ship_type=ShipType.CARGO,
                length=150,
                width=25,
                draught=8.5
            )
            
            yield ship_state
            
            # Stop if we've reached the destination
            if progress_ratio >= 1.0:
                break


class AISGenerator:
    """Main AIS data generator - Crawl version"""
    
    def __init__(self):
        self.active_ships: List[SimpleShipMovement] = []
    
    def create_simple_route(self, 
                          start_lat: float, 
                          start_lon: float, 
                          end_lat: float, 
                          end_lon: float, 
                          speed_knots: float = 10.0) -> Route:
        """Create a simple point-to-point route"""
        return Route(
            start_position=Position(start_lat, start_lon),
            end_position=Position(end_lat, end_lon),
            speed_knots=speed_knots
        )
    
    def add_ship(self, route: Route, mmsi: int, ship_name: str = "VESSEL") -> SimpleShipMovement:
        """Add a ship to the generator"""
        ship = SimpleShipMovement(route, mmsi, ship_name)
        self.active_ships.append(ship)
        return ship
    
    def generate_sample_irish_sea_route(self) -> Route:
        """Generate a sample route in the Irish Sea"""
        # Dublin to Holyhead (main ferry route)
        dublin_port = Position(latitude=53.3498, longitude=-6.2603)
        holyhead_port = Position(latitude=53.3090, longitude=-4.6324)
        
        return Route(
            start_position=dublin_port,
            end_position=holyhead_port,
            speed_knots=12.0
        )
