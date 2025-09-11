#!/usr/bin/env python3
"""
Test unknown location geocoding
"""

import sys
import os
import asyncio
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

from src.mcp_integration.mcp_server import AISMCPServer


async def test_unknown_locations():
    """Test unknown location geocoding"""
    
    print("🔍 Testing Unknown Location Geocoding")
    print("=" * 50)
    
    server = AISMCPServer()
    
    # Test various locations
    test_locations = [
        "Genoa",  # Should be found in extended database
        "Split",  # Should be found in extended database
        "Istanbul",  # Should be found in extended database
        "Aegean Sea",  # Should be found in extended database
        "Unknown City XYZ",  # Should fail and use fallback
        "Port of Nowhere",  # Should fail and use fallback
    ]
    
    for location in test_locations:
        print(f"\nTesting: '{location}'")
        print("-" * 30)
        
        try:
            coords = server._parse_location(location)
            print(f"✅ Coordinates: ({coords.latitude:.4f}, {coords.longitude:.4f})")
            
            # Check if it's the fallback coordinates
            if abs(coords.latitude - 50.0) < 0.01 and abs(coords.longitude - 0.0) < 0.01:
                print("⚠️ Using fallback coordinates (English Channel)")
            else:
                print("✅ Found specific coordinates!")
                
        except Exception as e:
            print(f"❌ Error: {e}")


if __name__ == "__main__":
    asyncio.run(test_unknown_locations())
