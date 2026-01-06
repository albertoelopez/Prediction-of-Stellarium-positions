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
    "gibeon": {"lat": 31.85, "lon": 35.18, "alt": 700, "name": "Gibeon"},
    "aijalon": {"lat": 31.86, "lon": 34.98, "alt": 250, "name": "Valley of Aijalon"},
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
        "description": "Jupiter-Venus conjunction (Star of Bethlehem candidate) - planets 0.056° apart",
        "julian_date": 1720860.33,
        "iso_date": "-0001-06-17T20:00:00",
        "location": "bethlehem",
        "focus_object": "Jupiter",
        "notes": "Jupiter and Venus in Leo near Regulus, combined mag -4.55",
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
    "joshua_long_day": {
        "description": "Sun stood still over Gibeon, Moon in Valley of Aijalon (Joshua 10:12-13)",
        "julian_date": 1280869.083,
        "iso_date": "-1206-10-30T14:00:00",
        "location": "gibeon",
        "focus_object": "Sun",
        "notes": "Annular solar eclipse - Oct 30, 1207 BC (proleptic Gregorian). Humphreys theory: Hebrew 'dmm' means 'cease/be silent' (eclipse darkening), not 'stand still'",
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
async def animate_single_day(
    year: int,
    month: int,
    day: int,
    start_hour: float = 6.0,
    end_hour: float = 18.0,
    step_minutes: int = 30,
    delay_seconds: float = 0.5
) -> str:
    """
    Animate through a single day by stepping through specific times.
    This keeps the date fixed while showing time progression - useful for watching
    eclipses, conjunctions, or other events unfold throughout a day.

    year: Year (negative for BC using astronomical numbering, e.g., -1206 for 1207 BC)
    month: Month (1-12)
    day: Day of month
    start_hour: Starting hour (0-24, default 6.0 for 6 AM)
    end_hour: Ending hour (0-24, default 18.0 for 6 PM)
    step_minutes: Minutes between each frame (default 30)
    delay_seconds: Pause between frames in real seconds (default 0.5)

    Returns progress updates as animation runs.
    """
    results = []
    current_hour = start_hour
    frame = 0

    date_str = f"{abs(year)} {'BC' if year < 0 else 'AD'}"
    results.append(f"Starting animation: {month}/{day}/{date_str}")
    results.append(f"From {start_hour}:00 to {end_hour}:00, step={step_minutes}min")

    while current_hour <= end_hour:
        jd = gregorian_to_julian(year, month, day, current_hour)
        data = {"time": jd, "timerate": 0}

        result = await stellarium_request("POST", "main/time", data)
        if not result["success"]:
            results.append(f"Error at {current_hour}:00 - {result['error']}")
            break

        hour_int = int(current_hour)
        minute_int = int((current_hour - hour_int) * 60)
        results.append(f"Frame {frame}: {hour_int:02d}:{minute_int:02d}")

        await asyncio.sleep(delay_seconds)

        current_hour += step_minutes / 60.0
        frame += 1

    results.append(f"Animation complete: {frame} frames shown")
    return "\n".join(results)


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


@mcp.tool()
async def get_sky_snapshot() -> str:
    """
    Get a snapshot of the current sky showing positions of Sun, Moon, and visible planets.
    Returns altitude, azimuth, constellation, and phase information.
    """
    objects = ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn"]
    results = []

    for obj in objects:
        info = await stellarium_request("GET", "objects/info", {"name": obj, "format": "json"})
        if info["success"] and info["data"]:
            d = info["data"]
            alt = d.get("altitude", "N/A")
            az = d.get("azimuth", "N/A")
            const = d.get("constellation-short", "N/A")
            phase = d.get("phase", "")
            mag = d.get("vmag", "N/A")

            visibility = "visible" if isinstance(alt, (int, float)) and alt > 0 else "below horizon"
            phase_str = f", phase: {phase:.1f}%" if isinstance(phase, (int, float)) else ""

            results.append(f"{obj}: alt={alt:.1f}°, az={az:.1f}°, in {const}, mag={mag}{phase_str} ({visibility})")

    return "Current Sky Snapshot:\n" + "\n".join(results)


@mcp.tool()
async def get_angular_separation(object1: str, object2: str) -> str:
    """
    Calculate the angular separation between two celestial objects.
    Useful for checking conjunctions, eclipses, and alignments.

    object1: First object name (e.g., "Jupiter")
    object2: Second object name (e.g., "Venus")
    """
    import math

    info1 = await stellarium_request("GET", "objects/info", {"name": object1, "format": "json"})
    info2 = await stellarium_request("GET", "objects/info", {"name": object2, "format": "json"})

    if not info1["success"] or not info2["success"]:
        return f"Failed to get object info: {info1.get('error', '')} {info2.get('error', '')}"

    d1, d2 = info1["data"], info2["data"]

    ra1 = math.radians(d1.get("raJ2000", 0))
    dec1 = math.radians(d1.get("decJ2000", 0))
    ra2 = math.radians(d2.get("raJ2000", 0))
    dec2 = math.radians(d2.get("decJ2000", 0))

    cos_sep = math.sin(dec1) * math.sin(dec2) + math.cos(dec1) * math.cos(dec2) * math.cos(ra1 - ra2)
    cos_sep = max(-1, min(1, cos_sep))
    separation = math.degrees(math.acos(cos_sep))

    if separation < 1:
        sep_str = f"{separation * 60:.1f} arcminutes"
    else:
        sep_str = f"{separation:.2f}°"

    conjunction_note = ""
    if separation < 0.5:
        conjunction_note = " - VERY CLOSE CONJUNCTION!"
    elif separation < 2:
        conjunction_note = " - Close conjunction"
    elif separation < 5:
        conjunction_note = " - Notable proximity"

    return f"Angular separation between {object1} and {object2}: {sep_str}{conjunction_note}"


@mcp.tool()
async def set_field_of_view(fov_degrees: float) -> str:
    """
    Set Stellarium's field of view (zoom level).

    fov_degrees: Field of view in degrees
        - 180° = full hemisphere view
        - 60° = wide view (default)
        - 20° = medium zoom
        - 5° = close zoom
        - 1° = very close (good for planets)
        - 0.5° = tight zoom (Sun/Moon size)
    """
    result = await stellarium_request("POST", "main/fov", {"fov": fov_degrees})
    if result["success"]:
        return f"Field of view set to {fov_degrees}°"
    return f"Failed to set FOV: {result['error']}"


@mcp.tool()
async def set_view_direction(azimuth: float, altitude: float) -> str:
    """
    Point Stellarium's view at a specific compass direction and elevation.

    azimuth: Compass direction in degrees (0=North, 90=East, 180=South, 270=West)
    altitude: Elevation above horizon in degrees (0=horizon, 90=zenith)
    """
    result = await stellarium_request("POST", "main/view", {"az": azimuth, "alt": altitude})
    if result["success"]:
        directions = {0: "North", 45: "NE", 90: "East", 135: "SE", 180: "South", 225: "SW", 270: "West", 315: "NW"}
        closest_dir = min(directions.keys(), key=lambda x: abs((azimuth % 360) - x))
        return f"View set to {directions[closest_dir]} (az={azimuth}°), altitude {altitude}°"
    return f"Failed to set view: {result['error']}"


@mcp.tool()
async def toggle_display_option(option: str, enabled: bool) -> str:
    """
    Toggle Stellarium display options on/off.

    option: One of:
        - constellation_lines: Draw constellation stick figures
        - constellation_labels: Show constellation names
        - constellation_art: Show constellation artwork
        - atmosphere: Show atmospheric effects (blue sky)
        - ground: Show ground/horizon
        - cardinal_points: Show N/S/E/W markers
        - equatorial_grid: Show RA/Dec grid
        - azimuthal_grid: Show Alt/Az grid
        - ecliptic_line: Show ecliptic path
        - planet_labels: Show planet names
        - star_labels: Show star names
    enabled: True to show, False to hide
    """
    option_map = {
        "constellation_lines": "actionShow_Constellation_Lines",
        "constellation_labels": "actionShow_Constellation_Labels",
        "constellation_art": "actionShow_Constellation_Art",
        "atmosphere": "actionShow_Atmosphere",
        "ground": "actionShow_Ground",
        "cardinal_points": "actionShow_Cardinal_Points",
        "equatorial_grid": "actionShow_Equatorial_Grid",
        "azimuthal_grid": "actionShow_Azimuthal_Grid",
        "ecliptic_line": "actionShow_Ecliptic_Line",
        "planet_labels": "actionShow_Planets_Labels",
        "star_labels": "actionShow_Stars_Labels",
    }

    if option not in option_map:
        available = ", ".join(option_map.keys())
        return f"Unknown option: {option}. Available: {available}"

    action = option_map[option]
    value = "true" if enabled else "false"

    result = await stellarium_request("POST", f"stelaction/do", {"id": action, "value": value})
    if result["success"]:
        state = "enabled" if enabled else "disabled"
        return f"{option} {state}"
    return f"Failed to toggle {option}: {result['error']}"


@mcp.tool()
async def take_screenshot(filename: str = "stellarium_capture.png") -> str:
    """
    Take a screenshot of the current Stellarium view.

    filename: Name for the screenshot file (saved to Stellarium's screenshot directory)
    """
    result = await stellarium_request("POST", "stelaction/do", {"id": "actionSave_Screenshot"})
    if result["success"]:
        return f"Screenshot saved. Check Stellarium's screenshot directory."
    return f"Failed to take screenshot: {result['error']}"


@mcp.tool()
async def run_script_command(command: str) -> str:
    """
    Execute a Stellarium scripting command.

    command: Stellarium script command (JavaScript-like syntax)

    Examples:
        - core.setDate("2017-09-23T12:00:00")
        - core.moveToAltAzi(45, 180)
        - LandscapeMgr.setFlagLandscape(false)
        - ConstellationMgr.setFlagLines(true)
    """
    result = await stellarium_request("POST", "scripts/direct", {"code": command})
    if result["success"]:
        return f"Script executed: {command}"
    return f"Script failed: {result['error']}"


@mcp.tool()
async def get_current_time_info() -> str:
    """
    Get detailed information about Stellarium's current simulation time.
    Returns Julian date, Gregorian date, and time rate.
    """
    result = await stellarium_request("GET", "main/status")
    if result["success"]:
        data = result["data"]
        jd = data.get("time", {}).get("jday", "N/A")
        rate = data.get("time", {}).get("timerate", "N/A")

        if isinstance(jd, (int, float)):
            z = int(jd + 0.5)
            f = jd + 0.5 - z
            if z < 2299161:
                a = z
            else:
                alpha = int((z - 1867216.25) / 36524.25)
                a = z + 1 + alpha - int(alpha / 4)
            b = a + 1524
            c = int((b - 122.1) / 365.25)
            d = int(365.25 * c)
            e = int((b - d) / 30.6001)

            day = b - d - int(30.6001 * e) + f
            month = e - 1 if e < 14 else e - 13
            year = c - 4716 if month > 2 else c - 4715

            day_int = int(day)
            hour = (day - day_int) * 24
            hour_int = int(hour)
            minute = int((hour - hour_int) * 60)

            year_str = f"{abs(year)} {'BC' if year <= 0 else 'AD'}"
            date_str = f"{month}/{day_int}/{year_str} {hour_int:02d}:{minute:02d}"
        else:
            date_str = "Unknown"

        return f"Current Time:\n  Julian Date: {jd}\n  Gregorian: {date_str}\n  Time Rate: {rate}x"
    return f"Failed to get time info: {result['error']}"


@mcp.tool()
async def search_for_conjunctions(
    planet1: str,
    planet2: str,
    start_year: int,
    end_year: int,
    max_separation_degrees: float = 2.0
) -> str:
    """
    Search for conjunctions between two planets in a date range.
    This steps through months and checks separation.

    planet1: First planet (e.g., "Jupiter")
    planet2: Second planet (e.g., "Venus")
    start_year: Start of search range (negative for BC)
    end_year: End of search range
    max_separation_degrees: Maximum separation to report as conjunction

    Note: This is a simple search - for precise conjunction times,
    additional refinement near found dates is recommended.
    """
    import math

    results = [f"Searching for {planet1}-{planet2} conjunctions ({start_year} to {end_year})..."]
    conjunctions_found = []

    for year in range(start_year, end_year + 1):
        for month in range(1, 13):
            jd = gregorian_to_julian(year, month, 15, 12)
            await stellarium_request("POST", "main/time", {"time": jd, "timerate": 0})
            await asyncio.sleep(0.1)

            info1 = await stellarium_request("GET", "objects/info", {"name": planet1, "format": "json"})
            info2 = await stellarium_request("GET", "objects/info", {"name": planet2, "format": "json"})

            if info1["success"] and info2["success"]:
                d1, d2 = info1["data"], info2["data"]
                ra1 = math.radians(d1.get("raJ2000", 0))
                dec1 = math.radians(d1.get("decJ2000", 0))
                ra2 = math.radians(d2.get("raJ2000", 0))
                dec2 = math.radians(d2.get("decJ2000", 0))

                cos_sep = math.sin(dec1) * math.sin(dec2) + math.cos(dec1) * math.cos(dec2) * math.cos(ra1 - ra2)
                cos_sep = max(-1, min(1, cos_sep))
                separation = math.degrees(math.acos(cos_sep))

                if separation <= max_separation_degrees:
                    year_str = f"{abs(year)} {'BC' if year < 0 else 'AD'}"
                    conjunctions_found.append((year, month, separation))
                    results.append(f"  {month}/{year_str}: separation {separation:.2f}°")

    if not conjunctions_found:
        results.append(f"No conjunctions closer than {max_separation_degrees}° found.")
    else:
        results.append(f"\nFound {len(conjunctions_found)} potential conjunction(s)")

    return "\n".join(results)


@mcp.tool()
async def show_night_sky(remove_daylight: bool = True) -> str:
    """
    Configure Stellarium to show a clear night sky view.
    Removes atmosphere, shows stars clearly, enables constellation lines.

    remove_daylight: If True, removes atmosphere to see stars even during day
    """
    commands = []

    if remove_daylight:
        await toggle_display_option("atmosphere", False)
        commands.append("Atmosphere hidden")

    await toggle_display_option("constellation_lines", True)
    commands.append("Constellation lines shown")

    await toggle_display_option("planet_labels", True)
    commands.append("Planet labels shown")

    await toggle_display_option("ecliptic_line", True)
    commands.append("Ecliptic line shown")

    return "Night sky view configured:\n" + "\n".join(f"  - {c}" for c in commands)


@mcp.tool()
async def show_daytime_realistic() -> str:
    """
    Configure Stellarium to show realistic daytime view.
    Enables atmosphere, ground, and hides star features.
    """
    await toggle_display_option("atmosphere", True)
    await toggle_display_option("ground", True)
    await toggle_display_option("constellation_lines", False)
    await toggle_display_option("ecliptic_line", False)

    return "Daytime realistic view configured"


@mcp.tool()
async def look_at_horizon_direction(direction: str) -> str:
    """
    Point the view at a cardinal direction on the horizon.

    direction: One of 'north', 'south', 'east', 'west', 'zenith',
               'northeast', 'southeast', 'southwest', 'northwest'
    """
    directions = {
        "north": (0, 15),
        "northeast": (45, 15),
        "east": (90, 15),
        "southeast": (135, 15),
        "south": (180, 15),
        "southwest": (225, 15),
        "west": (270, 15),
        "northwest": (315, 15),
        "zenith": (0, 90),
    }

    dir_key = direction.lower().replace(" ", "")
    if dir_key not in directions:
        available = ", ".join(directions.keys())
        return f"Unknown direction: {direction}. Available: {available}"

    az, alt = directions[dir_key]
    return await set_view_direction(az, alt)


if __name__ == "__main__":
    mcp.run()
