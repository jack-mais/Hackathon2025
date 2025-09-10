#!/usr/bin/env python3
"""
Test Data Visualization Script
Creates visualizations from generated test data
"""

import os
import json
import folium
import webbrowser
from datetime import datetime
from pathlib import Path
import sys
from rich.console import Console
from rich.panel import Panel
from rich.table import Table


class TestDataVisualizer:
    """Visualize all generated test data"""
    
    def __init__(self, output_dir="output"):
        self.console = Console()
        self.output_dir = Path(output_dir)
        self.visualizations_created = []
        
    def find_data_files(self):
        """Find all JSON data files to visualize"""
        if not self.output_dir.exists():
            self.console.print(f"❌ Output directory '{self.output_dir}' does not exist")
            return []
        
        json_files = list(self.output_dir.glob("*.json"))
        if not json_files:
            self.console.print(f"❌ No JSON files found in '{self.output_dir}'")
            return []
        
        # Sort by modification time (newest first)
        json_files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
        return json_files
    
    def load_json_data(self, file_path):
        """Load JSON data from file"""
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            return data
        except Exception as e:
            self.console.print(f"❌ Error loading {file_path}: {e}")
            return None
    
    def detect_data_type(self, data):
        """Detect if data is single ship or multi-ship"""
        if isinstance(data, list):
            return "multi_ship" if len(data) > 1 else "single_ship"
        elif isinstance(data, dict):
            if "ships" in data:
                return "multi_ship"
            elif "ais_data" in data or "positions" in data:
                return "single_ship"
            elif "ship_name" in data or "mmsi" in data:
                return "single_ship"
        return "unknown"
    
    def create_single_ship_map(self, data, filename):
        """Create map for single ship data"""
        try:
            # Extract positions
            positions = []
            ship_name = "Unknown Ship"
            mmsi = "Unknown"
            
            if "ais_data" in data:
                positions = data["ais_data"]
                ship_name = data.get("metadata", {}).get("ship_name", "Unknown Ship")
                mmsi = data.get("metadata", {}).get("mmsi", "Unknown")
            elif "positions" in data:
                positions = data["positions"]
                ship_name = data.get("ship_name", "Unknown Ship")
                mmsi = data.get("mmsi", "Unknown")
            elif isinstance(data, list):
                positions = data
                
            if not positions:
                self.console.print(f"⚠️  No positions found in {filename}")
                return None
            
            # Create map centered on first position
            first_pos = positions[0]
            if "position" in first_pos:
                lat, lon = first_pos["position"]["latitude"], first_pos["position"]["longitude"]
            else:
                lat, lon = first_pos.get("latitude", 53.0), first_pos.get("longitude", -6.0)
            
            map_obj = folium.Map(location=[lat, lon], zoom_start=9, tiles='OpenStreetMap')
            
            # Add ship track
            track_coords = []
            for pos in positions:
                if "position" in pos:
                    pos_data = pos["position"]
                else:
                    pos_data = pos
                    
                track_coords.append([pos_data.get("latitude"), pos_data.get("longitude")])
            
            # Add track line
            folium.PolyLine(
                track_coords,
                color='blue',
                weight=3,
                opacity=0.7,
                popup=f'{ship_name} Track'
            ).add_to(map_obj)
            
            # Add start marker
            folium.Marker(
                track_coords[0],
                popup=f'🚢 Start: {ship_name}',
                icon=folium.Icon(color='green', icon='play')
            ).add_to(map_obj)
            
            # Add end marker  
            folium.Marker(
                track_coords[-1],
                popup=f'🏁 End: {ship_name}',
                icon=folium.Icon(color='red', icon='stop')
            ).add_to(map_obj)
            
            # Save map
            map_filename = f"visualization_single_{filename.stem}.html"
            map_path = self.output_dir / map_filename
            map_obj.save(str(map_path))
            
            return {
                "type": "single_ship",
                "ship_name": ship_name,
                "mmsi": mmsi,
                "positions": len(positions),
                "map_file": map_filename,
                "map_path": str(map_path)
            }
            
        except Exception as e:
            self.console.print(f"❌ Error creating single ship map: {e}")
            return None
    
    def create_multi_ship_map(self, data, filename):
        """Create map for multi-ship data"""
        try:
            ships_data = []
            
            # Extract ships data
            if "ships" in data:
                ships_data = data["ships"]
            elif isinstance(data, list):
                ships_data = data
            
            if not ships_data:
                self.console.print(f"⚠️  No ships found in {filename}")
                return None
            
            # Find map center (average of all first positions)
            center_lat, center_lon = 53.0, -6.0
            valid_positions = []
            
            for ship in ships_data:
                positions = ship.get("positions", [])
                if positions:
                    first_pos = positions[0]
                    if "position" in first_pos:
                        pos_data = first_pos["position"]
                    else:
                        pos_data = first_pos
                    
                    lat = pos_data.get("latitude")
                    lon = pos_data.get("longitude")
                    if lat is not None and lon is not None:
                        valid_positions.append([lat, lon])
            
            if valid_positions:
                center_lat = sum(pos[0] for pos in valid_positions) / len(valid_positions)
                center_lon = sum(pos[1] for pos in valid_positions) / len(valid_positions)
            
            # Create map
            map_obj = folium.Map(location=[center_lat, center_lon], zoom_start=8, tiles='OpenStreetMap')
            
            # Colors for different ships
            colors = ['blue', 'red', 'green', 'purple', 'orange', 'darkred', 'darkblue', 'darkgreen', 'cadetblue', 'gray']
            
            ship_summary = []
            
            for i, ship in enumerate(ships_data):
                color = colors[i % len(colors)]
                ship_name = ship.get("ship_name", f"Ship_{i+1}")
                ship_type = ship.get("ship_type", "Unknown")
                positions = ship.get("positions", [])
                
                if not positions:
                    continue
                
                # Create track
                track_coords = []
                for pos in positions:
                    if "position" in pos:
                        pos_data = pos["position"]
                    else:
                        pos_data = pos
                    
                    lat = pos_data.get("latitude")
                    lon = pos_data.get("longitude")
                    if lat is not None and lon is not None:
                        track_coords.append([lat, lon])
                
                if not track_coords:
                    continue
                
                # Add track line
                folium.PolyLine(
                    track_coords,
                    color=color,
                    weight=3,
                    opacity=0.7,
                    popup=f'{ship_name} ({ship_type}) - {len(track_coords)} positions'
                ).add_to(map_obj)
                
                # Add ship marker
                ship_icon = '🚢' if ship_type == 'PASSENGER' else '📦' if ship_type == 'CARGO' else '🎣' if ship_type == 'FISHING' else '⚓'
                
                folium.Marker(
                    track_coords[0],
                    popup=f'{ship_icon} {ship_name}<br>Type: {ship_type}<br>Positions: {len(track_coords)}',
                    icon=folium.Icon(color=color.replace('dark', ''), icon='ship', prefix='fa')
                ).add_to(map_obj)
                
                ship_summary.append({
                    "name": ship_name,
                    "type": ship_type,
                    "positions": len(track_coords),
                    "color": color
                })
            
            # Save map
            map_filename = f"visualization_multi_{filename.stem}.html"
            map_path = self.output_dir / map_filename
            map_obj.save(str(map_path))
            
            return {
                "type": "multi_ship",
                "ships": ship_summary,
                "total_ships": len(ship_summary),
                "map_file": map_filename,
                "map_path": str(map_path)
            }
            
        except Exception as e:
            self.console.print(f"❌ Error creating multi-ship map: {e}")
            return None
    
    def visualize_all_data(self):
        """Create visualizations for all data files"""
        self.console.print(Panel(
            "🗺️  **Test Data Visualization**\n"
            "Creating interactive maps for all generated data",
            title="📊 Data Visualizer",
            style="bold green"
        ))
        
        # Find data files
        data_files = self.find_data_files()
        if not data_files:
            return
        
        self.console.print(f"\n📁 Found {len(data_files)} data files to visualize:")
        
        # Create table of files
        table = Table(title="Data Files")
        table.add_column("File", style="cyan")
        table.add_column("Size", style="green")
        table.add_column("Modified", style="yellow")
        table.add_column("Type", style="magenta")
        
        results = []
        
        for file_path in data_files:
            # Show file info
            size = file_path.stat().st_size
            modified = datetime.fromtimestamp(file_path.stat().st_mtime).strftime('%H:%M:%S')
            
            # Load and analyze data
            data = self.load_json_data(file_path)
            if not data:
                continue
                
            data_type = self.detect_data_type(data)
            table.add_row(file_path.name, f"{size} bytes", modified, data_type)
            
            # Create visualization
            self.console.print(f"\n🎨 Creating visualization for {file_path.name}...")
            
            if data_type == "single_ship":
                result = self.create_single_ship_map(data, file_path)
            elif data_type == "multi_ship":
                result = self.create_multi_ship_map(data, file_path)
            else:
                self.console.print(f"⚠️  Unknown data type for {file_path.name}")
                continue
            
            if result:
                results.append(result)
                self.visualizations_created.append(result["map_path"])
                self.console.print(f"✅ Created: {result['map_file']}")
        
        self.console.print(table)
        
        # Show results summary
        if results:
            self.console.print(f"\n🎉 Created {len(results)} visualizations!")
            
            # Summary table
            viz_table = Table(title="Generated Visualizations")
            viz_table.add_column("Map File", style="cyan")
            viz_table.add_column("Type", style="green")
            viz_table.add_column("Details", style="yellow")
            
            for result in results:
                if result["type"] == "single_ship":
                    details = f"{result['positions']} positions"
                else:
                    details = f"{result['total_ships']} ships"
                
                viz_table.add_row(result["map_file"], result["type"], details)
            
            self.console.print(viz_table)
            
            # Offer to open maps
            self.console.print(Panel(
                "🌐 **View Your Maps:**\n"
                f"• Open files in browser from: {self.output_dir}/\n"
                "• Or run this script with --open to open automatically\n\n"
                "🎯 **Files created:**\n" + 
                "\n".join(f"• {Path(path).name}" for path in self.visualizations_created),
                title="✅ Visualizations Ready",
                style="green"
            ))
        else:
            self.console.print("❌ No visualizations were created")
    
    def open_visualizations(self):
        """Open all created visualizations in browser"""
        if not self.visualizations_created:
            self.console.print("❌ No visualizations to open")
            return
        
        self.console.print(f"🌐 Opening {len(self.visualizations_created)} visualizations...")
        
        for viz_path in self.visualizations_created:
            try:
                webbrowser.open(f"file://{Path(viz_path).absolute()}")
                self.console.print(f"✅ Opened: {Path(viz_path).name}")
            except Exception as e:
                self.console.print(f"❌ Failed to open {viz_path}: {e}")


def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Visualize generated AIS test data")
    parser.add_argument("--open", action="store_true", help="Open visualizations in browser")
    parser.add_argument("--output-dir", default="output", help="Output directory (default: output)")
    
    args = parser.parse_args()
    
    visualizer = TestDataVisualizer(args.output_dir)
    visualizer.visualize_all_data()
    
    if args.open:
        visualizer.open_visualizations()


if __name__ == "__main__":
    main()
