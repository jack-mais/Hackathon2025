#!/usr/bin/env python3
"""
Quick start script for the AIS Generator API
"""

import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(__file__))

if __name__ == "__main__":
    import uvicorn
    from src.main import app
    
    print("🚢 Starting AIS NMEA Data Generator - Hackathon 2025")
    print("=" * 60)
    print("🌐 Server will be available at: http://localhost:8000")
    print("📖 API docs at: http://localhost:8000/docs")
    print("🏃 Crawl version: Single ship point-to-point movement")
    print("💾 Output files saved to: ./output/")
    print("=" * 60)
    print()
    print("Quick demo API calls:")
    print("1. Create Irish Sea demo: POST /generate-irish-sea-demo")
    print("2. List generated files: GET /files")
    print("3. View file content: GET /files/{filename}")
    print()
    print("Starting server...")
    
    # Create output directory if it doesn't exist
    os.makedirs("output", exist_ok=True)
    
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8000,
        log_level="info"
    )
