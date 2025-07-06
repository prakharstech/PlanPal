from langchain.agents import initialize_agent, AgentType
from langchain_core.tools import Tool
from langchain.chat_models import ChatOpenAI
from dotenv import load_dotenv
import os
from backend.calendar_utils import list_upcoming_events, book_event, delete_event, reschedule_event
import dateparser 
from datetime import datetime

load_dotenv()

llm = ChatOpenAI(
    temperature=0.7,
    model="openai/gpt-4o-mini",
    openai_api_key=os.getenv("OPENAI_API_KEY"),
    openai_api_base=os.getenv("OPENAI_BASE_URL")
)

def list_events_tool_func(_: str = ""):
    events = list_upcoming_events()
    if not events:
        return "You have no upcoming events."
    response = "\n".join(
    f"'{e.get('summary', 'No Title')}' (ID: {e['id']}) from {e['start'].get('dateTime', e['start'].get('date'))} to {e['end'].get('dateTime', e['end'].get('date'))}"
    for e in events
)

    return response

from dateutil.parser import parse as parse_datetime

def book_event_tool_func(input: str):
    try:
        # Split input: 'Summary, Start Time, End Time'
        parts = list(map(lambda s: s.strip().strip("'").strip('"'), input.split(",")))
        if len(parts) != 3:
            return "Error: Input must be in format 'Summary, Start Time, End Time'"

        summary, start_raw, end_raw = parts

        # Use dateparser to support natural language like "tomorrow 6pm"
        start_dt = dateparser.parse(start_raw)
        end_dt = dateparser.parse(end_raw)

        if not start_dt or not end_dt:
            return "Error: Couldn't parse start or end time."

        # Convert to RFC3339 format (required by Google Calendar)
        start_time = start_dt.isoformat()
        end_time = end_dt.isoformat()

        return book_event(summary, start_time, end_time)
    except Exception as e:
        return f"Error parsing input: {e}"
    
def delete_event_tool_func(input: str):
    try:
        event_id = input.strip().strip("'").strip('"')
        return delete_event(event_id)
    except Exception as e:
        return f"Error deleting event: {e}"


def reschedule_event_tool_func(input: str):
    try:
        # Expected format: 'Event ID, New Start Time, New End Time'
        parts = list(map(lambda s: s.strip().strip("'").strip('"'), input.split(",")))
        if len(parts) != 3:
            return "Error: Input must be in format 'Event ID, New Start Time, New End Time'"

        event_id, start_raw, end_raw = parts

        start_time = dateparser.parse(start_raw)
        end_time = dateparser.parse(end_raw)

        if not start_time or not end_time:
            return "Error: Invalid start or end time."

        # Convert to RFC3339 (ISO format + timezone)
        start_iso = start_time.isoformat()
        end_iso = end_time.isoformat()

        return reschedule_event(event_id, start_iso, end_iso)

    except Exception as e:
        return f"Error rescheduling event: {e}"


reschedule_event_tool = Tool.from_function(
    func=reschedule_event_tool_func,
    name="reschedule_event",
    description="Reschedules an event. Input format: 'Event ID, New Start Time, New End Time'. Time can be natural (e.g., 'tomorrow 6pm')"
)



delete_event_tool = Tool.from_function(
    func=delete_event_tool_func,
    name="delete_event",
    description="Deletes an event. Input format: 'Event ID'"
)


list_events_tool = Tool.from_function(
    func=list_events_tool_func,
    name="check_availability",
    description="Returns a list of upcoming events from the user's calendar. Takes no input."
)

book_event_tool = Tool.from_function(
    func=book_event_tool_func,
    name="book_meeting",
    description="Books a meeting. Input format: 'Summary, Start Time, End Time'"
)


agent_executor = initialize_agent(
    tools=[list_events_tool, book_event_tool, delete_event_tool, reschedule_event_tool],
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,
    handle_parsing_errors=True
)

def run_agent(prompt: str):
    try:
        return agent_executor.run(prompt)
    except Exception as e:
        return f"Sorry, I encountered an error: {str(e)}"
