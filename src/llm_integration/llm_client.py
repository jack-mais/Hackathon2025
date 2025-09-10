"""
LLM Client for natural language processing
Integrates with OpenAI API and MCP server
"""

import os
import json
import asyncio
from typing import Dict, List, Any, Optional
from openai import AsyncOpenAI
from datetime import datetime

from ..mcp_integration.mcp_server import AISMCPServer


class AISLLMClient:
    """LLM client for processing natural language requests about ship generation"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY environment variable.")
        
        self.client = AsyncOpenAI(api_key=self.api_key)
        self.mcp_server = AISMCPServer()
        self.conversation_history = []
        
        # System prompt for the LLM
        self.system_prompt = """You are an expert maritime AIS (Automatic Identification System) data generator assistant. 

You help users generate realistic ship movement data for any maritime region worldwide. You have access to tools that can:
1. Generate multiple ships with realistic routes in any specified region
2. Create custom ships with specific types and routes between any ports
3. List available ports and ship types
4. Save all generated data to JSON files for analysis

You support worldwide maritime operations including major commercial ports, ferry terminals, and fishing harbors across all continents. Available ship types: PASSENGER (ferries), CARGO (container/bulk), FISHING (trawlers), PILOT_VESSEL (patrol/pilot), HIGH_SPEED_CRAFT (fast boats).

When users ask for ship generation:
- Parse their request to understand: number of ships, types, routes, duration, and region/location
- Use the appropriate tools to generate the data
- Always provide a clear summary of what was generated
- Mention that data is saved to JSON files and can be visualized on maps

You can handle requests for any maritime region including Mediterranean, North Sea, Atlantic, Pacific, Indian Ocean, Caribbean, Baltic Sea, and many others. If users specify coordinates or specific regions, work with those. If they mention specific ports worldwide, generate appropriate scenarios.

Be conversational and helpful, but focus on maritime operations. Ask clarifying questions if the request is ambiguous about location or requirements.
"""

    async def process_request(self, user_message: str) -> str:
        """Process a user request and return response"""
        
        # Add user message to conversation
        self.conversation_history.append({
            "role": "user", 
            "content": user_message
        })
        
        try:
            # Get LLM response with tool access
            messages = [
                {"role": "system", "content": self.system_prompt},
                *self.conversation_history
            ]
            
            tools = self.mcp_server.get_tools_schema()["tools"]
            
            response = await self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                tools=tools,
                tool_choice="auto",
                temperature=0.7,
                max_tokens=1000
            )
            
            response_message = response.choices[0].message
            
            # Handle tool calls
            if response_message.tool_calls:
                tool_responses = []
                
                for tool_call in response_message.tool_calls:
                    tool_name = tool_call.function.name
                    tool_args = json.loads(tool_call.function.arguments)
                    
                    print(f"🔧 Calling tool: {tool_name}")
                    print(f"📝 Arguments: {tool_args}")
                    
                    # Call the MCP tool
                    tool_result = await self.mcp_server.call_tool(tool_name, tool_args)
                    tool_responses.append(tool_result)
                    
                    # Add tool call and result to conversation
                    self.conversation_history.append({
                        "role": "assistant",
                        "content": None,
                        "tool_calls": [tool_call.model_dump()]
                    })
                    
                    self.conversation_history.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": json.dumps(tool_result)
                    })
                
                # Get final response after tool calls
                final_response = await self.client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": self.system_prompt},
                        *self.conversation_history
                    ],
                    temperature=0.7,
                    max_tokens=1000
                )
                
                final_message = final_response.choices[0].message.content
                self.conversation_history.append({
                    "role": "assistant",
                    "content": final_message
                })
                
                return final_message
                
            else:
                # No tools called, just return the response
                assistant_message = response_message.content
                self.conversation_history.append({
                    "role": "assistant",
                    "content": assistant_message  
                })
                
                return assistant_message
                
        except Exception as e:
            error_message = f"❌ Error processing request: {str(e)}"
            print(error_message)
            return error_message
    
    def clear_conversation(self):
        """Clear conversation history"""
        self.conversation_history = []
    
    async def get_available_capabilities(self) -> str:
        """Get information about what the assistant can do"""
        capabilities = """
🚢 **AIS Ship Data Generator Capabilities**

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

**Output:**
• JSON files with detailed AIS position reports
• Interactive map visualization available 
• NMEA format data for marine systems
• Realistic timestamps, speeds, and navigation status

Just tell me what kind of maritime scenario you'd like to create!
        """
        return capabilities.strip()


# Example usage functions for testing
async def test_llm_integration():
    """Test the LLM integration"""
    
    # Check for API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ Please set OPENAI_API_KEY environment variable")
        print("💡 Get your API key from: https://platform.openai.com/api-keys")
        return
    
    try:
        client = AISLLMClient(api_key)
        
        print("🤖 Testing LLM integration...")
        
        # Test basic capability query
        capabilities = await client.get_available_capabilities()
        print("✅ LLM client initialized successfully")
        print(f"📋 Capabilities: {capabilities[:200]}...")
        
        # Test a simple request
        response = await client.process_request("What ship types can you generate?")
        print(f"🗣️  LLM Response: {response[:200]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing LLM integration: {e}")
        return False


if __name__ == "__main__":
    asyncio.run(test_llm_integration())
