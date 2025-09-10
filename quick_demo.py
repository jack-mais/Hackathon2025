#!/usr/bin/env python3
"""
Quick demo script that generates AIS data and saves to JSON
"""

import sys
import os
import requests
import json
from time import sleep

sys.path.append(os.path.dirname(__file__))

def main():
    print("🚢 AIS Generator Quick Demo - Hackathon 2025")
    print("=" * 50)
    
    # Check if server is running
    try:
        response = requests.get("http://localhost:8000/health")
        if response.status_code == 200:
            print("✅ Server is running")
        else:
            print("❌ Server responded with error")
            return
    except requests.ConnectionError:
        print("❌ Server not running. Please start with: python start_server.py")
        return
    
    print()
    print("🎯 Generating Irish Sea demo data...")
    
    # Generate demo data
    demo_request = {
        "duration_hours": 0.5,  # 30 minutes
        "report_interval_seconds": 60,  # Every minute
        "output_format": "both",
        "save_to_file": True,
        "filename_prefix": "irish_sea_hackathon_demo"
    }
    
    try:
        response = requests.post(
            "http://localhost:8000/generate-irish-sea-demo",
            json=demo_request
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Demo data generated successfully!")
            print(f"📊 Ship: {result['ship_info']['name']} (MMSI: {result['ship_info']['mmsi']})")
            print(f"🛣️  Route: {result['ship_info']['route']}")
            print(f"📈 Reports: {result['data_summary']['total_reports']}")
            print(f"⏱️  Duration: {result['data_summary']['duration_hours']} hours")
            print()
            
            print("💾 Files saved:")
            for format_type, filepath in result['saved_files'].items():
                print(f"  📁 {format_type.upper()}: {filepath}")
            
        else:
            print(f"❌ Error generating demo: {response.text}")
            return
            
    except Exception as e:
        print(f"❌ Request error: {e}")
        return
    
    print()
    print("📂 Listing all output files...")
    
    try:
        response = requests.get("http://localhost:8000/files")
        if response.status_code == 200:
            files_data = response.json()
            print(f"📁 Output directory: {files_data['output_directory']}")
            print(f"📄 Total files: {files_data['count']}")
            print()
            
            for file_info in files_data['files'][:5]:  # Show first 5 files
                print(f"  📄 {file_info['filename']}")
                print(f"     Size: {file_info['size_bytes']} bytes")
                print(f"     Modified: {file_info['modified_at']}")
                print()
                
        else:
            print(f"❌ Error listing files: {response.text}")
            
    except Exception as e:
        print(f"❌ Request error: {e}")
    
    print()
    print("🎉 Demo completed successfully!")
    print("🌐 Check the API docs at: http://localhost:8000/docs")
    print("💾 View your generated files in the ./output/ directory")


if __name__ == "__main__":
    main()
