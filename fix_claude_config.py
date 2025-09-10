#!/usr/bin/env python3
"""
Fix Claude Desktop configuration for the Vessel Track Generator MCP
"""

import json
import os
import platform
from pathlib import Path

def get_claude_config_path():
    """Get the Claude Desktop config file path based on OS"""
    system = platform.system()
    
    if system == "Darwin":  # macOS
        return Path.home() / "Library" / "Application Support" / "Claude" / "claude_desktop_config.json"
    elif system == "Windows":
        return Path(os.environ["APPDATA"]) / "Claude" / "claude_desktop_config.json"
    else:  # Linux
        return Path.home() / ".config" / "claude" / "claude_desktop_config.json"

def create_working_config():
    """Create a working MCP server configuration"""
    project_dir = Path(__file__).parent.absolute()
    venv_python = project_dir / "venv" / "bin" / "python"
    start_script = project_dir / "start_server.py"
    
    # Multiple configuration options to try
    configs = [
        # Option 1: Direct virtual environment Python
        {
            "name": "vessel-track-generator",
            "config": {
                "command": str(venv_python),
                "args": [str(start_script)],
                "cwd": str(project_dir)
            }
        },
        # Option 2: Using bash to activate venv
        {
            "name": "vessel-track-generator-bash",
            "config": {
                "command": "bash",
                "args": [
                    "-c",
                    f"cd {project_dir} && source venv/bin/activate && python start_server.py"
                ]
            }
        },
        # Option 3: Using shell script
        {
            "name": "vessel-track-generator-shell",
            "config": {
                "command": "/bin/bash",
                "args": [
                    "-c",
                    f"cd {project_dir} && source venv/bin/activate && exec python start_server.py"
                ]
            }
        }
    ]
    
    return configs

def test_server_startup():
    """Test if the server can start properly"""
    project_dir = Path(__file__).parent.absolute()
    venv_python = project_dir / "venv" / "bin" / "python"
    start_script = project_dir / "start_server.py"
    
    print("🧪 Testing server startup...")
    
    # Check if files exist
    if not venv_python.exists():
        print(f"❌ Virtual environment Python not found: {venv_python}")
        return False
    
    if not start_script.exists():
        print(f"❌ Start script not found: {start_script}")
        return False
    
    print(f"✅ Virtual environment Python: {venv_python}")
    print(f"✅ Start script: {start_script}")
    
    # Test Python import
    try:
        import subprocess
        result = subprocess.run([
            str(venv_python), "-c", 
            "import mcp; import vessel_track_generator; print('All imports successful')"
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("✅ All Python imports successful")
            return True
        else:
            print(f"❌ Import test failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Import test error: {e}")
        return False

def main():
    """Main fix function"""
    print("🔧 Fixing Claude Desktop MCP Configuration")
    print("=" * 50)
    
    # Test server startup first
    if not test_server_startup():
        print("\n❌ Server startup test failed. Please check:")
        print("1. Virtual environment is properly set up")
        print("2. All dependencies are installed")
        print("3. Files are in the correct location")
        return
    
    # Get config path
    config_path = get_claude_config_path()
    print(f"\n📁 Claude config location: {config_path}")
    
    # Create config directory if it doesn't exist
    config_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Get working configurations
    configs = create_working_config()
    
    # Read existing config
    existing_config = {}
    if config_path.exists():
        try:
            with open(config_path, 'r') as f:
                existing_config = json.load(f)
            print("✅ Found existing Claude config file")
        except json.JSONDecodeError:
            print("⚠️  Existing config file has invalid JSON, will be overwritten")
            existing_config = {}
    
    # Update MCP servers section
    if "mcpServers" not in existing_config:
        existing_config["mcpServers"] = {}
    
    # Remove old vessel track generator entries
    keys_to_remove = [key for key in existing_config["mcpServers"].keys() 
                     if "vessel" in key.lower() or "track" in key.lower()]
    for key in keys_to_remove:
        del existing_config["mcpServers"][key]
        print(f"🗑️  Removed old config: {key}")
    
    # Add the working configuration (try the first one)
    working_config = configs[0]
    existing_config["mcpServers"][working_config["name"]] = working_config["config"]
    
    # Write the configuration
    try:
        with open(config_path, 'w') as f:
            json.dump(existing_config, f, indent=2)
        print(f"✅ Successfully updated Claude config")
        print(f"📝 Config written to: {config_path}")
    except Exception as e:
        print(f"❌ Error writing config: {e}")
        return
    
    print(f"\n🎉 Configuration updated!")
    print(f"📋 Using configuration: {working_config['name']}")
    print(json.dumps(working_config["config"], indent=2))
    
    print("\n🔄 Next steps:")
    print("1. Restart Claude Desktop completely")
    print("2. Check if 'vessel-track-generator' appears in MCP servers")
    print("3. Try enabling it")
    
    print("\n🔍 If it still doesn't work, try these alternative configurations:")
    for i, config in enumerate(configs[1:], 1):
        print(f"\nOption {i+1}: {config['name']}")
        print(json.dumps(config["config"], indent=2))

if __name__ == "__main__":
    main()

