#!/usr/bin/env python3
"""
Vessel Track Generator MCP Server

Install dependencies:
pip install mcp geopy numpy

Usage:
python vessel_track_server.py
"""

from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import Resource, Tool, TextContent, ImageContent, EmbeddedResource
import json
import asyncio
from typing import Any, Sequence
import logging

# Import your track generator classes
from vessel_track_generator import VesselTrackMCPServer, VesselPromptParser, VesselTrackGenerator

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("vessel-track-server")

class MCPVesselTrackServer:
    def __init__(self):
        self.track_service = VesselTrackMCPServer()
        self.server = Server("vessel-track-generator")
        
        # Store generated tracks for later access
        self.generated_tracks = {}
        
        # Register handlers using decorators
        @self.server.list_tools()
        async def handle_list_tools() -> list[Tool]:
            return await self.list_tools()
        
        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: dict) -> list[TextContent]:
            return await self.call_tool(name, arguments)
        
        @self.server.list_resources()
        async def handle_list_resources() -> list[Resource]:
            return await self.list_resources()
        
        @self.server.read_resource()
        async def handle_read_resource(uri: str) -> str:
            return await self.read_resource(uri)

    async def list_tools(self) -> list[Tool]:
        """List available tools for the MCP client"""
        return [
            Tool(
                name="generate_vessel_tracks",
                description="Generate realistic vessel tracks based on natural language prompts",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "prompt": {
                            "type": "string",
                            "description": "Natural language description of vessel tracks to generate. "
                                         "Examples: '20 vessels class A and B point to point voyages', "
                                         "'5 cargo ships from Rotterdam to Singapore', "
                                         "'fishing vessels with random patterns for 12 hours'"
                        }
                    },
                    "required": ["prompt"]
                }
            ),
            Tool(
                name="export_tracks_geojson",
                description="Export generated vessel tracks as GeoJSON format",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "track_id": {
                            "type": "string",
                            "description": "ID of the track set to export (from previous generation)"
                        }
                    },
                    "required": ["track_id"]
                }
            ),
            Tool(
                name="get_track_statistics",
                description="Get statistics about generated vessel tracks",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "track_id": {
                            "type": "string",
                            "description": "ID of the track set to analyze"
                        }
                    },
                    "required": ["track_id"]
                }
            )
        ]

    async def call_tool(self, name: str, arguments: dict) -> list[TextContent]:
        """Handle tool calls from the MCP client"""
        try:
            if name == "generate_vessel_tracks":
                return await self._handle_generate_tracks(arguments)
            elif name == "export_tracks_geojson":
                return await self._handle_export_geojson(arguments)
            elif name == "get_track_statistics":
                return await self._handle_track_statistics(arguments)
            else:
                raise ValueError(f"Unknown tool: {name}")
        
        except Exception as e:
            logger.error(f"Error in tool {name}: {e}")
            return [TextContent(
                type="text",
                text=f"Error: {str(e)}"
            )]

    async def _handle_generate_tracks(self, arguments: dict) -> list[TextContent]:
        """Generate vessel tracks from prompt"""
        prompt = arguments.get("prompt", "")
        
        if not prompt:
            return [TextContent(
                type="text",
                text="Error: No prompt provided"
            )]
        
        logger.info(f"Generating tracks for prompt: {prompt}")
        
        # Generate tracks
        result = self.track_service.generate_tracks_from_prompt(prompt)
        
        if not result['success']:
            return [TextContent(
                type="text",
                text=f"Failed to generate tracks: {result.get('error', 'Unknown error')}"
            )]
        
        # Store tracks for later access
        track_id = f"tracks_{len(self.generated_tracks) + 1}"
        self.generated_tracks[track_id] = result
        
        # Format response
        summary = self._format_track_summary(result, track_id)
        
        return [TextContent(
            type="text",
            text=summary
        )]

    async def _handle_export_geojson(self, arguments: dict) -> list[TextContent]:
        """Export tracks as GeoJSON"""
        track_id = arguments.get("track_id", "")
        
        if track_id not in self.generated_tracks:
            return [TextContent(
                type="text",
                text=f"Track ID '{track_id}' not found. Available IDs: {list(self.generated_tracks.keys())}"
            )]
        
        tracks_data = self.generated_tracks[track_id]
        geojson = self._convert_to_geojson(tracks_data['tracks'])
        
        return [TextContent(
            type="text",
            text=f"GeoJSON export for {track_id}:\n\n```json\n{json.dumps(geojson, indent=2)}\n```"
        )]

    async def _handle_track_statistics(self, arguments: dict) -> list[TextContent]:
        """Generate track statistics"""
        track_id = arguments.get("track_id", "")
        
        if track_id not in self.generated_tracks:
            return [TextContent(
                type="text",
                text=f"Track ID '{track_id}' not found. Available IDs: {list(self.generated_tracks.keys())}"
            )]
        
        tracks_data = self.generated_tracks[track_id]
        stats = self._calculate_statistics(tracks_data['tracks'])
        
        return [TextContent(
            type="text",
            text=stats
        )]

    def _format_track_summary(self, result: dict, track_id: str) -> str:
        """Format a summary of generated tracks"""
        params = result['parameters_used']
        tracks = result['tracks']
        
        summary = f"✅ Successfully generated {len(tracks)} vessel tracks (ID: {track_id})\n\n"
        summary += "**Parameters Used:**\n"
        summary += f"• Vessel count: {params['vessel_count']}\n"
        summary += f"• Vessel classes: {params.get('vessel_classes', 'Mixed')}\n"
        summary += f"• Voyage type: {params['voyage_type']}\n"
        summary += f"• Duration: {params['duration_hours']} hours\n"
        
        if params.get('start_region') or params.get('end_region'):
            summary += f"• Route: {params.get('start_region', 'Random')} → {params.get('end_region', 'Random')}\n"
        
        summary += f"\n**Sample Tracks:**\n"
        for i, track in enumerate(tracks[:3]):  # Show first 3 tracks
            points_count = len(track['points'])
            first_point = track['points'][0] if track['points'] else {}
            last_point = track['points'][-1] if track['points'] else {}
            
            summary += f"• MMSI {track['mmsi']} ({track['vessel_class']}): "
            summary += f"{points_count} points"
            if first_point and last_point:
                summary += f" from ({first_point.get('latitude', 0):.2f}, {first_point.get('longitude', 0):.2f}) "
                summary += f"to ({last_point.get('latitude', 0):.2f}, {last_point.get('longitude', 0):.2f})"
            summary += "\n"
        
        if len(tracks) > 3:
            summary += f"... and {len(tracks) - 3} more tracks\n"
        
        summary += f"\nUse track ID '{track_id}' to export or analyze these tracks."
        
        return summary

    async def list_resources(self) -> list[Resource]:
        """List available resources"""
        resources = []
        for track_id in self.generated_tracks.keys():
            resources.append(Resource(
                uri=f"track://{track_id}",
                name=f"Vessel Tracks {track_id}",
                description=f"Generated vessel tracks with ID {track_id}",
                mimeType="application/json"
            ))
        return resources

    async def read_resource(self, uri: str) -> str:
        """Read a resource by URI"""
        if uri.startswith("track://"):
            track_id = uri.replace("track://", "")
            if track_id in self.generated_tracks:
                return json.dumps(self.generated_tracks[track_id], indent=2)
        return "Resource not found"

    def _convert_to_geojson(self, tracks: list) -> dict:
        """Convert tracks to GeoJSON format"""
        features = []
        
        for track in tracks:
            if not track['points']:
                continue
            
            # Create linestring from track points
            coordinates = [
                [point['longitude'], point['latitude']] 
                for point in track['points']
            ]
            
            feature = {
                "type": "Feature",
                "properties": {
                    "mmsi": track['mmsi'],
                    "vessel_class": track['vessel_class'],
                    "point_count": len(track['points']),
                    "start_time": track['points'][0]['timestamp'],
                    "end_time": track['points'][-1]['timestamp']
                },
                "geometry": {
                    "type": "LineString",
                    "coordinates": coordinates
                }
            }
            features.append(feature)
        
        return {
            "type": "FeatureCollection",
            "features": features
        }

    def _calculate_statistics(self, tracks: list) -> str:
        """Calculate and format track statistics"""
        if not tracks:
            return "No tracks to analyze."
        
        total_vessels = len(tracks)
        total_points = sum(len(track['points']) for track in tracks)
        
        # Vessel class distribution
        class_counts = {}
        for track in tracks:
            vessel_class = track['vessel_class']
            class_counts[vessel_class] = class_counts.get(vessel_class, 0) + 1
        
        # Speed statistics
        all_speeds = []
        for track in tracks:
            for point in track['points']:
                all_speeds.append(point['speed_over_ground'])
        
        avg_speed = sum(all_speeds) / len(all_speeds) if all_speeds else 0
        max_speed = max(all_speeds) if all_speeds else 0
        min_speed = min(all_speeds) if all_speeds else 0
        
        # Format statistics
        stats = f"**Track Set Statistics**\n\n"
        stats += f"• Total vessels: {total_vessels}\n"
        stats += f"• Total track points: {total_points:,}\n"
        stats += f"• Average points per vessel: {total_points // total_vessels if total_vessels else 0}\n\n"
        
        stats += "**Vessel Class Distribution:**\n"
        for vessel_class, count in sorted(class_counts.items()):
            stats += f"• {vessel_class}: {count} ({count*100/total_vessels:.1f}%)\n"
        
        stats += f"\n**Speed Statistics:**\n"
        stats += f"• Average speed: {avg_speed:.1f} knots\n"
        stats += f"• Max speed: {max_speed:.1f} knots\n"
        stats += f"• Min speed: {min_speed:.1f} knots\n"
        
        return stats