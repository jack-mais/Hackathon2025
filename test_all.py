#!/usr/bin/env python3
"""
Comprehensive Test Suite for AIS Ship Data Generator
Tests all phases: Crawl, Walk, Run
"""

import os
import sys
import asyncio
import json
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

# Load .env if available
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn


class AISTestSuite:
    """Comprehensive test suite for all AIS functionality"""
    
    def __init__(self):
        self.console = Console()
        self.results = {}
        
    def print_header(self, title: str):
        """Print a test section header"""
        self.console.print(Panel(title, style="bold blue"))
    
    def print_result(self, test_name: str, success: bool, details: str = ""):
        """Print test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        self.results[test_name] = success
        
        message = f"{status} {test_name}"
        if details:
            message += f" - {details}"
        
        style = "green" if success else "red"
        self.console.print(message, style=style)
    
    def test_imports(self):
        """Test all module imports"""
        self.print_header("🧪 Testing Module Imports")
        
        try:
            from src.core.models import Position, ShipState, Route
            self.print_result("Core Models Import", True)
        except Exception as e:
            self.print_result("Core Models Import", False, str(e))
        
        try:
            from src.generators.ais_generator import AISGenerator
            self.print_result("AIS Generator Import", True)
        except Exception as e:
            self.print_result("AIS Generator Import", False, str(e))
        
        try:
            from src.generators.ais_generator import AISGenerator
            self.print_result("AIS Generator Import", True)
        except Exception as e:
            self.print_result("AIS Generator Import", False, str(e))
        
        try:
            from src.mcp_integration.mcp_server import AISMCPServer
            self.print_result("MCP Server Import", True)
        except Exception as e:
            self.print_result("MCP Server Import", False, str(e))
    
    def test_crawl_phase(self):
        """Test Crawl phase (single ship generation)"""
        self.print_header("🐛 Testing Crawl Phase - Single Ship Generation")
        
        try:
            from src.generators.ais_generator import AISGenerator
            
            # Create generator
            generator = AISGenerator()
            
            # Generate sample route
            route = generator.generate_sample_irish_sea_route()
            self.print_result("Route Generation", True, f"{len(route.waypoints)} waypoints")
            
            # Generate ship data
            ship = generator.create_ship("TEST_CRAWL", route)
            self.print_result("Ship Creation", True, f"MMSI: {ship.mmsi}")
            
            # Generate position reports
            reports = []
            duration_minutes = 30  # 30 minutes of data
            report_interval = 2    # Every 2 minutes
            
            for _ in range(duration_minutes // report_interval):
                report = generator.get_current_position()
                if report:
                    reports.append(report)
                generator.update_position(report_interval)
            
            self.print_result("Position Generation", len(reports) > 0, f"{len(reports)} reports generated")
            
        except Exception as e:
            self.print_result("Crawl Phase", False, str(e))
    
    def test_walk_phase(self):
        """Test Walk phase (multi-ship generation)"""
        self.print_header("🚶 Testing Walk Phase - Multi-Ship Generation")
        
        try:
            from src.generators.ais_generator import AISGenerator
            
            # Create generator
            generator = AISGenerator()
            
            # Generate scenario
            scenario_result = generator.generate_irish_sea_scenario(
                num_ships=3,
                duration_hours=1.0,
                report_interval_minutes=5,
                scenario_name="test_walk"
            )
            
            self.print_result("Multi-Ship Scenario", 'ships' in scenario_result, 
                            f"{len(scenario_result.get('ships', []))} ships generated")
            
            # Test individual ship types
            for ship_type in ['PASSENGER', 'CARGO', 'FISHING']:
                try:
                    custom_result = generator.generate_custom_ships([{
                        'ship_type': ship_type,
                        'ship_name': f'TEST_{ship_type}',
                        'start_port': 'DUBLIN',
                        'end_port': 'HOLYHEAD'
                    }], duration_hours=0.5, scenario_name=f"test_{ship_type.lower()}")
                    
                    self.print_result(f"{ship_type} Ship Generation", 'ships' in custom_result)
                    
                except Exception as e:
                    self.print_result(f"{ship_type} Ship Generation", False, str(e))
                    
        except Exception as e:
            self.print_result("Walk Phase", False, str(e))
    
    async def test_run_phase(self):
        """Test Run phase (LLM integration)"""
        self.print_header("🏃 Testing Run Phase - LLM Integration")
        
        # Test MCP Server
        try:
            from src.mcp_integration.mcp_server import AISMCPServer
            server = AISMCPServer()
            
            # Test tool listing
            tools = server.list_tools()
            self.print_result("MCP Tools Available", len(tools) > 0, f"{len(tools)} tools")
            
            # Test sample generation
            result = await server.call_tool("generate_irish_sea_scenario", {
                "num_ships": 2,
                "duration_hours": 0.5,
                "scenario_name": "mcp_test"
            })
            
            self.print_result("MCP Tool Execution", 'success' in result)
            
        except Exception as e:
            self.print_result("MCP Integration", False, str(e))
        
        # Test LLM Clients
        llm_tests = [
            ("Demo Client", "src.llm_integration.demo_client", "AISDemo", None),
            ("Gemini Client", "src.llm_integration.gemini_client", "AISGeminiClient", "GEMINI_KEY"),
            ("OpenAI Client", "src.llm_integration.llm_client", "AISLLMClient", "OPENAI_API_KEY")
        ]
        
        for name, module_path, class_name, env_var in llm_tests:
            try:
                if env_var and not os.getenv(env_var):
                    self.print_result(f"{name} (API Key)", False, f"{env_var} not set")
                    continue
                
                module = __import__(module_path, fromlist=[class_name])
                client_class = getattr(module, class_name)
                
                if env_var:
                    client = client_class()
                    # Test basic functionality
                    if hasattr(client, 'process_request'):
                        response = await client.process_request("What ship types can you generate?")
                        self.print_result(f"{name} Response", len(response) > 0)
                    else:
                        self.print_result(f"{name} Import", True, "Available but no API key")
                else:
                    client = client_class()
                    self.print_result(f"{name} Import", True)
                    
            except Exception as e:
                self.print_result(f"{name}", False, str(e))
    
    def test_visualization(self):
        """Test map visualization components"""
        self.print_header("🗺️  Testing Visualization")
        
        try:
            import folium
            self.print_result("Folium Import", True, "Map visualization available")
            
            # Check if map viewer files exist
            viewers = ["map_viewer.py", "map_multi_viewer.py"]
            for viewer in viewers:
                if Path(viewer).exists():
                    self.print_result(f"{viewer} Available", True)
                else:
                    self.print_result(f"{viewer} Available", False, "File not found")
                    
        except ImportError:
            self.print_result("Folium Import", False, "Install folium for map visualization")
    
    def test_file_operations(self):
        """Test file I/O operations"""
        self.print_header("📁 Testing File Operations")
        
        try:
            from src.core.file_output import FileOutputManager
            
            manager = FileOutputManager()
            
            # Test directory creation
            output_dir = Path("output")
            if not output_dir.exists():
                output_dir.mkdir()
            
            self.print_result("Output Directory", output_dir.exists())
            
            # Test sample data save
            sample_data = {
                "test": "data",
                "timestamp": datetime.now().isoformat(),
                "ships": []
            }
            
            filename = manager.save_to_json("test_file_ops", sample_data)
            self.print_result("JSON File Save", Path(filename).exists())
            
            # Clean up test file
            if Path(filename).exists():
                Path(filename).unlink()
                
        except Exception as e:
            self.print_result("File Operations", False, str(e))
    
    async def run_all_tests(self):
        """Run the complete test suite"""
        self.console.print(Panel(
            "🧪 **AIS Ship Data Generator - Comprehensive Test Suite**\n"
            "Testing all phases: Crawl → Walk → Run",
            title="🚢 Maritime AI Test Suite",
            style="bold green"
        ))
        
        # Run all test phases
        self.test_imports()
        self.test_file_operations()
        self.test_crawl_phase()
        self.test_walk_phase()
        await self.test_run_phase()
        self.test_visualization()
        
        # Summary
        self.print_header("📊 Test Summary")
        
        total_tests = len(self.results)
        passed_tests = sum(self.results.values())
        failed_tests = total_tests - passed_tests
        
        if failed_tests == 0:
            self.console.print(f"🎉 **All {total_tests} tests passed!**", style="bold green")
            self.console.print("✅ Your AIS Ship Data Generator is fully functional!")
        else:
            self.console.print(f"📊 **{passed_tests}/{total_tests} tests passed**", style="yellow")
            self.console.print(f"❌ {failed_tests} tests failed", style="red")
        
        self.console.print(Panel(
            "🚀 **Ready to use:**\n"
            "• `python ais_chat.py` - Start AI chat interface\n"
            "• `python quick_demo.py` - Quick demo generation\n"
            "• `python map_multi_viewer.py` - Visualize generated data",
            title="Next Steps",
            style="blue"
        ))


async def main():
    """Run the test suite"""
    test_suite = AISTestSuite()
    await test_suite.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main())
