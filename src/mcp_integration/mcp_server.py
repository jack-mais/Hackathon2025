"""
Simplified MCP Server for AIS Ship Generation
Single unified tool that handles all generation requests
"""

import json
import asyncio
import random
import re
import math
from typing import Dict, List, Any, Optional
from datetime import datetime

from ..generators.ais_generator import AISGenerator, Position, Route, ShipType, RouteType, RealisticShipMovement
from ..core.file_output import FileOutputManager


class AISMCPServer:
    """Simplified MCP Server with one unified generation tool"""
    
    def __init__(self):
        self.generator = AISGenerator()
        self.file_manager = FileOutputManager()
        self.available_tools = self._define_tools()
    
    def _define_tools(self) -> Dict[str, Dict[str, Any]]:
        """Define simplified MCP tools - one unified generation tool"""
        return {
            "generate_ais_data": {
                "description": "Generate AIS ship tracking data for any location worldwide",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "num_ships": {
                            "type": "integer",
                            "description": "Number of ships to generate (1-20)",
                            "minimum": 1,
                            "maximum": 20,
                            "default": 3
                        },
                        "location": {
                            "type": "string",
                            "description": "Location description (e.g. 'Southampton', 'off coast of Sicily', 'North Sea', coordinates)",
                            "default": "Mediterranean Sea"
                        },
                        "ship_types": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Optional ship types: CARGO, PASSENGER, FISHING, PILOT_VESSEL, HIGH_SPEED_CRAFT",
                            "default": []
                        },
                        "destination": {
                            "type": "string", 
                            "description": "Optional destination for point-to-point routes",
                            "default": ""
                        },
                        "duration_hours": {
                            "type": "number",
                            "description": "Simulation duration in hours",
                            "default": 3.0,
                            "minimum": 0.5,
                            "maximum": 48.0
                        },
                        "scenario_name": {
                            "type": "string",
                            "description": "Name for the scenario",
                            "default": "ais_scenario"
                        }
                    },
                    "required": ["num_ships", "location"]
                }
            },
            
            "list_available_ports": {
                "description": "List major ports worldwide",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "region": {
                            "type": "string",
                            "description": "Optional region filter",
                            "default": "all"
                        }
                    }
                }
            },
            
            "get_ship_types": {
                "description": "Get available ship types and their characteristics",
                "parameters": {
                    "type": "object",
                    "properties": {}
                }
            }
        }
    
    async def call_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Call a specific MCP tool"""
        
        if tool_name not in self.available_tools:
            return {
                "success": False,
                "error": f"Unknown tool: {tool_name}",
                "available_tools": list(self.available_tools.keys())
            }
        
        try:
            if tool_name == "generate_ais_data":
                return await self._generate_ais_data(parameters)
            elif tool_name == "list_available_ports":
                return await self._list_available_ports(parameters)
            elif tool_name == "get_ship_types":
                return await self._get_ship_types(parameters)
            else:
                return {"success": False, "error": f"Tool {tool_name} not implemented"}
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Error calling {tool_name}: {str(e)}"
            }
    
    async def _generate_ais_data(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Generate AIS data based on flexible location parameters"""
        
        num_ships = params.get("num_ships", 3)
        location = params.get("location", "Mediterranean Sea")
        ship_types = params.get("ship_types", [])
        destination = params.get("destination", "")
        duration_hours = params.get("duration_hours", 3.0)
        scenario_name = params.get("scenario_name", "ais_scenario")
        
        print(f"🗺️ Generating {num_ships} ships at '{location}'")
        if destination:
            print(f"🎯 Destination: '{destination}'")
        
        try:
            # Parse the location to get coordinates
            start_coords = self._parse_location(location)
            end_coords = None
            
            if destination:
                end_coords = self._parse_location(destination)
            
            # Generate ships
            ships = []
            ship_summaries = []
            all_ship_data = {}
            
            for i in range(num_ships):
                # Determine ship type
                if ship_types and i < len(ship_types):
                    ship_type_str = ship_types[i].upper()
                elif ship_types:
                    ship_type_str = random.choice(ship_types).upper()
                else:
                    # Generate variety of ship types for better visualization
                    ship_type_str = self._get_varied_ship_type(i, num_ships, location)
                
                ship_type = self._str_to_ship_type(ship_type_str)
                
                # Create route
                if end_coords:
                    # Point-to-point route
                    route_start = start_coords
                    route_end = end_coords
                else:
                    # Generate local movement area around the location
                    route_start = start_coords
                    route_end = self._generate_nearby_position(start_coords, ship_type)
                
                # Create route with appropriate speed
                speed = self._get_ship_speed(ship_type)
                route = Route(route_start, route_end, speed)
                
                # Create ship
                mmsi = 123456000 + i
                ship_name = self._generate_ship_name(ship_type, i, location)
                
                route_type = self._get_route_type(ship_type)
                
                ship = RealisticShipMovement(route, mmsi, ship_name, ship_type, route_type)
                ships.append(ship)
                
                # Generate movement data
                report_interval_seconds = 5 * 60  # 5 minutes
                states = list(ship.generate_movement(duration_hours, report_interval_seconds))
                all_ship_data[ship.mmsi] = states
                
                # Create summary
                ship_summaries.append({
                    "mmsi": ship.mmsi,
                    "name": ship.ship_name,
                    "type": ship_type.name,
                    "speed_knots": ship.route.speed_knots,
                    "distance_nm": ship.total_distance_nm,
                    "estimated_time_hours": ship.total_time_hours,
                    "total_reports": len(states)
                })
            
            # Save to file
            saved_files = self.file_manager.save_multi_ship_data(
                all_ship_data, f"{scenario_name}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
            )
            
            # Create response message
            files_info = []
            if "json" in saved_files:
                files_info.append(f"📁 JSON data: {saved_files['json']}")
            if "map" in saved_files:
                files_info.append(f"🗺️ Interactive map: {saved_files['map']}")
            
            files_text = "\n".join(files_info) if files_info else "Files saved"
            
            return {
                "success": True,
                "scenario_name": scenario_name,
                "location": location,
                "destination": destination or "Local area",
                "ships_generated": len(ships),
                "duration_hours": duration_hours,
                "ships": ship_summaries,
                "saved_files": saved_files,
                "message": f"✅ Generated {len(ships)} ships near {location}!\n\n{files_text}\n\n🎯 AIS tracking data created with realistic ship movements."
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to generate AIS data: {str(e)}"
            }
    
    def _parse_location(self, location_str: str) -> Position:
        """Parse location string to coordinates"""
        location_lower = location_str.lower().strip()
        
        # Check for known ports first
        port_mapping = {
            # UK Ports
            'southampton': Position(latitude=50.8992, longitude=-1.4044),
            'portsmouth': Position(latitude=50.8058, longitude=-1.0872),
            'london': Position(latitude=51.5074, longitude=-0.1278),
            'liverpool': Position(latitude=53.4084, longitude=-2.9916),
            'glasgow': Position(latitude=55.8642, longitude=-4.2518),
            'bristol': Position(latitude=51.4545, longitude=-2.5879),
            
            # European Ports
            'rotterdam': Position(latitude=51.9225, longitude=4.4792),
            'hamburg': Position(latitude=53.5511, longitude=9.9937),
            'antwerp': Position(latitude=51.2194, longitude=4.4025),
            'marseille': Position(latitude=43.2965, longitude=5.3698),
            'barcelona': Position(latitude=41.3851, longitude=2.1734),
            'naples': Position(latitude=40.8518, longitude=14.2681),
            'venice': Position(latitude=45.4408, longitude=12.3155),
            
            # Other major ports
            'new york': Position(latitude=40.7128, longitude=-74.0060),
            'singapore': Position(latitude=1.2966, longitude=103.7764),
            'shanghai': Position(latitude=31.2304, longitude=121.4737),
            'tokyo': Position(latitude=35.6762, longitude=139.6503),
        }
        
        # Check exact port matches
        for port_name, coords in port_mapping.items():
            if port_name in location_lower:
                return coords
        
        # Check for regional/area descriptions
        area_mapping = {
            # Seas and regions
            'north sea': Position(latitude=55.0, longitude=3.0),
            'english channel': Position(latitude=50.0, longitude=-1.0),
            'irish sea': Position(latitude=53.5, longitude=-5.0),
            'mediterranean': Position(latitude=40.0, longitude=15.0),
            'mediterranean sea': Position(latitude=40.0, longitude=15.0),
            'baltic sea': Position(latitude=57.0, longitude=18.0),
            'bay of biscay': Position(latitude=44.0, longitude=-4.0),
            
            # Coastal areas
            'off southampton': Position(latitude=50.7, longitude=-1.2),
            'south of southampton': Position(latitude=50.7, longitude=-1.4),
            'outside southampton': Position(latitude=50.7, longitude=-1.2),
            'off portsmouth': Position(latitude=50.6, longitude=-0.9),
            'coast of sicily': Position(latitude=37.5, longitude=13.8),
            'off sicily': Position(latitude=37.0, longitude=13.0),
            'coast of spain': Position(latitude=41.2, longitude=2.0),
            'coast of france': Position(latitude=43.5, longitude=7.0),
            'norwegian coast': Position(latitude=58.0, longitude=5.0),
            'dutch coast': Position(latitude=52.5, longitude=4.0),
            
            # Countries (use major port)
            'uk': Position(latitude=51.5, longitude=-1.0),
            'england': Position(latitude=51.5, longitude=-1.0),
            'france': Position(latitude=43.3, longitude=5.4),
            'spain': Position(latitude=41.4, longitude=2.2),
            'italy': Position(latitude=40.9, longitude=14.3),
            'germany': Position(latitude=53.6, longitude=10.0),
            'netherlands': Position(latitude=51.9, longitude=4.5),
            'norway': Position(latitude=58.0, longitude=5.0),
        }
        
        for area_name, coords in area_mapping.items():
            if area_name in location_lower:
                return coords
        
        # If no match found, try to extract coordinates from text
        coord_match = re.search(r'(\d+\.?\d*)[°\s]*[NnSs][,\s]+(\d+\.?\d*)[°\s]*[EeWw]', location_str)
        if coord_match:
            lat = float(coord_match.group(1))
            lon = float(coord_match.group(2))
            # Handle N/S and E/W
            if 's' in location_lower:
                lat = -lat
            if 'w' in location_lower:
                lon = -lon
            return Position(latitude=lat, longitude=lon)
        
        # Default fallback - generic ocean position
        print(f"⚠️ Unknown location '{location_str}', using default coordinates")
        return Position(latitude=50.0, longitude=0.0)  # English Channel
    
    def _generate_nearby_position(self, start_pos: Position, ship_type: ShipType) -> Position:
        """Generate a nearby position for local area movement"""
        
        # Distance based on ship type
        if ship_type == ShipType.FISHING:
            max_distance = 0.3  # ~20 nautical miles
        elif ship_type == ShipType.PILOT_VESSEL:
            max_distance = 0.2  # ~15 nautical miles  
        else:
            max_distance = 0.5  # ~35 nautical miles
        
        # Random direction
        angle = random.uniform(0, 2 * math.pi)
        distance = random.uniform(0.1, max_distance)
        
        # Calculate new position
        lat_offset = distance * math.cos(angle)
        lon_offset = distance * math.sin(angle)
        
        return Position(
            latitude=start_pos.latitude + lat_offset,
            longitude=start_pos.longitude + lon_offset
        )
    
    def _infer_ship_type(self, location: str) -> str:
        """Infer likely ship type from location context"""
        location_lower = location.lower()
        
        if any(word in location_lower for word in ['tanker', 'oil', 'cargo', 'container']):
            return 'CARGO'
        elif any(word in location_lower for word in ['fishing', 'trawl', 'nets']):
            return 'FISHING' 
        elif any(word in location_lower for word in ['ferry', 'passenger', 'cruise']):
            return 'PASSENGER'
        elif any(word in location_lower for word in ['patrol', 'coast guard', 'military']):
            return 'PILOT_VESSEL'
        elif any(word in location_lower for word in ['fast', 'speed', 'racing']):
            return 'HIGH_SPEED_CRAFT'
        else:
            # Default based on location
            if any(word in location_lower for word in ['port', 'harbour', 'harbor']):
                return 'CARGO'  # Port areas likely cargo
            else:
                return 'CARGO'  # Default to cargo ships
    
    def _get_varied_ship_type(self, ship_index: int, total_ships: int, location: str) -> str:
        """Get varied ship types for better map visualization"""
        # Define ship types in order of preference for variety
        ship_types = ['CARGO', 'PASSENGER', 'FISHING', 'PILOT_VESSEL', 'HIGH_SPEED_CRAFT']
        
        # If we have more ships than types, cycle through them
        if total_ships <= len(ship_types):
            return ship_types[ship_index % len(ship_types)]
        else:
            # For many ships, mix types based on location context
            base_type = self._infer_ship_type(location)
            if ship_index == 0:
                return base_type
            else:
                # Alternate between base type and other types
                other_types = [t for t in ship_types if t != base_type]
                return other_types[(ship_index - 1) % len(other_types)]
    
    def _str_to_ship_type(self, ship_type_str: str) -> ShipType:
        """Convert string to ShipType enum"""
        mapping = {
            'CARGO': ShipType.CARGO,
            'PASSENGER': ShipType.PASSENGER, 
            'FISHING': ShipType.FISHING,
            'PILOT_VESSEL': ShipType.PILOT_VESSEL,
            'HIGH_SPEED_CRAFT': ShipType.HIGH_SPEED_CRAFT
        }
        return mapping.get(ship_type_str.upper(), ShipType.CARGO)
    
    def _get_ship_speed(self, ship_type: ShipType) -> float:
        """Get appropriate speed for ship type"""
        speeds = {
            ShipType.CARGO: 12.0,
            ShipType.PASSENGER: 18.0,
            ShipType.FISHING: 8.0,
            ShipType.PILOT_VESSEL: 20.0,
            ShipType.HIGH_SPEED_CRAFT: 35.0
        }
        return speeds.get(ship_type, 12.0)
    
    def _get_route_type(self, ship_type: ShipType):
        """Get route type for ship type"""        
        mapping = {
            ShipType.CARGO: RouteType.CARGO,
            ShipType.PASSENGER: RouteType.FERRY,
            ShipType.FISHING: RouteType.FISHING,
            ShipType.PILOT_VESSEL: RouteType.PATROL,
            ShipType.HIGH_SPEED_CRAFT: RouteType.COASTAL
        }
        return mapping.get(ship_type, RouteType.CARGO)
    
    def _generate_ship_name(self, ship_type: ShipType, index: int, location: str) -> str:
        """Generate ship name based on type and location"""
        
        # Extract region/country from location
        location_lower = location.lower()
        region = "MARITIME"
        
        if any(word in location_lower for word in ['uk', 'england', 'british', 'southampton', 'london']):
            region = "BRITISH"
        elif any(word in location_lower for word in ['mediterranean', 'italy', 'spain', 'france']):
            region = "EUROPEAN"
        elif any(word in location_lower for word in ['north sea', 'norwegian', 'dutch', 'german']):
            region = "NORTHERN"
        elif any(word in location_lower for word in ['asia', 'singapore', 'china', 'japan']):
            region = "ASIAN"
        
        # Ship type prefixes
        prefixes = {
            ShipType.CARGO: [f"{region} TRADER", f"{region} CARGO", f"{region} CONTAINER"],
            ShipType.PASSENGER: [f"{region} FERRY", f"{region} STAR", f"{region} PRINCESS"], 
            ShipType.FISHING: [f"{region} FISHER", f"{region} CATCH", f"{region} HUNTER"],
            ShipType.PILOT_VESSEL: [f"{region} PILOT", f"{region} PATROL", f"{region} GUARDIAN"],
            ShipType.HIGH_SPEED_CRAFT: [f"{region} ARROW", f"{region} SPEED", f"{region} SWIFT"]
        }
        
        prefix_list = prefixes.get(ship_type, [f"{region} VESSEL"])
        chosen_prefix = prefix_list[index % len(prefix_list)]
        
        return f"{chosen_prefix}_{index + 1}"
    
    async def _list_available_ports(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """List available ports"""
        
        # Simplified port list
        ports = {
            "SOUTHAMPTON": {"latitude": 50.8992, "longitude": -1.4044, "country": "UK"},
            "PORTSMOUTH": {"latitude": 50.8058, "longitude": -1.0872, "country": "UK"},
            "LIVERPOOL": {"latitude": 53.4084, "longitude": -2.9916, "country": "UK"},
            "ROTTERDAM": {"latitude": 51.9225, "longitude": 4.4792, "country": "Netherlands"},
            "HAMBURG": {"latitude": 53.5511, "longitude": 9.9937, "country": "Germany"},
            "BARCELONA": {"latitude": 41.3851, "longitude": 2.1734, "country": "Spain"},
            "MARSEILLE": {"latitude": 43.2965, "longitude": 5.3698, "country": "France"},
            "NAPLES": {"latitude": 40.8518, "longitude": 14.2681, "country": "Italy"},
            "SINGAPORE": {"latitude": 1.2966, "longitude": 103.7764, "country": "Singapore"},
            "NEW_YORK": {"latitude": 40.7128, "longitude": -74.0060, "country": "USA"}
        }
        
        return {
            "success": True,
            "ports": ports,
            "total_ports": len(ports),
            "message": f"Available major ports: {', '.join(ports.keys())}"
        }
    
    async def _get_ship_types(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get ship types information"""
        
        ship_types = {
            "CARGO": {
                "description": "Cargo ships, container vessels, tankers",
                "typical_speed": "10-15 knots",
                "characteristics": "Large, slow, point-to-point routes"
            },
            "PASSENGER": {
                "description": "Ferries, cruise ships, passenger vessels",
                "typical_speed": "15-20 knots", 
                "characteristics": "Regular routes, scheduled services"
            },
            "FISHING": {
                "description": "Fishing vessels, trawlers",
                "typical_speed": "6-10 knots",
                "characteristics": "Circular patterns, fishing grounds"
            },
            "PILOT_VESSEL": {
                "description": "Pilot boats, patrol vessels, coast guard",
                "typical_speed": "15-25 knots",
                "characteristics": "Harbor approaches, patrol patterns" 
            },
            "HIGH_SPEED_CRAFT": {
                "description": "Fast boats, hydrofoils, speedboats",
                "typical_speed": "25-40 knots",
                "characteristics": "High speed, short routes"
            }
        }
        
        return {
            "success": True,
            "ship_types": ship_types,
            "total_types": len(ship_types),
            "message": f"Available ship types: {', '.join(ship_types.keys())}"
        }
    
    def get_tools_schema(self) -> Dict[str, Any]:
        """Get the tools schema for LLM"""
        return {
            "tools": [
                {
                    "type": "function",
                    "function": {
                        "name": tool_name,
                        "description": tool_info["description"],
                        "parameters": tool_info["parameters"]
                    }
                }
                for tool_name, tool_info in self.available_tools.items()
            ]
        }
