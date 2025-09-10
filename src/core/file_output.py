"""File output utilities for saving AIS data"""

import json
import os
from datetime import datetime
from typing import List, Dict, Any
from pathlib import Path

from .models import ShipState
from ..generators.nmea_formatter import NMEAFormatter


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
        
        return {"json": str(json_path)}
    
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
    
    def get_file_content(self, filename: str) -> str:
        """Get content of a file in the output directory"""
        file_path = self.base_output_dir / filename
        
        if not file_path.exists():
            raise FileNotFoundError(f"File {filename} not found")
        
        with open(file_path, 'r') as f:
            return f.read()
