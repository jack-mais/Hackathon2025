"""
Demo LLM Client - No API keys required!
Perfect for hackathon presentations and demos
"""

import asyncio
import random
import re
from typing import Dict, List, Any, Optional
from datetime import datetime

from ..mcp_integration.mcp_server import AISMCPServer


class AISDemo:
    """Demo client that simulates LLM behavior without any API keys"""
    
    def __init__(self):
        self.mcp_server = AISMCPServer()
        self.conversation_history = []
        
        # Pre-defined responses for common queries
        self.response_templates = {
            'greeting': [
                "Hello! I'm your maritime AIS data generation assistant. I can create realistic ship movement data for the Irish Sea region.",
                "Hi there! Ready to generate some ship data? I can create multiple vessels with realistic routes and movements.",
                "Welcome to the AIS Generator! Tell me what kind of ships you'd like me to create."
            ],
            'capabilities': [
                "I can generate multiple ships with different types (passenger ferries, cargo ships, fishing vessels, patrol boats, and high-speed craft) across the Irish Sea region.",
                "My capabilities include creating realistic ship routes between major ports like Dublin, Holyhead, Liverpool, Belfast, Cork, and Swansea, with proper AIS tracking data.",
                "I specialize in maritime data generation - I can simulate ship movements, create realistic timing and speed profiles, and output data in JSON and NMEA formats."
            ],
            'ports': [
                "The available ports in our Irish Sea region include: Dublin, Holyhead, Liverpool, Belfast, Cork, Swansea, Isle of Man, and Cardiff.",
                "I have 8 major ports configured: Dublin (Ireland), Holyhead (Wales), Liverpool (England), Belfast (Northern Ireland), Cork (Ireland), Swansea (Wales), Isle of Man, and Cardiff (Wales).",
                "Our port network covers the entire Irish Sea region with major commercial and ferry terminals."
            ],
            'ship_types': [
                "I can generate 5 different ship types: PASSENGER ferries (12-18 knots), CARGO ships (8-12 knots), FISHING vessels (6-10 knots), PILOT_VESSEL patrol boats (15-25 knots), and HIGH_SPEED_CRAFT (20-40 knots).",
                "Available ship types include passenger ferries for regular routes, cargo ships for commercial transport, fishing vessels with circular movement patterns, pilot vessels for harbor operations, and high-speed craft for express services.",
                "Each ship type has realistic characteristics - ferries follow scheduled routes, cargo ships use shipping lanes, fishing boats work in circular patterns, and patrol vessels have back-and-forth movements."
            ]
        }
    
    async def process_request(self, user_message: str) -> str:
        """Process user request with pattern matching and tool calls"""
        
        user_lower = user_message.lower().strip()
        
        # Handle greetings
        if any(word in user_lower for word in ['hello', 'hi', 'hey', 'start']):
            return random.choice(self.response_templates['greeting'])
        
        # Handle capability queries
        if any(word in user_lower for word in ['what can you do', 'capabilities', 'help', 'what do you do']):
            return random.choice(self.response_templates['capabilities'])
        
        # Handle port queries
        if any(word in user_lower for word in ['ports', 'available ports', 'what ports', 'list ports']):
            print("🔧 Calling tool: list_available_ports")
            result = await self.mcp_server.call_tool("list_available_ports", {})
            if result["success"]:
                ports = list(result["ports"].keys())
                return f"✅ I have access to {len(ports)} ports in the Irish Sea region: {', '.join(ports)}. Each port has specific coordinates and can serve as start or end points for ship routes."
            else:
                return random.choice(self.response_templates['ports'])
        
        # Handle ship type queries
        if any(word in user_lower for word in ['ship types', 'types of ships', 'what ships', 'available ships', 'kinds of ships']):
            print("🔧 Calling tool: get_ship_types")
            result = await self.mcp_server.call_tool("get_ship_types", {})
            if result["success"]:
                ship_types = list(result["ship_types"].keys())
                return f"✅ I can generate {len(ship_types)} different ship types: {', '.join(ship_types)}. Each type has realistic speed profiles and movement patterns appropriate for their maritime operations."
            else:
                return random.choice(self.response_templates['ship_types'])
        
        # Handle generation requests
        if any(word in user_lower for word in ['generate', 'create', 'make']) and any(word in user_lower for word in ['ship', 'ships', 'vessel', 'vessels']):
            return await self._handle_generation_request(user_message)
        
        # Handle examples and demos
        if any(word in user_lower for word in ['example', 'demo', 'sample', 'show me']):
            print("🔧 Calling tool: generate_irish_sea_scenario (demo)")
            result = await self.mcp_server.call_tool("generate_irish_sea_scenario", {
                "num_ships": 3,
                "duration_hours": 1.5,
                "scenario_name": "demo_scenario"
            })
            
            if result["success"]:
                ships_summary = []
                for ship in result["ships"]:
                    ships_summary.append(f"• {ship['name']} ({ship['type']}) - {ship['speed_knots']} knots")
                
                return f"""✅ **Demo Generated Successfully!**

I've created {result['ships_generated']} ships for demonstration:
{chr(10).join(ships_summary)}

📁 **Data saved to:** `{result['saved_files']['json']}`
🗺️  **To visualize:** Run `python map_multi_viewer.py`
⏱️  **Simulation:** {result['duration_hours']} hours of movement data
📊 **Total reports:** {sum(ship['total_reports'] for ship in result['ships'])} position updates

This shows realistic AIS tracking data with proper timestamps, coordinates, speeds, and navigation status for each vessel!"""
            else:
                return f"❌ Demo generation failed: {result.get('error', 'Unknown error')}"
        
        # Fallback conversational responses
        return self._generate_conversational_response(user_message)
    
    async def _handle_generation_request(self, user_message: str) -> str:
        """Handle ship generation requests with parameter extraction"""
        
        # Extract number of ships
        import re
        numbers = re.findall(r'\d+', user_message)
        num_ships = int(numbers[0]) if numbers else random.randint(2, 4)
        num_ships = min(num_ships, 10)  # Cap at 10
        
        # Extract duration
        duration = 2.0
        if 'hour' in user_message:
            hour_matches = re.findall(r'(\d+)\s*hour', user_message)
            if hour_matches:
                duration = float(hour_matches[0])
        
        # Check for specific ports or routes
        ports = ['dublin', 'holyhead', 'liverpool', 'belfast', 'cork', 'swansea', 'cardiff']
        mentioned_ports = [port for port in ports if port in user_message.lower()]
        
        # Check for specific ship types
        ship_type_mapping = {
            'cargo': 'CARGO',
            'ferry': 'PASSENGER', 
            'passenger': 'PASSENGER',
            'fishing': 'FISHING',
            'patrol': 'PILOT_VESSEL',
            'pilot': 'PILOT_VESSEL',
            'fast': 'HIGH_SPEED_CRAFT',
            'high-speed': 'HIGH_SPEED_CRAFT'
        }
        
        mentioned_types = []
        for word, ship_type in ship_type_mapping.items():
            if word in user_message.lower():
                mentioned_types.append(ship_type)
        
        # Determine if custom or general scenario
        if len(mentioned_ports) >= 2 or mentioned_types:
            # Custom ship generation
            ships = []
            if mentioned_types and len(mentioned_ports) >= 2:
                ships.append({
                    'ship_type': mentioned_types[0],
                    'ship_name': f'CUSTOM_{mentioned_types[0]}',
                    'start_port': mentioned_ports[0].upper(),
                    'end_port': mentioned_ports[1].upper()
                })
            elif len(mentioned_ports) >= 2:
                ships.append({
                    'ship_type': 'PASSENGER',
                    'ship_name': 'CUSTOM_FERRY',
                    'start_port': mentioned_ports[0].upper(),
                    'end_port': mentioned_ports[1].upper()
                })
            
            if ships:
                print(f"🔧 Calling tool: generate_custom_ships")
                result = await self.mcp_server.call_tool("generate_custom_ships", {
                    'ships': ships,
                    'duration_hours': duration,
                    'scenario_name': 'demo_custom_scenario'
                })
            else:
                # Fallback to general scenario
                print(f"🔧 Calling tool: generate_irish_sea_scenario")
                result = await self.mcp_server.call_tool("generate_irish_sea_scenario", {
                    "num_ships": num_ships,
                    "duration_hours": duration,
                    "scenario_name": "demo_irish_sea_scenario"
                })
        else:
            # General Irish Sea scenario
            print(f"🔧 Calling tool: generate_irish_sea_scenario")
            result = await self.mcp_server.call_tool("generate_irish_sea_scenario", {
                "num_ships": num_ships,
                "duration_hours": duration,
                "scenario_name": "demo_irish_sea_scenario"
            })
        
        if result["success"]:
            ships_summary = []
            for ship in result["ships"]:
                ships_summary.append(f"• {ship['name']} ({ship['type']}) - {ship['speed_knots']} knots, {ship['total_reports']} reports")
            
            return f"""✅ **Ships Generated Successfully!**

I've created {result['ships_generated']} ships for your scenario:
{chr(10).join(ships_summary)}

📁 **Data saved to:** `{result['saved_files']['json']}`
🗺️  **To visualize:** Run `python map_multi_viewer.py`
⏱️  **Simulation duration:** {result['duration_hours']} hours
📡 **Report interval:** Every 5 minutes
🌊 **Area:** Irish Sea region

The generated data includes realistic AIS position reports with proper maritime timestamps, navigation status, speed over ground, course over ground, and vessel characteristics. Perfect for testing maritime systems or data analysis!"""
        else:
            return f"❌ Generation failed: {result.get('error', 'Unknown error occurred')}"
    
    def _generate_conversational_response(self, user_message: str) -> str:
        """Generate conversational responses for unmatched queries"""
        
        responses = [
            "I'm specialized in generating AIS maritime data. You can ask me to generate ships, list available ports, or show ship types. What would you like to create?",
            "I can help you create realistic ship movement data for the Irish Sea region. Try asking me to 'generate 3 ships' or 'show me available ports'.",
            "As a maritime AIS assistant, I can create ships with realistic routes and movement patterns. What kind of vessel scenario would you like me to generate?",
            "I'm here to help with ship data generation! You can request specific numbers of ships, certain routes, or ask about my capabilities. What interests you?",
            "My expertise is in creating realistic maritime AIS tracking data. I can generate multiple ships with different types and routes. What scenario would you like to explore?"
        ]
        
        return random.choice(responses)
    
    def clear_conversation(self):
        """Clear conversation history"""
        self.conversation_history = []
    
    async def get_available_capabilities(self) -> str:
        """Get capabilities information"""
        return """
🚢 **AIS Ship Data Generator - DEMO MODE** (No API Keys Required!)

**What I can generate:**
• Multiple ships (1-10) with realistic Irish Sea routes
• Different ship types: Passenger ferries, Cargo ships, Fishing vessels, Patrol boats, High-speed craft  
• Custom routes between major ports: Dublin, Holyhead, Liverpool, Belfast, Cork, Swansea, etc.
• Realistic movement patterns: Ferry routes, cargo lanes, fishing circles, patrol patterns

**Example requests:**
• "Generate 3 ships in the Irish Sea"
• "Create 2 cargo ships from Dublin to Liverpool"
• "Show me an example"
• "What ports are available?"

**Demo Features:**
✅ **No API costs** - Works completely offline
✅ **Instant responses** - No network delays
✅ **Full functionality** - Real ship generation
✅ **Perfect for demos** - Reliable and fast

**Output:**
• JSON files with detailed AIS position reports
• Interactive map visualization available
• NMEA format data for marine systems  
• Realistic timestamps, speeds, and navigation status

Just tell me what kind of maritime scenario you'd like to create!
        """


# Test function
async def test_demo_client():
    """Test the demo client"""
    print("🚢 Testing Demo Client (No API Keys Required)")
    print("=" * 50)
    
    client = AISDemo()
    
    test_queries = [
        "Hello",
        "What can you do?",
        "What ports are available?", 
        "Generate 3 ships",
        "Show me an example"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{i}. Testing: '{query}'")
        response = await client.process_request(query)
        print(f"✅ Response: {response[:100]}...")
    
    print("\n🎉 Demo client test completed!")


if __name__ == "__main__":
    asyncio.run(test_demo_client())
