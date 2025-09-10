# AIS NMEA Data Generator - Hackathon 2025

> 🚢 Generate synthetic AIS/NMEA maritime data with natural language prompts

## Project Overview

This hackathon project creates an LLM-powered AIS (Automatic Identification System) data generator that can take natural language prompts like "Generate AIS NMEA data for 2 ships roaming about the Irish sea" and produce realistic maritime tracking data saved to JSON files.

### Current Implementation Status

**✅ CRAWL Version (Completed)**
- Single ship point-to-point movement
- Realistic AIS data generation
- NMEA sentence formatting
- JSON file output
- REST API interface

**✅ WALK Version (Completed)**
- Multiple ships with realistic routing
- Different ship types (Passenger, Cargo, Fishing, Pilot, High-Speed)
- Varied movement patterns (Ferry routes, Cargo lanes, Fishing circles, Patrol patterns)
- Multi-ship map visualization
- Realistic speeds and behaviors per ship type

**🚧 RUN Version (Next)**
- LLM prompt parsing: "Generate AIS NMEA data for 2 ships roaming about the Irish sea"
- MCP integration
- Natural language interface

## Quick Start

### 1. Set Up Virtual Environment (Recommended)
```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Or use the convenience script
source activate.sh
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Start the Server
```bash
# Make sure venv is activated first!
source venv/bin/activate
python start_server.py
```

The server will be available at `http://localhost:8000`

### 4. Run Quick Demo
```bash
python quick_demo.py
```

This generates sample Irish Sea route data and saves it to JSON files.

### 5. Test Core Functionality
```bash
python test_crawl.py
```

### Convenience Scripts
- `source activate.sh` - Activate venv with helpful info
- `python start_server.py` - Start the FastAPI server  
- `python test_crawl.py` - Test single ship (Crawl version)
- `python test_walk.py` - Test multiple ships (Walk version) 🚢🚢🚢
- `python map_viewer.py` - View single ship on map 🗺️
- `python map_multi_viewer.py` - View multiple ships on map 🗺️

## API Endpoints

### Core Operations
- `GET /` - Server status and info
- `GET /health` - Health check

### Ship Management
- `POST /ships/add` - Add a ship with route
- `GET /ships` - List all active ships
- `GET /ships/irish-sea-demo` - Create demo Irish Sea route
- `DELETE /ships/{mmsi}` - Remove a ship

### Data Generation
- `POST /generate/{mmsi}` - Generate AIS data for specific ship
- `POST /generate-irish-sea-demo` - Generate demo data

### File Management
- `GET /files` - List all generated files
- `GET /files/{filename}` - View file content
- `GET /files/{filename}/download` - Download file

## Example Usage

### Create a Ship Route
```bash
curl -X POST "http://localhost:8000/ships/add" \\
  -H "Content-Type: application/json" \\
  -d '{
    "start_lat": 53.3498,
    "start_lon": -6.2603,
    "end_lat": 53.3090,
    "end_lon": -4.6324,
    "speed_knots": 12.0,
    "ship_name": "HACKATHON_VESSEL",
    "mmsi": 123456789
  }'
```

### Generate AIS Data
```bash
curl -X POST "http://localhost:8000/generate/123456789" \\
  -H "Content-Type: application/json" \\
  -d '{
    "duration_hours": 1.0,
    "report_interval_seconds": 30,
    "output_format": "json",
    "save_to_file": true,
    "filename_prefix": "my_route"
  }'
```

## Output Files

Generated files are saved to `./output/` directory:

### JSON Format
```json
{
  "metadata": {
    "mmsi": 123456789,
    "ship_name": "HACKATHON_VESSEL",
    "generated_at": "2025-09-10T10:30:00Z",
    "total_reports": 120
  },
  "route_summary": {
    "start_position": {"latitude": 53.3498, "longitude": -6.2603},
    "end_position": {"latitude": 53.3090, "longitude": -4.6324}
  },
  "ais_data": [
    {
      "mmsi": 123456789,
      "position": {"latitude": 53.3498, "longitude": -6.2603},
      "speed_knots": 12.0,
      "course_degrees": 85.2,
      "timestamp": "2025-09-10T10:30:00Z"
    }
  ]
}
```

### NMEA Format
```
# AIS/NMEA Data for HACKATHON_VESSEL (MMSI: 123456789)
# Generated: 2025-09-10T10:30:00Z

$GPGGA,103000,5320.9880,N,00615.6180,W,1,08,1.0,10.0,M,0.0,M,,*65
$GPRMC,103000,A,5320.9880,N,00615.6180,W,12.0,85.2,100925,,*7A
```

## Architecture

```
┌─────────────────────┐    ┌─────────────────────┐    ┌─────────────────────┐
│   Natural Language  │───▶│    AIS Generator    │───▶│    JSON Output      │
│      Prompts        │    │   (Core Engine)     │    │      Files          │
└─────────────────────┘    └─────────────────────┘    └─────────────────────┘
                                      │
                           ┌─────────────────────┐
                           │   NMEA Formatter    │
                           │  (Maritime Format)  │
                           └─────────────────────┘
```

## Development Progress

Following the **Crawl → Walk → Run** approach:

1. **✅ Crawl**: Single ship, simple movement ✅ 
2. **🚧 Walk**: Multiple ships, realistic patterns
3. **🚀 Run**: LLM integration, MCP protocol

## Docker Support

```bash
docker-compose up --build
```

Access the API at `http://localhost:8000` and generated files will be in `./output/`

## Technology Stack

- **FastAPI** - REST API framework
- **Python 3.11** - Core language
- **Pydantic** - Data validation
- **Folium** - Interactive map visualization
- **Docker** - Containerization
- **OpenAI GPT** - Future LLM integration

## Contributing

This is a hackathon project! Feel free to:

1. Extend to multiple ships (Walk version)
2. Add LLM prompt parsing (Run version) 
3. Enhance movement patterns
4. Add more maritime data types

## License

Hackathon 2025 Project - Open for collaboration!
