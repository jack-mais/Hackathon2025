#!/usr/bin/env python3
"""
AIS Chat CLI - Google Gemini AI Interface
Talk to AI about generating AIS ship data via natural language
Powered by Google Gemini AI
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
# 🚢 AIS Ship Data Generator - Gemini AI Powered

**Chat with Google Gemini AI to generate realistic maritime AIS data!**

🌟 **Powered by Google Gemini** - Advanced AI for natural language understanding

Type your requests in natural language like:
• "Generate a convoy off the coast of Sicily"
• "Create 3 ships in the Mediterranean for 6 hours"
• "I need cargo ships from Barcelona to Naples"
• "Generate fishing vessels in Norwegian waters"

Type 'help' for more examples, 'quit' to exit.

🔑 **Setup:** Set your GEMINI_KEY environment variable to get started!
        """
        
        self.console.print(Panel(
            Markdown(banner_text),
            title="🌊 Maritime AI Assistant",
            border_style="green"
        ))
    
    def detect_gemini_key(self) -> bool:
        """Check if Gemini API key is available"""
        return bool(os.getenv("GEMINI_KEY"))
    
    def check_setup(self) -> bool:
        """Check if Gemini is properly configured"""
        if not self.detect_gemini_key():
            self.console.print("\n❌ **GEMINI_KEY not found!**", style="red")
            self.console.print("")
            self.console.print("🔧 **Setup Instructions:**", style="yellow")
            self.console.print("1. Get a free API key from https://aistudio.google.com/app/apikey")
            self.console.print("2. Set environment variable: export GEMINI_KEY='your-api-key-here'")
            self.console.print("3. Or add to .env file: GEMINI_KEY=your-api-key-here")
            self.console.print("")
            return False
        return True
    
    async def initialize_gemini(self):
        """Initialize the Gemini AI client"""
        self.llm_type = "gemini"
        
        try:
            from src.llm_integration.gemini_client import AISGeminiClient
            self.console.print("🌟 Initializing Google Gemini AI assistant...", style="yellow")
            self.llm_client = AISGeminiClient()
            self.console.print("✅ Google Gemini AI assistant ready! 🌟", style="green")
            return True
            
        except Exception as e:
            self.console.print(f"❌ Failed to initialize Gemini: {e}", style="red")
            self.console.print("💡 Make sure your GEMINI_KEY is valid and you have internet connection", style="yellow")
            return False
    
    def show_help(self):
        """Show help information"""
        help_text = """
# 🚢 AIS Generator Commands & Examples - Google Gemini AI

## **Example Natural Language Requests:**

**Regional Generation:**
• "Generate a convoy off the coast of Sicily"
• "Create 4 ships in the Mediterranean for 6 hours"
• "I need vessels in Norwegian waters"
• "Generate ships near the Greek islands"

**Specific Ship Types:**
• "Generate 2 cargo ships and 1 ferry"
• "Create a fishing vessel and 2 passenger ferries"
• "I need 1 high-speed craft and 3 cargo ships"

**Custom Routes & Locations:**
• "Generate ships from Barcelona to Naples"
• "Create ships between Singapore and Shanghai"
• "I want vessels from Rotterdam to Hamburg"

**Complex Scenarios:**
• "Generate a rescue scenario with 5 ships"
• "Create a convoy escort mission off Sicily"
• "I need a fishing fleet in the North Sea"

**Information Queries:**
• "What ports are available in Asia?"
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
• Interactive HTML maps automatically generated
• NMEA format data for marine systems
• Individual ship files for detailed analysis

**Powered by:** Google Gemini AI - Advanced natural language understanding
        """
        
        self.console.print(Panel(
            Markdown(help_text),
            title="🌟 Gemini AI Help & Examples",
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
                title="🌟 Gemini AI Capabilities",
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
            self.console.print(f"🌟 Google Gemini is thinking...", style="yellow")
            
            if hasattr(self.llm_client, 'process_request'):
                response = await self.llm_client.process_request(user_input)
            else:
                response = f"Sorry, {self.llm_type} doesn't support this request type."
            
            # Display response in a panel
            self.console.print(Panel(
                Markdown(response),
                title="🌟 Gemini AI Assistant",
                border_style="green"
            ))
            
        except Exception as e:
            self.console.print(f"❌ Error: {e}", style="red")
        
        return True
    
    async def run_chat_loop(self):
        """Main chat loop"""
        self.console.print(f"\n🗣️  **Start chatting with Google Gemini!** Type your request or 'help' for examples.\n")
        
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
        
        # Check if Gemini is properly set up
        if not self.check_setup():
            return
        
        # Initialize Gemini
        if not await self.initialize_gemini():
            return
        
        # Show quick intro
        self.console.print(Panel(
            "💡 **Quick Start:** Try saying 'Generate a convoy off Sicily' or 'What can you do?'",
            border_style="blue"
        ))
        
        # Run chat loop
        await self.run_chat_loop()
        
        self.console.print(f"\n🌊 Thank you for using the AIS Generator with Google Gemini!", style="green")
        self.console.print("📁 Check the ./output/ directory for generated files")
        self.console.print("🗺️  Interactive maps are automatically generated for each scenario!")


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
