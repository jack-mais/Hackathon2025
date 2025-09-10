# AIS NMEA Data Generator - Hackathon 2025

> 🚢 Generate synthetic AIS/NMEA maritime data with natural language prompts

## Project Overview

This hackathon project creates an **LLM-powered AIS** (Automatic Identification System) data generator that can take natural language prompts like "Generate AIS NMEA data for 2 ships roaming about the Irish sea" and produce realistic maritime tracking data saved to JSON files.

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

### 2. Set API Key (Optional)
Create a `.env` file:
```env
# Google Gemini (Recommended - Free tier)
GEMINI_KEY=your_gemini_api_key_here

# Or OpenAI (Optional)
OPENAI_API_KEY=your_openai_api_key_here

# No API key? No problem - Demo mode works without any keys!
```

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
- **Natural Language Interface**: "Generate 3 ships in the Irish Sea"
- **Smart Routing**: AI understands ports, ship types, and realistic patterns
- **Multiple LLMs**: Gemini (free), OpenAI, or Demo mode
- **Maritime Knowledge**: Built-in understanding of ship types and behaviors

### 🚢 Realistic Ship Simulation  
- **Ship Types**: Passenger ferries, Cargo ships, Fishing vessels, Patrol boats, High-speed craft
- **Realistic Routes**: Ferry lines, cargo lanes, fishing patterns, patrol circuits
- **Accurate Physics**: Speed, course, turning rates per ship type
- **Rich Metadata**: Names, dimensions, navigation status

### 📊 Professional Output
- **JSON Format**: Structured data with metadata and position reports
- **NMEA Sentences**: Industry-standard marine data format  
- **Interactive Maps**: HTML visualizations with ship tracks and info
- **Time-series Data**: Realistic timestamps and movement progression

## 💬 Example AI Conversations

**User:** "Generate 3 ships in the Irish Sea"  
**AI:** *Creates mixed ship types with realistic routes and saves to JSON*

**User:** "I need 2 cargo ships from Dublin to Liverpool and 1 ferry"  
**AI:** *Generates specific ship types with custom routes*

**User:** "Create a 4-hour simulation with fishing vessels"  
**AI:** *Generates fishing boats with circular patterns for 4 hours*

## 📁 File Structure (Clean & Organized)

```
📦 AIS Generator
├── 🤖 ais_chat.py              # Main AI chat interface
├── 🧪 test_all.py              # Comprehensive test suite
├── ⚡ quick_demo.py             # Quick demo generation
├── 🗺️  map_multi_viewer.py      # Multi-ship map visualization
├── 🗺️  map_viewer.py            # Single ship map visualization  
├── 🌐 start_server.py          # FastAPI server
├── 📁 src/                     # Core source code
│   ├── core/                   # Data models & file I/O
│   ├── generators/             # AIS & multi-ship generators
│   ├── llm_integration/        # Gemini, OpenAI, Demo clients
│   ├── mcp_integration/        # MCP server for LLM tools
│   └── main.py                # FastAPI application
├── 📁 output/                  # Generated JSON & NMEA files
├── 📄 requirements.txt         # Python dependencies
└── 📋 README.md               # This file
```

## 🌟 Why This Project Rocks

### ✅ **Production Ready**
- Clean, modular codebase
- Comprehensive error handling  
- Professional logging and output
- Docker containerization support

### ✅ **LLM Flexibility** 
- **Gemini**: Free tier, fast responses (recommended)
- **OpenAI**: Enterprise-grade accuracy
- **Demo Mode**: Works without any API keys

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

## 🛠️ Technical Architecture

**LLM Layer** → **MCP Protocol** → **Multi-Ship Generator** → **JSON/NMEA Output** → **Interactive Maps**

📐 **[View Complete Technical Architecture →](TECHNICAL_ARCHITECTURE.md)**

## 🚢 Sample Output

```json
{
  "metadata": {
    "scenario_name": "gemini_irish_sea_3_ships",
    "generated_at": "2025-09-10T14:30:00Z", 
    "total_ships": 3,
    "duration_hours": 2.0
  },
  "ships": [
    {
      "ship_name": "CELTIC_SEA_1",
      "mmsi": 123456000,
      "ship_type": "PASSENGER",
      "route_type": "FERRY",
      "positions": [...]
    }
  ]
}
```

## 🏆 Hackathon Value

- **🚀 Innovative**: AI-powered maritime data generation
- **🔧 Practical**: Industry-applicable output formats  
- **📈 Scalable**: Clean architecture, easy to extend
- **🎯 Demonstrable**: Visual maps, real-time chat, comprehensive tests
- **💡 Accessible**: Works with free APIs or no APIs at all

---

**🌊 Ready to generate some ships? Run `python ais_chat.py` and start chatting!** ⚓