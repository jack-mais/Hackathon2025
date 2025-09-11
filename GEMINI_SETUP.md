# 🌟 Gemini AI Setup Guide

This project now uses **Google Gemini AI exclusively** for natural language ship generation.

## 🚀 Quick Start

### 1. Get Your Free API Key
Visit: https://aistudio.google.com/app/apikey
- Sign in with your Google account
- Create a new API key
- Copy the key

### 2. Set Environment Variable
```bash
# Option 1: Export in terminal
export GEMINI_KEY='your-api-key-here'

# Option 2: Add to .env file
echo "GEMINI_KEY=your-api-key-here" > .env
```

### 3. Start Using
```bash
# Activate virtual environment
source venv/bin/activate

# Start AI chat interface
python ais_chat.py
```

## 💬 Example Commands

Once in the chat interface, try:

- **"6 ships outside Southampton"**
- **"Generate 3 tankers off Sicily for 8 hours"** 
- **"Create fishing boats in Norwegian waters"**
- **"5 cargo ships from Barcelona to Naples"**

## ✅ What Works

- ✅ **Worldwide Location Recognition**: Southampton, Sicily, Mediterranean, North Sea, etc.
- ✅ **Accurate Ship Counts**: "6 ships" generates exactly 6 ships
- ✅ **Intelligent Duration**: Cargo ships get longer routes automatically
- ✅ **Real File Generation**: JSON data + Interactive HTML maps
- ✅ **Smart Ship Types**: Tankers, cargo, passenger, fishing, patrol vessels

## 🎯 Key Features

### **Single Unified System**
- One tool: `generate_ais_data`
- No more confusing scenarios or regions
- Works for any location worldwide

### **Intelligent Location Parsing**
- Recognizes ports: "Southampton", "Singapore"  
- Understands regions: "North Sea", "Mediterranean"
- Handles descriptions: "off coast of Sicily", "outside Southampton"

### **Realistic Ship Generation**
- Appropriate speeds by ship type
- Region-specific ship names  
- Accurate coordinates and routes
- Industry-standard AIS data

## 🔧 Technical Architecture

```
ais_chat.py
    ↓
AISGeminiClient (pattern matching + tool calls)
    ↓ 
AISMCPServer (single generate_ais_data tool)
    ↓
AISGenerator (unified ship generation)
    ↓
Output: JSON + HTML files
```

## 🚨 Troubleshooting

**"Gemini API key is required"**
→ Set `GEMINI_KEY` environment variable

**"No data generated"**  
→ Your request might not be detected. Try: "Generate X ships near [location]"

**"Unknown location"**
→ Use major ports or seas like "Southampton", "Mediterranean", "North Sea"

---
🌊 **Ready to generate some ships?** Run `python ais_chat.py` and start chatting!
