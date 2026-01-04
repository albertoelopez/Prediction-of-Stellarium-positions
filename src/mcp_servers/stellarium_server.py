#!/usr/bin/env python3
"""
Stellarium MCP Server
Provides tools to control Stellarium planetarium software via its RemoteControl HTTP API.
Enables visualization of celestial events for prophetic scripture analysis.
"""

import asyncio
import json
from datetime import datetime
from typing import Optional
import httpx
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("stellarium-prophecy")

STELLARIUM_BASE_URL = "http://localhost:8090/api"

BIBLICAL_LOCATIONS = {
    "jerusalem": {"lat": 31.7781, "lon": 35.2353, "alt": 754, "name": "Jerusalem"},
    "babylon": {"lat": 32.5390, "lon": 44.4208, "alt": 35, "name": "Babylon"},
    "bethlehem": {"lat": 31.7054, "lon": 35.2024, "alt": 765, "name": "Bethlehem"},
    "nazareth": {"lat": 32.6996, "lon": 35.3035, "alt": 347, "name": "Nazareth"},
    "patmos": {"lat": 37.3113, "lon": 26.5449, "alt": 50, "name": "Patmos"},
    "ur": {"lat": 30.9620, "lon": 46.1031, "alt": 5, "name": "Ur of Chaldees"},
    "nineveh": {"lat": 36.3600, "lon": 43.1500, "alt": 223, "name": "Nineveh"},
    "damascus": {"lat": 33.5138, "lon": 36.2765, "alt": 680, "name": "Damascus"},
    "rome": {"lat": 41.9028, "lon": 12.4964, "alt": 21, "name": "Rome"},
    "egypt": {"lat": 30.0444, "lon": 31.2357, "alt": 75, "name": "Egypt (Cairo)"},
    "mount_sinai": {"lat": 28.5394, "lon": 33.9752, "alt": 2285, "name": "Mount Sinai"},
    "galilee": {"lat": 32.8331, "lon": 35.5081, "alt": -212, "name": "Sea of Galilee"},
}

PROPHETIC_EVENTS = {
    "revelation_12_sign": {
        "description": "Woman clothed with the sun, moon under feet (Rev 12:1-2)",
        "julian_date": 2458019.5,
        "iso_date": "2017-09-23T12:00:00",
        "location": "jerusalem",
        "focus_object": "Virgo",
    },
    "star_of_bethlehem_conjunction": {
        "description": "Jupiter-Regulus conjunction (possible Star of Bethlehem)",
        "julian_date": 1720692.5,
        "iso_date": "-0002-09-14T18:00:00",
        "location": "bethlehem",
        "focus_object": "Jupiter",
    },
    "crucifixion_eclipse": {
        "description": "Darkness during crucifixion (Luke 23:44-45)",
        "julian_date": 1733204.5,
        "iso_date": "0033-04-03T12:00:00",
        "location": "jerusalem",
        "focus_object": "Sun",
    },
    "blood_moon_prophecy": {
        "description": "Moon turned to blood (Joel 2:31, Acts 2:20)",
        "julian_date": 2456749.5,
        "iso_date": "2014-04-15T07:00:00",
        "location": "jerusalem",
        "focus_object": "Moon",
    },
}


async def stellarium_request(
    method: str, endpoint: str, data: Optional[dict] = None
) -> dict:
    async with httpx.AsyncClient(timeout=10.0) as client:
        url = f"{STELLARIUM_BASE_URL}/{endpoint}"
        if method.upper() == "GET":
            response = await client.get(url, params=data)
        else:
            response = await client.post(url, data=data)

        if response.status_code == 200:
            try:
                return {"success": True, "data": response.json()}
            except json.JSONDecodeError:
                return {"success": True, "data": response.text}
        else:
            return {"success": False, "error": f"HTTP {response.status_code}: {response.text}"}


def gregorian_to_julian(year: int, month: int, day: int, hour: float = 12.0) -> float:
    if month <= 2:
        year -= 1
        month += 12

    A = int(year / 100)
    B = 2 - A + int(A / 4)

    JD = (
        int(365.25 * (year + 4716))
        + int(30.6001 * (month + 1))
        + day
        + B
        - 1524.5
        + hour / 24.0
    )
    return JD


@mcp.tool()
async def get_stellarium_status() -> str:
    """Get the current status of Stellarium including time, location, and view information."""
    result = await stellarium_request("GET", "main/status")
    if result["success"]:
        return f"Stellarium Status: {json.dumps(result['data'], indent=2)}"
    return f"Error connecting to Stellarium: {result['error']}"


@mcp.tool()
async def set_biblical_location(location_name: str) -> str:
    """
    Set Stellarium's observer location to a biblical city.
    Available locations: jerusalem, babylon, bethlehem, nazareth, patmos, ur,
    nineveh, damascus, rome, egypt, mount_sinai, galilee
    """
    location_key = location_name.lower().replace(" ", "_")
    if location_key not in BIBLICAL_LOCATIONS:
        available = ", ".join(BIBLICAL_LOCATIONS.keys())
        return f"Unknown location: {location_name}. Available: {available}"

    loc = BIBLICAL_LOCATIONS[location_key]
    data = {
        "latitude": loc["lat"],
        "longitude": loc["lon"],
        "altitude": loc["alt"],
        "name": loc["name"],
        "planet": "Earth",
    }

    result = await stellarium_request("POST", "location/setlocationfields", data)
    if result["success"]:
        return f"Location set to {loc['name']} ({loc['lat']}°N, {loc['lon']}°E, {loc['alt']}m)"
    return f"Failed to set location: {result['error']}"


@mcp.tool()
async def set_custom_location(
    latitude: float, longitude: float, altitude: int, name: str
) -> str:
    """
    Set Stellarium's observer to custom coordinates.
    latitude: Decimal degrees (-90 to 90)
    longitude: Decimal degrees (-180 to 180)
    altitude: Meters above sea level
    name: Location name for display
    """
    data = {
        "latitude": latitude,
        "longitude": longitude,
        "altitude": altitude,
        "name": name,
        "planet": "Earth",
    }

    result = await stellarium_request("POST", "location/setlocationfields", data)
    if result["success"]:
        return f"Location set to {name} ({latitude}°, {longitude}°, {altitude}m)"
    return f"Failed to set location: {result['error']}"


@mcp.tool()
async def set_time_julian(julian_date: float, pause_time: bool = True) -> str:
    """
    Set Stellarium's simulation time using Julian Date.
    julian_date: Julian Day number (e.g., 2458019.5 for Sept 23, 2017)
    pause_time: If True, pause time flow after setting
    """
    data = {"time": julian_date}
    if pause_time:
        data["timerate"] = 0

    result = await stellarium_request("POST", "main/time", data)
    if result["success"]:
        return f"Time set to Julian Date {julian_date}"
    return f"Failed to set time: {result['error']}"


@mcp.tool()
async def set_time_gregorian(
    year: int, month: int, day: int, hour: float = 12.0, pause_time: bool = True
) -> str:
    """
    Set Stellarium's simulation time using Gregorian date.
    For BC dates, use negative years (e.g., -2 for 3 BC).
    year: Year (negative for BC, using astronomical numbering)
    month: Month (1-12)
    day: Day of month
    hour: Hour in 24-hour format (default 12.0 for noon)
    pause_time: If True, pause time flow
    """
    jd = gregorian_to_julian(year, month, day, hour)
    data = {"time": jd}
    if pause_time:
        data["timerate"] = 0

    result = await stellarium_request("POST", "main/time", data)
    if result["success"]:
        date_str = f"{abs(year)} {'BC' if year < 0 else 'AD'}"
        return f"Time set to {month}/{day}/{date_str} {hour}:00 (JD: {jd})"
    return f"Failed to set time: {result['error']}"


@mcp.tool()
async def focus_on_object(
    object_name: str, zoom: bool = True, select: bool = True
) -> str:
    """
    Focus Stellarium's view on a celestial object.
    object_name: Name of object (e.g., "Moon", "Jupiter", "Virgo", "Orion")
    zoom: Whether to zoom in on the object
    select: Whether to select/highlight the object
    """
    mode = "zoom" if zoom else "center"
    data = {"target": object_name, "mode": mode}
    if select:
        data["select"] = "true"

    result = await stellarium_request("POST", "main/focus", data)
    if result["success"]:
        return f"Focused on {object_name} (mode: {mode})"
    return f"Failed to focus: {result['error']}"


@mcp.tool()
async def search_object(search_term: str) -> str:
    """
    Search for celestial objects in Stellarium by name.
    Returns up to 5 matching results.
    """
    result = await stellarium_request("GET", f"objects/find?str={search_term}")
    if result["success"]:
        return f"Search results for '{search_term}': {json.dumps(result['data'], indent=2)}"
    return f"Search failed: {result['error']}"


@mcp.tool()
async def get_object_info(object_name: str) -> str:
    """Get detailed information about a celestial object."""
    result = await stellarium_request(
        "GET", "objects/info", {"name": object_name, "format": "json"}
    )
    if result["success"]:
        return f"Object Info for '{object_name}': {json.dumps(result['data'], indent=2)}"
    return f"Failed to get info: {result['error']}"


@mcp.tool()
async def show_prophetic_event(event_name: str) -> str:
    """
    Configure Stellarium to show a known prophetic astronomical event.
    Available events: revelation_12_sign, star_of_bethlehem_conjunction,
    crucifixion_eclipse, blood_moon_prophecy
    """
    event_key = event_name.lower().replace(" ", "_")
    if event_key not in PROPHETIC_EVENTS:
        available = ", ".join(PROPHETIC_EVENTS.keys())
        return f"Unknown event: {event_name}. Available: {available}"

    event = PROPHETIC_EVENTS[event_key]
    results = []

    loc_result = await set_biblical_location(event["location"])
    results.append(loc_result)

    time_result = await set_time_julian(event["julian_date"])
    results.append(time_result)

    if event.get("focus_object"):
        focus_result = await focus_on_object(event["focus_object"])
        results.append(focus_result)

    return f"Showing: {event['description']}\n" + "\n".join(results)


@mcp.tool()
async def set_time_rate(rate: float) -> str:
    """
    Set the time flow rate in Stellarium.
    rate: Time multiplier (1.0 = real-time, 0 = paused, 100 = 100x speed)
    Negative values run time backwards.
    """
    result = await stellarium_request("POST", "main/time", {"timerate": rate})
    if result["success"]:
        if rate == 0:
            return "Time paused"
        elif rate == 1:
            return "Time set to real-time"
        else:
            return f"Time rate set to {rate}x"
    return f"Failed to set time rate: {result['error']}"


@mcp.tool()
async def list_prophetic_events() -> str:
    """List all available pre-configured prophetic astronomical events."""
    events = []
    for key, event in PROPHETIC_EVENTS.items():
        events.append(f"- {key}: {event['description']} ({event['iso_date']})")
    return "Available Prophetic Events:\n" + "\n".join(events)


@mcp.tool()
async def list_biblical_locations() -> str:
    """List all available pre-configured biblical locations."""
    locations = []
    for key, loc in BIBLICAL_LOCATIONS.items():
        locations.append(f"- {key}: {loc['name']} ({loc['lat']}°N, {loc['lon']}°E)")
    return "Available Biblical Locations:\n" + "\n".join(locations)


@mcp.tool()
async def find_possible_dates_for_prophecy(
    description: str,
    start_year: int,
    end_year: int,
    event_type: str = "lunar_eclipse"
) -> str:
    """
    Search for astronomical events that could match a prophecy description.
    This tool helps identify multiple candidate dates when the exact date is uncertain.

    description: The prophetic text or event to match
    start_year: Start of search range (negative for BC)
    end_year: End of search range (negative for BC)
    event_type: Type of event to search for (lunar_eclipse, solar_eclipse, conjunction, etc.)

    Returns a list of candidate dates that could be visualized in Stellarium.
    """
    return f"""
Searching for {event_type} events between {abs(start_year)} {'BC' if start_year < 0 else 'AD'} and {abs(end_year)} {'BC' if end_year < 0 else 'AD'}
matching: "{description}"

Note: For accurate eclipse and conjunction data, use astronomical ephemeris services.
Common sources:
- NASA Eclipse Database: https://eclipse.gsfc.nasa.gov/
- Stellarium's built-in script: core.getDateString()
- Fred Espenak's Eclipse Catalogs

To visualize a candidate date in Stellarium, use:
- set_time_gregorian(year, month, day, hour)
- set_biblical_location(location)
- focus_on_object(object_name)

Example workflow:
1. Search eclipse database for dates
2. For each candidate, call set_time_gregorian
3. Verify visually in Stellarium
4. Save confirmed dates to prophetic_events
"""


if __name__ == "__main__":
    mcp.run()
