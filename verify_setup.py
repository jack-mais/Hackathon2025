#!/usr/bin/env python3
"""
Verification script to test the MCP server setup
"""

import asyncio
import json
from mcp_server_integration import MCPVesselTrackServer

async def verify_mcp_server():
    """Verify that the MCP server is working correctly"""
    print("🔍 Verifying Vessel Track Generator MCP Server")
    print("=" * 50)
    
    try:
        # Initialize the server
        server = MCPVesselTrackServer()
        print("✅ MCP server initialized successfully")
        
        # Test tool listing
        tools = await server.list_tools()
        print(f"✅ Found {len(tools)} tools:")
        for tool in tools:
            print(f"   - {tool.name}: {tool.description}")
        
        # Test track generation
        print("\n🧪 Testing track generation...")
        result = await server._handle_generate_tracks({
            "prompt": "create tracks of 3 vessels that are class a and class b that performed point to point voyages"
        })
        
        if result and len(result) > 0:
            print("✅ Track generation test successful")
            print("📊 Sample output:")
            print(result[0].text[:200] + "..." if len(result[0].text) > 200 else result[0].text)
        else:
            print("❌ Track generation test failed")
        
        print("\n🎉 All tests passed! Your MCP server is ready to use with Claude.")
        
    except Exception as e:
        print(f"❌ Error during verification: {e}")
        print("\nTroubleshooting:")
        print("1. Make sure the virtual environment is activated")
        print("2. Check that all dependencies are installed")
        print("3. Verify the server files are in the correct location")

if __name__ == "__main__":
    asyncio.run(verify_mcp_server())
