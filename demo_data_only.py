#!/usr/bin/env python3
"""
Pure Data Generation Demo
Generates AIS data using working APIs - no visualization
"""

import sys
import os
from pathlib import Path
from rich.console import Console
from rich.panel import Panel

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

console = Console()

def generate_demo_data():
    """Generate demo data using the working multi-ship generator"""
    console.print(Panel(
        "📊 **Pure Data Generation Demo**\n"
        "Creating AIS data files without visualization",
        title="🚢 Data Generator",
        style="bold blue"
    ))
    
    try:
        from src.generators.multi_ship_generator import MultiShipGenerator
        
        generator = MultiShipGenerator()
        console.print("✅ MultiShipGenerator initialized")
        
        # Check available methods
        methods = [method for method in dir(generator) if not method.startswith('_')]
        console.print(f"📋 Available methods: {', '.join(methods[:5])}...")
        
        # Try the working method from quick_demo approach
        console.print("\n🎯 Generating Irish Sea scenario...")
        
        # Check if the method exists and call it
        if hasattr(generator, 'generate_irish_sea_scenario'):
            # Try without duration_hours first to see expected parameters
            try:
                result = generator.generate_irish_sea_scenario(
                    num_ships=3,
                    report_interval_minutes=5,
                    scenario_name="demo_data_test"
                )
                console.print("✅ Generated scenario without duration_hours")
                console.print(f"📊 Result keys: {list(result.keys()) if isinstance(result, dict) else 'Not a dict'}")
                
            except Exception as e:
                console.print(f"❌ Error: {e}")
                
                # Try with different parameters
                try:
                    result = generator.generate_irish_sea_scenario(
                        num_ships=3,
                        scenario_name="demo_data_test_2"
                    )
                    console.print("✅ Generated scenario with minimal parameters")
                    
                except Exception as e2:
                    console.print(f"❌ Second attempt failed: {e2}")
        else:
            console.print("❌ Method generate_irish_sea_scenario not found")
        
        # Try any other generation methods
        generation_methods = [m for m in methods if 'generate' in m.lower()]
        if generation_methods:
            console.print(f"\n🔍 Found generation methods: {generation_methods}")
            
            for method_name in generation_methods[:2]:  # Try first 2
                try:
                    method = getattr(generator, method_name)
                    console.print(f"\n🧪 Testing {method_name}...")
                    
                    if method_name == 'generate_custom_ships' and hasattr(generator, method_name):
                        # Try custom ships
                        result = method([{
                            'ship_type': 'PASSENGER',
                            'ship_name': 'TEST_FERRY',
                            'start_port': 'DUBLIN',
                            'end_port': 'HOLYHEAD'
                        }], scenario_name="custom_test")
                        console.print(f"✅ {method_name} worked!")
                        
                except Exception as e:
                    console.print(f"❌ {method_name} failed: {e}")
        
        # Show what files were created
        output_dir = Path("output")
        if output_dir.exists():
            json_files = list(output_dir.glob("*.json"))
            console.print(f"\n📁 Found {len(json_files)} JSON files in output/")
            
            if json_files:
                console.print("📄 Latest files:")
                for file_path in sorted(json_files, key=lambda f: f.stat().st_mtime)[-3:]:
                    size = file_path.stat().st_size
                    console.print(f"  • {file_path.name} ({size} bytes)")
        
    except Exception as e:
        console.print(f"❌ Generation failed: {e}")
    
    console.print(Panel(
        "🎯 **Next Step:**\n"
        "Use `python visualize_test_data.py` to create maps from generated data",
        title="✅ Data Generated",
        style="green"
    ))

if __name__ == "__main__":
    generate_demo_data()
