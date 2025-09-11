# AIS NMEA Data Generator - Hackathon 2025

> 🚢 Generate synthetic AIS/NMEA maritime data with natural language prompts

## Project Overview

This hackathon project creates an **LLM-powered AIS** (Automatic Identification System) data generator that can take natural language prompts like "Generate AIS NMEA data for 2 ships roaming about the Irish sea" or "Create a convoy off the coast of Sicily" and produce realistic maritime tracking data with worldwide port coverage, saved to JSON files with interactive maps.

### ✅ **COMPLETED** - All Phases Functional

**🐛 CRAWL** - Single ship point-to-point movement  
**🚶 WALK** - Multiple ships with realistic routing  
**🏃 RUN** - LLM integration with natural language interface  

## 🚀 Quick Start

### 1. Set Up Environment
```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies  
pip install -r requirements.txt
```

### 2. Set API Key
Create a `.env` file in the project root:
```env
# Google Gemini (Primary - Free tier with 1500 requests/day)
GEMINI_KEY=your_gemini_api_key_here

# Optional: OpenAI (Alternative LLM)
OPENAI_API_KEY=your_openai_api_key_here
```

**🔑 Get your free Gemini API key:**
1. Visit [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Sign in with Google account
3. Create API key (free tier: 1500 requests/day)
4. Copy to `.env` file as shown above

### 3. Start Using

**🤖 AI Chat Interface (Recommended)**
```bash
python ais_chat.py
```

**⚡ Quick Demo**
```bash
python quick_demo.py
```

**🧪 Full Test Suite**
```bash
python test_all.py
```

**🗺️ View Generated Data on Maps**
```bash
python map_multi_viewer.py    # Multi-ship visualization
python map_viewer.py          # Single ship visualization
```

## 🎯 Core Features

### 🤖 AI-Powered Generation
- **Natural Language Interface**: "Generate 3 ships near Sicily" or "Create cargo convoy from Barcelona to Naples"
- **Smart Routing**: AI understands worldwide ports, ship types, and realistic patterns
- **Primary LLM**: Google Gemini (free tier 1500 requests/day)
- **Maritime Knowledge**: Built-in understanding of ship types, worldwide ports, and behaviors

### 🌍 Worldwide Port Coverage
- **Irish Sea**: Dublin, Liverpool, Holyhead, Belfast, Cork, Cardiff
- **Mediterranean**: Barcelona, Marseille, Naples, Venice, Athens, Istanbul
- **North Sea**: Rotterdam, Hamburg, Antwerp, Copenhagen, Oslo
- **Atlantic**: Lisbon, Southampton, Brest, Cadiz
- **Asia**: Singapore, Shanghai, Hong Kong, Tokyo, Mumbai
- **Americas**: New York, Los Angeles, Miami, Santos, Vancouver

### 🚢 Realistic Ship Simulation  
- **Ship Types**: Passenger ferries, Cargo ships, Fishing vessels, Pilot boats, High-speed craft
- **Realistic Routes**: Ferry lines, cargo lanes, fishing patterns, patrol circuits
- **Accurate Physics**: Speed, course, turning rates per ship type
- **Rich Metadata**: Names, dimensions, navigation status, MMSI codes

### 📊 Professional Output
- **JSON Format**: Structured data with metadata and position reports
- **NMEA Sentences**: Industry-standard marine data format  
- **Interactive Maps**: HTML visualizations with ship tracks and info
- **Time-series Data**: Realistic timestamps and movement progression

## 💬 Example AI Conversations

**User:** "Generate a convoy off the coast of Sicily"  
**AI:** *Creates mixed ship types around Sicily with realistic Mediterranean routes*

**User:** "I need 2 cargo ships from Barcelona to Naples"  
**AI:** *Generates cargo vessels with specific Mediterranean route*

**User:** "Create fishing vessels in Norwegian waters"  
**AI:** *Generates Norwegian fishing fleet with circular fishing patterns*

**User:** "Generate 3 ships near Singapore for 6 hours"  
**AI:** *Creates Asian port scenario with cargo and passenger ships*

## 📁 File Structure (Clean & Organized)

```
📦 AIS Generator
├── 🤖 ais_chat.py              # Main Gemini AI chat interface
├── ⚡ quick_demo.py             # Quick demo generation
├── 🗺️  map_multi_viewer.py      # Multi-ship map visualization
├── 🗺️  map_viewer.py            # Single ship map visualization  
├── 🌐 start_server.py          # FastAPI server
├── 📁 src/                     # Core source code
│   ├── core/                   # Data models & file I/O
│   │   ├── models.py           # Ship, Position, Route models
│   │   └── file_output.py      # JSON/NMEA file management
│   ├── generators/             # AIS & multi-ship generators
│   │   ├── ais_generator.py    # Unified worldwide generator
│   │   └── nmea_formatter.py   # NMEA 0183 sentence formatting
│   ├── llm_integration/        # LLM clients
│   │   └── gemini_client.py    # Google Gemini API client
│   ├── mcp_integration/        # MCP server for LLM tools
│   │   └── mcp_server.py       # Maritime tool server
│   └── main.py                # FastAPI application
├── 🧪 Test Suite               # Comprehensive testing
│   ├── test_all.py             # Run all tests
│   ├── test_crawl.py           # Single ship tests
│   ├── test_walk.py            # Multi-ship tests
│   ├── test_gemini_only.py     # Gemini integration tests
│   ├── test_worldwide_context.py # Global port tests
│   ├── test_sophisticated_scenarios.py # Complex scenarios
│   └── test_integrated_map_generation.py # Map generation tests
├── 📁 output/                  # Generated files (JSON, HTML maps, KML)
├── 🐳 docker-compose.yml       # Docker deployment
├── 📄 requirements.txt         # Python dependencies
├── 📋 TECHNICAL_ARCHITECTURE.md # Detailed technical docs
└── 📋 README.md               # This file
```

## 🌟 Why This Project Rocks

### ✅ **Production Ready**
- Clean, modular codebase
- Comprehensive error handling  
- Professional logging and output
- Docker containerization support

### ✅ **LLM Integration** 
- **Google Gemini**: Primary AI engine with generous free tier (1500 requests/day)
- **OpenAI GPT**: Optional alternative for enterprise use
- **Natural Language Processing**: Understands complex maritime requests
- **Worldwide Context**: AI knows global ports and realistic shipping routes

### ✅ **Real-World Applicable**
- Industry-standard NMEA format
- Realistic maritime physics and behaviors
- Professional visualization and analysis
- Extensible architecture for new features

## 🎮 Try These Commands

```bash
# Start AI chat (auto-detects available LLMs)
python ais_chat.py

# Run comprehensive tests
python test_all.py  

# Generate quick demo data
python quick_demo.py

# View ships on interactive map
python map_multi_viewer.py

# Start REST API server
python start_server.py
```

## 🧪 Comprehensive Testing

The project includes extensive test coverage for all functionality:

```bash
# Run all tests (recommended)
python test_all.py

# Specific test categories
python test_crawl.py              # Single ship movement tests
python test_walk.py               # Multi-ship scenario tests
python test_gemini_only.py        # Gemini AI integration tests
python test_worldwide_context.py  # Global port coverage tests
python test_sophisticated_scenarios.py # Complex maritime scenarios
python test_integrated_map_generation.py # Map visualization tests
```

**Test Coverage:**
- ✅ Single ship point-to-point movement
- ✅ Multi-ship complex scenarios
- ✅ Gemini AI natural language processing
- ✅ Worldwide port database (50+ major ports)
- ✅ Interactive map generation (HTML + KML)
- ✅ JSON and NMEA output format validation
- ✅ Ship physics and navigation accuracy

## 🛠️ Technical Architecture

### 🔄 **Modern AI-Driven Pipeline**

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Natural Language│───▶│   Gemini AI     │───▶│  MCP Tools      │
│  "Generate ships │    │   LLM Client    │    │  Server         │
│   near Sicily"   │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │                        │
                                ▼                        ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ Worldwide Port  │◄───│  AI Request     │───▶│ Multi-Ship      │
│ Database (50+)  │    │  Processing     │    │ Generator       │
│ • Mediterranean │    │                 │    │                 │
│ • North Sea     │    └─────────────────┘    └─────────────────┘
│ • Atlantic      │                                     │
│ • Asia/Americas │                                     ▼
└─────────────────┘              ┌─────────────────────────────────┐
                                 │   Realistic Ship Movement       │
                                 │ • Physics-based routing         │
                                 │ • Ship type behaviors          │
                                 │ • Maritime navigation status   │
                                 │ • Time-series position data    │
                                 └─────────────────────────────────┘
                                              │
                     ┌────────────────────────┼────────────────────────┐
                     ▼                        ▼                        ▼
           ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
           │  JSON Files     │    │ Interactive     │    │  NMEA Sentences │
           │ • Ship metadata │    │ HTML Maps       │    │ • Industry std. │
           │ • AIS positions │    │ • Ship tracks   │    │ • Real-time     │
           │ • Timestamps    │    │ • Info popups   │    │ • GPS format    │
           └─────────────────┘    └─────────────────┘    └─────────────────┘
                     │                        │                        │
                     └────────────────────────┼────────────────────────┘
                                              ▼
                              ┌─────────────────────────────────┐
                              │      Additional Outputs         │
                              │ • KML files (Google Earth)     │
                              │ • FastAPI REST endpoints       │
                              │ • Docker containerization      │
                              └─────────────────────────────────┘
```

### 🧭 **Core System Flow**

1. **🗣️ Natural Language Input**: User describes maritime scenario
2. **🧠 Gemini AI Processing**: LLM understands intent and context
3. **🔧 MCP Tool Selection**: Routes to appropriate maritime generation tools
4. **🌍 Port Database Lookup**: Validates and selects from 50+ worldwide ports
5. **🚢 Multi-Ship Generation**: Creates realistic ships with proper physics
6. **📊 Data Processing**: Generates time-series position data with AIS compliance
7. **💾 Multi-Format Output**: Saves to JSON, HTML maps, NMEA sentences, KML
8. **📱 Visualization**: Interactive maps with ship tracking and metadata

### ⚡ **Key Architecture Benefits**
- **🤖 AI-First Design**: Natural language drives the entire pipeline
- **🌍 Global Scale**: Worldwide port database with regional expertise
- **🔧 Modular Components**: Clean separation between AI, data, and output layers
- **📊 Multi-Format**: Industry-standard outputs for various use cases
- **🧪 Fully Tested**: Comprehensive test suite for all components

📐 **[View Complete Technical Architecture →](TECHNICAL_ARCHITECTURE.md)**

## 🚢 Sample Output

```json
{
  "metadata": {
    "scenario_name": "gemini_scenario_mediterranean_convoy",
    "generated_at": "2025-09-10T15:10:55.986458",
    "total_ships": 3,
    "format": "Multi-ship AIS/NMEA JSON format"
  },
  "ships": {
    "123456000": {
      "ship_info": {
        "mmsi": 123456000,
        "ship_name": "MEDITERRANEAN STAR_1",
        "ship_type": "PASSENGER",
        "total_reports": 73
      },
      "route_summary": {
        "start_position": {
          "latitude": 41.3851,
          "longitude": 2.1734,
          "timestamp": "2025-09-10T15:10:55.984509"
        },
        "end_position": {
          "latitude": 42.1481,
          "longitude": 3.4577,
          "timestamp": "2025-09-10T21:10:55.984509"
        }
      },
      "ais_data": [
        {
          "mmsi": 123456000,
          "latitude": 41.3851,
          "longitude": 2.1734,
          "speed_knots": 12.0,
          "course": 45.2,
          "timestamp": "2025-09-10T15:10:55.984509",
          "navigation_status": "UNDER_WAY_USING_ENGINE"
        }
      ]
    }
  }
}
```

**Output includes:**
- 🗺️ **Interactive HTML maps** with ship tracks and info popups
- 📄 **KML files** for Google Earth visualization
- 📊 **NMEA sentences** for marine system integration
- 🔢 **Structured JSON** for data analysis and processing

## 🏆 Hackathon Value

- **🚀 Innovative**: AI-powered maritime data generation
- **🔧 Practical**: Industry-applicable output formats  
- **📈 Scalable**: Clean architecture, easy to extend
- **🎯 Demonstrable**: Visual maps, real-time chat, comprehensive tests
- **💡 Accessible**: Works with free APIs or no APIs at all

---

## 🚀 Getting Started

1. **Clone & Setup**: `git clone` → `pip install -r requirements.txt`
2. **Get Gemini Key**: [Free API key from Google AI Studio](https://aistudio.google.com/app/apikey)
3. **Configure**: Create `.env` file with `GEMINI_KEY=your-api-key`
4. **Start Chatting**: `python ais_chat.py`

**🐳 Docker Alternative**: `docker-compose up` (includes FastAPI server on port 8000)

**🌊 Ready to generate some ships? Run `python ais_chat.py` and start chatting with Gemini AI!** ⚓

### 📈 Generated Data Usage
- **Maritime Research**: Simulate ship traffic patterns for analysis
- **System Testing**: Generate test data for maritime software
- **Education**: Learn about AIS data format and ship behaviors  
- **Visualization**: Create compelling maritime visualizations
- **Machine Learning**: Training data for maritime AI models