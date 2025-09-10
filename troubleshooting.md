# MCP Server Troubleshooting Guide

## Issue: "vessel-track-generator is available but cannot be enabled"

This is a common issue with MCP servers in Claude Desktop. Here are the solutions:

### ✅ **Solution 1: Fixed Configuration (Already Applied)**

The configuration has been updated to use the correct virtual environment Python path. 

**Current working config:**
```json
{
  "mcpServers": {
    "vessel-track-generator": {
      "command": "/Users/christosmantzouranis/code/Hackathon2025/venv/bin/python",
      "args": ["/Users/christosmantzouranis/code/Hackathon2025/start_server.py"],
      "cwd": "/Users/christosmantzouranis/code/Hackathon2025"
    }
  }
}
```

### 🔄 **Next Steps:**

1. **Restart Claude Desktop completely** (quit and reopen)
2. **Check MCP servers section** in Claude Desktop settings
3. **Try enabling the server** again

### 🛠️ **If Still Not Working - Alternative Configurations:**

#### Option A: Bash Activation
```json
{
  "mcpServers": {
    "vessel-track-generator": {
      "command": "bash",
      "args": [
        "-c",
        "cd /Users/christosmantzouranis/code/Hackathon2025 && source venv/bin/activate && python start_server.py"
      ]
    }
  }
}
```

#### Option B: Shell Script
```json
{
  "mcpServers": {
    "vessel-track-generator": {
      "command": "/bin/bash",
      "args": [
        "-c",
        "cd /Users/christosmantzouranis/code/Hackathon2025 && source venv/bin/activate && exec python start_server.py"
      ]
    }
  }
}
```

### 🔍 **Common Causes & Solutions:**

#### 1. **Python Path Issues**
- **Problem**: Claude can't find the correct Python interpreter
- **Solution**: Use full path to virtual environment Python
- **Check**: Run `which python` in your venv to get the correct path

#### 2. **Working Directory Issues**
- **Problem**: Server can't find required files
- **Solution**: Set `cwd` to project directory
- **Check**: Ensure all files are in the correct location

#### 3. **Environment Variables**
- **Problem**: Missing environment variables
- **Solution**: Use virtual environment activation
- **Check**: Verify `PATH` includes venv/bin

#### 4. **File Permissions**
- **Problem**: Claude can't execute the script
- **Solution**: Check file permissions
- **Fix**: `chmod +x start_server.py`

#### 5. **Dependencies Missing**
- **Problem**: Required packages not installed
- **Solution**: Reinstall dependencies
- **Fix**: `pip install -r requirements.txt`

### 🧪 **Testing Commands:**

#### Test Server Manually:
```bash
cd /Users/christosmantzouranis/code/Hackathon2025
source venv/bin/activate
python start_server.py
```

#### Test Imports:
```bash
source venv/bin/activate
python -c "import mcp; import vessel_track_generator; print('Success')"
```

#### Run Test Suite:
```bash
source venv/bin/activate
python test_server_startup.py
python verify_setup.py
```

### 📋 **Claude Desktop Config Location:**

**macOS:**
```
~/Library/Application Support/Claude/claude_desktop_config.json
```

**Windows:**
```
%APPDATA%\Claude\claude_desktop_config.json
```

**Linux:**
```
~/.config/claude/claude_desktop_config.json
```

### 🚨 **Emergency Reset:**

If nothing works, try a complete reset:

1. **Remove MCP server from config**
2. **Restart Claude Desktop**
3. **Run setup script again:**
   ```bash
   source venv/bin/activate
   python setup_claude_config.py
   ```
4. **Restart Claude Desktop again**

### 📞 **Still Having Issues?**

If the server still won't enable:

1. **Check Claude Desktop logs** for error messages
2. **Try the alternative configurations** above
3. **Verify all file paths** are correct
4. **Test server startup manually** to isolate the issue

### ✅ **Success Indicators:**

When working correctly, you should see:
- ✅ "vessel-track-generator" appears in MCP servers list
- ✅ Server can be enabled without errors
- ✅ Tools appear in Claude's interface
- ✅ Can generate vessel tracks with prompts

