"""File output utilities for saving AIS data and generating maps"""

import json
import os
import random
from datetime import datetime
from typing import List, Dict, Any
from pathlib import Path

from .models import ShipState
from ..generators.nmea_formatter import NMEAFormatter

# Import map generation dependencies
try:
    import folium
    FOLIUM_AVAILABLE = True
except ImportError:
    FOLIUM_AVAILABLE = False


class FileOutputManager:
    """Manages file output for AIS data"""
    
    def __init__(self, base_output_dir: str = "output"):
        self.base_output_dir = Path(base_output_dir)
        self.formatter = NMEAFormatter()
        
        # Create output directory if it doesn't exist
        self.base_output_dir.mkdir(exist_ok=True)
    
    def save_route_data(self, 
                       ship_states: List[ShipState], 
                       filename_prefix: str = "ais_route",
                       format_type: str = "json") -> Dict[str, str]:
        """
        Save route data to files
        
        Args:
            ship_states: List of ship states to save
            filename_prefix: Prefix for output filename
            format_type: 'json', 'nmea', or 'both'
            
        Returns:
            Dictionary with saved file paths
        """
        if not ship_states:
            raise ValueError("No ship states to save")
        
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        mmsi = ship_states[0].mmsi
        
        saved_files = {}
        
        if format_type in ["json", "both"]:
            json_filename = f"{filename_prefix}_mmsi_{mmsi}_{timestamp}.json"
            json_path = self.base_output_dir / json_filename
            
            # Convert ship states to JSON
            json_data = {
                "metadata": {
                    "mmsi": mmsi,
                    "ship_name": ship_states[0].ship_name,
                    "generated_at": datetime.utcnow().isoformat(),
                    "total_reports": len(ship_states),
                    "duration_hours": self._calculate_duration(ship_states),
                    "format": "AIS/NMEA JSON format"
                },
                "route_summary": {
                    "start_position": {
                        "latitude": ship_states[0].position.latitude,
                        "longitude": ship_states[0].position.longitude,
                        "timestamp": ship_states[0].timestamp.isoformat()
                    },
                    "end_position": {
                        "latitude": ship_states[-1].position.latitude,
                        "longitude": ship_states[-1].position.longitude,
                        "timestamp": ship_states[-1].timestamp.isoformat()
                    }
                },
                "ais_data": [self.formatter.create_ais_summary(state) for state in ship_states]
            }
            
        with open(json_path, 'w') as f:
            json.dump(json_data, f, indent=2)
        
        saved_files['json'] = str(json_path)
        
        # Generate interactive map if Folium is available
        if FOLIUM_AVAILABLE:
            try:
                map_filename = f"{filename_prefix}_map_mmsi_{mmsi}_{timestamp}.html"
                map_path = self.base_output_dir / map_filename
                
                # Generate the interactive map
                map_created = self._generate_interactive_map(json_data, str(map_path))
                if map_created:
                    saved_files["map"] = str(map_path)
            except Exception as e:
                print(f"⚠️  Warning: Could not generate map - {e}")
        
        if format_type in ["nmea", "both"]:
            nmea_filename = f"{filename_prefix}_mmsi_{mmsi}_{timestamp}.nmea"
            nmea_path = self.base_output_dir / nmea_filename
            
            # Convert ship states to NMEA sentences
            nmea_lines = []
            nmea_lines.append(f"# AIS/NMEA Data for {ship_states[0].ship_name} (MMSI: {mmsi})")
            nmea_lines.append(f"# Generated: {datetime.utcnow().isoformat()}")
            nmea_lines.append(f"# Total reports: {len(ship_states)}")
            nmea_lines.append("")
            
            for i, state in enumerate(ship_states):
                nmea_lines.append(f"# Report {i+1} - {state.timestamp.isoformat()}")
                nmea_sentence = self.formatter.format_realistic_position_report(state)
                nmea_lines.append(nmea_sentence)
                nmea_lines.append("")
            
            with open(nmea_path, 'w') as f:
                f.write("\\n".join(nmea_lines))
            
            saved_files['nmea'] = str(nmea_path)
        
        return saved_files
    
    def save_multi_ship_data(self, 
                           ships_data: Dict[int, List[ShipState]], 
                           scenario_name: str = "multi_ship_scenario") -> Dict[str, str]:
        """
        Save data for multiple ships to a single JSON file
        
        Args:
            ships_data: Dictionary mapping MMSI to list of ship states
            scenario_name: Name for the scenario
            
        Returns:
            Dictionary with saved file paths
        """
        if not ships_data:
            raise ValueError("No ship data to save")
        
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        json_filename = f"{scenario_name}_{timestamp}.json"
        json_path = self.base_output_dir / json_filename
        
        # Build multi-ship JSON structure
        json_data = {
            "metadata": {
                "scenario_name": scenario_name,
                "generated_at": datetime.utcnow().isoformat(),
                "total_ships": len(ships_data),
                "format": "Multi-ship AIS/NMEA JSON format"
            },
            "ships": {}
        }
        
        for mmsi, ship_states in ships_data.items():
            if ship_states:
                json_data["ships"][str(mmsi)] = {
                    "ship_info": {
                        "mmsi": mmsi,
                        "ship_name": ship_states[0].ship_name,
                        "ship_type": ship_states[0].ship_type.name,
                        "total_reports": len(ship_states)
                    },
                    "route_summary": {
                        "start_position": {
                            "latitude": ship_states[0].position.latitude,
                            "longitude": ship_states[0].position.longitude,
                            "timestamp": ship_states[0].timestamp.isoformat()
                        },
                        "end_position": {
                            "latitude": ship_states[-1].position.latitude,
                            "longitude": ship_states[-1].position.longitude,
                            "timestamp": ship_states[-1].timestamp.isoformat()
                        }
                    },
                    "ais_data": [self.formatter.create_ais_summary(state) for state in ship_states]
                }
        
        with open(json_path, 'w') as f:
            json.dump(json_data, f, indent=2)
        
        saved_files = {"json": str(json_path)}
        
        # Generate interactive map if Folium is available
        if FOLIUM_AVAILABLE:
            try:
                map_filename = f"{scenario_name}_map_{timestamp}.html"
                map_path = self.base_output_dir / map_filename
                
                # Generate the interactive map
                map_created = self._generate_interactive_map(json_data, str(map_path))
                if map_created:
                    saved_files["map"] = str(map_path)
            except Exception as e:
                print(f"⚠️  Warning: Could not generate map - {e}")
        
        return saved_files
    
    def _calculate_duration(self, ship_states: List[ShipState]) -> float:
        """Calculate duration in hours between first and last report"""
        if len(ship_states) < 2:
            return 0.0
        
        start_time = ship_states[0].timestamp
        end_time = ship_states[-1].timestamp
        duration = end_time - start_time
        
        return duration.total_seconds() / 3600
    
    def list_output_files(self) -> List[Dict[str, Any]]:
        """List all files in the output directory"""
        files = []
        
        if not self.base_output_dir.exists():
            return files
        
        for file_path in self.base_output_dir.iterdir():
            if file_path.is_file():
                stat = file_path.stat()
                files.append({
                    "filename": file_path.name,
                    "full_path": str(file_path),
                    "size_bytes": stat.st_size,
                    "modified_at": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    "extension": file_path.suffix
                })
        
        return sorted(files, key=lambda x: x["modified_at"], reverse=True)
    
    def _generate_interactive_map(self, json_data: Dict[str, Any], map_path: str) -> bool:
        """Generate interactive HTML map from ship data"""
        if not FOLIUM_AVAILABLE:
            return False
            
        try:
            # Handle different data formats
            if 'ships' in json_data:
                ships_data = json_data['ships']
                metadata = json_data.get('metadata', {})
            else:
                # Single ship format - convert to multi-ship
                ships_data = {'single_ship': json_data}
                metadata = json_data.get('metadata', {})
            
            if not ships_data:
                return False
            
            # Calculate map center from all ship positions
            all_lats, all_lons = [], []
            for ship_id, ship_info in ships_data.items():
                if 'ais_data' in ship_info:
                    for report in ship_info['ais_data']:
                        if 'position' in report:
                            all_lats.append(report['position']['latitude'])
                            all_lons.append(report['position']['longitude'])
            
            if not all_lats or not all_lons:
                return False
            
            center_lat = sum(all_lats) / len(all_lats)
            center_lon = sum(all_lons) / len(all_lons)
            
            # Create base map
            m = folium.Map(
                location=[center_lat, center_lon],
                zoom_start=8,
                tiles='OpenStreetMap'
            )
            
            # Add ships to map
            ship_index = 0
            for ship_id, ship_info in ships_data.items():
                if 'ais_data' not in ship_info or not ship_info['ais_data']:
                    continue
                
                # Get ship details
                ship_name = ship_info.get('ship_info', {}).get('ship_name', f'Ship_{ship_id}')
                ship_type = ship_info.get('ais_data', [{}])[0].get('ship_type', 'UNKNOWN')
                
                # Get color and icon for ship type
                color = self._get_ship_color(ship_type, ship_index)
                icon = self._get_ship_icon(ship_type)
                
                # Extract positions for route line
                positions = []
                for report in ship_info['ais_data']:
                    if 'position' in report:
                        lat = report['position']['latitude']
                        lon = report['position']['longitude']
                        positions.append([lat, lon])
                
                if len(positions) < 2:
                    continue
                
                # Add route line
                folium.PolyLine(
                    positions,
                    color=color,
                    weight=3,
                    opacity=0.8,
                    popup=f"{ship_name} Route"
                ).add_to(m)
                
                # Add start marker (green)
                start_pos = positions[0]
                start_report = ship_info['ais_data'][0]
                start_popup = f"""
                <b>{ship_name}</b><br>
                Type: {ship_type}<br>
                MMSI: {ship_info.get('ship_info', {}).get('mmsi', 'N/A')}<br>
                <b>START POSITION</b><br>
                Time: {start_report.get('timestamp', 'N/A')}<br>
                Speed: {start_report.get('speed_knots', 0):.1f} knots<br>
                Course: {start_report.get('course_degrees', 0):.1f}°
                """
                
                folium.Marker(
                    start_pos,
                    popup=folium.Popup(start_popup, max_width=300),
                    icon=folium.Icon(color='green', icon='play'),
                    tooltip=f"{ship_name} - START"
                ).add_to(m)
                
                # Add end marker (ship type color)
                end_pos = positions[-1]
                end_report = ship_info['ais_data'][-1]
                end_popup = f"""
                <b>{ship_name}</b><br>
                Type: {ship_type}<br>
                MMSI: {ship_info.get('ship_info', {}).get('mmsi', 'N/A')}<br>
                <b>END POSITION</b><br>
                Time: {end_report.get('timestamp', 'N/A')}<br>
                Speed: {end_report.get('speed_knots', 0):.1f} knots<br>
                Course: {end_report.get('course_degrees', 0):.1f}°<br>
                Total Reports: {ship_info.get('ship_info', {}).get('total_reports', len(ship_info['ais_data']))}
                """
                
                folium.Marker(
                    end_pos,
                    popup=folium.Popup(end_popup, max_width=300),
                    icon=folium.Icon(color=color, icon=icon),
                    tooltip=f"{ship_name} - END"
                ).add_to(m)
                
                # Add intermediate waypoints as small circles
                if len(positions) > 2:
                    for i, pos in enumerate(positions[1:-1], 1):
                        folium.CircleMarker(
                            pos,
                            radius=4,
                            popup=f"{ship_name} - Waypoint {i}",
                            color=color,
                            fill=True,
                            opacity=0.6
                        ).add_to(m)
                
                ship_index += 1
            
            # Add legend
            legend_html = self._generate_map_legend(ships_data)
            m.get_root().html.add_child(folium.Element(legend_html))
            
            # Add title
            title_html = f"""
            <div style='position: fixed; top: 10px; left: 50px; z-index: 1000; 
                        background: white; padding: 10px; border: 2px solid black; border-radius: 5px;'>
                <h3 style='margin: 0;'>🚢 {metadata.get('scenario_name', 'AIS Ship Tracking')}</h3>
                <p style='margin: 5px 0 0 0; font-size: 12px;'>
                    Ships: {metadata.get('total_ships', len(ships_data))} | 
                    Generated: {metadata.get('generated_at', datetime.now().strftime('%Y-%m-%d %H:%M'))}
                </p>
            </div>
            """
            m.get_root().html.add_child(folium.Element(title_html))
            
            # Save map
            m.save(map_path)
            return True
            
        except Exception as e:
            print(f"Error generating map: {e}")
            return False
    
    def _get_ship_color(self, ship_type: str, ship_index: int) -> str:
        """Get color for ship based on type"""
        color_map = {
            'PASSENGER': 'blue',
            'CARGO': 'green',
            'FISHING': 'orange', 
            'PILOT_VESSEL': 'red',
            'HIGH_SPEED_CRAFT': 'purple',
            'LAW_ENFORCEMENT': 'darkred',
            'SEARCH_RESCUE': 'cadetblue',
        }
        
        # Fallback color sequence if type not found
        fallback_colors = ['blue', 'red', 'green', 'purple', 'orange', 'darkred', 'lightred', 'beige', 'darkblue', 'darkgreen']
        
        return color_map.get(ship_type, fallback_colors[ship_index % len(fallback_colors)])

    def _get_ship_icon(self, ship_type: str) -> str:
        """Get icon for ship based on type"""
        icon_map = {
            'PASSENGER': 'ship',
            'CARGO': 'cube', 
            'FISHING': 'anchor',
            'PILOT_VESSEL': 'shield',
            'HIGH_SPEED_CRAFT': 'forward',
            'LAW_ENFORCEMENT': 'star',
            'SEARCH_RESCUE': 'plus',
        }
        
        return icon_map.get(ship_type, 'ship')
    
    def _generate_map_legend(self, ships_data: Dict[str, Any]) -> str:
        """Generate HTML legend for the map"""
        ship_types = set()
        for ship_info in ships_data.values():
            if 'ais_data' in ship_info and ship_info['ais_data']:
                ship_type = ship_info['ais_data'][0].get('ship_type', 'UNKNOWN')
                ship_types.add(ship_type)
        
        legend_items = []
        for i, ship_type in enumerate(sorted(ship_types)):
            color = self._get_ship_color(ship_type, i)
            legend_items.append(f"""
                <div style='margin: 3px 0;'>
                    <span style='display: inline-block; width: 15px; height: 15px; 
                                background-color: {color}; border: 1px solid black; margin-right: 8px;'></span>
                    {ship_type}
                </div>
            """)
        
        legend_html = f"""
        <div style='position: fixed; bottom: 10px; left: 10px; z-index: 1000; 
                    background: white; padding: 10px; border: 2px solid black; border-radius: 5px;
                    font-family: Arial, sans-serif; font-size: 12px;'>
            <h4 style='margin: 0 0 8px 0;'>🏷️ Ship Types</h4>
            {''.join(legend_items)}
            <hr style='margin: 8px 0 5px 0;'>
            <div style='font-size: 10px; color: #666;'>
                🟢 Start | 🔴 End | ⚫ Waypoints
            </div>
        </div>
        """
        
        return legend_html
    
    def get_file_content(self, filename: str) -> str:
        """Get content of a file in the output directory"""
        file_path = self.base_output_dir / filename
        
        if not file_path.exists():
            raise FileNotFoundError(f"File {filename} not found")
        
        with open(file_path, 'r') as f:
            return f.read()
