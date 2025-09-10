#!/usr/bin/env python3
"""
Multi-Ship AIS Data Map Viewer - Walk Version
Visualize multiple ships on an interactive map using Folium
"""

import os
import json
import folium
import webbrowser
from datetime import datetime
from pathlib import Path
import sys
import random


def find_latest_multi_ship_file(output_dir="output"):
    """Find the most recent multi-ship JSON file"""
    output_path = Path(output_dir)
    
    if not output_path.exists():
        print(f"❌ Output directory '{output_dir}' does not exist")
        return None
    
    # Look for multi-ship files first
    multi_files = list(output_path.glob("*multi_ship*.json")) + list(output_path.glob("*ships*.json"))
    
    if multi_files:
        latest_file = max(multi_files, key=lambda f: f.stat().st_mtime)
        return latest_file
    
    # Fallback to any JSON file
    json_files = list(output_path.glob("*.json"))
    if not json_files:
        print(f"❌ No JSON files found in '{output_dir}'")
        return None
    
    latest_file = max(json_files, key=lambda f: f.stat().st_mtime)
    return latest_file


def load_multi_ship_data(json_file):
    """Load multi-ship AIS data from JSON file"""
    try:
        with open(json_file, 'r') as f:
            data = json.load(f)
        return data
    except Exception as e:
        print(f"❌ Error loading JSON file: {e}")
        return None


def get_ship_color(ship_type: str, ship_index: int) -> str:
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


def get_ship_icon(ship_type: str) -> str:
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


def create_multi_ship_map(multi_ship_data, save_path="multi_ship_map.html"):
    """Create interactive map with multiple ships"""
    
    if not multi_ship_data:
        print("❌ Invalid multi-ship data format")
        return None
    
    # Handle different data formats
    if 'ships' in multi_ship_data:
        # Multi-ship format
        ships_data = multi_ship_data['ships']
        metadata = multi_ship_data.get('metadata', {})
    else:
        # Single ship format - convert to multi-ship
        ships_data = {'single_ship': multi_ship_data}
        metadata = multi_ship_data.get('metadata', {})
    
    if not ships_data:
        print("❌ No ship data found")
        return None
    
    # Calculate map center from all ships
    all_lats = []
    all_lons = []
    
    for ship_mmsi, ship_info in ships_data.items():
        if isinstance(ship_info, dict) and 'ais_data' in ship_info:
            ais_data = ship_info['ais_data']
        else:
            # Handle direct list format
            ais_data = ship_info if isinstance(ship_info, list) else []
            
        for pos_data in ais_data:
            if 'position' in pos_data:
                all_lats.append(pos_data['position']['latitude'])
                all_lons.append(pos_data['position']['longitude'])
    
    if not all_lats:
        print("❌ No position data found in any ship")
        return None
    
    center_lat = sum(all_lats) / len(all_lats)
    center_lon = sum(all_lons) / len(all_lons)
    
    # Create map
    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=8,
        tiles='OpenStreetMap'
    )
    
    # Add title
    total_ships = len(ships_data)
    scenario_name = metadata.get('scenario_name', 'Multi-Ship Scenario')
    generated_at = metadata.get('generated_at', 'Unknown time')
    
    title_html = f'''
    <h3 align="center" style="font-size:20px"><b>🚢 Multi-Ship AIS Visualization</b></h3>
    <p align="center">
        <b>Scenario:</b> {scenario_name}<br>
        <b>Ships:</b> {total_ships}<br>
        <b>Generated:</b> {generated_at[:19] if generated_at != 'Unknown time' else generated_at}<br>
        <b>Walk Version - Hackathon 2025</b>
    </p>
    '''
    m.get_root().html.add_child(folium.Element(title_html))
    
    # Add each ship to the map
    ship_index = 0
    for ship_mmsi, ship_info in ships_data.items():
        
        # Extract ship info
        if isinstance(ship_info, dict) and 'ship_info' in ship_info:
            ship_name = ship_info['ship_info'].get('ship_name', f'Ship {ship_mmsi}')
            ship_type = ship_info['ship_info'].get('ship_type', 'UNKNOWN')
            ais_data = ship_info.get('ais_data', [])
            route_summary = ship_info.get('route_summary', {})
        else:
            # Handle direct list or different format
            if isinstance(ship_info, list) and ship_info:
                ais_data = ship_info
                ship_name = ais_data[0].get('ship_name', f'Ship {ship_mmsi}')
                ship_type = ais_data[0].get('ship_type', 'UNKNOWN')
                route_summary = {}
            else:
                continue
        
        if not ais_data:
            continue
        
        # Get ship color and icon
        ship_color = get_ship_color(ship_type, ship_index)
        ship_icon = get_ship_icon(ship_type)
        
        # Extract path coordinates
        path_coords = []
        for pos in ais_data:
            if 'position' in pos:
                lat = pos['position']['latitude']
                lon = pos['position']['longitude']
                path_coords.append([lat, lon])
        
        if not path_coords:
            continue
        
        # Draw ship's path
        folium.PolyLine(
            path_coords,
            color=ship_color,
            weight=3,
            opacity=0.8,
            popup=f"{ship_name} ({ship_type})"
        ).add_to(m)
        
        # Add start marker
        start_pos = ais_data[0]
        start_popup = f"""
        <b>🟢 START: {ship_name}</b><br>
        <b>MMSI:</b> {ship_mmsi}<br>
        <b>Type:</b> {ship_type}<br>
        <b>Time:</b> {start_pos.get('timestamp', 'Unknown')[:19]}<br>
        <b>Position:</b> {start_pos['position']['latitude']:.6f}, {start_pos['position']['longitude']:.6f}<br>
        <b>Speed:</b> {start_pos.get('speed_knots', 'N/A')} knots
        """
        
        folium.Marker(
            location=[start_pos['position']['latitude'], start_pos['position']['longitude']],
            popup=folium.Popup(start_popup, max_width=300),
            tooltip=f"START: {ship_name}",
            icon=folium.Icon(color='green', icon='play', prefix='fa')
        ).add_to(m)
        
        # Add end marker  
        end_pos = ais_data[-1]
        end_popup = f"""
        <b>🔴 CURRENT: {ship_name}</b><br>
        <b>MMSI:</b> {ship_mmsi}<br>
        <b>Type:</b> {ship_type}<br>
        <b>Time:</b> {end_pos.get('timestamp', 'Unknown')[:19]}<br>
        <b>Position:</b> {end_pos['position']['latitude']:.6f}, {end_pos['position']['longitude']:.6f}<br>
        <b>Speed:</b> {end_pos.get('speed_knots', 'N/A')} knots<br>
        <b>Status:</b> {end_pos.get('navigation_status', 'N/A')}
        """
        
        folium.Marker(
            location=[end_pos['position']['latitude'], end_pos['position']['longitude']],
            popup=folium.Popup(end_popup, max_width=300),
            tooltip=f"CURRENT: {ship_name}",
            icon=folium.Icon(color=ship_color, icon=ship_icon, prefix='fa')
        ).add_to(m)
        
        # Add a few intermediate points for longer routes
        if len(ais_data) > 4:
            mid_points = [len(ais_data)//4, len(ais_data)//2, 3*len(ais_data)//4]
            for i, mid_idx in enumerate(mid_points):
                if mid_idx < len(ais_data):
                    mid_pos = ais_data[mid_idx]
                    folium.CircleMarker(
                        location=[mid_pos['position']['latitude'], mid_pos['position']['longitude']],
                        radius=5,
                        popup=f"{ship_name} - Point {mid_idx+1}",
                        color=ship_color,
                        fillColor=ship_color,
                        fillOpacity=0.7
                    ).add_to(m)
        
        ship_index += 1
    
    # Add legend
    legend_html = '''
    <div style="position: fixed; 
                bottom: 50px; right: 50px; width: 200px; height: 120px; 
                background-color: white; border:2px solid grey; z-index:9999; 
                font-size:14px; padding: 10px">
    <h4>Ship Types</h4>
    <p><i style="color:blue">●</i> Passenger<br>
       <i style="color:green">●</i> Cargo<br>
       <i style="color:orange">●</i> Fishing<br>
       <i style="color:red">●</i> Pilot<br>
       <i style="color:purple">●</i> High Speed</p>
    </div>
    '''
    m.get_root().html.add_child(folium.Element(legend_html))
    
    # Fit bounds to show all ships
    if len(all_lats) > 1:
        bounds = [[min(all_lats), min(all_lons)], [max(all_lats), max(all_lons)]]
        m.fit_bounds(bounds, padding=(20, 20))
    
    # Save map
    try:
        m.save(save_path)
        print(f"✅ Multi-ship map saved to: {save_path}")
        return save_path
    except Exception as e:
        print(f"❌ Error saving map: {e}")
        return None


def open_map(map_path):
    """Open the map in the default web browser"""
    try:
        abs_path = os.path.abspath(map_path)
        file_url = f"file://{abs_path}"
        
        print(f"🌐 Opening multi-ship map in browser: {file_url}")
        webbrowser.open(file_url)
        
    except Exception as e:
        print(f"❌ Error opening browser: {e}")
        print(f"📂 You can manually open: {map_path}")


def main():
    """Main function"""
    print("🗺️  Multi-Ship AIS Map Viewer - Walk Version")
    print("=" * 60)
    
    # Check if a specific file was provided
    if len(sys.argv) > 1:
        json_file = Path(sys.argv[1])
        if not json_file.exists():
            print(f"❌ File not found: {json_file}")
            return
    else:
        # Find the latest multi-ship file
        json_file = find_latest_multi_ship_file()
        if not json_file:
            print("💡 Tip: Generate multi-ship data first with 'python test_walk.py'")
            return
    
    print(f"📁 Loading: {json_file}")
    
    # Load multi-ship data
    multi_ship_data = load_multi_ship_data(json_file)
    if not multi_ship_data:
        return
    
    # Display data summary
    if 'metadata' in multi_ship_data:
        metadata = multi_ship_data['metadata']
        print(f"🚢 Scenario: {metadata.get('scenario_name', 'Unknown')}")
        print(f"📊 Ships: {metadata.get('total_ships', 'Unknown')}")
    
    if 'ships' in multi_ship_data:
        print(f"🗂️  Ship details:")
        for mmsi, ship_info in multi_ship_data['ships'].items():
            if 'ship_info' in ship_info:
                info = ship_info['ship_info']
                print(f"  • {info.get('ship_name', mmsi)} ({info.get('ship_type', 'Unknown')})")
    
    # Create map
    map_filename = "multi_ship_map_walk.html"
    map_path = create_multi_ship_map(multi_ship_data, map_filename)
    
    if map_path:
        print()
        print("🎯 Multi-Ship Map Features:")
        print("  🟢 Green markers = Start positions")
        print("  🔴 Colored markers = Current positions") 
        print("  ● Small circles = Intermediate waypoints")
        print("  📍 Click markers for detailed ship info")
        print("  📏 Colored lines show each ship's track")
        print("  🗂️  Legend shows ship type colors")
        print()
        
        # Ask user if they want to open the map
        try:
            response = input("🌐 Open multi-ship map in browser? (y/n): ").lower().strip()
            if response in ['y', 'yes', '']:
                open_map(map_path)
            else:
                print(f"📂 Multi-ship map saved as: {map_path}")
                print("💡 You can open it manually in any web browser")
        except KeyboardInterrupt:
            print(f"\n📂 Multi-ship map saved as: {map_path}")
    
    print("\n✅ Multi-ship map viewer completed!")


if __name__ == "__main__":
    main()
