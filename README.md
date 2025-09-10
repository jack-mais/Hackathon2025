# Vessel Track Generator MCP Server

A Model Context Protocol (MCP) server that generates realistic vessel tracks based on natural language prompts. This system can create maritime vessel tracks for different vessel classes, voyage types, and routes.

## Features

- **Natural Language Processing**: Parse complex prompts to extract vessel parameters
- **Multiple Vessel Classes**: Support for Class A, Class B, cargo ships, tankers, fishing vessels, passenger ships, and yachts
- **Various Voyage Types**: Point-to-point, random, circular patrol, fishing patterns
- **Geographic Routing**: Realistic routes between major ports and coastal areas
- **MCP Integration**: Full MCP server with tools for generation, export, and analysis
- **GeoJSON Export**: Export generated tracks in standard GeoJSON format

## Installation

1. **Create a virtual environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Adding to Claude Desktop

The easiest way to use this MCP server is with Claude Desktop:

1. **Automatic Setup** (Recommended):
   ```bash
   source venv/bin/activate
   python setup_claude_config.py
   ```

2. **Manual Setup**: Follow the instructions in `setup_claude_integration.md`

3. **Restart Claude Desktop** after setup

4. **Verify Setup**:
   ```bash
   source venv/bin/activate
   python verify_setup.py
   ```

### Starting the MCP Server Manually

```bash
source venv/bin/activate
python start_server.py
```

### Example Prompts

The system can understand natural language prompts like:

- `"create tracks of 20 vessels that are class a and class b that performed point to point voyages"`
- `"5 cargo ships from Rotterdam to Singapore"`
- `"10 fishing vessels with random patterns for 12 hours"`
- `"3 tankers from Hamburg to New York"`
- `"15 yachts with circular patrol patterns"`

### Available Tools

1. **generate_vessel_tracks**: Generate vessel tracks from natural language prompts
2. **export_tracks_geojson**: Export generated tracks as GeoJSON
3. **get_track_statistics**: Get statistics about generated tracks

### Testing

Run the test suite to verify functionality:

```bash
source venv/bin/activate
python test_vessel_tracks.py
python test_mcp_server.py
```

## Architecture

### Core Components

- **VesselPromptParser**: Parses natural language prompts to extract parameters
- **VesselTrackGenerator**: Generates realistic vessel tracks based on parameters
- **VesselTrackMCPServer**: Main service class that coordinates the generation
- **MCPVesselTrackServer**: MCP server implementation with tool handlers

### Supported Parameters

- **Vessel Count**: Number of vessels to generate
- **Vessel Classes**: A, B, cargo, tanker, fishing, passenger, yacht
- **Voyage Types**: point_to_point, random, circular, patrol, fishing_pattern
- **Duration**: Time span for the tracks (in hours)
- **Regions**: Start and end locations for point-to-point voyages

### Geographic Coverage

The system includes coordinates for major ports:
- Rotterdam, Hamburg, Antwerp, London
- New York, Los Angeles
- Tokyo, Shanghai, Singapore
- Dubai, Sydney, Cape Town

## Example Output

When you run a prompt like `"5 cargo ships from Rotterdam to Singapore"`, the system will:

1. Parse the prompt to extract: 5 vessels, cargo class, point-to-point voyage, Rotterdam to Singapore
2. Generate 5 realistic cargo ship tracks with proper MMSI numbers
3. Create tracks with appropriate speed ranges for cargo ships
4. Generate route points from Rotterdam (51.924, 4.478) to Singapore (1.352, 103.819)
5. Return a summary with track IDs for further analysis or export

## File Structure

```
├── mcp_server_integration.py    # Main MCP server implementation
├── vessel_track_generator.py    # Core track generation logic
├── start_server.py             # Server startup script
├── test_vessel_tracks.py       # Core functionality tests
├── test_mcp_server.py          # MCP server tests
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

## Dependencies

- `mcp>=1.0.0`: Model Context Protocol library
- `geopy>=2.3.0`: Geographic calculations
- `numpy>=1.24.0`: Numerical computations

## License

This project is part of Hackathon2025.
