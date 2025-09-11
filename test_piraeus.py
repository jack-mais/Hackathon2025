#!/usr/bin/env python3
"""
Test Piraeus location parsing
"""

import sys
import os
import asyncio
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

from src.mcp_integration.mcp_server import AISMCPServer


async def test_piraeus():
    """Test Piraeus location parsing"""
    
    print("🔍 Testing Piraeus Location Parsing")
    print("=" * 50)
    
    server = AISMCPServer()
    
    # Test Piraeus
    test_locations = [
        "Piraeus",
        "piraeus",
        "PIRAEUS", 
        "port of piraeus",
        "off piraeus",
        "coast of piraeus"
    ]
    
    for location in test_locations:
        print(f"\nTesting: '{location}'")
        print("-" * 30)
        
        try:
            coords = server._parse_location(location)
            print(f"✅ Coordinates: ({coords.latitude:.4f}, {coords.longitude:.4f})")
            
            # Check if it's the correct Piraeus coordinates
            if abs(coords.latitude - 37.9755) < 0.01 and abs(coords.longitude - 23.7348) < 0.01:
                print("✅ Correct Piraeus coordinates!")
            else:
                print("❌ Wrong coordinates - not Piraeus")
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    # Test actual ship generation
    print(f"\n🚢 Testing ship generation at Piraeus")
    print("-" * 40)
    
    try:
        result = await server.call_tool("generate_ais_data", {
            "num_ships": 2,
            "location": "Piraeus",
            "duration_hours": 1.0,
            "scenario_name": "piraeus_test"
        })
        
        if result.get("success"):
            ships_generated = result.get("ships_generated", 0)
            print(f"✅ Success: {ships_generated} ships generated at Piraeus")
            
            # Check if files were generated
            if result.get("saved_files"):
                print("📁 Files generated:")
                for file_type, path in result["saved_files"].items():
                    print(f"   {file_type}: {path}")
        else:
            print(f"❌ Failed: {result.get('error')}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_piraeus())
