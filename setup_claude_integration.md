# Adding Vessel Track Generator MCP to Claude

## Method 1: Claude Desktop (Recommended)

### Step 1: Find Claude Desktop Config File

The config file location depends on your operating system:

**macOS:**
```bash
~/Library/Application Support/Claude/claude_desktop_config.json
```

**Windows:**
```bash
%APPDATA%\Claude\claude_desktop_config.json
```

**Linux:**
```bash
~/.config/claude/claude_desktop_config.json
```

### Step 2: Create or Edit Config File

If the file doesn't exist, create it. If it exists, add the vessel track generator to the existing `mcpServers` section.

**For macOS (your system):**
```json
{
  "mcpServers": {
    "vessel-track-generator": {
      "command": "python",
      "args": ["/Users/christosmantzouranis/code/Hackathon2025/start_server.py"],
      "cwd": "/Users/christosmantzouranis/code/Hackathon2025",
      "env": {
        "PATH": "/Users/christosmantzouranis/code/Hackathon2025/venv/bin:/usr/local/bin:/usr/bin:/bin"
      }
    }
  }
}
```

### Step 3: Restart Claude Desktop

Close and reopen Claude Desktop for the changes to take effect.

## Method 2: Using Virtual Environment Path

If you want to use the virtual environment directly:

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

## Method 3: Alternative Config (if above doesn't work)

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

## Verification

After adding the MCP server:

1. **Restart Claude Desktop**
2. **Check for MCP tools**: You should see vessel track generation tools available
3. **Test with a prompt**: Try "Generate tracks for 5 cargo ships from Rotterdam to Singapore"

## Troubleshooting

### If the MCP server doesn't appear:

1. **Check the config file syntax**: Make sure JSON is valid
2. **Verify paths**: Ensure all paths in the config are correct
3. **Check permissions**: Make sure the script is executable
4. **Test manually**: Run the server manually to ensure it works:
   ```bash
   cd /Users/christosmantzouranis/code/Hackathon2025
   source venv/bin/activate
   python start_server.py
   ```

### Common Issues:

- **Python path issues**: Use the full path to the virtual environment's Python
- **Working directory**: Make sure the `cwd` is set to the project directory
- **Environment variables**: Include the virtual environment's bin directory in PATH

## Available Tools in Claude

Once connected, you'll have access to these tools:

1. **generate_vessel_tracks**: Generate vessel tracks from natural language prompts
2. **export_tracks_geojson**: Export generated tracks as GeoJSON format
3. **get_track_statistics**: Get statistics about generated vessel tracks

## Example Usage in Claude

After setup, you can ask Claude:

- "Generate tracks for 20 vessels that are class A and class B performing point-to-point voyages"
- "Create 5 cargo ship tracks from Rotterdam to Singapore"
- "Generate fishing vessel tracks with random patterns for 12 hours"
- "Export the last generated tracks as GeoJSON"
- "Show me statistics for the generated vessel tracks"
