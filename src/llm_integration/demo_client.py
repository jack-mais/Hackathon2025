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
                "Hello! I'm your maritime AIS data generation assistant. I can create realistic ship movement data for any maritime region worldwide.",
                "Hi there! Ready to generate some ship data? I can create multiple vessels with realistic routes and movements anywhere on Earth.",
                "Welcome to the AIS Generator! Tell me what kind of ships and which maritime region you'd like me to create."
            ],
            'capabilities': [
                "I can generate multiple ships with different types (passenger ferries, cargo ships, fishing vessels, patrol boats, and high-speed craft) in any maritime region worldwide.",
                "My capabilities include creating realistic ship routes between any major ports worldwide, with proper AIS tracking data for regions like Mediterranean, North Sea, Pacific, Atlantic, and more.",
                "I specialize in maritime data generation worldwide - I can simulate ship movements in any ocean or sea, create realistic timing and speed profiles, and output data in JSON and NMEA formats."
            ],
            'ports': [
                "I have access to major ports worldwide including commercial harbors, ferry terminals, and fishing ports across all continents and maritime regions.",
                "My port database includes thousands of locations from major shipping hubs like Shanghai, Rotterdam, Singapore to regional ports in Mediterranean, Caribbean, Baltic Sea, and beyond.",
                "I can work with any maritime region - just specify the area, ports, or even coordinates you're interested in."
            ],
            'ship_types': [
                "I can generate 5 different ship types: PASSENGER ferries (12-18 knots), CARGO ships (8-12 knots), FISHING vessels (6-10 knots), PILOT_VESSEL patrol boats (15-25 knots), and HIGH_SPEED_CRAFT (20-40 knots).",
                "Available ship types include passenger ferries for regular routes, cargo ships for commercial transport, fishing vessels with circular movement patterns, pilot vessels for harbor operations, and high-speed craft for express services.",
                "Each ship type has realistic characteristics - ferries follow scheduled routes, cargo ships use shipping lanes, fishing boats work in circular patterns, and patrol vessels have back-and-forth movements. All work in any maritime region worldwide."
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
                
                # Generate output message based on available files
                files_info = []
                if 'json' in result['saved_files']:
                    files_info.append(f"📁 JSON data: `{result['saved_files']['json']}`")
                if 'map' in result['saved_files']:
                    files_info.append(f"🗺️ Interactive map: `{result['saved_files']['map']}`")
                
                files_text = "\n".join(files_info) if files_info else "📁 Files saved successfully"
                
                return f"""✅ **Demo Generated Successfully!**

I've created {result['ships_generated']} ships for demonstration:
{chr(10).join(ships_summary)}

{files_text}

⏱️  **Simulation:** {result['duration_hours']} hours of movement data
📊 **Total reports:** {sum(ship['total_reports'] for ship in result['ships'])} position updates

🎯 **Both JSON data and interactive HTML map created automatically!** 
Open the HTML file in your browser to see ships moving on the map with detailed info popups."""
            else:
                return f"❌ Demo generation failed: {result.get('error', 'Unknown error')}"
        
        # Fallback conversational responses
        return self._generate_conversational_response(user_message)
    
    async def _handle_generation_request(self, user_message: str) -> str:
        """Handle sophisticated ship generation requests with advanced parameter extraction"""
        
        # Parse the complex scenario request
        scenario_details = self._parse_advanced_scenario(user_message)
        
        # Determine the best tool and parameters
        tool_name, params = self._determine_generation_strategy(scenario_details)
        
        print(f"🔧 Calling tool: {tool_name}")
        print(f"📝 Parsed scenario: {scenario_details['description']}")
        
        # Execute the generation
        result = await self.mcp_server.call_tool(tool_name, params)
        
        if result["success"]:
            ships_summary = []
            for ship in result["ships"]:
                ships_summary.append(f"• {ship['name']} ({ship['type']}) - {ship['speed_knots']} knots, {ship['total_reports']} reports")
            
            # Generate output message based on available files
            files_info = []
            if 'json' in result['saved_files']:
                files_info.append(f"📁 JSON data: `{result['saved_files']['json']}`")
            if 'map' in result['saved_files']:
                files_info.append(f"🗺️ Interactive map: `{result['saved_files']['map']}`")
            
            files_text = "\n".join(files_info) if files_info else "📁 Files saved successfully"
            
            return f"""✅ **Ships Generated Successfully!**

I've created {result['ships_generated']} ships for your scenario:
{chr(10).join(ships_summary)}

{files_text}

⏱️  **Simulation duration:** {result['duration_hours']} hours
📡 **Report interval:** Every 5 minutes
🌊 **Area:** {result.get('region', 'Maritime region')}

🎯 **Both JSON data and interactive HTML map created automatically!** 
The generated data includes realistic AIS position reports with proper maritime timestamps, navigation status, speed over ground, course over ground, and vessel characteristics. Open the HTML file in your browser to see ships moving on the interactive map!"""
        else:
            return f"❌ Generation failed: {result.get('error', 'Unknown error occurred')}"
    
    def _parse_advanced_scenario(self, user_message: str) -> Dict[str, Any]:
        """Parse sophisticated natural language scenario requests"""
        import re
        
        user_lower = user_message.lower().strip()
        
        scenario_details = {
            'num_ships': 3,
            'duration': 2.0,
            'region': None,
            'ship_types': [],
            'custom_ships': [],
            'coordinates': [],
            'scenario_type': None,
            'special_params': {},
            'scenario_name': f'demo_scenario_{random.randint(1000, 9999)}',
            'description': 'Basic maritime scenario',
            'original_message': user_message  # Store original message for location parsing
        }
        
        # Enhanced ship count extraction
        ship_count_patterns = [
            r'(\d+)\s*ships?',
            r'(\d+)\s*vessels?',
            r'(\d+)\s*boats?',
            r'fleet\s+of\s+(\d+)',
            r'(\d+)[-\s]*ship',
            r'(\d+)\s*craft',
            r'group\s+of\s+(\d+)',
            r'(\d+)\s*units?'
        ]
        
        for pattern in ship_count_patterns:
            matches = re.findall(pattern, user_lower)
            if matches:
                scenario_details['num_ships'] = min(int(matches[0]), 20)  # Increased cap
                break
        
        # Enhanced duration extraction
        if 'minute' in user_lower:
            minutes = re.findall(r'(\d+(?:\.\d+)?)\s*minutes?', user_lower)
            if minutes:
                scenario_details['duration'] = float(minutes[0]) / 60
        elif 'hour' in user_lower:
            hours = re.findall(r'(\d+(?:\.\d+)?)\s*hours?', user_lower)
            if hours:
                scenario_details['duration'] = float(hours[0])
        elif 'day' in user_lower:
            days = re.findall(r'(\d+(?:\.\d+)?)\s*days?', user_lower)
            if days:
                scenario_details['duration'] = float(days[0]) * 24
        
        # Advanced scenario type detection
        scenario_patterns = {
            'convoy': ['convoy', 'formation', 'group travel', 'escort', 'military formation'],
            'cruise_tourism': ['cruise', 'tourism', 'tourist', 'vacation', 'holiday', 'leisure'],
            'emergency_rescue': ['rescue', 'emergency', 'distress', 'mayday', 'search and rescue', 'sar'],
            'military_exercise': ['military', 'naval exercise', 'defense', 'maneuver', 'war game'],
            'cargo_convoy': ['cargo convoy', 'shipping lane', 'trade route', 'commercial fleet'],
            'fishing_fleet': ['fishing fleet', 'trawler group', 'fishing expedition'],
            'port_operations': ['port', 'harbor', 'docking', 'loading', 'unloading', 'berth'],
            'storm_avoidance': ['storm', 'weather', 'hurricane', 'typhoon', 'rough seas'],
            'oil_platform': ['oil rig', 'offshore', 'drilling', 'supply vessel', 'platform'],
            'racing_regatta': ['race', 'regatta', 'competition', 'sailing race', 'yacht race'],
            'border_patrol': ['border', 'patrol', 'surveillance', 'coast guard'],
            'whale_watching': ['whale', 'dolphin', 'marine life', 'eco tour'],
            'research_expedition': ['research', 'scientific', 'survey', 'exploration', 'oceanographic']
        }
        
        for scenario_type, keywords in scenario_patterns.items():
            if any(keyword in user_lower for keyword in keywords):
                scenario_details['scenario_type'] = scenario_type
                scenario_details['description'] = f"{scenario_type.replace('_', ' ').title()} scenario"
                break
        
        # Enhanced region detection with specific geographical references
        region_detection = {
            'mediterranean': ['mediterranean', 'med sea', 'italy', 'spain', 'greece', 'turkey', 'malta', 'cyprus', 
                            'sicily', 'coast of sicily', 'off sicily', 'italian coast', 'spanish coast', 
                            'french riviera', 'greek islands', 'turkish coast', 'corsica', 'sardinia',
                            'balearic', 'crete', 'rhodes', 'gibraltar', 'tyrrhenian'],
            'north_sea': ['north sea', 'norway', 'denmark', 'netherlands', 'north sea oil', 'dogger bank',
                         'norwegian waters', 'danish waters', 'dutch coast', 'german bight', 'shetland'],
            'baltic_sea': ['baltic', 'sweden', 'finland', 'poland', 'estonia', 'latvia', 'lithuania',
                          'stockholm archipelago', 'finnish waters', 'gulf of bothnia', 'gulf of finland'],
            'caribbean': ['caribbean', 'bahamas', 'jamaica', 'cuba', 'barbados', 'puerto rico',
                         'west indies', 'tropical waters', 'lesser antilles', 'greater antilles'],
            'pacific': ['pacific', 'japan', 'china', 'korea', 'california', 'hawaii', 'australia',
                       'transpacific', 'japan waters', 'philippines', 'pacific coast', 'california coast'],
            'atlantic': ['atlantic', 'transatlantic', 'across atlantic', 'north atlantic', 'south atlantic',
                        'azores', 'canary islands', 'bay of biscay', 'newfoundland', 'mid atlantic'],
            'indian_ocean': ['indian ocean', 'india', 'sri lanka', 'maldives', 'madagascar', 'indian waters'],
            'english_channel': ['english channel', 'channel', 'dover', 'calais', 'portsmouth', 'dover strait'],
            'persian_gulf': ['persian gulf', 'gulf', 'qatar', 'bahrain', 'kuwait', 'uae', 'arabian gulf'],
            'red_sea': ['red sea', 'suez canal', 'egypt', 'saudi arabia', 'egyptian waters'],
            'arctic': ['arctic', 'greenland', 'alaska', 'siberia', 'northwest passage', 'polar waters'],
            'black_sea': ['black sea', 'romania', 'bulgaria', 'ukraine', 'turkey', 'crimea'],
            'asia': ['asia', 'singapore', 'hong kong', 'shanghai', 'mumbai', 'southeast asia', 'far east'],
            'irish_sea': ['irish sea', 'ireland', 'dublin', 'liverpool', 'wales', 'isle of man', 'irish waters']
        }
        
        for region, keywords in region_detection.items():
            if any(keyword in user_lower for keyword in keywords):
                scenario_details['region'] = region
                if not scenario_details['scenario_type']:
                    scenario_details['description'] = f"Maritime activity in {region.replace('_', ' ').title()}"
                break
        
        # Enhanced ship type detection
        ship_type_detection = {
            'CARGO': ['cargo', 'container', 'freight', 'bulk carrier', 'tanker', 'oil tanker'],
            'PASSENGER': ['passenger', 'ferry', 'cruise ship', 'liner', 'tourist boat'],
            'FISHING': ['fishing', 'trawler', 'seiner', 'longline', 'crab boat', 'shrimp boat'],
            'PILOT_VESSEL': ['pilot', 'patrol', 'coast guard', 'police boat', 'border patrol'],
            'HIGH_SPEED_CRAFT': ['fast boat', 'speedboat', 'racing yacht', 'hydrofoil', 'catamaran'],
            'SEARCH_RESCUE': ['rescue boat', 'lifeboat', 'sar vessel', 'emergency response'],
            'LAW_ENFORCEMENT': ['naval ship', 'warship', 'destroyer', 'frigate', 'gunboat'],
            'TUG': ['tugboat', 'tug', 'assist vessel', 'harbor tug'],
            'SAILING': ['sailing yacht', 'sailboat', 'regatta boat', 'racing yacht']
        }
        
        for ship_type, keywords in ship_type_detection.items():
            if any(keyword in user_lower for keyword in keywords):
                scenario_details['ship_types'].append(ship_type)
        
        # Parse specific ports and routes
        port_mapping = {
            'singapore': 'SINGAPORE', 'shanghai': 'SHANGHAI', 'hong kong': 'HONG_KONG',
            'rotterdam': 'ROTTERDAM', 'hamburg': 'HAMBURG', 'antwerp': 'ANTWERP',
            'dublin': 'DUBLIN', 'liverpool': 'LIVERPOOL', 'holyhead': 'HOLYHEAD',
            'new york': 'NEW_YORK', 'los angeles': 'LOS_ANGELES', 'miami': 'MIAMI',
            'tokyo': 'TOKYO', 'mumbai': 'MUMBAI', 'dubai': 'DUBAI',
            'barcelona': 'BARCELONA', 'marseille': 'MARSEILLE', 'venice': 'VENICE',
            'copenhagen': 'COPENHAGEN', 'stockholm': 'STOCKHOLM', 'oslo': 'OSLO',
            'naples': 'NAPLES', 'athens': 'ATHENS', 'istanbul': 'ISTANBUL'
        }
        
        mentioned_ports = []
        for port_name, port_code in port_mapping.items():
            if port_name in user_lower or port_name.replace(' ', '') in user_lower:
                mentioned_ports.append(port_code)
        
        # Create custom ships for specific routes
        if len(mentioned_ports) >= 2:
            ship_type = scenario_details['ship_types'][0] if scenario_details['ship_types'] else 'PASSENGER'
            for i in range(min(scenario_details['num_ships'], len(mentioned_ports) - 1)):
                scenario_details['custom_ships'].append({
                    'ship_type': ship_type,
                    'ship_name': f'{ship_type}_{i+1}_{random.randint(100, 999)}',
                    'start_port': mentioned_ports[i],
                    'end_port': mentioned_ports[i + 1 if i + 1 < len(mentioned_ports) else -1]
                })
        
        # Coordinate extraction (lat, lon)
        coord_pattern = r'(-?\d+(?:\.\d+)?)[°,\s]+(-?\d+(?:\.\d+)?)'
        coordinates = re.findall(coord_pattern, user_message)
        if coordinates:
            scenario_details['coordinates'] = [(float(lat), float(lon)) for lat, lon in coordinates]
        
        # Special parameters based on scenario type
        if scenario_details['scenario_type'] == 'convoy':
            scenario_details['special_params']['formation_type'] = 'line_abreast'
            scenario_details['special_params']['spacing_nm'] = 0.5
        elif scenario_details['scenario_type'] == 'fishing_fleet':
            scenario_details['special_params']['pattern'] = 'circular'
            scenario_details['special_params']['spread_radius'] = 2.0
        elif scenario_details['scenario_type'] == 'emergency_rescue':
            scenario_details['special_params']['search_pattern'] = 'expanding_square'
            scenario_details['special_params']['urgency'] = 'high'
        
        # Generate intelligent scenario name
        if scenario_details['custom_ships']:
            start_port = scenario_details['custom_ships'][0]['start_port']
            end_port = scenario_details['custom_ships'][0]['end_port']
            scenario_details['scenario_name'] = f"route_{start_port}_to_{end_port}"
        elif scenario_details['scenario_type']:
            scenario_details['scenario_name'] = f"{scenario_details['scenario_type']}_scenario"
        elif scenario_details['region']:
            scenario_details['scenario_name'] = f"{scenario_details['region']}_scenario"
        
        return scenario_details
    
    def _determine_generation_strategy(self, scenario_details: Dict[str, Any]) -> tuple:
        """Determine the best tool and parameters for the parsed scenario"""
        
        # Strategy 1: Custom ships with specific routes
        if scenario_details['custom_ships']:
            return ('generate_custom_ships', {
                'ships': scenario_details['custom_ships'],
                'duration_hours': scenario_details['duration'],
                'scenario_name': scenario_details['scenario_name']
            })
        
        # Strategy 2: Coordinate-based generation (fallback to region)
        elif scenario_details['coordinates']:
            # For now, fall back to regional generation near coordinates
            # This could be enhanced with actual coordinate-based generation
            return ('generate_maritime_scenario', {
                'num_ships': scenario_details['num_ships'],
                'region': scenario_details['region'] or 'irish_sea',
                'duration_hours': scenario_details['duration'],
                'scenario_name': scenario_details['scenario_name']
            })
        
        # Strategy 3: Regional generation with ship types
        elif scenario_details['region'] or scenario_details['ship_types']:
            return ('generate_maritime_scenario', {
                'num_ships': scenario_details['num_ships'],
                'region': scenario_details['region'] or 'irish_sea',
                'duration_hours': scenario_details['duration'],
                'scenario_name': scenario_details['scenario_name'],
                'location_hint': scenario_details.get('original_message', '')
            })
        
        # Strategy 4: Default fallback
        else:
            return ('generate_irish_sea_scenario', {
                'num_ships': scenario_details['num_ships'],
                'duration_hours': scenario_details['duration'],
                'scenario_name': scenario_details['scenario_name']
            })
    
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
• Multiple ships (1-10) with realistic routes in any maritime region worldwide
• Different ship types: Passenger ferries, Cargo ships, Fishing vessels, Patrol boats, High-speed craft  
• Custom routes between any major ports worldwide or using coordinates
• Realistic movement patterns: Ferry routes, cargo lanes, fishing circles, patrol patterns

**Example requests:**
• "Generate 3 ships in the Mediterranean"
• "Create 2 cargo ships from Singapore to Rotterdam"  
• "Generate fishing vessels in the North Sea"
• "Show me ships crossing the Atlantic"
• "Create ferries in the Caribbean"

**Supported Regions:**
🌊 **Atlantic, Pacific, Indian Ocean, Arctic Ocean**
🏝️ **Mediterranean, Caribbean, North Sea, Baltic Sea**
🇪🇺 **European waters, Asian maritime routes**
🌏 **Any coordinates worldwide**

**Demo Features:**
✅ **No API costs** - Works completely offline
✅ **Instant responses** - No network delays
✅ **Full functionality** - Real ship generation
✅ **Perfect for demos** - Reliable and fast
✅ **Worldwide coverage** - Any maritime region

**Output (Automatically Generated):**
• 📁 JSON files with detailed AIS position reports
• 🗺️ Interactive HTML maps (automatic - no extra steps needed!)
• 📡 NMEA format data for marine systems  
• ⚓ Realistic timestamps, speeds, and navigation status

🎯 **Every prompt generates BOTH data and map automatically** - just open the HTML file to see your ships on an interactive map with detailed popups!

Just tell me what kind of maritime scenario and which region you'd like to create!
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
