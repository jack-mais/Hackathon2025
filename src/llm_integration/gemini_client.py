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

You help users generate realistic ship movement data for any maritime region worldwide. You can:
1. Generate multiple ships with realistic routes in specified regions or worldwide
2. Create custom ships with specific types and routes between any ports
3. List available ports and ship types
4. Save all generated data to JSON files for analysis

You support a wide range of ports worldwide including major commercial ports, ferry terminals, and fishing harbors across all continents. Available ship types: PASSENGER (ferries), CARGO (container/bulk), FISHING (trawlers), PILOT_VESSEL (patrol/pilot), HIGH_SPEED_CRAFT (fast boats).

When users ask for ship generation, determine what tools to call based on their request:

TOOLS AVAILABLE:
1. generate_maritime_scenario - For general requests (defaults to Mediterranean region)
   Parameters: num_ships, duration_hours, report_interval_minutes, scenario_name

2. generate_custom_ships - For specific ship requests with custom routes anywhere worldwide
   Parameters: ships[] (with ship_type, start_port, end_port), duration_hours, scenario_name

3. list_available_ports - To show available ports

4. get_ship_types - To show available ship types

You can handle requests for any maritime region including Mediterranean, North Sea, Atlantic, Pacific, Indian Ocean, Caribbean, Baltic Sea, and many others. Users can specify regions, ports, or even exact coordinates. Ask clarifying questions if you need more specific location information.

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
        """Advanced pattern matching for sophisticated scenario generation"""
        
        user_lower = user_message.lower().strip()
        
        # Handle information queries first
        if any(word in user_lower for word in ['ports', 'available ports', 'what ports', 'list ports']):
            return ('list_available_ports', {})
        
        elif any(word in user_lower for word in ['ship types', 'types', 'what ships', 'available ships', 'kinds of ships']):
            return ('get_ship_types', {})
        
        elif any(word in user_lower for word in ['generate', 'create', 'make', 'simulate', 'show me']) and any(word in user_lower for word in ['ship', 'ships', 'vessel', 'boat', 'fleet']):
            # Use advanced scenario parsing
            scenario_details = self._parse_sophisticated_scenario(user_message)
            
            # Determine best tool based on parsed details
            if scenario_details['custom_routes']:
                return ('generate_custom_ships', {
                    'ships': scenario_details['custom_routes'],
                    'duration_hours': scenario_details['duration'],
                    'scenario_name': scenario_details['scenario_name']
                })
            elif scenario_details['region']:
                return ('generate_maritime_scenario', {
                    'num_ships': scenario_details['num_ships'],
                    'region': scenario_details['region'],
                    'duration_hours': scenario_details['duration'],
                    'scenario_name': scenario_details['scenario_name'],
                    'location_hint': user_message  # Pass original message for location parsing
                })
            else:
                return ('generate_maritime_scenario', {
                    'num_ships': scenario_details['num_ships'],
                    'region': 'mediterranean',
                    'duration_hours': scenario_details['duration'],
                    'scenario_name': scenario_details['scenario_name']
                })
        
        return None
    
    def _parse_sophisticated_scenario(self, user_message: str) -> Dict[str, Any]:
        """Parse complex maritime scenarios from natural language"""
        import re
        import random
        
        user_lower = user_message.lower().strip()
        
        scenario = {
            'num_ships': 3,
            'duration': 2.0,
            'region': 'mediterranean',
            'ship_types': [],
            'custom_routes': [],
            'scenario_name': f'gemini_scenario_{random.randint(1000, 9999)}',
            'scenario_type': None
        }
        
        # Advanced ship count extraction
        ship_patterns = [
            r'(\d+)\s*ships?', r'(\d+)\s*vessels?', r'(\d+)\s*boats?',
            r'fleet\s+of\s+(\d+)', r'(\d+)[-\s]*ship', r'(\d+)\s*craft',
            r'group\s+of\s+(\d+)', r'(\d+)\s*units?', r'(\d+)\s*maritime'
        ]
        
        for pattern in ship_patterns:
            matches = re.findall(pattern, user_lower)
            if matches:
                scenario['num_ships'] = min(int(matches[0]), 25)  # Generous cap
                break
        
        # Comprehensive duration extraction
        if re.search(r'(\d+(?:\.\d+)?)\s*minutes?', user_lower):
            minutes = re.findall(r'(\d+(?:\.\d+)?)\s*minutes?', user_lower)
            scenario['duration'] = float(minutes[0]) / 60
        elif re.search(r'(\d+(?:\.\d+)?)\s*hours?', user_lower):
            hours = re.findall(r'(\d+(?:\.\d+)?)\s*hours?', user_lower)
            scenario['duration'] = float(hours[0])
        elif re.search(r'(\d+(?:\.\d+)?)\s*days?', user_lower):
            days = re.findall(r'(\d+(?:\.\d+)?)\s*days?', user_lower)
            scenario['duration'] = float(days[0]) * 24
        
        # Sophisticated region detection with specific geographical references
        region_mapping = {
            'mediterranean': ['mediterranean', 'med', 'italy', 'spain', 'greece', 'turkish', 'malta',
                            'sicily', 'coast of sicily', 'off sicily', 'italian coast', 'spanish coast',
                            'french riviera', 'greek islands', 'turkish coast', 'corsica', 'sardinia',
                            'balearic', 'crete', 'rhodes', 'gibraltar', 'tyrrhenian'],
            'north_sea': ['north sea', 'norwegian', 'danish', 'dutch', 'uk waters', 'dogger bank',
                         'norwegian waters', 'danish waters', 'dutch coast', 'german bight', 'shetland'],
            'baltic_sea': ['baltic', 'swedish', 'finnish', 'polish', 'estonian', 'latvian',
                          'stockholm archipelago', 'finnish waters', 'gulf of bothnia'],
            'caribbean': ['caribbean', 'west indies', 'bahamas', 'jamaica', 'cuba', 'tropical',
                         'lesser antilles', 'greater antilles', 'barbados', 'puerto rico'],
            'pacific': ['pacific', 'transpacific', 'japan', 'china', 'korean', 'hawaii', 'california',
                       'japan waters', 'philippines', 'pacific coast', 'california coast'],
            'atlantic': ['atlantic', 'transatlantic', 'oceanic', 'north atlantic', 'south atlantic',
                        'azores', 'canary islands', 'bay of biscay', 'newfoundland'],
            'indian_ocean': ['indian ocean', 'indian', 'sri lanka', 'maldives', 'madagascar'],
            'english_channel': ['english channel', 'channel', 'dover strait', 'la manche', 'dover'],
            'persian_gulf': ['persian gulf', 'arabian gulf', 'gulf states', 'middle east waters'],
            'red_sea': ['red sea', 'suez canal', 'egyptian', 'saudi waters'],
            'arctic': ['arctic', 'polar', 'greenland', 'alaskan', 'northwest passage'],
            'black_sea': ['black sea', 'romanian', 'bulgarian', 'ukrainian'],
            'asia': ['asian', 'southeast asia', 'far east', 'oriental'],
            'europe': ['european', 'continental', 'scandinavian']
        }
        
        for region, keywords in region_mapping.items():
            if any(keyword in user_lower for keyword in keywords):
                scenario['region'] = region
                break
        
        # Advanced scenario type detection
        scenario_types = {
            'convoy_escort': ['convoy', 'escort', 'formation', 'group sailing', 'protected transit'],
            'cruise_liner': ['cruise', 'luxury', 'tourist', 'vacation', 'leisure sailing'],
            'emergency_response': ['emergency', 'rescue', 'distress', 'mayday', 'search and rescue', 'sar'],
            'military_ops': ['military', 'naval', 'defense', 'patrol', 'exercise', 'maneuvers'],
            'commercial_shipping': ['cargo', 'container', 'bulk', 'freight', 'trade route', 'shipping'],
            'fishing_operation': ['fishing', 'trawling', 'commercial fishing', 'fleet fishing'],
            'port_traffic': ['port', 'harbor', 'terminal', 'docking', 'berthing', 'approach'],
            'weather_routing': ['storm', 'weather', 'hurricane', 'rough seas', 'avoiding weather'],
            'offshore_support': ['oil rig', 'offshore', 'platform', 'supply vessel', 'drilling'],
            'racing_regatta': ['race', 'sailing race', 'regatta', 'yacht race', 'competition']
        }
        
        for scenario_type, keywords in scenario_types.items():
            if any(keyword in user_lower for keyword in keywords):
                scenario['scenario_type'] = scenario_type
                break
        
        # Enhanced ship type recognition
        ship_type_mapping = {
            'CARGO': ['cargo', 'container', 'freight', 'bulk carrier', 'tanker', 'oil tanker', 'lng'],
            'PASSENGER': ['passenger', 'ferry', 'cruise', 'liner', 'tourist vessel'],
            'FISHING': ['fishing', 'trawler', 'seiner', 'longline', 'crab vessel', 'shrimp boat'],
            'PILOT_VESSEL': ['pilot', 'patrol', 'coast guard', 'border patrol', 'police vessel'],
            'HIGH_SPEED_CRAFT': ['fast', 'speed', 'racing', 'hydrofoil', 'catamaran', 'racing yacht'],
            'SEARCH_RESCUE': ['rescue', 'lifeboat', 'sar vessel', 'emergency boat'],
            'LAW_ENFORCEMENT': ['naval', 'warship', 'destroyer', 'frigate', 'military vessel'],
            'TUG': ['tugboat', 'tug', 'harbor assist', 'towing vessel'],
            'SAILING': ['sailing', 'yacht', 'sailboat', 'wind-powered']
        }
        
        for ship_type, keywords in ship_type_mapping.items():
            if any(keyword in user_lower for keyword in keywords):
                scenario['ship_types'].append(ship_type)
        
        # Parse specific port-to-port routes
        port_database = {
            'singapore': 'SINGAPORE', 'shanghai': 'SHANGHAI', 'hong kong': 'HONG_KONG',
            'rotterdam': 'ROTTERDAM', 'hamburg': 'HAMBURG', 'antwerp': 'ANTWERP',
            'dubai': 'DUBAI', 'mumbai': 'MUMBAI', 'tokyo': 'TOKYO',
            'new york': 'NEW_YORK', 'los angeles': 'LOS_ANGELES', 'miami': 'MIAMI',
            'dublin': 'DUBLIN', 'liverpool': 'LIVERPOOL', 'holyhead': 'HOLYHEAD',
            'barcelona': 'BARCELONA', 'marseille': 'MARSEILLE', 'venice': 'VENICE',
            'oslo': 'OSLO', 'copenhagen': 'COPENHAGEN', 'stockholm': 'STOCKHOLM',
            'naples': 'NAPLES', 'athens': 'ATHENS', 'istanbul': 'ISTANBUL'
        }
        
        identified_ports = []
        for port_name, port_code in port_database.items():
            if port_name in user_lower or port_name.replace(' ', '') in user_lower:
                identified_ports.append(port_code)
        
        # Create custom routes for specific port pairs
        if len(identified_ports) >= 2:
            ship_type = scenario['ship_types'][0] if scenario['ship_types'] else 'PASSENGER'
            scenario['custom_routes'] = [{
                'ship_type': ship_type,
                'ship_name': f'{ship_type}_ROUTE_{random.randint(100, 999)}',
                'start_port': identified_ports[0],
                'end_port': identified_ports[1]
            }]
        
        # Smart scenario naming
        if scenario['custom_routes']:
            start = scenario['custom_routes'][0]['start_port']
            end = scenario['custom_routes'][0]['end_port']
            scenario['scenario_name'] = f'route_{start}_to_{end}'
        elif scenario['scenario_type']:
            scenario['scenario_name'] = f"{scenario['scenario_type']}_scenario"
        elif scenario['region'] != 'mediterranean':
            scenario['scenario_name'] = f"{scenario['region']}_scenario"
        
        return scenario
    
    def clear_conversation(self):
        """Clear conversation history"""
        self.conversation_history = []
    
    async def get_available_capabilities(self) -> str:
        """Get information about capabilities"""
        return """
🚢 **AIS Ship Data Generator Capabilities (Gemini-Powered)**

**What I can generate:**
• Multiple ships (1-10) with realistic routes in any maritime region worldwide
• Different ship types: Passenger ferries, Cargo ships, Fishing vessels, Patrol boats, High-speed craft
• Custom routes between major ports: Dublin, Holyhead, Liverpool, Belfast, Cork, Swansea, etc.
• Realistic movement patterns: Ferry routes, cargo lanes, fishing circles, patrol patterns

**Example requests:**
• "Generate 3 ships in the Mediterranean"
• "Create 2 cargo ships from Dublin to Liverpool and 1 ferry from Dublin to Holyhead"
• "I need a fishing vessel and 2 ferries for a 4-hour simulation"
• "Generate AIS NMEA data for ships roaming about the Mediterranean"

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
