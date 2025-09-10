#!/usr/bin/env python3
"""
Test script for AIS Generator - Walk Version
Demonstrates multiple ships with realistic routes
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from src.generators.multi_ship_generator import MultiShipGenerator
from src.generators.nmea_formatter import NMEAFormatter
from src.core.file_output import FileOutputManager
import json


def test_multi_ship_irish_sea():
    """Test multiple ships in Irish Sea with realistic routes"""
    print("🚢🚢🚢 Testing AIS Generator - Walk Version (Multiple Ships)")
    print("=" * 70)
    
    # Get number of ships from user
    try:
        num_ships = int(input("How many ships would you like to generate? (1-10): "))
        if not 1 <= num_ships <= 10:
            print("Using default: 5 ships")
            num_ships = 5
    except (ValueError, KeyboardInterrupt):
        print("Using default: 5 ships")
        num_ships = 5
    
    print(f"\n🎯 Generating {num_ships} ships with realistic Irish Sea routes...")
    print("-" * 50)
    
    # Create multi-ship generator and file manager
    generator = MultiShipGenerator()
    formatter = NMEAFormatter()
    file_manager = FileOutputManager()
    
    # Generate ships
    ships = generator.generate_irish_sea_scenario(num_ships)
    
    # Display ship details
    for i, ship in enumerate(ships, 1):
        route_start = ship.route.start_position
        route_end = ship.route.end_position
        print(f"🛳️  Ship {i}: {ship.ship_name}")
        print(f"   MMSI: {ship.mmsi}")
        print(f"   Type: {ship.ship_type.name}")
        print(f"   Route: {ship.route_type.value}")
        print(f"   From: ({route_start.latitude:.3f}, {route_start.longitude:.3f})")
        print(f"   To: ({route_end.latitude:.3f}, {route_end.longitude:.3f})")
        print(f"   Distance: {ship.total_distance_nm:.1f} nm")
        print(f"   Speed: {ship.route.speed_knots:.1f} knots")
        print(f"   Est. Time: {ship.total_time_hours:.1f} hours")
        print(f"   Waypoints: {len(ship.waypoints)} points")
        print()
    
    # Generate movement data for all ships
    print("📡 Generating movement data for all ships...")
    
    # Use different durations based on ship types for realism
    duration_hours = 2.0  # 2 hours of movement
    report_interval = 300  # 5 minutes
    
    all_ship_data = {}
    
    for ship in ships:
        print(f"  Generating data for {ship.ship_name}...")
        
        # Generate states for this ship
        states = list(ship.generate_movement(duration_hours, report_interval))
        all_ship_data[ship.mmsi] = states
        
        print(f"    ✅ {len(states)} position reports generated")
    
    print(f"\n📊 Generated data for {len(ships)} ships")
    print(f"⏱️  Duration: {duration_hours} hours")
    print(f"📡 Report interval: {report_interval // 60} minutes")
    
    # Show sample positions from first few ships
    print("\n📍 Sample positions from first 3 ships:")
    print("-" * 60)
    
    for i, ship in enumerate(ships[:3]):
        states = all_ship_data[ship.mmsi]
        if states:
            first_state = states[0]
            last_state = states[-1]
            
            print(f"🚢 {ship.ship_name} ({ship.ship_type.name})")
            print(f"   Start: {first_state.position.latitude:.4f}, {first_state.position.longitude:.4f}")
            print(f"   After {duration_hours}h: {last_state.position.latitude:.4f}, {last_state.position.longitude:.4f}")
            print(f"   Status: {last_state.navigation_status.name}")
            print()
    
    # Save multi-ship data to file
    print("💾 Saving multi-ship scenario to file...")
    try:
        saved_files = file_manager.save_multi_ship_data(
            all_ship_data, 
            f"irish_sea_{num_ships}_ships_walk"
        )
        
        print(f"✅ Multi-ship data saved to: {saved_files['json']}")
        
        # Also save individual ship files for detailed analysis
        for ship in ships[:3]:  # Save first 3 ships individually
            if ship.mmsi in all_ship_data:
                individual_files = file_manager.save_route_data(
                    all_ship_data[ship.mmsi],
                    f"walk_{ship.ship_name.lower().replace(' ', '_')}",
                    "json"
                )
                print(f"✅ Individual file for {ship.ship_name}: {individual_files['json']}")
        
    except Exception as e:
        print(f"❌ File save error: {e}")
    
    print("\n🎉 Walk version test completed successfully!")
    print("🗺️  Use 'python map_multi_viewer.py' to visualize all ships on one map")
    print("🚀 Ready to implement Run version (LLM integration)")
    
    return ships, all_ship_data


def show_ship_types():
    """Show available ship types"""
    print("\n🚢 Ship Types in Walk Version:")
    print("================================")
    print("🚢 FERRY - Passenger/car ferries with regular routes")
    print("📦 CARGO - Container ships and bulk carriers") 
    print("🎣 FISHING - Fishing vessels with circular patterns")
    print("🚁 PATROL - Coast guard/navy patrol boats")
    print("⚡ HIGH_SPEED - Fast passenger craft")
    print("\n🗺️  Route Types:")
    print("• Ferry routes: Major port-to-port connections")
    print("• Cargo routes: Commercial shipping lanes")
    print("• Fishing areas: Circular patterns in fishing grounds")
    print("• Patrol routes: Back-and-forth coastal patrol")
    print("• Coastal routes: Following coastline patterns")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--info":
        show_ship_types()
    else:
        test_multi_ship_irish_sea()
