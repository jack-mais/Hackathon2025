#!/usr/bin/env python3
"""
Test script for AIS Generator - Crawl Version
Demonstrates single ship point-to-point movement
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from src.generators.ais_generator import AISGenerator
from src.generators.nmea_formatter import NMEAFormatter
from src.core.models import Position, Route
from src.core.file_output import FileOutputManager
import json


def test_irish_sea_route():
    """Test the Irish Sea demo route"""
    print("🚢 Testing AIS Generator - Crawl Version")
    print("=" * 50)
    
    # Create generator, formatter, and file manager
    generator = AISGenerator()
    formatter = NMEAFormatter()
    file_manager = FileOutputManager()
    
    # Create Irish Sea route (Dublin to Holyhead)
    route = generator.generate_sample_irish_sea_route()
    print(f"📍 Route: Dublin ({route.start_position.latitude:.4f}, {route.start_position.longitude:.4f})")
    print(f"📍    to: Holyhead ({route.end_position.latitude:.4f}, {route.end_position.longitude:.4f})")
    print(f"🚤 Speed: {route.speed_knots} knots")
    
    # Add ship
    mmsi = 123456789
    ship_name = "HACKATHON_DEMO"
    ship = generator.add_ship(route, mmsi, ship_name)
    
    print(f"🛳️  Ship: {ship_name} (MMSI: {mmsi})")
    print(f"📏 Distance: {ship.total_distance_nm:.1f} nautical miles")
    print(f"⏱️  Estimated time: {ship.total_time_hours:.1f} hours")
    print(f"🧭 Bearing: {ship.bearing:.1f}°")
    print()
    
    # Generate sample data for complete journey
    duration_hours = ship.total_time_hours + 0.1  # Full journey time plus a bit extra
    report_interval = 300  # 5 minutes (to keep reasonable number of points)
    
    print("📡 Generating AIS data...")
    states = list(ship.generate_movement(duration_hours, report_interval))
    
    print(f"Generated {len(states)} position reports")
    print()
    
    # Show first few positions
    print("📊 Sample position reports:")
    print("-" * 80)
    
    for i, state in enumerate(states[:5]):  # Show first 5 reports
        json_data = formatter.create_ais_summary(state)
        print(f"Report {i+1}:")
        print(f"  Time: {state.timestamp.strftime('%H:%M:%S')}")
        print(f"  Position: {state.position.latitude:.6f}, {state.position.longitude:.6f}")
        print(f"  Speed: {state.speed_over_ground:.1f} knots")
        print(f"  Course: {state.course_over_ground:.1f}°")
        print(f"  Status: {state.navigation_status.name}")
        print()
    
    if len(states) > 5:
        print(f"... ({len(states) - 5} more reports)")
        print()
        
        # Show final position
        final_state = states[-1]
        print("🏁 Final position:")
        print(f"  Time: {final_state.timestamp.strftime('%H:%M:%S')}")
        print(f"  Position: {final_state.position.latitude:.6f}, {final_state.position.longitude:.6f}")
        print(f"  Speed: {final_state.speed_over_ground:.1f} knots")
        print(f"  Status: {final_state.navigation_status.name}")
        print()
    
    # Generate sample NMEA data
    print("📟 Sample NMEA sentences:")
    print("-" * 40)
    for i, state in enumerate(states[:3]):
        nmea_sentence = formatter.format_realistic_position_report(state)
        print(f"Report {i+1}: {nmea_sentence[:60]}...")
    
    
    # Test file output
    print("💾 Testing file output...")
    try:
        saved_files = file_manager.save_route_data(states, "test_crawl", "json")
        print(f"✅ Saved to: {saved_files['json']}")
        
        # Save NMEA version too
        saved_nmea = file_manager.save_route_data(states, "test_crawl", "nmea")
        print(f"✅ Saved NMEA to: {saved_nmea['nmea']}")
        
    except Exception as e:
        print(f"❌ File save error: {e}")
    
    print()
    print("✅ Crawl version test completed successfully!")
    print("💾 Data saved to JSON files in ./output/ directory")
    print("🚀 Ready to implement Walk (multiple ships) and Run (LLM integration) versions")


if __name__ == "__main__":
    test_irish_sea_route()
