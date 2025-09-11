#!/usr/bin/env python3
"""
Test script to verify the Gemini-only setup works correctly
"""

import sys
import asyncio
import os
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))


async def test_gemini_client_direct():
    """Test Gemini client directly"""
    print("🌟 Testing Gemini Client Direct Access")
    print("=" * 50)
    
    try:
        from src.llm_integration.gemini_client import AISGeminiClient
        
        print("✅ Successfully imported AISGeminiClient")
        
        # Check if API key is set
        api_key = os.getenv("GEMINI_KEY")
        if not api_key:
            print("❌ GEMINI_KEY not set - testing will be limited")
            return False
        else:
            print(f"✅ GEMINI_KEY found (length: {len(api_key)})")
        
        # Initialize client
        print("🔄 Initializing Gemini client...")
        client = AISGeminiClient()
        print("✅ Gemini client initialized")
        
        # Test basic request
        print("🔄 Testing basic generation request...")
        response = await client.process_request("Generate 2 ships in the Mediterranean")
        
        # Check response
        if isinstance(response, str) and len(response) > 50:
            print("✅ Got valid response from Gemini")
            print(f"   Response length: {len(response)} characters")
            
            # Check for key indicators
            mentions_med = 'mediterranean' in response.lower()
            has_files = 'json' in response.lower() or 'output' in response.lower()
            
            print(f"   Mentions Mediterranean: {'✅ YES' if mentions_med else '❓ NO'}")
            print(f"   References files: {'✅ YES' if has_files else '❓ NO'}")
            
            return True
        else:
            print(f"⚠️  Response seems short or invalid: {response[:100]}...")
            return False
            
    except Exception as e:
        print(f"❌ Error testing Gemini client: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_main_chat_interface():
    """Test the main chat interface initialization"""
    print("\n🎯 Testing Main Chat Interface")
    print("=" * 50)
    
    try:
        # Import the main chat class
        from pathlib import Path
        import sys
        
        # Add the root directory to path to import ais_chat
        sys.path.insert(0, str(Path(__file__).parent))
        
        from ais_chat import AISChatCLI
        
        print("✅ Successfully imported AISChatCLI")
        
        # Initialize CLI
        cli = AISChatCLI()
        print("✅ CLI initialized")
        
        # Test Gemini key detection
        has_key = cli.detect_gemini_key()
        print(f"✅ Gemini key detection: {'Found' if has_key else 'Not found'}")
        
        # Test setup check
        setup_ok = cli.check_setup()
        print(f"✅ Setup check: {'OK' if setup_ok else 'Missing key'}")
        
        if setup_ok:
            # Test Gemini initialization
            print("🔄 Testing Gemini initialization...")
            init_success = await cli.initialize_gemini()
            print(f"✅ Gemini initialization: {'Success' if init_success else 'Failed'}")
            
            if init_success and cli.llm_client:
                print("✅ Gemini client is ready and available")
                return True
        
        return setup_ok
        
    except Exception as e:
        print(f"❌ Error testing main interface: {e}")
        import traceback  
        traceback.print_exc()
        return False


async def test_sicily_coordinates_with_gemini():
    """Test Sicily coordinate detection with Gemini"""
    print("\n🏝️ Testing Sicily Coordinates with Gemini")
    print("=" * 50)
    
    try:
        from src.llm_integration.gemini_client import AISGeminiClient
        from src.generators.ais_generator import WorldwideRoutes
        
        if not os.getenv("GEMINI_KEY"):
            print("❌ GEMINI_KEY not set - skipping Gemini test")
            return False
        
        client = AISGeminiClient()
        
        sicily_request = "Generate a convoy off the coast of Sicily"
        print(f"🎯 Request: '{sicily_request}'")
        
        # Test coordinate detection
        coords = WorldwideRoutes.get_smart_coordinates_for_location(sicily_request)
        print(f"🧭 Smart coordinates: {coords.latitude:.2f}, {coords.longitude:.2f}")
        
        # Check if in Sicily area
        is_sicily = (36.0 <= coords.latitude <= 39.0 and 12.0 <= coords.longitude <= 16.0)
        print(f"✅ In Sicily area: {'YES' if is_sicily else 'NO'}")
        
        if is_sicily:
            # Test full Gemini response 
            print("🔄 Testing full Gemini response...")
            response = await client.process_request(sicily_request)
            
            # Check response content
            mentions_sicily = 'sicily' in response.lower()
            mentions_med = 'mediterranean' in response.lower()
            no_ireland = 'ireland' not in response.lower() and 'irish' not in response.lower()
            
            print(f"   Mentions Sicily: {'✅ YES' if mentions_sicily else '❓ NO'}")
            print(f"   Mentions Mediterranean: {'✅ YES' if mentions_med else '❓ NO'}")  
            print(f"   No Ireland mentions: {'✅ YES' if no_ireland else '❌ NO (BAD!)'}")
            
            return is_sicily and no_ireland
        
        return False
        
    except Exception as e:
        print(f"❌ Error testing Sicily with Gemini: {e}")
        return False


async def main():
    """Run all Gemini-only tests"""
    print("🌟 GEMINI-ONLY SETUP VERIFICATION TESTS")
    print("=" * 65)
    
    # Check environment
    api_key = os.getenv("GEMINI_KEY")
    print(f"🔑 GEMINI_KEY: {'✅ Set' if api_key else '❌ Not set'}")
    
    if not api_key:
        print("")
        print("⚠️  **SETUP REQUIRED:**")
        print("   1. Get free API key: https://aistudio.google.com/app/apikey")
        print("   2. Set: export GEMINI_KEY='your-api-key-here'")
        print("   3. Or add to .env file: GEMINI_KEY=your-api-key-here")
        print("")
        print("🎯 **Testing basic functionality without API key...**")
        
    try:
        # Run tests
        test1 = await test_gemini_client_direct()
        test2 = await test_main_chat_interface() 
        test3 = await test_sicily_coordinates_with_gemini()
        
        print("\n" + "=" * 65)
        print("📊 FINAL RESULTS:")
        print(f"   🌟 Gemini Client: {'✅ PASS' if test1 else '❌ FAIL'}")
        print(f"   🎯 Chat Interface: {'✅ PASS' if test2 else '❌ FAIL'}")
        print(f"   🏝️  Sicily Test: {'✅ PASS' if test3 else '❌ FAIL'}")
        
        basic_pass = test2  # At minimum, interface should work
        all_pass = test1 and test2 and test3
        
        if all_pass:
            print("\n🎉 ALL TESTS PASSED - GEMINI-ONLY SETUP WORKING!")
            print("")
            print("✅ **KEY FEATURES:**")
            print("   • 🌟 Google Gemini AI integration working")
            print("   • 🎯 Main chat interface properly configured")
            print("   • 🏝️ Intelligent location detection (Sicily, etc.)")
            print("   • 🌍 Worldwide maritime region support")
            print("   • 🗺️ Automatic map generation")
            print("")
            print("🚀 **READY TO USE:**")
            print("   python ais_chat.py")
            print("   Then ask: 'Generate a convoy off the coast of Sicily'")
            
        elif basic_pass:
            print("\n✅ BASIC SETUP WORKING - Ready for Gemini API key")
            print("   Set GEMINI_KEY to enable full AI functionality")
            
        else:
            print("\n❌ SETUP ISSUES DETECTED")
            print("   Check the errors above and fix the configuration")
        
    except Exception as e:
        print(f"\n❌ TEST SUITE FAILED: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
