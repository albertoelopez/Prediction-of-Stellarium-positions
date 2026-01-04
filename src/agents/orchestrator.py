#!/usr/bin/env python3
"""
Prophecy Vision Agent Orchestrator
Multi-agent system using LangGraph with Ollama for coordinating scripture search
and Stellarium visualization.
"""

import asyncio
import json
import os
from typing import TypedDict, Annotated, Literal, Optional
from dataclasses import dataclass

from langchain_ollama import ChatOllama
from langchain.tools import tool
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import Command

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

SUPERVISOR_MODEL = "llama3.1:8b-instruct-q4_K_M"
RESEARCHER_MODEL = "qwen2.5:7b-instruct-q4_K_M"
EXECUTOR_MODEL = "llama3.1:8b-instruct-q4_K_M"


@dataclass
class ProphecyQuery:
    scripture_reference: Optional[str] = None
    search_theme: Optional[str] = None
    location: Optional[str] = None
    date_range: Optional[tuple] = None
    celestial_focus: Optional[str] = None


class AgentState(TypedDict):
    messages: Annotated[list, "Conversation history"]
    current_query: Optional[ProphecyQuery]
    scripture_results: list
    stellarium_commands: list
    candidate_dates: list
    selected_date_index: int
    task_status: str
    next_action: str


def get_supervisor_model():
    return ChatOllama(
        model=SUPERVISOR_MODEL,
        base_url=OLLAMA_BASE_URL,
        temperature=0.7,
    )


def get_researcher_model():
    return ChatOllama(
        model=RESEARCHER_MODEL,
        base_url=OLLAMA_BASE_URL,
        temperature=0.3,
    )


def get_executor_model():
    return ChatOllama(
        model=EXECUTOR_MODEL,
        base_url=OLLAMA_BASE_URL,
        temperature=0.1,
    )


SUPERVISOR_PROMPT = """You are a supervisor agent coordinating a team to visualize biblical prophecies in Stellarium.

Your team:
- RESEARCHER: Searches scripture for prophetic verses, analyzes celestial references
- EXECUTOR: Configures Stellarium to display astronomical events
- PLANNER: Identifies candidate dates when exact dates are uncertain

Given the user's request, decide which agent should handle the next step.
Respond with ONLY one of: RESEARCHER, EXECUTOR, PLANNER, or FINISH

Current state:
- Scripture results: {scripture_count} verses found
- Stellarium commands: {stellarium_count} pending
- Candidate dates: {dates_count} dates identified
- Task status: {task_status}

User request: {user_message}

Which agent should act next?"""


RESEARCHER_PROMPT = """You are a scripture research specialist focused on finding prophetic verses with astronomical significance.

Your capabilities:
1. Search for verses about cosmic events (sun darkening, blood moons, stars falling)
2. Analyze passages for celestial imagery
3. Identify cross-references between prophecies
4. Determine relevant biblical locations for viewing events

Given the request, search for relevant scripture and extract:
- Specific verse references
- Celestial objects mentioned (sun, moon, stars, constellations)
- Suggested viewing location (Jerusalem, Babylon, etc.)
- Date clues from the text

Request: {request}

Provide your findings in a structured format."""


EXECUTOR_PROMPT = """You are a Stellarium execution specialist. You translate scripture analysis into Stellarium commands.

Based on the research findings, determine:
1. Which location to set (use set_biblical_location)
2. What time/date to set (use set_time_gregorian or set_time_julian)
3. Which celestial object to focus on (use focus_on_object)

Research findings:
{findings}

Generate the sequence of Stellarium commands needed.
If the date is uncertain, flag this for the PLANNER agent."""


PLANNER_PROMPT = """You are a date analysis specialist. When prophecies have uncertain dates, you identify candidate astronomical events.

For prophecies about:
- Blood moons: Look for total lunar eclipses
- Sun darkening: Look for solar eclipses
- Star signs: Look for notable conjunctions or meteor events
- General celestial signs: Look for remarkable astronomical alignments

Research context:
{context}

Date range to search: {start_year} to {end_year}

Identify 3-5 candidate dates that could match this prophecy.
Format each as: YYYY-MM-DD (or -YYYY for BC dates) with brief explanation."""


@tool
def search_scripture_mock(query: str) -> str:
    """Search for prophetic scripture about celestial events."""
    mock_results = {
        "blood moon": [
            {"ref": "Joel 2:31", "text": "The sun shall be turned into darkness, and the moon into blood..."},
            {"ref": "Acts 2:20", "text": "The sun shall be turned into darkness, and the moon into blood..."},
            {"ref": "Revelation 6:12", "text": "...the moon became as blood..."},
        ],
        "star": [
            {"ref": "Numbers 24:17", "text": "...there shall come a Star out of Jacob..."},
            {"ref": "Revelation 22:16", "text": "...I am the bright and morning star."},
            {"ref": "Matthew 2:2", "text": "...for we have seen his star in the east..."},
        ],
        "sun": [
            {"ref": "Matthew 24:29", "text": "...shall the sun be darkened..."},
            {"ref": "Isaiah 13:10", "text": "...the sun shall be darkened in his going forth..."},
        ],
        "revelation 12": [
            {"ref": "Revelation 12:1", "text": "...a woman clothed with the sun, and the moon under her feet, and upon her head a crown of twelve stars..."},
        ],
    }

    for key, verses in mock_results.items():
        if key in query.lower():
            return json.dumps(verses)

    return json.dumps([{"ref": "No match", "text": "Try searching for: blood moon, star, sun, revelation 12"}])


@tool
def configure_stellarium_mock(location: str, date: str, focus_object: str) -> str:
    """Configure Stellarium to display a specific astronomical scene."""
    return json.dumps({
        "status": "configured",
        "location": location,
        "date": date,
        "focus": focus_object,
        "commands_executed": [
            f"set_biblical_location('{location}')",
            f"set_time_gregorian({date})",
            f"focus_on_object('{focus_object}')",
        ]
    })


@tool
def find_eclipse_dates_mock(event_type: str, start_year: int, end_year: int) -> str:
    """Find candidate dates for astronomical events."""
    mock_eclipses = {
        "lunar": [
            {"date": "2014-04-15", "type": "Total Lunar Eclipse", "notes": "First of 2014-2015 tetrad"},
            {"date": "2014-10-08", "type": "Total Lunar Eclipse", "notes": "Second of tetrad"},
            {"date": "2015-04-04", "type": "Total Lunar Eclipse", "notes": "Third of tetrad"},
            {"date": "2015-09-28", "type": "Total Lunar Eclipse", "notes": "Fourth of tetrad"},
        ],
        "solar": [
            {"date": "2017-08-21", "type": "Total Solar Eclipse", "notes": "Great American Eclipse"},
            {"date": "2024-04-08", "type": "Total Solar Eclipse", "notes": "North American Eclipse"},
        ],
        "conjunction": [
            {"date": "-0002-09-14", "type": "Jupiter-Regulus Conjunction", "notes": "Possible Star of Bethlehem"},
            {"date": "2017-09-23", "type": "Virgo-Leo Alignment", "notes": "Revelation 12 sign candidate"},
        ],
    }

    results = mock_eclipses.get(event_type.lower(), [])
    filtered = [e for e in results if start_year <= int(e["date"][:4]) <= end_year]
    return json.dumps(filtered if filtered else mock_eclipses.get(event_type.lower(), []))


def supervisor_node(state: AgentState) -> Command:
    model = get_supervisor_model()

    messages = state.get("messages", [])
    last_message = messages[-1].content if messages else "No request yet"

    prompt = SUPERVISOR_PROMPT.format(
        scripture_count=len(state.get("scripture_results", [])),
        stellarium_count=len(state.get("stellarium_commands", [])),
        dates_count=len(state.get("candidate_dates", [])),
        task_status=state.get("task_status", "starting"),
        user_message=last_message,
    )

    response = model.invoke([SystemMessage(content=prompt)])
    decision = response.content.strip().upper()

    if "FINISH" in decision:
        return Command(goto=END, update={"task_status": "completed"})
    elif "RESEARCHER" in decision:
        return Command(goto="researcher", update={"next_action": "research"})
    elif "EXECUTOR" in decision:
        return Command(goto="executor", update={"next_action": "execute"})
    elif "PLANNER" in decision:
        return Command(goto="planner", update={"next_action": "plan"})
    else:
        return Command(goto="researcher", update={"next_action": "research"})


def researcher_node(state: AgentState) -> Command:
    model = get_researcher_model()

    messages = state.get("messages", [])
    last_message = messages[-1].content if messages else ""

    prompt = RESEARCHER_PROMPT.format(request=last_message)
    response = model.invoke([SystemMessage(content=prompt)])

    scripture_results = state.get("scripture_results", [])
    scripture_results.append({
        "query": last_message,
        "analysis": response.content,
    })

    new_messages = messages + [AIMessage(content=f"[RESEARCHER] {response.content}")]

    return Command(
        goto="supervisor",
        update={
            "messages": new_messages,
            "scripture_results": scripture_results,
            "task_status": "researched",
        }
    )


def executor_node(state: AgentState) -> Command:
    model = get_executor_model()

    scripture_results = state.get("scripture_results", [])
    findings = json.dumps(scripture_results[-1] if scripture_results else {})

    prompt = EXECUTOR_PROMPT.format(findings=findings)
    response = model.invoke([SystemMessage(content=prompt)])

    stellarium_commands = state.get("stellarium_commands", [])
    stellarium_commands.append({
        "generated_commands": response.content,
    })

    messages = state.get("messages", [])
    new_messages = messages + [AIMessage(content=f"[EXECUTOR] {response.content}")]

    return Command(
        goto="supervisor",
        update={
            "messages": new_messages,
            "stellarium_commands": stellarium_commands,
            "task_status": "configured",
        }
    )


def planner_node(state: AgentState) -> Command:
    model = get_researcher_model()

    scripture_results = state.get("scripture_results", [])
    context = json.dumps(scripture_results[-1] if scripture_results else {})

    prompt = PLANNER_PROMPT.format(
        context=context,
        start_year=-100,
        end_year=2030,
    )
    response = model.invoke([SystemMessage(content=prompt)])

    candidate_dates = state.get("candidate_dates", [])
    candidate_dates.append({
        "analysis": response.content,
    })

    messages = state.get("messages", [])
    new_messages = messages + [AIMessage(content=f"[PLANNER] {response.content}")]

    return Command(
        goto="supervisor",
        update={
            "messages": new_messages,
            "candidate_dates": candidate_dates,
            "task_status": "dates_identified",
        }
    )


def build_agent_graph():
    builder = StateGraph(AgentState)

    builder.add_node("supervisor", supervisor_node)
    builder.add_node("researcher", researcher_node)
    builder.add_node("executor", executor_node)
    builder.add_node("planner", planner_node)

    builder.add_edge(START, "supervisor")

    checkpointer = InMemorySaver()
    graph = builder.compile(checkpointer=checkpointer)

    return graph


async def run_prophecy_query(query: str, max_iterations: int = 10) -> dict:
    graph = build_agent_graph()

    initial_state = {
        "messages": [HumanMessage(content=query)],
        "current_query": None,
        "scripture_results": [],
        "stellarium_commands": [],
        "candidate_dates": [],
        "selected_date_index": 0,
        "task_status": "starting",
        "next_action": "",
    }

    config = {"configurable": {"thread_id": "prophecy-session-1"}}

    result = None
    iterations = 0

    async for event in graph.astream(initial_state, config=config):
        iterations += 1
        result = event
        print(f"Iteration {iterations}: {json.dumps(list(event.keys()), default=str)}")

        if iterations >= max_iterations:
            print("Max iterations reached")
            break

    return result


def main():
    print("Prophecy Vision Agent Orchestrator")
    print("=" * 40)

    test_queries = [
        "Show me the blood moon prophecy from Joel 2:31 in Stellarium",
        "Find the Revelation 12 sign and display it",
        "What astronomical events match the Star of Bethlehem?",
    ]

    for query in test_queries[:1]:
        print(f"\nQuery: {query}")
        print("-" * 40)

        result = asyncio.run(run_prophecy_query(query))

        if result:
            for key, value in result.items():
                if isinstance(value, dict):
                    print(f"\n{key}:")
                    for inner_key, inner_value in value.items():
                        if inner_key == "messages":
                            print(f"  {inner_key}: {len(inner_value)} messages")
                        else:
                            print(f"  {inner_key}: {inner_value}")


if __name__ == "__main__":
    main()
