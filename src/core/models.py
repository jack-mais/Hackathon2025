"""Core data models for AIS/NMEA generation"""

from dataclasses import dataclass
from datetime import datetime
from enum import IntEnum
from typing import Optional


class ShipType(IntEnum):
    """AIS ship and cargo types"""
    FISHING = 30
    TOWING = 31
    DREDGING = 33
    DIVING_OPS = 34
    SAILING = 36
    PLEASURE_CRAFT = 37
    HIGH_SPEED_CRAFT = 40
    PILOT_VESSEL = 50
    SEARCH_RESCUE = 51
    TUG = 52
    PORT_TENDER = 53
    ANTI_POLLUTION = 54
    LAW_ENFORCEMENT = 55
    MEDICAL_TRANSPORT = 58
    PASSENGER = 60
    CARGO = 70
    TANKER = 80
    OTHER = 90


class NavigationStatus(IntEnum):
    """AIS navigation status codes"""
    UNDER_WAY_USING_ENGINE = 0
    AT_ANCHOR = 1
    NOT_UNDER_COMMAND = 2
    RESTRICTED_MANEUVERABILITY = 3
    CONSTRAINED_BY_DRAUGHT = 4
    MOORED = 5
    AGROUND = 6
    ENGAGED_IN_FISHING = 7
    UNDER_WAY_SAILING = 8
    RESERVED_9 = 9
    RESERVED_10 = 10
    RESERVED_11 = 11
    RESERVED_12 = 12
    RESERVED_13 = 13
    AIS_SART = 14
    NOT_DEFINED = 15


@dataclass
class Position:
    """Geographic position with latitude and longitude"""
    latitude: float  # Degrees, positive = North
    longitude: float  # Degrees, positive = East
    
    def __post_init__(self):
        # Validate ranges
        if not -90 <= self.latitude <= 90:
            raise ValueError(f"Latitude {self.latitude} out of range [-90, 90]")
        if not -180 <= self.longitude <= 180:
            raise ValueError(f"Longitude {self.longitude} out of range [-180, 180]")


@dataclass
class ShipState:
    """Current state of a ship for AIS reporting"""
    mmsi: int  # Maritime Mobile Service Identity
    position: Position
    speed_over_ground: float  # Knots
    course_over_ground: float  # Degrees (0-359.9)
    heading: Optional[float]  # True heading in degrees
    navigation_status: NavigationStatus
    timestamp: datetime
    
    # Static ship information
    ship_name: str = "UNKNOWN"
    ship_type: ShipType = ShipType.OTHER
    length: int = 100  # Meters
    width: int = 20    # Meters
    draught: float = 5.0  # Meters
    
    def __post_init__(self):
        # Validate MMSI (9 digits)
        if not 100000000 <= self.mmsi <= 999999999:
            raise ValueError(f"MMSI {self.mmsi} must be 9 digits")
        
        # Validate speed
        if self.speed_over_ground < 0:
            raise ValueError("Speed cannot be negative")
            
        # Normalize course
        self.course_over_ground = self.course_over_ground % 360


@dataclass
class Route:
    """Defines a route between waypoints"""
    start_position: Position
    end_position: Position
    speed_knots: float = 10.0
    
    def __post_init__(self):
        if self.speed_knots <= 0:
            raise ValueError("Speed must be positive")
