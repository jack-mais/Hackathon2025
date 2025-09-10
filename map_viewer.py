#!/usr/bin/env python3
"""
AIS Data Map Viewer - Hackathon 2025
Visualize generated AIS/NMEA data on an interactive map using Folium
"""

import os
import json
import folium
import webbrowser
from datetime import datetime
from pathlib import Path
import sys


def find_latest_json_file(output_dir="output"):
    """Find the most recent JSON file in the output directory"""
    output_path = Path(output_dir)
    
    if not output_path.exists():
        print(f"❌ Output directory '{output_dir}' does not exist")
        return None
    
    json_files = list(output_path.glob("*.json"))
    
    if not json_files:
        print(f"❌ No JSON files found in '{output_dir}'")
        return None
    
    # Sort by modification time, newest first
    latest_file = max(json_files, key=lambda f: f.stat().st_mtime)
    return latest_file


def load_ais_data(json_file):
    """Load AIS data from JSON file"""
    try:
        with open(json_file, 'r') as f:
            data = json.load(f)
        return data
    except Exception as e:
        print(f"❌ Error loading JSON file: {e}")
        return None


def create_map(ais_data, save_path="ais_map.html"):
    """Create interactive map from AIS data"""
    
    if not ais_data or 'ais_data' not in ais_data:
        print("❌ Invalid AIS data format")
        return None
    
    positions = ais_data['ais_data']
    metadata = ais_data.get('metadata', {})
    route_summary = ais_data.get('route_summary', {})
    
    if not positions:
        print("❌ No position data found")
        return None
    
    # Calculate map center (middle of route)
    if route_summary:
        start_pos = route_summary.get('start_position', {})
        end_pos = route_summary.get('end_position', {})
        
        if start_pos and end_pos:
            center_lat = (start_pos['latitude'] + end_pos['latitude']) / 2
            center_lon = (start_pos['longitude'] + end_pos['longitude']) / 2
        else:
            # Fallback to first position
            center_lat = positions[0]['position']['latitude']
            center_lon = positions[0]['position']['longitude']
    else:
        center_lat = positions[0]['position']['latitude']
        center_lon = positions[0]['position']['longitude']
    
    # Create map
    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=10,
        tiles='OpenStreetMap'
    )
    
    # Add title
    ship_name = metadata.get('ship_name', 'Unknown Ship')
    mmsi = metadata.get('mmsi', 'N/A')
    total_reports = metadata.get('total_reports', len(positions))
    generated_at = metadata.get('generated_at', 'Unknown time')
    
    title_html = f'''
    <h3 align="center" style="font-size:20px"><b>🚢 AIS Track Visualization</b></h3>
    <p align="center">
        <b>Ship:</b> {ship_name} (MMSI: {mmsi})<br>
        <b>Reports:</b> {total_reports}<br>
        <b>Generated:</b> {generated_at[:19]}<br>
        <b>Hackathon 2025</b>
    </p>
    '''
    m.get_root().html.add_child(folium.Element(title_html))
    
    # Extract coordinates for the ship's path
    path_coords = []
    for pos in positions:
        lat = pos['position']['latitude']
        lon = pos['position']['longitude']
        path_coords.append([lat, lon])
    
    # Draw ship's path
    folium.PolyLine(
        path_coords,
        color='blue',
        weight=3,
        opacity=0.8,
        popup=f"Ship Track: {ship_name}"
    ).add_to(m)
    
    # Add markers for start, intermediate points, and end
    for i, pos in enumerate(positions):
        lat = pos['position']['latitude']
        lon = pos['position']['longitude']
        
        # Format timestamp
        timestamp = pos.get('timestamp', 'Unknown')
        if 'T' in timestamp:
            timestamp = timestamp.replace('T', ' ')[:19]
        
        # Create popup content
        popup_content = f"""
        <b>🚢 {ship_name}</b><br>
        <b>MMSI:</b> {mmsi}<br>
        <b>Time:</b> {timestamp}<br>
        <b>Position:</b> {lat:.6f}, {lon:.6f}<br>
        <b>Speed:</b> {pos.get('speed_knots', 'N/A')} knots<br>
        <b>Course:</b> {pos.get('course_degrees', 'N/A')}°<br>
        <b>Status:</b> {pos.get('navigation_status', 'N/A')}<br>
        <b>Report:</b> {i+1}/{total_reports}
        """
        
        # Different icons for different points
        if i == 0:
            # Start point
            icon = folium.Icon(color='green', icon='play', prefix='fa')
            popup_content = f"🟢 <b>START</b><br>" + popup_content
        elif i == len(positions) - 1:
            # End point
            icon = folium.Icon(color='red', icon='stop', prefix='fa')
            popup_content = f"🔴 <b>END</b><br>" + popup_content
        else:
            # Intermediate points (show only every few points to avoid clutter)
            if len(positions) > 10 and i % max(1, len(positions) // 10) != 0:
                continue  # Skip some intermediate points if too many
            icon = folium.Icon(color='blue', icon='ship', prefix='fa')
            popup_content = f"🔵 <b>POSITION</b><br>" + popup_content
        
        folium.Marker(
            location=[lat, lon],
            popup=folium.Popup(popup_content, max_width=300),
            tooltip=f"{ship_name} - Report {i+1}",
            icon=icon
        ).add_to(m)
    
    # Add map boundaries to fit all points
    if len(path_coords) > 1:
        m.fit_bounds(path_coords)
    
    # Save map
    try:
        m.save(save_path)
        print(f"✅ Map saved to: {save_path}")
        return save_path
    except Exception as e:
        print(f"❌ Error saving map: {e}")
        return None


def open_map(map_path):
    """Open the map in the default web browser"""
    try:
        # Convert to absolute path
        abs_path = os.path.abspath(map_path)
        file_url = f"file://{abs_path}"
        
        print(f"🌐 Opening map in browser: {file_url}")
        webbrowser.open(file_url)
        
    except Exception as e:
        print(f"❌ Error opening browser: {e}")
        print(f"📂 You can manually open: {map_path}")


def main():
    """Main function"""
    print("🗺️  AIS Data Map Viewer - Hackathon 2025")
    print("=" * 50)
    
    # Check if a specific file was provided
    if len(sys.argv) > 1:
        json_file = Path(sys.argv[1])
        if not json_file.exists():
            print(f"❌ File not found: {json_file}")
            return
    else:
        # Find the latest JSON file
        json_file = find_latest_json_file()
        if not json_file:
            print("💡 Tip: Generate some data first with 'python test_crawl.py'")
            return
    
    print(f"📁 Loading: {json_file}")
    
    # Load AIS data
    ais_data = load_ais_data(json_file)
    if not ais_data:
        return
    
    # Display data summary
    metadata = ais_data.get('metadata', {})
    print(f"🚢 Ship: {metadata.get('ship_name', 'Unknown')} (MMSI: {metadata.get('mmsi', 'N/A')})")
    print(f"📊 Reports: {metadata.get('total_reports', 'N/A')}")
    print(f"⏱️  Duration: {metadata.get('duration_hours', 'N/A')} hours")
    
    # Create map
    map_filename = f"ais_map_{metadata.get('mmsi', 'unknown')}.html"
    map_path = create_map(ais_data, map_filename)
    
    if map_path:
        print()
        print("🎯 Map Features:")
        print("  🟢 Green marker = Start position")
        print("  🔵 Blue markers = Intermediate positions") 
        print("  🔴 Red marker = End position")
        print("  📍 Click markers for detailed AIS info")
        print("  📏 Blue line shows ship's track")
        print()
        
        # Ask user if they want to open the map
        try:
            response = input("🌐 Open map in browser? (y/n): ").lower().strip()
            if response in ['y', 'yes', '']:
                open_map(map_path)
            else:
                print(f"📂 Map saved as: {map_path}")
                print("💡 You can open it manually in any web browser")
        except KeyboardInterrupt:
            print(f"\n📂 Map saved as: {map_path}")
    
    print("\n✅ Map viewer completed!")


if __name__ == "__main__":
    main()
