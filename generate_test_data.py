#!/usr/bin/env python3
"""
Data Generation Test Script
Generates AIS data without visualization - pure data output
"""

import os
import sys
import asyncio
import json
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn


class AISDataGenerator:
    """Test script focused purely on data generation"""
    
    def __init__(self):
        self.console = Console()
        self.generated_files = []
        
    def print_header(self, title: str):
        """Print a section header"""
        self.console.print(Panel(title, style="bold blue"))
    
    def generate_crawl_data(self):
        """Generate single ship data (Crawl phase)"""
        self.print_header("🐛 Generating Crawl Data - Single Ship")
        
        try:
            from src.generators.ais_generator import AISGenerator
            from src.core.file_output import FileOutputManager
            
            # Create generator
            generator = AISGenerator()
            file_manager = FileOutputManager()
            
            # Generate sample route
            route = generator.generate_sample_irish_sea_route()
            self.console.print(f"✅ Route created: {len(route.waypoints)} waypoints")
            
            # Create ship
            ship = generator.create_ship("TEST_CRAWL_SINGLE", route)
            self.console.print(f"✅ Ship created: {ship.ship_name} (MMSI: {ship.mmsi})")
            
            # Generate position reports
            reports = []
            duration_minutes = 60  # 1 hour of data
            report_interval = 3    # Every 3 minutes
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TaskProgressColumn(),
                console=self.console
            ) as progress:
                task = progress.add_task("Generating positions...", total=duration_minutes//report_interval)
                
                for i in range(duration_minutes // report_interval):
                    report = generator.get_current_position()
                    if report:
                        reports.append(report.dict())
                    generator.update_position(report_interval)
                    progress.update(task, advance=1)
            
            # Save to file
            filename = file_manager.save_ship_data("test_crawl_single", ship, reports)
            self.generated_files.append(filename)
            
            self.console.print(f"✅ Generated {len(reports)} position reports")
            self.console.print(f"💾 Saved to: {filename}")
            
        except Exception as e:
            self.console.print(f"❌ Crawl generation failed: {e}", style="red")
    
    def generate_walk_data(self):
        """Generate multi-ship data (Walk phase)"""
        self.print_header("🚶 Generating Walk Data - Multiple Ships")
        
        try:
            from src.generators.multi_ship_generator import MultiShipGenerator
            
            generator = MultiShipGenerator()
            
            # Generate different scenarios
            scenarios = [
                {"num_ships": 3, "name": "test_3_ships", "duration": 1.5},
                {"num_ships": 5, "name": "test_5_ships", "duration": 2.0},
                {"ships": [
                    {"ship_type": "CARGO", "ship_name": "CARGO_TEST", "start_port": "DUBLIN", "end_port": "LIVERPOOL"},
                    {"ship_type": "PASSENGER", "ship_name": "FERRY_TEST", "start_port": "DUBLIN", "end_port": "HOLYHEAD"},
                    {"ship_type": "FISHING", "ship_name": "FISHER_TEST", "start_port": "CORK", "end_port": "CORK"}
                ], "name": "test_mixed_types", "duration": 1.0}
            ]
            
            for i, scenario in enumerate(scenarios, 1):
                self.console.print(f"\n📊 Scenario {i}: {scenario['name']}")
                
                try:
                    if "ships" in scenario:
                        # Custom ships
                        result = generator.generate_custom_ships(
                            scenario["ships"],
                            duration_hours=scenario["duration"],
                            scenario_name=scenario["name"]
                        )
                    else:
                        # Random ships
                        result = generator.generate_irish_sea_scenario(
                            num_ships=scenario["num_ships"],
                            duration_hours=scenario["duration"],
                            scenario_name=scenario["name"]
                        )
                    
                    if result.get("success"):
                        ships = result.get("ships", [])
                        self.console.print(f"✅ Generated {len(ships)} ships")
                        
                        # Save individual files
                        for ship in ships:
                            if "filename" in ship:
                                self.generated_files.append(ship["filename"])
                        
                        # Save combined file
                        if "combined_filename" in result:
                            self.generated_files.append(result["combined_filename"])
                            self.console.print(f"💾 Combined file: {result['combined_filename']}")
                    else:
                        self.console.print(f"❌ Scenario failed: {result.get('error', 'Unknown error')}")
                        
                except Exception as e:
                    self.console.print(f"❌ Scenario {scenario['name']} failed: {e}")
                    
        except Exception as e:
            self.console.print(f"❌ Walk generation failed: {e}", style="red")
    
    async def generate_llm_data(self):
        """Generate data using LLM integration (Run phase)"""
        self.print_header("🏃 Generating Run Data - LLM Integration")
        
        # Load .env if available
        try:
            from dotenv import load_dotenv
            load_dotenv()
        except ImportError:
            pass
        
        # Try different LLM clients
        llm_configs = [
            ("Demo", "src.llm_integration.demo_client", "AISDemo", None),
            ("Gemini", "src.llm_integration.gemini_client", "AISGeminiClient", "GEMINI_KEY")
        ]
        
        for name, module_path, class_name, env_var in llm_configs:
            if env_var and not os.getenv(env_var):
                self.console.print(f"⚠️  {name}: {env_var} not set, skipping")
                continue
                
            try:
                self.console.print(f"\n🤖 Testing {name} LLM generation...")
                
                module = __import__(module_path, fromlist=[class_name])
                client_class = getattr(module, class_name)
                client = client_class()
                
                # Test prompts
                prompts = [
                    "Generate 2 ships for testing",
                    "Create 1 cargo ship and 1 ferry",
                    "I need 3 ships for a demo"
                ]
                
                for i, prompt in enumerate(prompts, 1):
                    try:
                        self.console.print(f"  📝 Prompt {i}: '{prompt}'")
                        response = await client.process_request(prompt)
                        
                        if "generated" in response.lower() or "created" in response.lower():
                            self.console.print(f"  ✅ {name} generation successful")
                        else:
                            self.console.print(f"  ⚠️  {name} response: {response[:100]}...")
                            
                    except Exception as e:
                        self.console.print(f"  ❌ {name} prompt {i} failed: {e}")
                
                break  # Use first available LLM
                
            except Exception as e:
                self.console.print(f"❌ {name} LLM failed: {e}")
    
    def show_generated_files(self):
        """Show summary of all generated files"""
        self.print_header("📁 Generated Files Summary")
        
        if not self.generated_files:
            self.console.print("⚠️  No files were generated")
            return
        
        # Check which files actually exist
        existing_files = []
        for file_path in self.generated_files:
            if Path(file_path).exists():
                existing_files.append(file_path)
        
        if not existing_files:
            self.console.print("⚠️  Generated files not found (may be in output/ directory)")
            
            # Check output directory
            output_dir = Path("output")
            if output_dir.exists():
                json_files = list(output_dir.glob("*.json"))
                if json_files:
                    self.console.print(f"\n📁 Found {len(json_files)} files in output/ directory:")
                    for file_path in json_files[-5:]:  # Show last 5
                        size = file_path.stat().st_size
                        modified = datetime.fromtimestamp(file_path.stat().st_mtime)
                        self.console.print(f"  📄 {file_path.name} ({size} bytes, {modified.strftime('%H:%M:%S')})")
            return
        
        self.console.print(f"✅ Successfully generated {len(existing_files)} files:")
        for file_path in existing_files:
            size = Path(file_path).stat().st_size if Path(file_path).exists() else 0
            self.console.print(f"  📄 {file_path} ({size} bytes)")
    
    async def run_generation_tests(self):
        """Run all data generation tests"""
        self.console.print(Panel(
            "🚢 **AIS Data Generation Tests**\n"
            "Generating test data for all phases: Crawl → Walk → Run",
            title="📊 Data Generator",
            style="bold green"
        ))
        
        # Generate data for each phase
        self.generate_crawl_data()
        self.generate_walk_data()
        await self.generate_llm_data()
        
        # Show summary
        self.show_generated_files()
        
        self.console.print(Panel(
            "🎯 **Next Steps:**\n"
            "• Use `python map_viewer.py` for single ship visualization\n"
            "• Use `python map_multi_viewer.py` for multi-ship visualization\n" 
            "• Use `python visualize_test_data.py` to visualize all generated data",
            title="🗺️  Visualization Options",
            style="blue"
        ))


async def main():
    """Run the data generation tests"""
    generator = AISDataGenerator()
    await generator.run_generation_tests()


if __name__ == "__main__":
    asyncio.run(main())
