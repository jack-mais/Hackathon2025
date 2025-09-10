"""Main FastAPI application for AIS NMEA Data Generator"""

from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional
import json
import io
from datetime import datetime

from .generators.ais_generator import AISGenerator, SimpleShipMovement
from .generators.nmea_formatter import NMEAFormatter
from .core.models import Position, Route
from .core.file_output import FileOutputManager


app = FastAPI(
    title="AIS NMEA Data Generator",
    description="Hackathon 2025 - Generate synthetic AIS/NMEA maritime data",
    version="0.1.0"
)

# Global instances
generator = AISGenerator()
formatter = NMEAFormatter()
file_manager = FileOutputManager()


class RouteRequest(BaseModel):
    """Request model for creating routes"""
    start_lat: float
    start_lon: float
    end_lat: float
    end_lon: float
    speed_knots: float = 10.0
    ship_name: str = "TEST_VESSEL"
    mmsi: int = 123456789


class GenerateRequest(BaseModel):
    """Request model for generating data"""
    duration_hours: float = 1.0
    report_interval_seconds: int = 30
    output_format: str = "json"  # "json", "nmea", "both"
    save_to_file: bool = True  # Whether to save to file
    filename_prefix: str = "ais_route"  # Prefix for saved files


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "AIS NMEA Data Generator - Hackathon 2025",
        "version": "0.1.0",
        "status": "running",
        "crawl_mode": "Single ship point-to-point movement"
    }


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}


@app.post("/ships/add")
async def add_ship(route_request: RouteRequest):
    """Add a ship with a route (Crawl version - single ship)"""
    try:
        # Create route
        route = generator.create_simple_route(
            route_request.start_lat,
            route_request.start_lon,
            route_request.end_lat,
            route_request.end_lon,
            route_request.speed_knots
        )
        
        # Add ship
        ship = generator.add_ship(route, route_request.mmsi, route_request.ship_name)
        
        return {
            "message": "Ship added successfully",
            "ship_details": {
                "mmsi": route_request.mmsi,
                "name": route_request.ship_name,
                "route": {
                    "start": {"lat": route_request.start_lat, "lon": route_request.start_lon},
                    "end": {"lat": route_request.end_lat, "lon": route_request.end_lon},
                    "speed": route_request.speed_knots
                },
                "distance_nm": ship.total_distance_nm,
                "estimated_time_hours": ship.total_time_hours,
                "bearing": ship.bearing
            }
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/ships/irish-sea-demo")
async def create_irish_sea_demo():
    """Create a demo ship route in the Irish Sea"""
    route = generator.generate_sample_irish_sea_route()
    mmsi = 123456001
    ship_name = "IRISH_SEA_DEMO"
    
    ship = generator.add_ship(route, mmsi, ship_name)
    
    return {
        "message": "Demo Irish Sea route created",
        "ship_details": {
            "mmsi": mmsi,
            "name": ship_name,
            "route": "Dublin to Holyhead",
            "distance_nm": ship.total_distance_nm,
            "estimated_time_hours": ship.total_time_hours,
            "bearing": ship.bearing
        }
    }


@app.post("/generate/{ship_mmsi}")
async def generate_data(ship_mmsi: int, request: GenerateRequest):
    """Generate AIS/NMEA data for a specific ship"""
    
    # Find the ship
    ship = None
    for s in generator.active_ships:
        if s.mmsi == ship_mmsi:
            ship = s
            break
    
    if not ship:
        raise HTTPException(status_code=404, detail=f"Ship with MMSI {ship_mmsi} not found")
    
    # Generate data
    ship_states = list(ship.generate_movement(
        request.duration_hours, 
        request.report_interval_seconds
    ))
    
    # Save to file if requested
    saved_files = {}
    if request.save_to_file:
        try:
            saved_files = file_manager.save_route_data(
                ship_states, 
                request.filename_prefix, 
                request.output_format
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to save files: {str(e)}")
    
    if request.output_format == "json":
        # Return JSON format
        data = []
        for state in ship_states:
            data.append(formatter.create_ais_summary(state))
        
        response = {"data": data, "count": len(data)}
        if saved_files:
            response["saved_files"] = saved_files
        return response
    
    elif request.output_format == "nmea":
        # Return NMEA sentences as text
        nmea_lines = []
        for i, state in enumerate(ship_states):
            nmea_line = formatter.format_realistic_position_report(state)
            nmea_lines.append(nmea_line)
        
        nmea_content = "\\n".join(nmea_lines)
        
        # If we saved files, return info about them instead of streaming
        if saved_files:
            return {
                "message": "NMEA data generated and saved to file",
                "saved_files": saved_files,
                "preview": nmea_content[:500] + "..." if len(nmea_content) > 500 else nmea_content,
                "total_lines": len(nmea_lines)
            }
        else:
            # Return as downloadable text file
            return StreamingResponse(
                io.StringIO(nmea_content),
                media_type="text/plain",
                headers={"Content-Disposition": f"attachment; filename=ais_data_{ship_mmsi}.nmea"}
            )
    
    elif request.output_format == "both":
        # Return both formats
        json_data = []
        nmea_lines = []
        
        for i, state in enumerate(ship_states):
            json_data.append(formatter.create_ais_summary(state))
            nmea_lines.append(formatter.format_realistic_position_report(state))
        
        response = {
            "json_data": json_data,
            "nmea_data": nmea_lines,
            "count": len(json_data)
        }
        if saved_files:
            response["saved_files"] = saved_files
        return response
    
    else:
        raise HTTPException(status_code=400, detail="Invalid output_format. Use 'json', 'nmea', or 'both'")


@app.get("/ships")
async def list_ships():
    """List all active ships"""
    ships = []
    for ship in generator.active_ships:
        ships.append({
            "mmsi": ship.mmsi,
            "name": ship.ship_name,
            "route": {
                "start": {
                    "lat": ship.route.start_position.latitude,
                    "lon": ship.route.start_position.longitude
                },
                "end": {
                    "lat": ship.route.end_position.latitude,
                    "lon": ship.route.end_position.longitude
                }
            },
            "speed_knots": ship.route.speed_knots,
            "distance_nm": ship.total_distance_nm,
            "estimated_time_hours": ship.total_time_hours
        })
    
    return {"ships": ships, "count": len(ships)}


@app.delete("/ships/{ship_mmsi}")
async def remove_ship(ship_mmsi: int):
    """Remove a ship from the generator"""
    for i, ship in enumerate(generator.active_ships):
        if ship.mmsi == ship_mmsi:
            removed_ship = generator.active_ships.pop(i)
            return {
                "message": f"Ship {ship_mmsi} removed successfully",
                "removed_ship": removed_ship.ship_name
            }
    
    raise HTTPException(status_code=404, detail=f"Ship with MMSI {ship_mmsi} not found")


@app.get("/files")
async def list_output_files():
    """List all generated output files"""
    try:
        files = file_manager.list_output_files()
        return {
            "files": files,
            "count": len(files),
            "output_directory": str(file_manager.base_output_dir)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list files: {str(e)}")


@app.get("/files/{filename}")
async def get_file_content(filename: str):
    """Get content of a specific output file"""
    try:
        content = file_manager.get_file_content(filename)
        
        # Determine content type based on file extension
        if filename.endswith('.json'):
            # Parse JSON and return as structured data
            try:
                json_content = json.loads(content)
                return json_content
            except json.JSONDecodeError:
                return {"raw_content": content, "error": "Invalid JSON format"}
        else:
            # Return as plain text
            return {"filename": filename, "content": content}
    
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"File {filename} not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read file: {str(e)}")


@app.get("/files/{filename}/download")
async def download_file(filename: str):
    """Download a specific output file"""
    try:
        content = file_manager.get_file_content(filename)
        
        # Determine media type
        media_type = "application/json" if filename.endswith('.json') else "text/plain"
        
        return StreamingResponse(
            io.StringIO(content),
            media_type=media_type,
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"File {filename} not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to download file: {str(e)}")


@app.post("/generate-irish-sea-demo")
async def generate_irish_sea_demo(request: Optional[GenerateRequest] = None):
    """Generate demo data for Irish Sea route and save to file"""
    # Use default request if none provided
    if request is None:
        request = GenerateRequest()
    
    # Create demo route if not exists
    demo_ship = None
    mmsi = 123456001
    
    for ship in generator.active_ships:
        if ship.mmsi == mmsi:
            demo_ship = ship
            break
    
    if not demo_ship:
        # Create the demo route
        route = generator.generate_sample_irish_sea_route()
        demo_ship = generator.add_ship(route, mmsi, "IRISH_SEA_DEMO")
    
    # Generate and save data
    ship_states = list(demo_ship.generate_movement(
        request.duration_hours, 
        request.report_interval_seconds
    ))
    
    try:
        saved_files = file_manager.save_route_data(
            ship_states, 
            "irish_sea_demo", 
            request.output_format
        )
        
        return {
            "message": "Irish Sea demo data generated successfully",
            "ship_info": {
                "mmsi": mmsi,
                "name": "IRISH_SEA_DEMO",
                "route": "Dublin to Holyhead"
            },
            "data_summary": {
                "total_reports": len(ship_states),
                "duration_hours": request.duration_hours,
                "report_interval_seconds": request.report_interval_seconds
            },
            "saved_files": saved_files
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate demo: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
