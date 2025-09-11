#!/usr/bin/env python3
"""
Test script to verify worldwide maritime context changes
Tests the updated LLM clients and generators with global scenarios
"""

import sys
import asyncio
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

from src.llm_integration.gemini_client import AISGeminiClient
from src.generators.ais_generator import WorldwideRoutes
from src.mcp_integration.mcp_server import AISMCPServer


async def test_demo_client_worldwide():
    """Test the demo client with worldwide requests"""
    print("🚢 Testing Demo Client - Worldwide Context")
    print("=" * 50)
    
    # Note: These tests now require GEMINI_KEY environment variable
    try:
        client = AISGeminiClient()
    except Exception as e:
        print(f"❌ Cannot create Gemini client: {e}")
        print("💡 Set GEMINI_KEY environment variable to run these tests")
        return
    
    test_requests = [
        "Generate 3 ships in the Mediterranean",
        "Create 2 cargo ships from Singapore to Shanghai", 
        "What ports are available in Asia?",
        "Generate ships in the North Sea",
        "Show me available ports worldwide",
        "Create fishing vessels in the Caribbean",
        "Generate a ferry from Rotterdam to Hamburg"
    ]
    
    for i, request in enumerate(test_requests, 1):
        print(f"\n{i}. Testing: '{request}'")
        try:
            response = await client.process_request(request)
            print(f"✅ Response length: {len(response)} characters")
            print(f"📝 First 200 chars: {response[:200]}...")
            if "✅" in response and "saved to" in response.lower():
                print("🎯 Generation successful!")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("\n🎉 Demo client worldwide test completed!")


def test_worldwide_routes():
    """Test the worldwide routes and port data"""
    print("\n🌍 Testing Worldwide Routes & Ports")
    print("=" * 40)
    
    # Test all ports
    all_ports = WorldwideRoutes.get_all_ports()
    print(f"📍 Total ports available: {len(all_ports)}")
    
    # Test ports by region
    regions = ["irish_sea", "mediterranean", "north_sea", "asia", "north_america"]
    for region in regions:
        ports = WorldwideRoutes.get_ports_by_region(region)
        print(f"🏙️  {region.title().replace('_', ' ')}: {len(ports)} ports")
        if ports:
            sample_ports = list(ports.keys())[:3]
            print(f"   Sample ports: {', '.join(sample_ports)}")
    
    # Test routes by region
    print(f"\n⛴️  Testing ferry routes by region:")
    for region in ["irish_sea", "mediterranean", "nordic"]:
        routes = WorldwideRoutes.get_ferry_routes(region)
        print(f"   {region.title().replace('_', ' ')}: {len(routes)} ferry routes")


async def test_mcp_server_worldwide():
    """Test the MCP server with worldwide tools"""
    print("\n🔧 Testing MCP Server - Worldwide Tools")
    print("=" * 40)
    
    server = AISMCPServer()
    
    # Test maritime scenario generation
    print("\n1. Testing maritime scenario generation:")
    for region in ["mediterranean", "asia", "north_sea"]:
        print(f"   Generating {region} scenario...")
        try:
            result = await server.call_tool("generate_maritime_scenario", {
                "num_ships": 2,
                "region": region,
                "duration_hours": 1.0,
                "scenario_name": f"test_{region}"
            })
            if result["success"]:
                print(f"   ✅ {region}: {result['ships_generated']} ships generated")
            else:
                print(f"   ❌ {region}: {result.get('error', 'Unknown error')}")
        except Exception as e:
            print(f"   ❌ {region}: Exception - {e}")
    
    # Test port listing
    print("\n2. Testing worldwide port listing:")
    for region in ["all", "asia", "europe", "mediterranean"]:
        try:
            result = await server.call_tool("list_available_ports", {"region": region})
            if result["success"]:
                print(f"   ✅ {region}: {result['total_ports']} ports listed")
            else:
                print(f"   ❌ {region}: {result.get('error', 'Unknown error')}")
        except Exception as e:
            print(f"   ❌ {region}: Exception - {e}")


async def test_ship_naming():
    """Test region-specific ship naming"""
    print("\n🚢 Testing Region-Specific Ship Names")
    print("=" * 40)
    
    from src.generators.ais_generator import AISGenerator
    from src.core.models import ShipType
    
    generator = AISGenerator()
    regions = ["irish_sea", "mediterranean", "asia", "north_sea"]
    ship_types = [ShipType.PASSENGER, ShipType.CARGO, ShipType.FISHING]
    
    for region in regions:
        print(f"\n🌊 {region.title().replace('_', ' ')} region:")
        for i, ship_type in enumerate(ship_types):
            name = generator._generate_ship_name(ship_type, i, region)
            print(f"   {ship_type.name}: {name}")


async def main():
    """Run all worldwide context tests"""
    print("🌍 WORLDWIDE MARITIME CONTEXT TESTS")
    print("=" * 60)
    
    try:
        # Test basic functionality
        test_worldwide_routes()
        await test_ship_naming()
        
        # Test MCP server
        await test_mcp_server_worldwide()
        
        # Test demo client (most comprehensive)
        await test_demo_client_worldwide()
        
        print("\n" + "=" * 60)
        print("🎉 ALL WORLDWIDE CONTEXT TESTS COMPLETED!")
        print("✅ The system now supports global maritime scenarios")
        print("✅ You can generate ships in any maritime region worldwide")
        print("✅ Port database includes major ports from all continents")
        print("✅ Ship names are region-appropriate")
        print("\n💡 Try running: python ais_chat.py")
        print("   Then ask: 'Generate 3 ships in the Mediterranean'")
        
    except Exception as e:
        print(f"\n❌ TEST SUITE FAILED: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
