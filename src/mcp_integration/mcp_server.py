"""
MCP Server for AIS Ship Generation
Exposes ship generation capabilities via Model Context Protocol
"""

import json
import asyncio
import random
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
            
            "generate_maritime_scenario": {
                "description": "Generate multiple ships in any maritime region worldwide with realistic routes",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "num_ships": {
                            "type": "integer",
                            "description": "Number of ships to generate (1-10)",
                            "minimum": 1,
                            "maximum": 10
                        },
                        "region": {
                            "type": "string",
                            "description": "Maritime region (mediterranean, north_sea, nordic, asia, north_america, europe, irish_sea)",
                            "default": "mediterranean",
                            "enum": ["mediterranean", "north_sea", "nordic", "asia", "north_america", "europe", "irish_sea"]
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
                            "default": "maritime_scenario"
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
                "description": "List all available ports worldwide or in a specific region",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "region": {
                            "type": "string",
                            "description": "Maritime region to filter by (optional, returns all if not specified)",
                            "enum": ["mediterranean", "north_sea", "nordic", "asia", "north_america", "europe", "irish_sea", "all"]
                        }
                    }
                }
            },
            
            "get_ship_types": {
                "description": "Get information about available ship types",
                "parameters": {
                    "type": "object", 
                    "properties": {}
                }
            },
            
            "generate_coordinate_scenario": {
                "description": "Generate ships using specific coordinates",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "coordinates": {
                            "type": "array",
                            "items": {
                                "type": "array",
                                "items": {"type": "number"},
                                "minItems": 2,
                                "maxItems": 2
                            },
                            "description": "Array of [latitude, longitude] coordinate pairs"
                        },
                        "num_ships": {
                            "type": "integer",
                            "description": "Number of ships to generate",
                            "minimum": 1,
                            "maximum": 20,
                            "default": 3
                        },
                        "duration_hours": {
                            "type": "number",
                            "description": "Simulation duration in hours",
                            "default": 2.0
                        },
                        "scenario_name": {
                            "type": "string",
                            "description": "Name for the scenario",
                            "default": "coordinate_scenario"
                        }
                    },
                    "required": ["coordinates"]
                }
            },
            
            "generate_specialized_scenario": {
                "description": "Generate specialized maritime scenarios (convoy, rescue, cruise, etc.)",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "scenario_type": {
                            "type": "string",
                            "enum": ["convoy", "rescue_operation", "cruise_tourism", "military_exercise", "fishing_fleet", "port_operations", "storm_avoidance", "oil_platform", "racing_regatta"],
                            "description": "Type of specialized scenario"
                        },
                        "num_ships": {
                            "type": "integer",
                            "description": "Number of ships in the scenario",
                            "minimum": 1,
                            "maximum": 30,
                            "default": 5
                        },
                        "region": {
                            "type": "string",
                            "description": "Maritime region for the scenario",
                            "default": "mediterranean"
                        },
                        "duration_hours": {
                            "type": "number",
                            "description": "Simulation duration in hours",
                            "default": 3.0
                        },
                        "special_parameters": {
                            "type": "object",
                            "properties": {
                                "formation_spacing": {"type": "number", "description": "Spacing between ships in nautical miles"},
                                "emergency_urgency": {"type": "string", "enum": ["low", "medium", "high"]},
                                "weather_severity": {"type": "string", "enum": ["mild", "moderate", "severe"]},
                                "operation_complexity": {"type": "string", "enum": ["simple", "complex", "expert"]}
                            }
                        },
                        "scenario_name": {
                            "type": "string",
                            "description": "Custom name for the scenario",
                            "default": "specialized_scenario"
                        }
                    },
                    "required": ["scenario_type"]
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
            elif tool_name == "generate_maritime_scenario":
                return await self._generate_maritime_scenario(parameters)
            elif tool_name == "generate_custom_ships":
                return await self._generate_custom_ships(parameters)
            elif tool_name == "generate_coordinate_scenario":
                return await self._generate_coordinate_scenario(parameters)
            elif tool_name == "generate_specialized_scenario":
                return await self._generate_specialized_scenario(parameters)
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
        
        return await self._process_ship_generation(ships, duration_hours, report_interval_minutes, scenario_name, "irish_sea")
    
    async def _generate_maritime_scenario(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Generate maritime scenario in any region worldwide"""
        
        num_ships = params.get("num_ships", 3)
        region = params.get("region", "mediterranean")
        duration_hours = params.get("duration_hours", 2.0)
        report_interval_minutes = params.get("report_interval_minutes", 5)
        scenario_name = params.get("scenario_name", f"{region}_scenario")
        location_hint = params.get("location_hint", "")  # Get location hint for intelligent coordinates
        
        # Generate ships for the specified region with location hint
        ships = self.generator.generate_maritime_scenario(num_ships, region, location_hint)
        
        return await self._process_ship_generation(ships, duration_hours, report_interval_minutes, scenario_name, region)
    
    async def _process_ship_generation(self, ships: List, duration_hours: float, report_interval_minutes: int, scenario_name: str, region: str) -> Dict[str, Any]:
        """Common processing for ship generation"""
        
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
        
        # Create enhanced message based on what was generated
        files_info = []
        if "json" in saved_files:
            files_info.append(f"📁 JSON data: {saved_files['json']}")
        if "map" in saved_files:
            files_info.append(f"🗺️ Interactive map: {saved_files['map']}")
        
        files_text = "\n".join(files_info) if files_info else "Files saved"
        
        return {
            "success": True,
            "scenario_name": scenario_name,
            "region": region,
            "ships_generated": len(ships),
            "duration_hours": duration_hours,
            "report_interval_minutes": report_interval_minutes,
            "ships": ship_summaries,
            "saved_files": saved_files,
            "message": f"✅ Generated {len(ships)} ships in {region} scenario!\n\n{files_text}\n\n🎯 Both JSON data and interactive HTML map have been created automatically."
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
        
        # Create enhanced message based on what was generated
        files_info = []
        if "json" in saved_files:
            files_info.append(f"📁 JSON data: {saved_files['json']}")
        if "map" in saved_files:
            files_info.append(f"🗺️ Interactive map: {saved_files['map']}")
        
        files_text = "\n".join(files_info) if files_info else "Files saved"
        
        return {
            "success": True,
            "scenario_name": scenario_name,
            "ships_generated": len(generated_ships),
            "duration_hours": duration_hours,
            "ships": ship_summaries,
            "saved_files": saved_files,
            "message": f"✅ Generated {len(generated_ships)} custom ships!\n\n{files_text}\n\n🎯 Both JSON data and interactive HTML map have been created automatically."
        }
    
    async def _list_available_ports(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """List available ports worldwide or in a specific region"""
        
        region = params.get("region", "all")
        
        # Get ports from the worldwide routes
        from ..generators.multi_ship_generator import WorldwideRoutes
        
        if region == "all" or region is None:
            # Return all ports
            all_ports = WorldwideRoutes.get_all_ports()
        else:
            # Return ports for specific region
            all_ports = WorldwideRoutes.get_ports_by_region(region)
        
        # Convert to response format with additional metadata
        ports = {}
        for name, position in all_ports.items():
            # Add region/country info based on port location
            country_info = self._get_port_country_info(name)
            ports[name] = {
                "latitude": position.latitude,
                "longitude": position.longitude,
                **country_info
            }
        
        region_text = f"in the {region} region" if region != "all" else "worldwide"
        
        return {
            "success": True,
            "region": region,
            "ports": ports,
            "total_ports": len(ports),
            "message": f"Available ports {region_text}: {', '.join(ports.keys())}"
        }
    
    def _get_port_country_info(self, port_name: str) -> Dict[str, str]:
        """Get country/region info for a port"""
        port_countries = {
            # Irish Sea
            "DUBLIN": {"country": "Ireland", "region": "Irish Sea"},
            "CORK": {"country": "Ireland", "region": "Irish Sea"},
            "LIVERPOOL": {"country": "England", "region": "Irish Sea"},
            "HOLYHEAD": {"country": "Wales", "region": "Irish Sea"},
            "BELFAST": {"country": "Northern Ireland", "region": "Irish Sea"},
            "SWANSEA": {"country": "Wales", "region": "Irish Sea"},
            "CARDIFF": {"country": "Wales", "region": "Irish Sea"},
            "ISLE_OF_MAN": {"country": "Isle of Man", "region": "Irish Sea"},
            
            # European
            "ROTTERDAM": {"country": "Netherlands", "region": "North Sea"},
            "HAMBURG": {"country": "Germany", "region": "North Sea"},
            "ANTWERP": {"country": "Belgium", "region": "North Sea"},
            "LE_HAVRE": {"country": "France", "region": "English Channel"},
            "BARCELONA": {"country": "Spain", "region": "Mediterranean"},
            "MARSEILLE": {"country": "France", "region": "Mediterranean"},
            "NAPLES": {"country": "Italy", "region": "Mediterranean"},
            "VENICE": {"country": "Italy", "region": "Mediterranean"},
            "ATHENS": {"country": "Greece", "region": "Mediterranean"},
            "ISTANBUL": {"country": "Turkey", "region": "Mediterranean"},
            
            # Nordic/Baltic
            "COPENHAGEN": {"country": "Denmark", "region": "Baltic Sea"},
            "STOCKHOLM": {"country": "Sweden", "region": "Baltic Sea"},
            "OSLO": {"country": "Norway", "region": "North Sea"},
            "HELSINKI": {"country": "Finland", "region": "Baltic Sea"},
            "GDANSK": {"country": "Poland", "region": "Baltic Sea"},
            
            # Asian
            "SINGAPORE": {"country": "Singapore", "region": "Southeast Asia"},
            "SHANGHAI": {"country": "China", "region": "East Asia"},
            "HONG_KONG": {"country": "Hong Kong", "region": "East Asia"},
            "TOKYO": {"country": "Japan", "region": "East Asia"},
            "BUSAN": {"country": "South Korea", "region": "East Asia"},
            "MUMBAI": {"country": "India", "region": "Indian Ocean"},
            "DUBAI": {"country": "UAE", "region": "Persian Gulf"},
            
            # North American
            "NEW_YORK": {"country": "USA", "region": "North Atlantic"},
            "LOS_ANGELES": {"country": "USA", "region": "North Pacific"},
            "MIAMI": {"country": "USA", "region": "Caribbean"},
            "VANCOUVER": {"country": "Canada", "region": "North Pacific"},
            "MONTREAL": {"country": "Canada", "region": "St. Lawrence"}
        }
        
        return port_countries.get(port_name, {"country": "Unknown", "region": "Unknown"})
    
    async def _generate_coordinate_scenario(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Generate ships using specific coordinates"""
        
        coordinates = params.get("coordinates", [])
        num_ships = params.get("num_ships", 3)
        duration_hours = params.get("duration_hours", 2.0)
        scenario_name = params.get("scenario_name", "coordinate_scenario")
        
        if not coordinates or len(coordinates) < 2:
            return {
                "success": False,
                "error": "At least 2 coordinate pairs required for coordinate-based generation"
            }
        
        try:
            # Create custom ships using coordinates
            from ..generators.multi_ship_generator import MultiShipGenerator, Route, Position
            from ..core.models import ShipType
            
            ships_data = []
            ship_types = [ShipType.PASSENGER, ShipType.CARGO, ShipType.FISHING, ShipType.PILOT_VESSEL]
            
            for i in range(num_ships):
                # Use coordinate pairs for start/end positions
                coord_idx = i % (len(coordinates) - 1)
                start_coord = coordinates[coord_idx]
                end_coord = coordinates[coord_idx + 1]
                
                start_pos = Position(latitude=start_coord[0], longitude=start_coord[1])
                end_pos = Position(latitude=end_coord[0], longitude=end_coord[1])
                
                # Create route
                route = Route(start_pos, end_pos, 12.0)
                
                # Create ship
                ship_type = ship_types[i % len(ship_types)]
                mmsi = 123456000 + i
                ship_name = f"COORD_SHIP_{i+1}_{random.randint(100, 999)}"
                
                from ..generators.multi_ship_generator import RealisticShipMovement, RouteType
                route_type = RouteType.FERRY if ship_type == ShipType.PASSENGER else RouteType.CARGO
                
                ship = RealisticShipMovement(route, mmsi, ship_name, ship_type, route_type)
                ships_data.append(ship)
            
            # Generate movement data and save
            all_ship_data = {}
            ship_summaries = []
            
            for ship in ships_data:
                report_interval_seconds = 5 * 60  # 5 minutes
                states = list(ship.generate_movement(duration_hours, report_interval_seconds))
                all_ship_data[ship.mmsi] = states
                
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
            
            # Save files
            saved_files = self.file_manager.save_multi_ship_data(
                all_ship_data, f"{scenario_name}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
            )
            
            # Create enhanced message
            files_info = []
            if "json" in saved_files:
                files_info.append(f"📁 JSON data: {saved_files['json']}")
            if "map" in saved_files:
                files_info.append(f"🗺️ Interactive map: {saved_files['map']}")
            
            files_text = "\n".join(files_info) if files_info else "Files saved"
            
            return {
                "success": True,
                "scenario_name": scenario_name,
                "scenario_type": "coordinate_based",
                "ships_generated": len(ships_data),
                "duration_hours": duration_hours,
                "coordinates_used": len(coordinates),
                "ships": ship_summaries,
                "saved_files": saved_files,
                "message": f"✅ Generated {len(ships_data)} ships using {len(coordinates)} coordinates!\n\n{files_text}\n\n🎯 Ships follow routes between specified coordinate points with realistic AIS tracking data."
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Error generating coordinate scenario: {str(e)}"
            }
    
    async def _generate_specialized_scenario(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Generate specialized maritime scenarios"""
        
        scenario_type = params.get("scenario_type", "convoy")
        num_ships = params.get("num_ships", 5)
        region = params.get("region", "mediterranean")
        duration_hours = params.get("duration_hours", 3.0)
        special_params = params.get("special_parameters", {})
        scenario_name = params.get("scenario_name", f"{scenario_type}_scenario")
        
        try:
            # Generate ships based on scenario type
            if scenario_type == "convoy":
                ships = await self._generate_convoy_scenario(num_ships, region, special_params)
            elif scenario_type == "rescue_operation":
                ships = await self._generate_rescue_scenario(num_ships, region, special_params)
            elif scenario_type == "cruise_tourism":
                ships = await self._generate_cruise_scenario(num_ships, region, special_params)
            elif scenario_type == "military_exercise":
                ships = await self._generate_military_scenario(num_ships, region, special_params)
            elif scenario_type == "fishing_fleet":
                ships = await self._generate_fishing_fleet_scenario(num_ships, region, special_params)
            elif scenario_type == "port_operations":
                ships = await self._generate_port_operations_scenario(num_ships, region, special_params)
            else:
                # Fallback to regional generation
                ships = self.generator.generate_maritime_scenario(num_ships, region)
            
            # Process the generated ships
            return await self._process_ship_generation(ships, duration_hours, 5, scenario_name, region)
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Error generating {scenario_type} scenario: {str(e)}"
            }
    
    async def _generate_convoy_scenario(self, num_ships: int, region: str, params: Dict[str, Any]) -> List:
        """Generate convoy formation scenario"""
        from ..core.models import ShipType
        
        # Create mixed convoy: 1 escort + cargo ships
        ships = []
        spacing = params.get("formation_spacing", 0.5)  # nautical miles
        
        # Lead escort vessel
        escort_ships = self.generator.generate_maritime_scenario(1, region)
        if escort_ships:
            # Override ship type to pilot vessel (escort)
            escort_ships[0].ship_type = ShipType.PILOT_VESSEL
            ships.append(escort_ships[0])
        
        # Cargo convoy
        cargo_ships = self.generator.generate_maritime_scenario(num_ships - 1, region)
        for ship in cargo_ships:
            ship.ship_type = ShipType.CARGO
            ships.append(ship)
        
        return ships
    
    async def _generate_rescue_scenario(self, num_ships: int, region: str, params: Dict[str, Any]) -> List:
        """Generate search and rescue scenario"""
        from ..core.models import ShipType
        
        ships = self.generator.generate_maritime_scenario(num_ships, region)
        
        # Convert ships to rescue vessels
        for i, ship in enumerate(ships):
            if i == 0:
                ship.ship_type = ShipType.SEARCH_RESCUE  # Lead rescue vessel
            elif i % 2 == 0:
                ship.ship_type = ShipType.PILOT_VESSEL  # Coast guard patrol
            else:
                ship.ship_type = ShipType.HIGH_SPEED_CRAFT  # Fast response
        
        return ships
    
    async def _generate_cruise_scenario(self, num_ships: int, region: str, params: Dict[str, Any]) -> List:
        """Generate cruise tourism scenario"""
        from ..core.models import ShipType
        
        ships = self.generator.generate_maritime_scenario(num_ships, region)
        
        # Convert to cruise/passenger vessels
        for ship in ships:
            ship.ship_type = ShipType.PASSENGER
        
        return ships
    
    async def _generate_military_scenario(self, num_ships: int, region: str, params: Dict[str, Any]) -> List:
        """Generate military exercise scenario"""
        from ..core.models import ShipType
        
        ships = self.generator.generate_maritime_scenario(num_ships, region)
        
        # Convert to military vessels
        for i, ship in enumerate(ships):
            if i % 3 == 0:
                ship.ship_type = ShipType.LAW_ENFORCEMENT  # Naval vessel
            else:
                ship.ship_type = ShipType.PILOT_VESSEL  # Patrol vessel
        
        return ships
    
    async def _generate_fishing_fleet_scenario(self, num_ships: int, region: str, params: Dict[str, Any]) -> List:
        """Generate fishing fleet scenario"""
        from ..core.models import ShipType
        
        ships = self.generator.generate_maritime_scenario(num_ships, region)
        
        # Convert all to fishing vessels
        for ship in ships:
            ship.ship_type = ShipType.FISHING
        
        return ships
    
    async def _generate_port_operations_scenario(self, num_ships: int, region: str, params: Dict[str, Any]) -> List:
        """Generate port operations scenario"""
        from ..core.models import ShipType
        
        ships = self.generator.generate_maritime_scenario(num_ships, region)
        
        # Mixed port operations fleet
        for i, ship in enumerate(ships):
            if i % 4 == 0:
                ship.ship_type = ShipType.TUG  # Harbor tug
            elif i % 4 == 1:
                ship.ship_type = ShipType.PILOT_VESSEL  # Port pilot
            elif i % 4 == 2:
                ship.ship_type = ShipType.CARGO  # Container ship
            else:
                ship.ship_type = ShipType.PASSENGER  # Ferry
        
        return ships
    
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
