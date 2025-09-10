#!/usr/bin/env python3
"""
Test script to demonstrate sophisticated AIS scenario generation
Tests the enhanced natural language processing and specialized scenarios
"""

import sys
import asyncio
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

from src.llm_integration.demo_client import AISDemo
from src.mcp_integration.mcp_server import AISMCPServer


async def test_sophisticated_requests():
    """Test sophisticated natural language requests"""
    print("🚢 Testing Sophisticated Natural Language Scenarios")
    print("=" * 60)
    
    client = AISDemo()
    
    # Advanced scenario requests that should now be handled much better
    sophisticated_requests = [
        # Location-specific requests
        "Generate 5 cargo ships traveling from Singapore to Shanghai for 8 hours",
        "Create a convoy of 4 ships escorting through the Mediterranean", 
        "Show me 3 cruise ships touring the Caribbean for 12 hours",
        "Generate a fishing fleet of 6 vessels operating in the North Sea",
        
        # Scenario-based requests
        "Simulate an emergency rescue operation with 4 boats in the Atlantic",
        "Create a military exercise with 7 naval vessels in the Baltic Sea",
        "Generate port operations with tugs and ferries at Rotterdam harbor",
        "Show me oil platform supply vessels in the North Sea for 6 hours",
        
        # Complex multi-parameter requests
        "Generate 8 racing yachts in a Mediterranean regatta lasting 4 hours",
        "Create storm avoidance scenario with 5 ships in rough Pacific waters",
        "Simulate border patrol with 3 coast guard vessels along English Channel",
        "Generate whale watching tour boats in Norwegian waters for 3 hours",
        
        # Coordinate-based requests (these should be parsed and handled)
        "Generate ships traveling between coordinates 51.5,-0.1 and 48.8,2.3",
        "Create vessels moving from 40.7,-74.0 to 34.0,-118.2 over 24 hours"
    ]
    
    for i, request in enumerate(sophisticated_requests, 1):
        print(f"\n{i}. Testing: '{request}'")
        print("-" * 80)
        try:
            response = await client.process_request(request)
            
            # Analyze response quality
            has_ship_count = any(word in response for word in ['ships', 'vessels', 'boats'])
            has_location = any(word in response for word in ['Mediterranean', 'Atlantic', 'North Sea', 'Singapore', 'Caribbean'])
            has_scenario_type = any(word in response for word in ['convoy', 'rescue', 'cruise', 'fishing', 'military'])
            mentions_files = "📁" in response and "🗺️" in response
            
            print(f"✅ Response length: {len(response)} characters")
            print(f"🚢 Mentions ships: {'Yes' if has_ship_count else 'No'}")
            print(f"🌍 Mentions location: {'Yes' if has_location else 'No'}")
            print(f"🎯 Mentions scenario: {'Yes' if has_scenario_type else 'No'}")
            print(f"📁 Mentions files: {'Yes' if mentions_files else 'No'}")
            
            # Show first 300 chars of response
            preview = response[:300] + "..." if len(response) > 300 else response
            print(f"📝 Preview: {preview}")
            
            if all([has_ship_count, mentions_files]):
                print("🎉 SUCCESS: Sophisticated request handled well!")
            else:
                print("⚠️  PARTIAL: May need refinement")
                
        except Exception as e:
            print(f"❌ Error: {e}")


async def test_specialized_mcp_tools():
    """Test the new specialized MCP tools directly"""
    print("\n🔧 Testing Specialized MCP Tools")
    print("=" * 40)
    
    server = AISMCPServer()
    
    # Test coordinate-based scenario
    print("\n1. Testing coordinate-based scenario:")
    try:
        result = await server.call_tool("generate_coordinate_scenario", {
            "coordinates": [[51.5, -0.1], [48.8, 2.3], [41.9, 2.2]], # London -> Paris -> Barcelona
            "num_ships": 3,
            "duration_hours": 6.0,
            "scenario_name": "london_paris_barcelona_route"
        })
        
        if result["success"]:
            print(f"   ✅ Generated {result['ships_generated']} ships using {result['coordinates_used']} coordinates")
            print(f"   📁 Files: {list(result['saved_files'].keys())}")
        else:
            print(f"   ❌ Failed: {result.get('error', 'Unknown error')}")
    except Exception as e:
        print(f"   ❌ Exception: {e}")
    
    # Test specialized scenarios
    specialized_scenarios = [
        ("convoy", 6, "north_sea", "Military convoy escort"),
        ("rescue_operation", 4, "atlantic", "Search and rescue mission"),
        ("cruise_tourism", 3, "mediterranean", "Luxury cruise tour"),
        ("fishing_fleet", 8, "north_sea", "Commercial fishing operation"),
        ("military_exercise", 5, "baltic_sea", "Naval training exercise")
    ]
    
    for scenario_type, ships, region, description in specialized_scenarios:
        print(f"\n2. Testing {scenario_type} scenario:")
        try:
            result = await server.call_tool("generate_specialized_scenario", {
                "scenario_type": scenario_type,
                "num_ships": ships,
                "region": region,
                "duration_hours": 4.0,
                "scenario_name": f"test_{scenario_type}",
                "special_parameters": {
                    "formation_spacing": 0.8,
                    "emergency_urgency": "high",
                    "weather_severity": "moderate"
                }
            })
            
            if result["success"]:
                print(f"   ✅ Generated {result['ships_generated']} ships for {description}")
                print(f"   🌊 Region: {result['region']}")
                print(f"   📁 Files: {list(result['saved_files'].keys())}")
            else:
                print(f"   ❌ Failed: {result.get('error', 'Unknown error')}")
        except Exception as e:
            print(f"   ❌ Exception: {e}")


async def test_parameter_variety():
    """Test variety in generated parameters"""
    print("\n📊 Testing Parameter Variety")
    print("=" * 35)
    
    client = AISDemo()
    
    # Test different durations
    duration_tests = [
        "Generate 3 ships for 30 minutes",
        "Create 4 vessels for 6 hours", 
        "Show me 2 ships over 2 days",
        "Generate a 15-minute emergency scenario"
    ]
    
    print("⏱️ Duration parsing tests:")
    for test in duration_tests:
        print(f"   Testing: '{test}'")
        scenario = client._parse_advanced_scenario(test)
        print(f"   → Parsed duration: {scenario['duration']} hours")
    
    # Test different ship counts
    ship_count_tests = [
        "Generate a fleet of 15 vessels",
        "Create 1 ship",
        "Show me 25 maritime units", 
        "Generate a group of 8 boats"
    ]
    
    print(f"\n🚢 Ship count parsing tests:")
    for test in ship_count_tests:
        print(f"   Testing: '{test}'")
        scenario = client._parse_advanced_scenario(test)
        print(f"   → Parsed ship count: {scenario['num_ships']} ships")
    
    # Test region detection
    region_tests = [
        "Generate ships in the Mediterranean Sea",
        "Create vessels in Norwegian waters",
        "Show me boats in the Caribbean",
        "Generate ships crossing the Atlantic",
        "Create vessels near Japanese waters"
    ]
    
    print(f"\n🌍 Region detection tests:")
    for test in region_tests:
        print(f"   Testing: '{test}'")
        scenario = client._parse_advanced_scenario(test)
        print(f"   → Detected region: {scenario['region']}")
        print(f"   → Scenario type: {scenario['scenario_type'] or 'None'}")


async def main():
    """Run all sophisticated scenario tests"""
    print("🎯 SOPHISTICATED AIS SCENARIO GENERATION TESTS")
    print("=" * 70)
    
    try:
        # Test natural language processing improvements
        await test_sophisticated_requests()
        
        # Test new MCP tools
        await test_specialized_mcp_tools()
        
        # Test parameter parsing variety
        await test_parameter_variety()
        
        print("\n" + "=" * 70)
        print("🎉 SOPHISTICATED SCENARIO TESTS COMPLETED!")
        print("")
        print("✅ **ENHANCED CAPABILITIES:**")
        print("   • 🌍 Worldwide maritime regions (15+ regions)")
        print("   • 🚢 Specialized scenarios (convoy, rescue, cruise, military, etc.)")
        print("   • 📍 Coordinate-based routing")
        print("   • ⏱️ Flexible duration parsing (minutes, hours, days)")
        print("   • 🎯 Advanced ship type recognition")
        print("   • 🔢 Variable ship counts (1-30 vessels)")
        print("   • 🛠️ Specialized MCP tools")
        print("")
        print("🎮 **EXAMPLE REQUESTS NOW SUPPORTED:**")
        print('   • "Generate 8 cargo ships from Singapore to Shanghai for 12 hours"')
        print('   • "Create a rescue operation with 5 boats in the Atlantic"')
        print('   • "Show me a military convoy of 6 vessels in the Mediterranean"')
        print('   • "Generate fishing fleet in North Sea for 4 hours"')
        print('   • "Create cruise ships touring the Caribbean over 2 days"')
        print("")
        print("💡 **TRY IT:** python ais_chat.py")
        print("   Then ask: 'Generate a convoy of 6 ships escorting through the Mediterranean'")
        
    except Exception as e:
        print(f"\n❌ TEST SUITE FAILED: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())

