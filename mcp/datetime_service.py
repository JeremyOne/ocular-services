from typing import Optional
import time
from datetime import datetime, timezone
from fastmcp import FastMCP
from starlette.requests import Request
from starlette.responses import PlainTextResponse, JSONResponse

# DateTime service for getting current date/time information
# Useful for timestamping, scheduling, and time-based analysis

# Create FastMCP server
mcp = FastMCP("DateTime Service")

def parse_datetime_info(dt: datetime) -> dict:
    """Parse datetime into structured format with various representations"""
    result = {
        "iso_format": dt.isoformat(),
        "timestamp": int(dt.timestamp()),
        "human_readable": dt.strftime("%Y-%m-%d %H:%M:%S"),
        "date_only": dt.strftime("%Y-%m-%d"),
        "time_only": dt.strftime("%H:%M:%S"),
        "timezone": str(dt.tzinfo) if dt.tzinfo else "Local",
        "weekday": dt.strftime("%A"),
        "month": dt.strftime("%B"),
        "year": dt.year,
        "month_num": dt.month,
        "day": dt.day,
        "hour": dt.hour,
        "minute": dt.minute,
        "second": dt.second,
        "microsecond": dt.microsecond,
        "day_of_year": dt.timetuple().tm_yday,
        "week_number": dt.isocalendar()[1]
    }
    return result

@mcp.custom_route("/datetime", methods=["GET", "POST"])
async def get_datetime(request: Request) -> JSONResponse:
    """Get current date and time with various format options.
        timezone: Timezone to convert to (default: local)
        format: Custom format string (strftime format)
        utc: Return UTC time (boolean, default: false)
    Returns:
        JSON response matching schema.json format with datetime information
    """
    start_time = time.time()
    
    try:
        # Get parameters from query string or JSON body
        if request.method == "GET":
            tz_param = request.query_params.get("timezone", "")
            custom_format = request.query_params.get("format", "")
            use_utc = request.query_params.get("utc", "false").lower() == "true"
        else:  # POST
            body = await request.json()
            tz_param = body.get("timezone", "")
            custom_format = body.get("format", "")
            use_utc = body.get("utc", False)
        
        # Get current datetime
        if use_utc:
            current_dt = datetime.now(timezone.utc)
        else:
            current_dt = datetime.now()
        
        end_time = time.time()
        process_time_ms = int((end_time - start_time) * 1000)
        
        # Parse datetime into structured format
        structured_output = parse_datetime_info(current_dt)
        
        # Add custom format if requested
        if custom_format:
            try:
                structured_output["custom_format"] = current_dt.strftime(custom_format)
            except ValueError as e:
                structured_output["custom_format_error"] = str(e)
        
        # Format response according to schema.json
        response = {
            "service": "datetime",
            "process_time_ms": process_time_ms,
            "target": "system_time",
            "arguments": {
                "timezone": tz_param if tz_param else "local",
                "format": custom_format,
                "utc": use_utc
            },
            "return_code": 0,
            "raw_output": current_dt.isoformat(),
            "raw_error": "",
            "structured_output": structured_output
        }
        
        return JSONResponse(response)
        
    except Exception as e:
        end_time = time.time()
        process_time_ms = int((end_time - start_time) * 1000)
        
        response = {
            "service": "datetime",
            "process_time_ms": process_time_ms,
            "target": "system_time",
            "arguments": {
                "timezone": tz_param if 'tz_param' in locals() else "",
                "format": custom_format if 'custom_format' in locals() else "",
                "utc": use_utc if 'use_utc' in locals() else False
            },
            "return_code": -1,
            "raw_output": "",
            "raw_error": str(e),
            "structured_output": {}
        }
        
        return JSONResponse(response, status_code=500)

@mcp.custom_route("/health", methods=["GET"])
async def health_check(request: Request) -> PlainTextResponse:
    return PlainTextResponse("OK")

if __name__ == "__main__":
    # mcp.run() # stdio
    mcp.run(transport="http", host="0.0.0.0", port=9003)
