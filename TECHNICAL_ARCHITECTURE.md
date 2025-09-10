# 🏗️ AIS Generator - Technical Architecture

## System Overview

This hackathon project implements a complete **LLM-powered maritime AIS data generation system** with progressive complexity following the **Crawl → Walk → Run** approach.

## 📐 High-Level Architecture

```
┌─────────────────────┐    ┌─────────────────────┐    ┌─────────────────────┐
│   Natural Language  │───▶│      LLM + MCP     │───▶│   AIS Generator     │
│  "Generate 3 ships" │    │   Tool Integration  │    │  Multi-Ship Engine  │
└─────────────────────┘    └─────────────────────┘    └─────────────────────┘
                                      │                          │
                           ┌─────────────────────┐    ┌─────────────────────┐
                           │  Interactive Maps   │◄───│    JSON Output     │
                           │   (Folium/HTML)     │    │      Files          │
                           └─────────────────────┘    └─────────────────────┘
```

## 🔄 Progressive Development Stages

### Stage 1: CRAWL Version
```
┌─────────────────────┐    ┌─────────────────────┐    ┌─────────────────────┐
│    Simple Route     │───▶│  Single Ship Gen.   │───▶│    JSON Output      │
│ Dublin → Holyhead   │    │  Point-to-Point     │    │   + Map Viewer      │
└─────────────────────┘    └─────────────────────┘    └─────────────────────┘
```

### Stage 2: WALK Version  
```
┌─────────────────────┐    ┌─────────────────────┐    ┌─────────────────────┐
│  Multiple Ship      │───▶│  Multi-Ship Gen.    │───▶│   Multi-Ship JSON   │
│  Types & Routes     │    │  Realistic Patterns │    │   + Multi-Map View  │
└─────────────────────┘    └─────────────────────┘    └─────────────────────┘
```

### Stage 3: RUN Version
```
┌─────────────────────┐    ┌─────────────────────┐    ┌─────────────────────┐
│  Natural Language   │───▶│    LLM Client       │───▶│   MCP Tool Server   │
│     CLI Chat        │    │  (OpenAI GPT)       │    │  (4 Maritime Tools) │
└─────────────────────┘    └─────────────────────┘    └─────────────────────┘
                                      │                          │
                                      ▼                          ▼
┌─────────────────────┐    ┌─────────────────────┐    ┌─────────────────────┐
│ Conversation Mgmt   │◄───│  Response Handler   │◄───│  Generator Engine   │
│   + History         │    │   + File Saving     │    │   + Map Creation    │
└─────────────────────┘    └─────────────────────┘    └─────────────────────┘
```

## 🧱 Component Details

### Core Data Models (`src/core/models.py`)
```
Position ──► ShipState ──► Route
    │           │           │
    │           │           ▼
    │           ▼       RouteType (Enum)
    │     NavigationStatus 
    │          (Enum)
    ▼
ShipType (Enum)
```

### Ship Generation Pipeline
```
MultiShipGenerator
    │
    ├── generate_irish_sea_scenario()
    │   ├── Choose ship types (Passenger, Cargo, Fishing, Pilot, High-Speed)
    │   ├── Assign realistic routes (Ferry, Cargo lanes, Fishing circles, Patrol)
    │   ├── Create RealisticShipMovement instances
    │   └── Generate waypoint-based movement
    │
    └── generate_custom_ships()
        ├── Parse user specifications
        ├── Map ports to coordinates
        └── Create custom movement patterns
```

### MCP Tool Server (`src/mcp_integration/mcp_server.py`)
```
AISMCPServer
    │
    ├── generate_irish_sea_scenario
    │   └── Parameters: num_ships, duration_hours, report_interval
    │
    ├── generate_custom_ships  
    │   └── Parameters: ships[], duration_hours, scenario_name
    │
    ├── list_available_ports
    │   └── Returns: 8 Irish Sea ports with coordinates
    │
    └── get_ship_types
        └── Returns: 5 ship types with descriptions
```

### LLM Integration (`src/llm_integration/llm_client.py`)
```
AISLLMClient
    │
    ├── OpenAI API Integration
    │   ├── GPT-3.5-turbo model
    │   ├── Function calling capability
    │   └── Conversation history management
    │
    ├── Tool Call Processing
    │   ├── Parse LLM tool requests
    │   ├── Route to MCP server
    │   └── Format responses
    │
    └── Domain-Specific System Prompt
        ├── Maritime knowledge base
        ├── Port and ship type awareness
        └── Natural language understanding
```

## 🗺️ Data Flow Architecture

### Input Processing
```
User Request
    │
    ▼
"Generate 3 ships in the Irish Sea"
    │
    ▼
LLM Processing (OpenAI GPT)
    │
    ▼
Tool Call: generate_irish_sea_scenario({num_ships: 3})
    │
    ▼
MCP Server Tool Execution
```

### Ship Generation
```
MultiShipGenerator.generate_irish_sea_scenario()
    │
    ├── Ship 1: PASSENGER (CELTIC SEA_1)
    │   ├── Route: Dublin → Holyhead  
    │   ├── Speed: 12 knots
    │   └── Waypoints: [4 points with realistic deviations]
    │
    ├── Ship 2: CARGO (IRISH CARGO_2)  
    │   ├── Route: Dublin → Liverpool
    │   ├── Speed: 9 knots (adjusted for cargo type)
    │   └── Waypoints: [4 commercial waypoints]
    │
    └── Ship 3: FISHING (ATLANTIC FISHER_3)
        ├── Route: Circular fishing pattern
        ├── Speed: 6 knots (adjusted for fishing)
        └── Waypoints: [8 circular pattern points]
```

### Movement Simulation
```
RealisticShipMovement.generate_movement()
    │
    ├── For each time interval (5 minutes):
    │   ├── Calculate progress ratio along route
    │   ├── Interpolate position between waypoints  
    │   ├── Determine navigation status (En Route/At Anchor/Fishing)
    │   ├── Calculate realistic bearing to next waypoint
    │   └── Create ShipState with AIS data
    │
    └── Generate complete movement history
```

### Output Generation
```
Generated Ship States
    │
    ├── JSON Format (FileOutputManager)
    │   ├── Metadata (ship info, timing, scenario)
    │   ├── Route summary (start/end positions)
    │   └── AIS data array (position reports)
    │
    ├── NMEA Format (NMEAFormatter) 
    │   ├── GPGGA sentences (GPS position)
    │   ├── GPRMC sentences (recommended minimum)
    │   └── Timestamped maritime data
    │
    └── Interactive Map (Folium)
        ├── Ship tracks with colored paths
        ├── Start/end markers with popups
        ├── Intermediate waypoint circles
        └── Type-based legend
```

## 🔧 Technology Stack

### Core Technologies
- **Python 3.13** - Main language
- **FastAPI** - REST API framework (future expansion)
- **Pydantic** - Data validation and modeling
- **OpenAI API** - LLM integration
- **Asyncio** - Asynchronous processing

### Visualization
- **Folium** - Interactive map generation
- **Rich** - Terminal UI and formatting
- **HTML/JavaScript** - Map interaction

### Data Processing
- **JSON** - Primary data format
- **NMEA 0183** - Maritime data standard
- **NumPy-style calculations** - Position interpolation
- **Haversine formula** - Nautical distance calculations

### Development Tools
- **Virtual Environment** - Dependency isolation
- **Git** - Version control
- **Docker** - Containerization support
- **pytest** - Testing framework (extensible)

## 🚦 Execution Flow

### CLI Chat Session
```
1. User: "Generate 3 ships in the Irish Sea"
   ↓
2. AISLLMClient processes natural language
   ↓  
3. OpenAI GPT determines tool call needed
   ↓
4. MCP Server receives: generate_irish_sea_scenario({num_ships: 3})
   ↓
5. MultiShipGenerator creates 3 realistic ships
   ↓
6. Movement simulation generates position reports
   ↓
7. FileOutputManager saves JSON data
   ↓
8. LLM formats user-friendly response
   ↓
9. User sees: "✅ Generated 3 ships! Saved to: output/scenario_xxx.json"
```

### Map Visualization Flow
```
1. python map_multi_viewer.py
   ↓
2. Load latest multi-ship JSON file
   ↓
3. Parse ship data and routes
   ↓
4. Create Folium map centered on Irish Sea
   ↓
5. Add colored ship tracks for each vessel
   ↓
6. Add markers (start=green, end=colored, waypoints=circles)
   ↓
7. Generate interactive HTML map
   ↓
8. Open in browser with ship details on click
```

## 📊 Performance Characteristics

### Data Generation Speed
- **Single ship**: ~0.1 seconds
- **Multi-ship (5)**: ~0.5 seconds  
- **Complex scenarios**: ~2 seconds
- **LLM response**: ~3-5 seconds (network dependent)

### Output File Sizes
- **Single ship JSON**: ~10-15 KB
- **Multi-ship JSON**: ~50-100 KB
- **NMEA files**: ~25% of JSON size
- **Interactive maps**: ~20-30 KB HTML

### Scalability
- **Max ships**: 10 (UI optimized)
- **Max simulation time**: 24 hours
- **Max waypoints**: 20 per ship
- **Memory usage**: ~10 MB for large scenarios

## 🔒 Security & Configuration

### Environment Variables
```
OPENAI_API_KEY=sk-xxx...    # Required for LLM features
LOG_LEVEL=INFO              # Optional logging
DEBUG_MODE=false            # Optional debugging
```

### API Key Security
- Environment variable only (not hardcoded)
- Graceful fallback when missing
- Local processing without external calls for core features

## 🎯 Architectural Benefits

### Modularity
- Clear separation between Crawl/Walk/Run versions
- Pluggable ship types and route patterns
- Independent visualization system

### Extensibility  
- Easy to add new ship types
- Simple route pattern expansion
- MCP tool interface allows new capabilities

### Maintainability
- Type hints throughout
- Clear class hierarchies  
- Comprehensive error handling

### Hackathon Optimized
- Progressive complexity demonstration
- Visual impact with maps
- Professional code organization
- Easy to demo and extend

---

*This architecture demonstrates modern software engineering practices combined with domain-specific maritime knowledge and cutting-edge AI integration - perfect for hackathon judging criteria.*
