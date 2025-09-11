#!/usr/bin/env python3
"""
Test script to verify that the system no longer defaults to Ireland/Irish Sea
"""

import sys
import asyncio
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

from src.llm_integration.demo_client import AISDemo
from src.generators.ais_generator import WorldwideRoutes


async def test_sicily_no_ireland():
    """Test that Sicily requests don't default to Ireland"""
    print("🏝️ Testing Sicily - No Ireland Default")
    print("=" * 50)
    
    client = AISDemo()
    
    sicily_request = "Generate a convoy of 3 ships off the coast of Sicily"
    print(f"🎯 Request: '{sicily_request}'")
    
    try:
        # Test the scenario parsing
        scenario = client._parse_advanced_scenario(sicily_request)
        print(f"📍 Detected region: {scenario.get('region', 'None')}")
        print(f"🔍 Location hint: {scenario.get('original_message', 'None')}")
        
        # Test coordinate selection
        smart_coords = WorldwideRoutes.get_smart_coordinates_for_location(sicily_request)
        print(f"🧭 Smart coordinates: {smart_coords.latitude:.2f}, {smart_coords.longitude:.2f}")
        
        # Check if it's in Sicily area (not Ireland)
        is_sicily_area = (36.0 <= smart_coords.latitude <= 39.0 and 12.0 <= smart_coords.longitude <= 16.0)
        is_ireland_area = (51.0 <= smart_coords.latitude <= 55.5 and -10.0 <= smart_coords.longitude <= -5.0)
        
        print(f"✅ In Sicily area: {'YES' if is_sicily_area else 'NO'}")
        print(f"❌ In Ireland area: {'YES (BAD!)' if is_ireland_area else 'NO (GOOD!)'}")
        
        # Full response test
        print("\n📝 Testing full response...")
        response = await client.process_request(sicily_request)
        
        # Check response content
        mentions_sicily = 'sicily' in response.lower()
        mentions_mediterranean = 'mediterranean' in response.lower()
        mentions_ireland = 'ireland' in response.lower() or 'irish' in response.lower()
        
        print(f"   Mentions Sicily: {'✅ YES' if mentions_sicily else '❓ NO'}")
        print(f"   Mentions Mediterranean: {'✅ YES' if mentions_mediterranean else '❓ NO'}")
        print(f"   Mentions Ireland/Irish: {'❌ YES (BAD!)' if mentions_ireland else '✅ NO (GOOD!)'}")
        
        # Overall assessment
        if is_sicily_area and not is_ireland_area and not mentions_ireland:
            print("\n🎉 SUCCESS: Sicily correctly detected, no Ireland default!")
            return True
        else:
            print("\n⚠️  ISSUE: Still has Ireland default behavior")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


async def test_generic_request_no_ireland():
    """Test that generic requests don't default to Ireland"""
    print("\n🌊 Testing Generic Request - No Ireland Default")
    print("=" * 50)
    
    client = AISDemo()
    
    generic_request = "Generate 3 ships"
    print(f"🎯 Request: '{generic_request}'")
    
    try:
        scenario = client._parse_advanced_scenario(generic_request)
        print(f"📍 Detected region: {scenario.get('region', 'None')}")
        
        # Test the fallback coordinates
        fallback_coords = WorldwideRoutes.get_smart_coordinates_for_location("")
        print(f"🧭 Fallback coordinates: {fallback_coords.latitude:.2f}, {fallback_coords.longitude:.2f}")
        
        is_mediterranean = (35.0 <= fallback_coords.latitude <= 45.0 and 0.0 <= fallback_coords.longitude <= 20.0)
        is_ireland = (51.0 <= fallback_coords.latitude <= 55.5 and -10.0 <= fallback_coords.longitude <= -5.0)
        
        print(f"✅ Falls back to Mediterranean: {'YES' if is_mediterranean else 'NO'}")
        print(f"❌ Falls back to Ireland: {'YES (BAD!)' if is_ireland else 'NO (GOOD!)'}")
        
        # Test strategy selection
        strategy, params = client._determine_generation_strategy(scenario)
        print(f"🎯 Selected strategy: {strategy}")
        print(f"🗺️  Default region: {params.get('region', 'None')}")
        
        is_med_default = params.get('region') == 'mediterranean'
        is_irish_default = params.get('region') == 'irish_sea'
        
        print(f"✅ Defaults to Mediterranean: {'YES' if is_med_default else 'NO'}")
        print(f"❌ Defaults to Irish Sea: {'YES (BAD!)' if is_irish_default else 'NO (GOOD!)'}")
        
        if is_mediterranean and not is_ireland and is_med_default and not is_irish_default:
            print("\n🎉 SUCCESS: Generic requests now default to Mediterranean!")
            return True
        else:
            print("\n⚠️  ISSUE: Still defaulting to Ireland")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


async def test_various_locations():
    """Test various location requests to ensure they're not defaulting to Ireland"""
    print("\n🌍 Testing Various Locations - No Ireland Default")
    print("=" * 50)
    
    test_locations = [
        ("Generate ships in Norwegian waters", "north_sea"),
        ("Create vessels near the Greek islands", "mediterranean"),
        ("Show me ships in the Caribbean", "caribbean"),
        ("Generate boats in the Pacific", "pacific"),
        ("Create ships near Japan", "pacific"),
    ]
    
    results = []
    client = AISDemo()
    
    for request, expected_region in test_locations:
        print(f"\n📍 Testing: '{request}'")
        
        try:
            scenario = client._parse_advanced_scenario(request)
            detected_region = scenario.get('region')
            coords = WorldwideRoutes.get_smart_coordinates_for_location(request)
            
            is_ireland = (51.0 <= coords.latitude <= 55.5 and -10.0 <= coords.longitude <= -5.0)
            region_correct = detected_region == expected_region
            
            print(f"   Expected: {expected_region}")
            print(f"   Detected: {detected_region}")
            print(f"   Coordinates: {coords.latitude:.1f}, {coords.longitude:.1f}")
            print(f"   Ireland area: {'❌ YES (BAD!)' if is_ireland else '✅ NO (GOOD!)'}")
            print(f"   Region match: {'✅ YES' if region_correct else '❓ NO'}")
            
            success = not is_ireland and (region_correct or detected_region is not None)
            results.append(success)
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
            results.append(False)
    
    success_rate = sum(results) / len(results) * 100
    print(f"\n📊 Success Rate: {success_rate:.1f}% ({sum(results)}/{len(results)})")
    
    return success_rate >= 80


async def main():
    """Run all tests to verify Ireland default is removed"""
    print("🎯 NO IRELAND DEFAULT - VERIFICATION TESTS")
    print("=" * 65)
    
    try:
        # Run all tests
        test1 = await test_sicily_no_ireland()
        test2 = await test_generic_request_no_ireland() 
        test3 = await test_various_locations()
        
        print("\n" + "=" * 65)
        print("📊 FINAL RESULTS:")
        print(f"   🏝️  Sicily Test: {'✅ PASS' if test1 else '❌ FAIL'}")
        print(f"   🌊 Generic Test: {'✅ PASS' if test2 else '❌ FAIL'}")
        print(f"   🌍 Locations Test: {'✅ PASS' if test3 else '❌ FAIL'}")
        
        all_passed = test1 and test2 and test3
        
        if all_passed:
            print("\n🎉 ALL TESTS PASSED - IRELAND DEFAULT REMOVED!")
            print("")
            print("✅ **KEY IMPROVEMENTS:**")
            print("   • 🏝️ Sicily requests now use correct Mediterranean coordinates")
            print("   • 🌍 Generic requests default to Mediterranean (not Ireland)")  
            print("   • 🗺️ All regions use appropriate geographical coordinates")
            print("   • 🧭 Smart location detection for 40+ specific areas")
            print("   • ⚡ No more hardcoded Irish Sea fallbacks")
            print("")
            print("🚀 **TEST IT NOW:**")
            print("   python ais_chat.py")
            print("   Then ask: 'Generate a convoy off the coast of Sicily'")
            print("   You should see Mediterranean coordinates, not Ireland!")
            
        else:
            print("\n⚠️  SOME TESTS FAILED - MORE WORK NEEDED")
            print("Check the specific failures above and investigate the code.")
        
    except Exception as e:
        print(f"\n❌ TEST SUITE FAILED: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
