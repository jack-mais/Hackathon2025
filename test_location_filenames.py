#!/usr/bin/env python3
"""
Test location-based filename generation
"""

import sys
import os
import asyncio
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

from src.mcp_integration.mcp_server import AISMCPServer


async def test_location_filenames():
    """Test location-based filename generation"""
    
    print("🔍 Testing Location-Based Filename Generation")
    print("=" * 60)
    
    server = AISMCPServer()
    
    # Test various locations and their filename cleaning
    test_locations = [
        "Piraeus",
        "off coast of Sicily", 
        "Southampton",
        "Port of Rotterdam",
        "North Sea",
        "outside Barcelona",
        "coast of France",
        "Aegean Sea"
    ]
    
    print("📝 Location Name Cleaning:")
    print("-" * 40)
    for location in test_locations:
        clean_name = server._clean_location_name(location)
        print(f"'{location}' → '{clean_name}'")
    
    print(f"\n🚢 Testing Ship Generation with Location Names:")
    print("-" * 50)
    
    # Test actual generation with different locations
    test_cases = [
        {"location": "Piraeus", "num_ships": 2},
        {"location": "off coast of Sicily", "num_ships": 3},
        {"location": "Southampton", "num_ships": 1},
    ]
    
    for i, params in enumerate(test_cases, 1):
        print(f"\n{i}. Testing: {params['location']}")
        print("-" * 30)
        
        try:
            result = await server.call_tool("generate_ais_data", {
                "num_ships": params["num_ships"],
                "location": params["location"],
                "duration_hours": 0.5,  # Short duration for testing
                "scenario_name": f"test_{i}"
            })
            
            if result.get("success"):
                ships_generated = result.get("ships_generated", 0)
                print(f"✅ Generated {ships_generated} ships")
                
                # Check filenames
                if result.get("saved_files"):
                    print("📁 Generated files:")
                    for file_type, path in result["saved_files"].items():
                        filename = os.path.basename(path)
                        print(f"   {file_type}: {filename}")
            else:
                print(f"❌ Failed: {result.get('error')}")
                
        except Exception as e:
            print(f"❌ Exception: {e}")


if __name__ == "__main__":
    asyncio.run(test_location_filenames())
