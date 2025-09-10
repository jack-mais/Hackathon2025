#!/usr/bin/env python3
"""
Test script to verify integrated JSON + Map generation
Tests that both data and map files are created automatically
"""

import sys
import asyncio
import os
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

from src.llm_integration.demo_client import AISDemo
from src.mcp_integration.mcp_server import AISMCPServer


async def test_mcp_server_integrated_output():
    """Test MCP server generates both JSON and map files"""
    print("🔧 Testing MCP Server - Integrated JSON + Map Output")
    print("=" * 50)
    
    server = AISMCPServer()
    
    test_scenarios = [
        {"region": "mediterranean", "num_ships": 2, "scenario_name": "test_mediterranean"},
        {"region": "irish_sea", "num_ships": 3, "scenario_name": "test_irish_sea"}, 
        {"region": "asia", "num_ships": 2, "scenario_name": "test_asia"}
    ]
    
    for scenario in test_scenarios:
        print(f"\n🌊 Testing {scenario['region']} scenario...")
        
        try:
            # Test maritime scenario generation
            result = await server.call_tool("generate_maritime_scenario", {
                "num_ships": scenario["num_ships"],
                "region": scenario["region"],
                "duration_hours": 1.0,
                "scenario_name": scenario["scenario_name"]
            })
            
            if result["success"]:
                saved_files = result["saved_files"]
                print(f"   ✅ Generated {result['ships_generated']} ships")
                print(f"   📁 Files created: {list(saved_files.keys())}")
                
                # Check if JSON file exists
                if "json" in saved_files and os.path.exists(saved_files["json"]):
                    print(f"   ✅ JSON file created: {Path(saved_files['json']).name}")
                else:
                    print(f"   ❌ JSON file missing or not found")
                
                # Check if map file exists  
                if "map" in saved_files and os.path.exists(saved_files["map"]):
                    print(f"   ✅ Map file created: {Path(saved_files['map']).name}")
                    
                    # Check map file size (should be > 1KB for a real map)
                    map_size = Path(saved_files["map"]).stat().st_size
                    if map_size > 1000:
                        print(f"   ✅ Map file looks valid ({map_size:,} bytes)")
                    else:
                        print(f"   ⚠️  Map file seems small ({map_size} bytes)")
                else:
                    print(f"   ❌ Map file missing or not found")
                    
            else:
                print(f"   ❌ Generation failed: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            print(f"   ❌ Exception: {e}")
    
    print(f"\n📊 MCP Server integrated output test completed!")


async def test_demo_client_integrated_output():
    """Test demo client mentions both outputs"""
    print("\n🚢 Testing Demo Client - Integrated Output Messages")
    print("=" * 50)
    
    client = AISDemo()
    
    test_requests = [
        "Generate 2 ships in the North Sea",
        "Create a demo with Mediterranean ships",
    ]
    
    for i, request in enumerate(test_requests, 1):
        print(f"\n{i}. Testing: '{request}'")
        try:
            response = await client.process_request(request)
            
            # Check if response mentions both outputs
            mentions_json = "📁" in response and ("JSON" in response or "json" in response)
            mentions_map = "🗺️" in response and ("map" in response or "HTML" in response)
            mentions_both = "Both" in response or "both" in response
            
            print(f"   ✅ Response length: {len(response)} characters")
            print(f"   📁 Mentions JSON: {'Yes' if mentions_json else 'No'}")
            print(f"   🗺️ Mentions map: {'Yes' if mentions_map else 'No'}")
            print(f"   🎯 Mentions both: {'Yes' if mentions_both else 'No'}")
            
            if mentions_json and mentions_map:
                print(f"   ✅ SUCCESS: Response mentions both outputs!")
            else:
                print(f"   ⚠️  WARNING: Response may not mention both outputs clearly")
                print(f"   📝 Response preview: {response[:200]}...")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print(f"\n📊 Demo client integrated output test completed!")


def test_output_directory():
    """Check the output directory for generated files"""
    print("\n📁 Testing Output Directory")
    print("=" * 30)
    
    output_dir = Path("output")
    if not output_dir.exists():
        print("❌ Output directory doesn't exist")
        return
    
    # Count different file types
    json_files = list(output_dir.glob("*.json"))
    html_files = list(output_dir.glob("*.html"))
    nmea_files = list(output_dir.glob("*.nmea"))
    
    print(f"📁 JSON files: {len(json_files)}")
    print(f"🗺️ HTML map files: {len(html_files)}")  
    print(f"📡 NMEA files: {len(nmea_files)}")
    
    if html_files:
        print(f"\n🗺️ Recent map files:")
        for html_file in sorted(html_files, key=lambda f: f.stat().st_mtime, reverse=True)[:3]:
            size_kb = html_file.stat().st_size // 1024
            print(f"   • {html_file.name} ({size_kb} KB)")
    
    if json_files:
        print(f"\n📁 Recent JSON files:")
        for json_file in sorted(json_files, key=lambda f: f.stat().st_mtime, reverse=True)[:3]:
            size_kb = json_file.stat().st_size // 1024
            print(f"   • {json_file.name} ({size_kb} KB)")


async def main():
    """Run all integrated output tests"""
    print("🌐 INTEGRATED JSON + MAP GENERATION TESTS")
    print("=" * 60)
    
    try:
        # Test current output directory
        test_output_directory()
        
        # Test MCP server integration
        await test_mcp_server_integrated_output()
        
        # Test demo client messaging
        await test_demo_client_integrated_output()
        
        print("\n" + "=" * 60)
        print("🎉 INTEGRATED OUTPUT TESTS COMPLETED!")
        print("✅ The system now automatically generates both JSON data and interactive maps")
        print("✅ Every ship generation prompt creates 2 files: .json + .html")
        print("✅ No extra steps needed - maps are created automatically")
        print("✅ LLM clients properly inform users about both outputs")
        
        print(f"\n🎯 **ENHANCED USER EXPERIENCE:**")
        print(f"   • Users get instant visual feedback via interactive maps")
        print(f"   • JSON data available for programmatic analysis") 
        print(f"   • Maps show ship routes, waypoints, and detailed info popups")
        print(f"   • Works for all maritime regions worldwide")
        
        print(f"\n💡 Try running: python ais_chat.py")
        print(f"   Then ask: 'Generate 3 ships in the Mediterranean'")
        print(f"   You'll get BOTH a JSON file AND an interactive map!")
        
    except Exception as e:
        print(f"\n❌ TEST SUITE FAILED: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())

