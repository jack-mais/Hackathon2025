"""
Gemini LLM Client - Free alternative to OpenAI
Uses Google's Gemini API with generous free tier
"""

import os
import json
import asyncio
from typing import Dict, List, Any, Optional
import google.generativeai as genai
from datetime import datetime

from ..mcp_integration.mcp_server import AISMCPServer


class AISGeminiClient:
    """Gemini-based LLM client for processing natural language requests"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GEMINI_KEY")
        if not self.api_key:
            raise ValueError("Gemini API key is required. Set GEMINI_KEY environment variable.")
        
        # Configure Gemini
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        
        self.mcp_server = AISMCPServer()
        self.conversation_history = []
        
        # System prompt for Gemini
        self.system_context = """You are an expert maritime AIS (Automatic Identification System) data generator assistant.

You help users generate realistic ship movement data for the Irish Sea region. You can:
1. Generate multiple ships with realistic routes in the Irish Sea
2. Create custom ships with specific types and routes  
3. List available ports and ship types
4. Save all generated data to JSON files for analysis

Available ports: Dublin, Holyhead, Liverpool, Belfast, Cork, Swansea, Isle of Man, Cardiff
Available ship types: PASSENGER (ferries), CARGO (container/bulk), FISHING (trawlers), PILOT_VESSEL (patrol/pilot), HIGH_SPEED_CRAFT (fast boats)

When users ask for ship generation, determine what tools to call based on their request:

TOOLS AVAILABLE:
1. generate_irish_sea_scenario - For general requests like "generate 3 ships"
   Parameters: num_ships, duration_hours, report_interval_minutes, scenario_name

2. generate_custom_ships - For specific ship requests like "create 1 cargo ship from Dublin to Liverpool"
   Parameters: ships[] (with ship_type, start_port, end_port), duration_hours, scenario_name

3. list_available_ports - To show available ports

4. get_ship_types - To show available ship types

Respond conversationally and always mention that data is saved to JSON files and can be visualized on maps.
"""

    async def process_request(self, user_message: str) -> str:
        """Process a user request and return response"""
        
        try:
            # Simple pattern matching to determine tool calls
            # This is a simplified approach compared to OpenAI's function calling
            tool_call = self._determine_tool_call(user_message.lower())
            
            if tool_call:
                tool_name, tool_args = tool_call
                print(f"🔧 Calling tool: {tool_name}")
                print(f"📝 Arguments: {tool_args}")
                
                # Call the MCP tool
                tool_result = await self.mcp_server.call_tool(tool_name, tool_args)
                
                # Generate response with tool result
                prompt = f"""
{self.system_context}

User request: {user_message}

Tool called: {tool_name}
Tool result: {json.dumps(tool_result, indent=2)}

Please provide a helpful response to the user explaining what was generated and where the files were saved. Be conversational and mention they can visualize the data with maps.
"""
                
                response = self.model.generate_content(prompt)
                return response.text
                
            else:
                # No tools needed, direct conversation
                prompt = f"""
{self.system_context}

User request: {user_message}

Please respond helpfully about AIS ship generation. If they're asking for information about capabilities, ports, or ship types, provide that information. If they want to generate ships, ask for clarification about what they need.
"""
                
                response = self.model.generate_content(prompt)
                return response.text
                
        except Exception as e:
            error_message = f"❌ Error processing request: {str(e)}"
            print(error_message)
            return error_message
    
    def _determine_tool_call(self, user_message: str) -> Optional[tuple]:
        """Simple pattern matching to determine what tool to call"""
        
        # Pattern matching for different requests
        if any(word in user_message for word in ['ports', 'available ports', 'what ports']):
            return ('list_available_ports', {})
        
        elif any(word in user_message for word in ['ship types', 'types', 'what ships', 'available ships']):
            return ('get_ship_types', {})
        
        elif any(word in user_message for word in ['generate', 'create', 'make']) and any(word in user_message for word in ['ship', 'ships']):
            # Extract number of ships
            import re
            numbers = re.findall(r'\d+', user_message)
            num_ships = int(numbers[0]) if numbers else 3
            
            # Check for specific routes
            ports = ['dublin', 'holyhead', 'liverpool', 'belfast', 'cork', 'swansea', 'cardiff']
            mentioned_ports = [port for port in ports if port in user_message]
            
            # Check for specific ship types
            ship_types = ['cargo', 'ferry', 'fishing', 'patrol', 'passenger', 'high-speed']
            mentioned_types = [ship_type for ship_type in ship_types if ship_type in user_message]
            
            # Extract duration if mentioned
            duration = 2.0  # default
            if 'hour' in user_message:
                hour_matches = re.findall(r'(\d+)\s*hour', user_message)
                if hour_matches:
                    duration = float(hour_matches[0])
            
            if len(mentioned_ports) >= 2 or mentioned_types:
                # Custom ships request
                ships = []
                if 'cargo' in user_message and len(mentioned_ports) >= 2:
                    ships.append({
                        'ship_type': 'CARGO',
                        'ship_name': 'CUSTOM_CARGO',
                        'start_port': mentioned_ports[0].upper(),
                        'end_port': mentioned_ports[1].upper()
                    })
                elif 'ferry' in user_message or 'passenger' in user_message:
                    ships.append({
                        'ship_type': 'PASSENGER',
                        'ship_name': 'CUSTOM_FERRY', 
                        'start_port': mentioned_ports[0].upper() if mentioned_ports else 'DUBLIN',
                        'end_port': mentioned_ports[1].upper() if len(mentioned_ports) > 1 else 'HOLYHEAD'
                    })
                
                if ships:
                    return ('generate_custom_ships', {
                        'ships': ships,
                        'duration_hours': duration,
                        'scenario_name': 'custom_gemini_scenario'
                    })
            
            # General scenario request
            return ('generate_irish_sea_scenario', {
                'num_ships': min(num_ships, 10),
                'duration_hours': duration,
                'scenario_name': f'gemini_scenario_{num_ships}_ships'
            })
        
        return None
    
    def clear_conversation(self):
        """Clear conversation history"""
        self.conversation_history = []
    
    async def get_available_capabilities(self) -> str:
        """Get information about capabilities"""
        return """
🚢 **AIS Ship Data Generator Capabilities (Gemini-Powered)**

**What I can generate:**
• Multiple ships (1-10) with realistic Irish Sea routes
• Different ship types: Passenger ferries, Cargo ships, Fishing vessels, Patrol boats, High-speed craft
• Custom routes between major ports: Dublin, Holyhead, Liverpool, Belfast, Cork, Swansea, etc.
• Realistic movement patterns: Ferry routes, cargo lanes, fishing circles, patrol patterns

**Example requests:**
• "Generate 3 ships in the Irish Sea"
• "Create 2 cargo ships from Dublin to Liverpool and 1 ferry from Dublin to Holyhead"
• "I need a fishing vessel and 2 ferries for a 4-hour simulation"
• "Generate AIS NMEA data for ships roaming about the Irish sea"

**Powered by Google Gemini** - Free API with generous limits!

**Output:**
• JSON files with detailed AIS position reports
• Interactive map visualization available 
• NMEA format data for marine systems
• Realistic timestamps, speeds, and navigation status

Just tell me what kind of maritime scenario you'd like to create!
        """


# Test function
async def test_gemini_integration():
    """Test Gemini integration"""
    
    api_key = os.getenv("GEMINI_KEY")
    if not api_key:
        print("❌ Please set GEMINI_KEY environment variable")
        print("💡 Get your free API key from: https://makersuite.google.com/app/apikey")
        return False
    
    try:
        client = AISGeminiClient(api_key)
        
        print("🤖 Testing Gemini integration...")
        
        capabilities = await client.get_available_capabilities()
        print("✅ Gemini client initialized successfully")
        
        response = await client.process_request("What ship types can you generate?")
        print(f"🗣️  Gemini Response: {response[:200]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing Gemini integration: {e}")
        return False


if __name__ == "__main__":
    asyncio.run(test_gemini_integration())
