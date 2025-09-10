"""
MCP Server for AIS Ship Generation
Exposes ship generation capabilities via Model Context Protocol
"""

import json
import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime

from ..generators.multi_ship_generator import MultiShipGenerator, IrishSeaRoutes
from ..core.models import ShipType, Position, Route
from ..core.file_output import FileOutputManager


class AISMCPServer:
    """MCP Server exposing AIS generation tools"""
    
    def __init__(self):
        self.generator = MultiShipGenerator()
        self.file_manager = FileOutputManager()
        self.available_tools = self._define_tools()
    
    def _define_tools(self) -> Dict[str, Dict[str, Any]]:
        """Define MCP tools for LLM to use"""
        return {
            "generate_irish_sea_scenario": {
                "description": "Generate multiple ships in the Irish Sea with realistic routes",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "num_ships": {
                            "type": "integer",
                            "description": "Number of ships to generate (1-10)",
                            "minimum": 1,
                            "maximum": 10
                        },
                        "duration_hours": {
                            "type": "number",
                            "description": "How long to simulate movement in hours",
                            "default": 2.0
                        },
                        "report_interval_minutes": {
                            "type": "integer", 
                            "description": "Interval between AIS reports in minutes",
                            "default": 5
                        },
                        "scenario_name": {
                            "type": "string",
                            "description": "Name for the generated scenario",
                            "default": "irish_sea_scenario"
                        }
                    },
                    "required": ["num_ships"]
                }
            },
            
            "generate_custom_ships": {
                "description": "Generate ships with specific types and routes",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "ships": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "ship_type": {
                                        "type": "string",
                                        "enum": ["PASSENGER", "CARGO", "FISHING", "PILOT_VESSEL", "HIGH_SPEED_CRAFT"],
                                        "description": "Type of ship"
                                    },
                                    "ship_name": {
                                        "type": "string",
                                        "description": "Name of the ship"
                                    },
                                    "start_port": {
                                        "type": "string",
                                        "enum": ["DUBLIN", "HOLYHEAD", "LIVERPOOL", "BELFAST", "CORK", "SWANSEA", "ISLE_OF_MAN", "CARDIFF"],
                                        "description": "Starting port"
                                    },
                                    "end_port": {
                                        "type": "string", 
                                        "enum": ["DUBLIN", "HOLYHEAD", "LIVERPOOL", "BELFAST", "CORK", "SWANSEA", "ISLE_OF_MAN", "CARDIFF"],
                                        "description": "Destination port"
                                    }
                                },
                                "required": ["ship_type", "start_port", "end_port"]
                            },
                            "description": "List of ships to generate"
                        },
                        "duration_hours": {
                            "type": "number",
                            "description": "Simulation duration in hours",
                            "default": 2.0
                        },
                        "scenario_name": {
                            "type": "string",
                            "description": "Name for the scenario",
                            "default": "custom_scenario"
                        }
                    },
                    "required": ["ships"]
                }
            },
            
            "list_available_ports": {
                "description": "List all available ports in the Irish Sea",
                "parameters": {
                    "type": "object",
                    "properties": {}
                }
            },
            
            "get_ship_types": {
                "description": "Get information about available ship types",
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
            if tool_name == "generate_irish_sea_scenario":
                return await self._generate_irish_sea_scenario(parameters)
            elif tool_name == "generate_custom_ships":
                return await self._generate_custom_ships(parameters)
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
    
    async def _generate_irish_sea_scenario(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Generate Irish Sea scenario with multiple ships"""
        
        num_ships = params.get("num_ships", 3)
        duration_hours = params.get("duration_hours", 2.0)
        report_interval_minutes = params.get("report_interval_minutes", 5)
        scenario_name = params.get("scenario_name", "irish_sea_scenario")
        
        # Generate ships
        ships = self.generator.generate_irish_sea_scenario(num_ships)
        
        # Generate movement data
        all_ship_data = {}
        ship_summaries = []
        
        for ship in ships:
            # Generate movement
            report_interval_seconds = report_interval_minutes * 60
            states = list(ship.generate_movement(duration_hours, report_interval_seconds))
            all_ship_data[ship.mmsi] = states
            
            # Create summary
            ship_summaries.append({
                "mmsi": ship.mmsi,
                "name": ship.ship_name,
                "type": ship.ship_type.name,
                "route_type": ship.route_type.value,
                "speed_knots": ship.route.speed_knots,
                "distance_nm": ship.total_distance_nm,
                "estimated_time_hours": ship.total_time_hours,
                "total_reports": len(states)
            })
        
        # Save to file
        saved_files = self.file_manager.save_multi_ship_data(
            all_ship_data, f"{scenario_name}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        )
        
        return {
            "success": True,
            "scenario_name": scenario_name,
            "ships_generated": len(ships),
            "duration_hours": duration_hours,
            "report_interval_minutes": report_interval_minutes,
            "ships": ship_summaries,
            "saved_files": saved_files,
            "message": f"Generated {len(ships)} ships in Irish Sea scenario. Data saved to {saved_files.get('json', 'file')}"
        }
    
    async def _generate_custom_ships(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Generate custom ships with specific configurations"""
        
        ships_config = params.get("ships", [])
        duration_hours = params.get("duration_hours", 2.0)
        scenario_name = params.get("scenario_name", "custom_scenario")
        
        if not ships_config:
            return {"success": False, "error": "No ships specified"}
        
        # Port positions mapping
        port_positions = {
            "DUBLIN": IrishSeaRoutes.DUBLIN,
            "HOLYHEAD": IrishSeaRoutes.HOLYHEAD,
            "LIVERPOOL": IrishSeaRoutes.LIVERPOOL,
            "BELFAST": IrishSeaRoutes.BELFAST,
            "CORK": IrishSeaRoutes.CORK,
            "SWANSEA": IrishSeaRoutes.SWANSEA,
            "ISLE_OF_MAN": IrishSeaRoutes.ISLE_OF_MAN,
            "CARDIFF": IrishSeaRoutes.CARDIFF
        }
        
        # Ship type mapping
        ship_type_mapping = {
            "PASSENGER": ShipType.PASSENGER,
            "CARGO": ShipType.CARGO,
            "FISHING": ShipType.FISHING,
            "PILOT_VESSEL": ShipType.PILOT_VESSEL,
            "HIGH_SPEED_CRAFT": ShipType.HIGH_SPEED_CRAFT
        }
        
        generated_ships = []
        all_ship_data = {}
        ship_summaries = []
        
        for i, ship_config in enumerate(ships_config):
            # Get configuration
            ship_type_str = ship_config.get("ship_type", "CARGO")
            ship_name = ship_config.get("ship_name", f"CUSTOM_SHIP_{i+1}")
            start_port = ship_config.get("start_port", "DUBLIN")
            end_port = ship_config.get("end_port", "HOLYHEAD")
            
            # Convert to objects
            ship_type = ship_type_mapping.get(ship_type_str, ShipType.CARGO)
            start_pos = port_positions.get(start_port, IrishSeaRoutes.DUBLIN)
            end_pos = port_positions.get(end_port, IrishSeaRoutes.HOLYHEAD)
            
            # Create route and ship
            route = Route(start_pos, end_pos, 12.0)  # Base speed
            mmsi = self.generator.ship_counter + i
            
            from ..generators.multi_ship_generator import RealisticShipMovement, RouteType
            # Determine route type from ship type
            route_type = RouteType.FERRY if ship_type == ShipType.PASSENGER else RouteType.CARGO
            
            ship = RealisticShipMovement(route, mmsi, ship_name, ship_type, route_type)
            generated_ships.append(ship)
            
            # Generate movement data
            states = list(ship.generate_movement(duration_hours, 300))  # 5 minute intervals
            all_ship_data[ship.mmsi] = states
            
            ship_summaries.append({
                "mmsi": ship.mmsi,
                "name": ship.ship_name,
                "type": ship.ship_type.name,
                "start_port": start_port,
                "end_port": end_port,
                "speed_knots": ship.route.speed_knots,
                "distance_nm": ship.total_distance_nm,
                "estimated_time_hours": ship.total_time_hours,
                "total_reports": len(states)
            })
        
        # Save to file
        saved_files = self.file_manager.save_multi_ship_data(
            all_ship_data, f"{scenario_name}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        )
        
        return {
            "success": True,
            "scenario_name": scenario_name,
            "ships_generated": len(generated_ships),
            "duration_hours": duration_hours,
            "ships": ship_summaries,
            "saved_files": saved_files,
            "message": f"Generated {len(generated_ships)} custom ships. Data saved to {saved_files.get('json', 'file')}"
        }
    
    async def _list_available_ports(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """List all available ports"""
        
        ports = {
            "DUBLIN": {"lat": 53.3498, "lon": -6.2603, "country": "Ireland"},
            "HOLYHEAD": {"lat": 53.3090, "lon": -4.6324, "country": "Wales"},
            "LIVERPOOL": {"lat": 53.4084, "lon": -2.9916, "country": "England"},
            "BELFAST": {"lat": 54.5973, "lon": -5.9301, "country": "Northern Ireland"},
            "CORK": {"lat": 51.8969, "lon": -8.4863, "country": "Ireland"},
            "SWANSEA": {"lat": 51.6214, "lon": -3.9436, "country": "Wales"},
            "ISLE_OF_MAN": {"lat": 54.1936, "lon": -4.5591, "country": "Isle of Man"},
            "CARDIFF": {"lat": 51.4816, "lon": -3.1791, "country": "Wales"}
        }
        
        return {
            "success": True,
            "ports": ports,
            "total_ports": len(ports),
            "message": f"Available ports in the Irish Sea region: {', '.join(ports.keys())}"
        }
    
    async def _get_ship_types(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get information about ship types"""
        
        ship_types = {
            "PASSENGER": {
                "description": "Passenger ferries and cruise ships",
                "typical_speed": "12-18 knots",
                "routes": "Regular scheduled ferry routes",
                "example": "Dublin-Holyhead ferry"
            },
            "CARGO": {
                "description": "Container ships and bulk carriers",
                "typical_speed": "8-12 knots",
                "routes": "Commercial shipping lanes",
                "example": "Container ship from Dublin to Liverpool"
            },
            "FISHING": {
                "description": "Commercial fishing vessels",
                "typical_speed": "6-10 knots", 
                "routes": "Circular patterns in fishing grounds",
                "example": "Trawler fishing in Irish Sea grounds"
            },
            "PILOT_VESSEL": {
                "description": "Pilot boats and patrol vessels",
                "typical_speed": "15-25 knots",
                "routes": "Harbor approaches and patrol patterns",
                "example": "Dublin Bay pilot vessel"
            },
            "HIGH_SPEED_CRAFT": {
                "description": "Fast passenger boats and hydrofoils", 
                "typical_speed": "20-40 knots",
                "routes": "Express passenger services",
                "example": "High-speed ferry between ports"
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
