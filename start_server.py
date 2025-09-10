#!/usr/bin/env python3
"""
Start the Vessel Track Generator MCP Server

This script starts the MCP server that can generate vessel tracks
based on natural language prompts.
"""

import asyncio
import logging
from mcp.server.stdio import stdio_server
from mcp_server_integration import MCPVesselTrackServer

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("vessel-track-server")

async def main():
    """Main entry point for the MCP server"""
    logger.info("Starting Vessel Track Generator MCP Server...")
    
    # Create the MCP server instance
    vessel_server = MCPVesselTrackServer()
    
    # Start the server using stdio transport
    async with stdio_server() as (read_stream, write_stream):
        await vessel_server.server.run(
            read_stream,
            write_stream,
            vessel_server.server.create_initialization_options()
        )

if __name__ == "__main__":
    asyncio.run(main())
