#!/usr/bin/env python3
"""
AIS Chat CLI - Unified LLM Interface
Talk to AI about generating AIS ship data via natural language
Supports Gemini (recommended), OpenAI, and Demo mode
"""

import os
import sys
import asyncio
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.prompt import Prompt
from rich.markdown import Markdown
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))


class AISChatCLI:
    """Unified CLI interface for chatting with different LLMs about AIS generation"""
    
    def __init__(self):
        self.console = Console()
        self.llm_client = None
        self.llm_type = None
        
    def print_banner(self):
        """Print welcome banner"""
        banner_text = """
# 🚢 AIS Ship Data Generator - AI Powered

**Chat with AI to generate realistic maritime AIS data!**

🤖 **Supported AI Models:**
• **Gemini** (Recommended) - Free tier, fast responses
• **OpenAI GPT** - Requires API key
• **Demo Mode** - Works without any API keys

Type your requests in natural language like:
• "Generate 3 ships in the Irish Sea"
• "Create 2 cargo ships and 1 ferry for a 4-hour simulation"  
• "I need AIS data for ships between Dublin and Holyhead"

Type 'help' for more examples, 'quit' to exit.
        """
        
        self.console.print(Panel(
            Markdown(banner_text),
            title="🌊 Maritime AI Assistant",
            border_style="green"
        ))
    
    def detect_available_llms(self) -> list:
        """Detect which LLM clients are available based on API keys"""
        available = []
        
        # Check for Gemini
        if os.getenv("GEMINI_KEY"):
            available.append(("gemini", "Google Gemini (Recommended) ✅"))
        
        # Check for OpenAI
        if os.getenv("OPENAI_API_KEY"):
            available.append(("openai", "OpenAI GPT ✅"))
        
        # Demo mode is always available
        available.append(("demo", "Demo Mode (No API key required) 🎯"))
        
        return available
    
    def choose_llm(self) -> str:
        """Let user choose which LLM to use"""
        available = self.detect_available_llms()
        
        if len(available) == 1 and available[0][0] == "demo":
            self.console.print("🎯 No API keys detected. Using Demo Mode.")
            return "demo"
        
        self.console.print("\n🤖 **Available AI Models:**")
        for i, (llm_id, description) in enumerate(available, 1):
            self.console.print(f"  {i}. {description}")
        
        while True:
            try:
                choice = int(Prompt.ask(f"\n🔍 Choose your AI model (1-{len(available)})", default="1"))
                if 1 <= choice <= len(available):
                    return available[choice - 1][0]
                else:
                    self.console.print("❌ Invalid choice. Please try again.", style="red")
            except (ValueError, KeyboardInterrupt):
                self.console.print("❌ Invalid input. Please enter a number.", style="red")
    
    async def initialize_llm(self, llm_type: str = None):
        """Initialize the chosen LLM client"""
        if not llm_type:
            llm_type = self.choose_llm()
        
        self.llm_type = llm_type
        
        try:
            if llm_type == "gemini":
                from src.llm_integration.gemini_client import AISGeminiClient
                self.console.print("🌟 Initializing Gemini AI assistant...", style="yellow")
                self.llm_client = AISGeminiClient()
                self.console.print("✅ Gemini AI assistant ready! 🌟", style="green")
                
            elif llm_type == "openai":
                from src.llm_integration.llm_client import AISLLMClient
                self.console.print("🤖 Initializing OpenAI GPT assistant...", style="yellow")
                self.llm_client = AISLLMClient()
                self.console.print("✅ OpenAI GPT assistant ready! 🤖", style="green")
                
            elif llm_type == "demo":
                from src.llm_integration.demo_client import AISDemo
                self.console.print("🎯 Initializing Demo mode assistant...", style="yellow")
                self.llm_client = AISDemo()
                self.console.print("✅ Demo assistant ready! 🎯", style="green")
                
            return True
            
        except Exception as e:
            self.console.print(f"❌ Failed to initialize {llm_type}: {e}", style="red")
            return False
    
    def show_help(self):
        """Show help information"""
        help_text = f"""
# 🚢 AIS Generator Commands & Examples - {self.llm_type.title()} Mode

## **Example Natural Language Requests:**

**Basic Generation:**
• "Generate 3 ships in the Irish Sea"
• "Create 5 ships with different types"
• "I want some AIS data for testing"

**Specific Ship Types:**
• "Generate 2 cargo ships and 1 ferry"
• "Create a fishing vessel and 2 passenger ferries"
• "I need 1 high-speed craft and 3 cargo ships"

**Custom Routes:**
• "Generate ships from Dublin to Holyhead"
• "Create 2 ferries between Dublin and Liverpool"
• "I want cargo ships from Cork to Cardiff"

**Simulation Parameters:**
• "Generate 4 ships for a 6-hour simulation"
• "Create ships with realistic movement patterns"
• "I need a 3-hour scenario with mixed ship types"

**Information Queries:**
• "What ports are available?"
• "What ship types can you generate?"
• "Show me your capabilities"

## **Special Commands:**
• `help` - Show this help
• `clear` - Clear conversation history
• `caps` - Show AI capabilities
• `demo` - Run a quick demo
• `quit` / `exit` - Exit the program

## **Generated Output:**
• JSON files saved to `./output/` directory
• Use `python map_multi_viewer.py` to visualize on map
• Individual ship files for detailed analysis

**Current AI Model:** {self.llm_type.title()}
        """
        
        self.console.print(Panel(
            Markdown(help_text),
            title="Help & Examples",
            border_style="cyan"
        ))
    
    async def show_capabilities(self):
        """Show AI capabilities"""
        if not self.llm_client:
            self.console.print("❌ AI not initialized", style="red")
            return
        
        try:
            if hasattr(self.llm_client, 'get_available_capabilities'):
                capabilities = await self.llm_client.get_available_capabilities()
            else:
                capabilities = "🚢 **AIS Ship Data Generator**\n\nGenerate realistic maritime AIS data with multiple ship types and routes in the Irish Sea region."
            
            self.console.print(Panel(
                Markdown(capabilities),
                title=f"{self.llm_type.title()} AI Capabilities",
                border_style="green"
            ))
        except Exception as e:
            self.console.print(f"❌ Error getting capabilities: {e}", style="red")
    
    def clear_conversation(self):
        """Clear conversation history"""
        if self.llm_client and hasattr(self.llm_client, 'clear_conversation'):
            self.llm_client.clear_conversation()
            self.console.print("🧹 Conversation history cleared", style="cyan")
        else:
            self.console.print("❌ AI not initialized or doesn't support conversation clearing", style="red")
    
    async def run_demo(self):
        """Run a quick demo"""
        if not self.llm_client:
            self.console.print("❌ AI not initialized", style="red")
            return
        
        self.console.print("🎯 Running quick demo generation...", style="yellow")
        
        try:
            if hasattr(self.llm_client, 'process_request'):
                response = await self.llm_client.process_request("Generate 2 ships for a demo")
            else:
                response = "Demo functionality not available for this AI model."
                
            self.console.print(Panel(
                Markdown(response),
                title="🎯 Demo Result",
                border_style="green"
            ))
        except Exception as e:
            self.console.print(f"❌ Demo error: {e}", style="red")
    
    async def process_user_input(self, user_input: str) -> bool:
        """Process user input and return False if should exit"""
        
        user_input_lower = user_input.strip().lower()
        
        # Handle special commands
        if user_input_lower in ['quit', 'exit', 'q']:
            return False
        elif user_input_lower in ['help', 'h']:
            self.show_help()
            return True
        elif user_input_lower in ['clear', 'cls']:
            self.clear_conversation()
            return True
        elif user_input_lower in ['caps', 'capabilities']:
            await self.show_capabilities()
            return True
        elif user_input_lower in ['demo', 'test']:
            await self.run_demo()
            return True
        elif user_input_lower == '':
            return True
        
        # Process with AI
        if not self.llm_client:
            self.console.print("❌ AI not initialized", style="red")
            return True
        
        try:
            self.console.print(f"🤖 {self.llm_type.title()} is thinking...", style="yellow")
            
            if hasattr(self.llm_client, 'process_request'):
                response = await self.llm_client.process_request(user_input)
            else:
                response = f"Sorry, {self.llm_type} doesn't support this request type."
            
            # Display response in a panel
            self.console.print(Panel(
                Markdown(response),
                title=f"🤖 {self.llm_type.title()} AI Assistant",
                border_style="green"
            ))
            
        except Exception as e:
            self.console.print(f"❌ Error: {e}", style="red")
        
        return True
    
    async def run_chat_loop(self):
        """Main chat loop"""
        self.console.print(f"\n🗣️  **Start chatting with {self.llm_type.title()}!** Type your request or 'help' for examples.\n")
        
        while True:
            try:
                # Get user input
                user_input = Prompt.ask(
                    "[bold green]You[/bold green]",
                    default=""
                )
                
                # Process input
                should_continue = await self.process_user_input(user_input)
                if not should_continue:
                    break
                    
                print()  # Add spacing
                
            except KeyboardInterrupt:
                self.console.print("\n👋 Goodbye!", style="yellow")
                break
            except EOFError:
                self.console.print("\n👋 Goodbye!", style="yellow")
                break
    
    async def run(self):
        """Main entry point"""
        self.print_banner()
        
        # Initialize LLM
        if not await self.initialize_llm():
            return
        
        # Show quick intro
        self.console.print(Panel(
            f"💡 **Quick Start:** Try saying 'Generate 3 ships' or 'What can you do?' using {self.llm_type.title()}",
            border_style="blue"
        ))
        
        # Run chat loop
        await self.run_chat_loop()
        
        self.console.print(f"\n🌊 Thank you for using the AIS Generator with {self.llm_type.title()}!", style="green")
        self.console.print("📁 Check the ./output/ directory for generated files")
        self.console.print("🗺️  Use 'python map_multi_viewer.py' to visualize your ships")


async def main():
    """Main function"""
    # Load environment variables from .env file if it exists
    env_file = Path(".env")
    if env_file.exists():
        try:
            from dotenv import load_dotenv
            load_dotenv()
        except ImportError:
            pass  # python-dotenv not installed, that's okay
    
    # Create and run CLI
    cli = AISChatCLI()
    await cli.run()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)
