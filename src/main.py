#!/usr/bin/env python3
"""
Prophecy Vision - Main Application Entry Point
Connects prophetic scripture search with Stellarium astronomical visualization.
"""

import asyncio
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from mcp_servers.stellarium_server import (
    get_stellarium_status,
    set_biblical_location,
    set_time_julian,
    set_time_gregorian,
    focus_on_object,
    show_prophetic_event,
    list_prophetic_events,
    list_biblical_locations,
)
from mcp_servers.scripture_server import (
    search_cosmic_prophecies,
    get_verse,
    analyze_prophetic_passage,
    get_all_cosmic_verses,
)


class ProphecyVisionApp:
    def __init__(self):
        self.current_location = None
        self.current_date = None
        self.current_focus = None
        self.search_results = []
        self.candidate_dates = []

    async def check_stellarium_connection(self) -> bool:
        try:
            status = await get_stellarium_status()
            return "Error" not in status
        except Exception:
            return False

    async def show_prophecy(
        self,
        reference: str,
        location: str = None,
        date_julian: float = None,
        focus_object: str = None
    ) -> dict:
        results = {
            "scripture": None,
            "analysis": None,
            "stellarium_configured": False,
            "errors": []
        }

        try:
            analysis = await analyze_prophetic_passage(reference)
            results["analysis"] = analysis
            print(f"\n{analysis}")
        except Exception as e:
            results["errors"].append(f"Scripture analysis failed: {e}")

        stellarium_ok = await self.check_stellarium_connection()
        if not stellarium_ok:
            results["errors"].append(
                "Stellarium not connected. Ensure RemoteControl plugin is enabled on port 8090."
            )
            return results

        try:
            if location:
                loc_result = await set_biblical_location(location)
                print(f"\nLocation: {loc_result}")
                self.current_location = location

            if date_julian:
                time_result = await set_time_julian(date_julian)
                print(f"Time: {time_result}")
                self.current_date = date_julian

            if focus_object:
                focus_result = await focus_on_object(focus_object)
                print(f"Focus: {focus_result}")
                self.current_focus = focus_object

            results["stellarium_configured"] = True

        except Exception as e:
            results["errors"].append(f"Stellarium configuration failed: {e}")

        return results

    async def search_and_show(self, theme: str, auto_show_first: bool = True) -> list:
        print(f"\nSearching for: {theme}")
        print("-" * 40)

        search_results = await search_cosmic_prophecies(theme)
        print(search_results)

        self.search_results = search_results
        return search_results

    async def show_known_event(self, event_name: str) -> str:
        stellarium_ok = await self.check_stellarium_connection()
        if not stellarium_ok:
            return "Stellarium not connected. Enable RemoteControl plugin."

        result = await show_prophetic_event(event_name)
        print(f"\n{result}")
        return result

    async def interactive_mode(self):
        print("\n" + "=" * 60)
        print("  PROPHECY VISION - Interactive Mode")
        print("  Connect Biblical Prophecy with Astronomical Visualization")
        print("=" * 60)

        stellarium_ok = await self.check_stellarium_connection()
        if stellarium_ok:
            print("✓ Stellarium connected")
        else:
            print("✗ Stellarium not connected (start Stellarium with RemoteControl enabled)")

        print("\nCommands:")
        print("  search <theme>     - Search cosmic prophecy verses")
        print("  show <event>       - Show known prophetic event")
        print("  analyze <ref>      - Analyze a verse reference")
        print("  events             - List available prophetic events")
        print("  locations          - List biblical locations")
        print("  verses             - Show all cosmic verses")
        print("  status             - Check Stellarium status")
        print("  quit               - Exit")
        print()

        while True:
            try:
                user_input = input("prophecy> ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\nGoodbye!")
                break

            if not user_input:
                continue

            parts = user_input.split(maxsplit=1)
            command = parts[0].lower()
            args = parts[1] if len(parts) > 1 else ""

            try:
                if command == "quit" or command == "exit":
                    print("Goodbye!")
                    break

                elif command == "search":
                    if args:
                        await self.search_and_show(args)
                    else:
                        print("Usage: search <theme>")
                        print("Examples: search blood moon, search stars falling")

                elif command == "show":
                    if args:
                        await self.show_known_event(args)
                    else:
                        print("Usage: show <event_name>")
                        events = await list_prophetic_events()
                        print(events)

                elif command == "analyze":
                    if args:
                        analysis = await analyze_prophetic_passage(args)
                        print(analysis)
                    else:
                        print("Usage: analyze <reference>")
                        print("Example: analyze Revelation 12:1-6")

                elif command == "events":
                    events = await list_prophetic_events()
                    print(events)

                elif command == "locations":
                    locations = await list_biblical_locations()
                    print(locations)

                elif command == "verses":
                    verses = await get_all_cosmic_verses()
                    print(verses)

                elif command == "status":
                    status = await get_stellarium_status()
                    print(status)

                elif command == "location":
                    if args:
                        result = await set_biblical_location(args)
                        print(result)
                    else:
                        print("Usage: location <name>")

                elif command == "time":
                    if args:
                        try:
                            jd = float(args)
                            result = await set_time_julian(jd)
                            print(result)
                        except ValueError:
                            print("Usage: time <julian_date>")
                            print("Example: time 2458019.5")
                    else:
                        print("Usage: time <julian_date>")

                elif command == "focus":
                    if args:
                        result = await focus_on_object(args)
                        print(result)
                    else:
                        print("Usage: focus <object_name>")
                        print("Examples: focus Moon, focus Jupiter, focus Virgo")

                elif command == "help":
                    print("\nCommands:")
                    print("  search <theme>     - Search cosmic prophecy verses")
                    print("  show <event>       - Show known prophetic event")
                    print("  analyze <ref>      - Analyze a verse reference")
                    print("  events             - List available prophetic events")
                    print("  locations          - List biblical locations")
                    print("  verses             - Show all cosmic verses")
                    print("  location <name>    - Set observer location")
                    print("  time <julian_date> - Set simulation time")
                    print("  focus <object>     - Focus on celestial object")
                    print("  status             - Check Stellarium status")
                    print("  quit               - Exit")

                else:
                    print(f"Unknown command: {command}")
                    print("Type 'help' for available commands")

            except Exception as e:
                print(f"Error: {e}")

            print()


async def demo_mode():
    print("\n" + "=" * 60)
    print("  PROPHECY VISION - Demo Mode")
    print("=" * 60)

    app = ProphecyVisionApp()

    print("\n1. Listing all cosmic prophecy verses:")
    print("-" * 40)
    verses = await get_all_cosmic_verses()
    print(verses[:1000] + "..." if len(verses) > 1000 else verses)

    print("\n\n2. Searching for 'blood moon' prophecies:")
    print("-" * 40)
    results = await search_cosmic_prophecies("blood moon")
    print(results)

    print("\n\n3. Analyzing Revelation 12:1:")
    print("-" * 40)
    analysis = await analyze_prophetic_passage("Revelation 12:1")
    print(analysis)

    print("\n\n4. Available prophetic events:")
    print("-" * 40)
    events = await list_prophetic_events()
    print(events)

    stellarium_ok = await app.check_stellarium_connection()
    if stellarium_ok:
        print("\n\n5. Showing Revelation 12 sign in Stellarium:")
        print("-" * 40)
        result = await app.show_known_event("revelation_12_sign")
        print(result)
    else:
        print("\n\n5. Stellarium not connected - skipping visualization")
        print("-" * 40)
        print("To enable Stellarium integration:")
        print("  1. Open Stellarium")
        print("  2. Press F2 → Plugins → Remote Control")
        print("  3. Check 'Load at startup' and restart Stellarium")
        print("  4. Configure → Start Server (port 8090)")


def main():
    parser = argparse.ArgumentParser(
        description="Prophecy Vision - Biblical Prophecy + Astronomical Visualization"
    )
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Run in demo mode"
    )
    parser.add_argument(
        "--interactive", "-i",
        action="store_true",
        help="Run in interactive mode"
    )
    parser.add_argument(
        "--search",
        type=str,
        help="Search for cosmic prophecy theme"
    )
    parser.add_argument(
        "--show",
        type=str,
        help="Show a known prophetic event"
    )
    parser.add_argument(
        "--analyze",
        type=str,
        help="Analyze a scripture reference"
    )

    args = parser.parse_args()

    app = ProphecyVisionApp()

    if args.demo:
        asyncio.run(demo_mode())
    elif args.interactive:
        asyncio.run(app.interactive_mode())
    elif args.search:
        asyncio.run(app.search_and_show(args.search))
    elif args.show:
        asyncio.run(app.show_known_event(args.show))
    elif args.analyze:
        async def analyze():
            result = await analyze_prophetic_passage(args.analyze)
            print(result)
        asyncio.run(analyze())
    else:
        asyncio.run(app.interactive_mode())


if __name__ == "__main__":
    main()
