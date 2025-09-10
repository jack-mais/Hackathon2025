#!/usr/bin/env python3
"""
Setup script to add the Vessel Track Generator MCP to Claude Desktop
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

def create_mcp_config():
    """Create the MCP server configuration"""
    project_dir = Path(__file__).parent.absolute()
    venv_python = project_dir / "venv" / "bin" / "python"
    start_script = project_dir / "start_server.py"
    
    # Check if virtual environment exists
    if not venv_python.exists():
        print("❌ Virtual environment not found!")
        print("Please run: python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt")
        return None
    
    # Check if start script exists
    if not start_script.exists():
        print("❌ Start script not found!")
        return None
    
    config = {
        "mcpServers": {
            "vessel-track-generator": {
                "command": str(venv_python),
                "args": [str(start_script)],
                "cwd": str(project_dir)
            }
        }
    }
    
    return config

def main():
    """Main setup function"""
    print("🚢 Setting up Vessel Track Generator MCP for Claude Desktop")
    print("=" * 60)
    
    # Get config path
    config_path = get_claude_config_path()
    print(f"📁 Claude config location: {config_path}")
    
    # Create config directory if it doesn't exist
    config_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Create MCP configuration
    mcp_config = create_mcp_config()
    if not mcp_config:
        return
    
    # Check if config file already exists
    existing_config = {}
    if config_path.exists():
        try:
            with open(config_path, 'r') as f:
                existing_config = json.load(f)
            print("✅ Found existing Claude config file")
        except json.JSONDecodeError:
            print("⚠️  Existing config file has invalid JSON, will be overwritten")
            existing_config = {}
    
    # Merge configurations
    if "mcpServers" in existing_config:
        existing_config["mcpServers"].update(mcp_config["mcpServers"])
    else:
        existing_config.update(mcp_config)
    
    # Write the configuration
    try:
        with open(config_path, 'w') as f:
            json.dump(existing_config, f, indent=2)
        print("✅ Successfully added Vessel Track Generator to Claude config")
        print(f"📝 Config written to: {config_path}")
    except Exception as e:
        print(f"❌ Error writing config: {e}")
        return
    
    print("\n🎉 Setup complete!")
    print("\nNext steps:")
    print("1. Restart Claude Desktop")
    print("2. Look for vessel track generation tools in Claude")
    print("3. Try asking: 'Generate tracks for 5 cargo ships from Rotterdam to Singapore'")
    
    print(f"\n📋 Your MCP server configuration:")
    print(json.dumps(mcp_config, indent=2))

if __name__ == "__main__":
    main()
