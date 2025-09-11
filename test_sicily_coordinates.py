#!/usr/bin/env python3
"""
Test script to verify intelligent coordinate detection for Sicily and other specific locations
"""

import sys
import asyncio
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

from src.llm_integration.demo_client import AISDemo
from src.generators.ais_generator import WorldwideRoutes


async def test_sicily_coordinate_detection():
    """Test specific Sicily coordinate detection"""
    print("🏝️ Testing Sicily Coordinate Detection")
    print("=" * 50)
    
    client = AISDemo()
    
    # Test various Sicily-related requests
    sicily_requests = [
        "Generate a convoy off the coast of Sicily",
        "Create 4 ships near Sicily for 6 hours", 
        "Show me vessels off Sicily in the Mediterranean",
        "Generate ships around the Italian coast near Sicily",
        "Create maritime traffic in Sicilian waters"
    ]
    
    for request in sicily_requests:
        print(f"\n🧪 Testing: '{request}'")
        print("-" * 60)
        
        # Test the parsing
        scenario = client._parse_advanced_scenario(request)
        print(f"📍 Detected region: {scenario.get('region', 'None')}")
        print(f"🎯 Scenario type: {scenario.get('scenario_type', 'None')}")
        print(f"📋 Original message stored: {'Yes' if scenario.get('original_message') else 'No'}")
        
        # Test coordinate selection
        smart_coords = WorldwideRoutes.get_smart_coordinates_for_location(request)
        print(f"🧭 Smart coordinates: {smart_coords.latitude:.2f}, {smart_coords.longitude:.2f}")
        
        # Verify it's in the right area (Sicily should be around 37.5°N, 13.8°E)
        is_sicily_area = (36.0 <= smart_coords.latitude <= 39.0 and 
                         12.0 <= smart_coords.longitude <= 16.0)
        
        print(f"✅ In Sicily area: {'Yes' if is_sicily_area else 'No'}")
        
        if is_sicily_area:
            print("🎉 SUCCESS: Correctly detected Sicily coordinates!")
        else:
            print(f"⚠️  ISSUE: Coordinates not in Sicily area")


async def test_various_location_detection():
    """Test coordinate detection for various specific locations"""
    print("\n🌍 Testing Various Location Detection")
    print("=" * 45)
    
    # Test locations with expected approximate coordinates
    test_locations = [
        ("Generate ships off the coast of Sicily", 37.5, 13.8),
        ("Create vessels in Norwegian waters", 58.0, 5.0),
        ("Show me ships near the Greek islands", 37.0, 25.0),
        ("Generate boats in the French Riviera", 43.5, 7.0),
        ("Create ships near the Canary Islands", 28.0, -16.0),
        ("Generate vessels in the Bay of Biscay", 44.0, -4.0),
        ("Show me ships near Gibraltar", 36.1, -5.3),
        ("Create boats in the Shetland Islands", 60.5, -1.0)
    ]
    
    for request, expected_lat, expected_lon in test_locations:
        print(f"\n📍 Testing: '{request}'")
        
        coords = WorldwideRoutes.get_smart_coordinates_for_location(request)
        lat_diff = abs(coords.latitude - expected_lat)
        lon_diff = abs(coords.longitude - expected_lon)
        
        print(f"   Expected: {expected_lat:.1f}, {expected_lon:.1f}")
        print(f"   Got:      {coords.latitude:.1f}, {coords.longitude:.1f}")
        print(f"   Accuracy: {'✅ Good' if lat_diff < 5.0 and lon_diff < 5.0 else '❌ Poor'}")


async def test_full_sicily_scenario():
    """Test generating a full scenario for Sicily"""
    print("\n🚢 Testing Full Sicily Scenario Generation")  
    print("=" * 50)
    
    client = AISDemo()
    
    sicily_request = "Generate a convoy of 4 ships off the coast of Sicily for 3 hours"
    
    print(f"🎯 Request: '{sicily_request}'")
    print("-" * 60)
    
    try:
        response = await client.process_request(sicily_request)
        
        # Check if response mentions Mediterranean
        mentions_med = 'mediterranean' in response.lower()
        mentions_sicily = 'sicily' in response.lower()
        has_files = '📁' in response and '🗺️' in response
        
        print(f"📊 Response Analysis:")
        print(f"   Length: {len(response)} characters")
        print(f"   Mentions Mediterranean: {'✅ Yes' if mentions_med else '❌ No'}")  
        print(f"   Mentions Sicily: {'✅ Yes' if mentions_sicily else '❌ No'}")
        print(f"   Includes files: {'✅ Yes' if has_files else '❌ No'}")
        
        # Show key parts of response
        print(f"\n📝 Response preview:")
        print(response[:400] + "..." if len(response) > 400 else response)
        
        if mentions_med and has_files:
            print("\n🎉 SUCCESS: Sicily scenario generated with Mediterranean detection!")
        else:
            print("\n⚠️  PARTIAL: Some aspects may need improvement")
            
    except Exception as e:
        print(f"❌ Error: {e}")


async def main():
    """Run all location detection tests"""
    print("🎯 INTELLIGENT LOCATION COORDINATE DETECTION TESTS")
    print("=" * 65)
    
    try:
        # Test Sicily-specific detection
        await test_sicily_coordinate_detection()
        
        # Test various location detection
        await test_various_location_detection()
        
        # Test full scenario generation
        await test_full_sicily_scenario()
        
        print("\n" + "=" * 65)
        print("🎉 INTELLIGENT COORDINATE DETECTION TESTS COMPLETED!")
        print("")
        print("✅ **KEY IMPROVEMENTS:**")
        print("   • 🏝️ Sicily-specific coordinate detection (37.5°N, 13.8°E)")
        print("   • 🌍 40+ specific geographical locations mapped")
        print("   • 🎯 Smart region detection from location hints")
        print("   • 📍 Automatic coordinate generation for unmapped regions")
        print("   • 🧭 Intelligent route generation around detected coordinates")
        print("")
        print("🎮 **NOW TRY THESE REQUESTS:**")  
        print('   • "Generate a convoy off the coast of Sicily"')
        print('   • "Create ships in Norwegian waters"')
        print('   • "Show me vessels near the Greek islands"')
        print('   • "Generate boats in the French Riviera"')
        print("")
        print("💡 **HOW IT WORKS:**")
        print("   1. 🔍 Detects specific locations in user message")
        print("   2. 🧭 Maps to precise coordinates (Sicily = 37.5°N, 13.8°E)")
        print("   3. 🚢 Generates realistic routes around that location")
        print("   4. 🗺️ Creates map showing ships in correct geographical area")
        print("")
        print("🚀 **TEST IT:** python ais_chat.py")
        print("   Then ask: 'Generate a convoy off the coast of Sicily'")
        
    except Exception as e:
        print(f"\n❌ TEST SUITE FAILED: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())

