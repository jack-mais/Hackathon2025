#!/usr/bin/env python3
"""
Test script to verify the MCP server can start properly
"""

import subprocess
import sys
import time
from pathlib import Path

def test_server_startup():
    """Test if the MCP server can start and respond"""
    project_dir = Path(__file__).parent.absolute()
    venv_python = project_dir / "venv" / "bin" / "python"
    start_script = project_dir / "start_server.py"
    
    print("🧪 Testing MCP Server Startup")
    print("=" * 40)
    
    # Check if files exist
    if not venv_python.exists():
        print(f"❌ Virtual environment Python not found: {venv_python}")
        return False
    
    if not start_script.exists():
        print(f"❌ Start script not found: {start_script}")
        return False
    
    print(f"✅ Virtual environment Python: {venv_python}")
    print(f"✅ Start script: {start_script}")
    
    # Test imports
    print("\n🔍 Testing imports...")
    try:
        result = subprocess.run([
            str(venv_python), "-c", 
            "import mcp; import vessel_track_generator; print('✅ All imports successful')"
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print(result.stdout.strip())
        else:
            print(f"❌ Import test failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Import test error: {e}")
        return False
    
    # Test server startup (briefly)
    print("\n🚀 Testing server startup...")
    try:
        # Start the server process
        process = subprocess.Popen([
            str(venv_python), str(start_script)
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        # Wait a bit for startup
        time.sleep(2)
        
        # Check if process is still running
        if process.poll() is None:
            print("✅ Server started successfully")
            process.terminate()
            process.wait()
            return True
        else:
            stdout, stderr = process.communicate()
            print(f"❌ Server failed to start")
            print(f"STDOUT: {stdout}")
            print(f"STDERR: {stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Server startup test error: {e}")
        return False

def main():
    """Main test function"""
    success = test_server_startup()
    
    if success:
        print("\n🎉 All tests passed! The MCP server should work with Claude Desktop.")
        print("\n📋 Next steps:")
        print("1. Restart Claude Desktop completely")
        print("2. Look for 'vessel-track-generator' in MCP servers")
        print("3. Enable it and test with a prompt")
    else:
        print("\n❌ Tests failed. Please check the issues above.")
        print("\n🔧 Troubleshooting:")
        print("1. Make sure virtual environment is activated")
        print("2. Reinstall dependencies: pip install -r requirements.txt")
        print("3. Check file permissions")

if __name__ == "__main__":
    main()
