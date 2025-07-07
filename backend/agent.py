from langchain.agents import initialize_agent, AgentType
from langchain_core.tools import Tool
from langchain.chat_models import ChatOpenAI
from dotenv import load_dotenv
import os
from backend.calendar_utils import list_upcoming_events, book_event, delete_event, reschedule_event
import dateparser 
from datetime import datetime
from zoneinfo import ZoneInfo

load_dotenv()

def get_local_now():
    return datetime.now()  

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
        parts = list(map(lambda s: s.strip().strip("'").strip('"'), input.split(",")))
        if len(parts) != 3:
            return "Error: Input must be in format 'Summary, Start Time, End Time'"

        summary, start_raw, end_raw = parts
        settings={
            'TIMEZONE': 'Asia/Kolkata',
            'TO_TIMEZONE': 'Asia/Kolkata',
            'RELATIVE_BASE': datetime.now(ZoneInfo("Asia/Kolkata")),
            'RETURN_AS_TIMEZONE_AWARE': True,
            'PREFER_DATES_FROM': 'future'
        }
        
        start_dt = dateparser.parse(start_raw, settings=settings)
        end_dt = dateparser.parse(end_raw, settings=settings)

        if not start_dt or not end_dt:
            return "Error: Couldn't parse start or end time."

        # Convert to RFC3339
        start_iso = start_dt.isoformat()
        end_iso = end_dt.isoformat()

        # Fetch existing events
        existing_events = list_upcoming_events()
        for event in existing_events:
            existing_start = event["start"].get("dateTime")
            existing_end = event["end"].get("dateTime")

            if not existing_start or not existing_end:
                continue

            existing_start_dt = datetime.fromisoformat(existing_start)
            existing_end_dt = datetime.fromisoformat(existing_end)

            # Check for overlap
            if not (end_dt <= existing_start_dt or start_dt >= existing_end_dt):
                return f"Cannot book: Conflicts with existing event. Please choose a different time'{event.get('summary', 'No Title')}' from {existing_start_dt.strftime('%I:%M %p')} to {existing_end_dt.strftime('%I:%M %p')}."

        # No conflict — proceed
        created_event = book_event(summary, start_iso, end_iso)
        link = "https://calendar.google.com/calendar/embed?src=prakhar.srivastava0509%40gmail.com&ctz=Asia%2FKolkata"
        return f"Meeting booked from {start_dt.strftime('%I:%M %p')} to {end_dt.strftime('%I:%M %p')}.\n[View Event]({link} provide this link to the user)" if link else "Meeting booked successfully."

    except Exception as e:
        return f"Error booking event: {e}"


    
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
        settings={
            'TIMEZONE': 'Asia/Kolkata',
            'TO_TIMEZONE': 'Asia/Kolkata',
            'RELATIVE_BASE': datetime.now(ZoneInfo("Asia/Kolkata")),
            'RETURN_AS_TIMEZONE_AWARE': True,
            'PREFER_DATES_FROM': 'future'
        }
        start_time = dateparser.parse(start_raw,settings=settings)
        end_time = dateparser.parse(end_raw,settings=settings)

        if not start_time or not end_time:
            return "Error: Invalid start or end time."

        # Convert to RFC3339 (ISO format + timezone)
        start_iso = start_time.isoformat()
        end_iso = end_time.isoformat()

        return reschedule_event(event_id, start_iso, end_iso)

    except Exception as e:
        return f"Error rescheduling event: {e}"
    
def casual_chat_tool_func(input: str):
    return "Hello! I can help you schedule, delete, or reschedule meetings. Try saying 'book a meeting tomorrow at 4pm'."


def get_current_datetime(_):
    return datetime.now().isoformat()

current_datetime_tool = Tool(
    name="CurrentDatetime",
    func=get_current_datetime,
    description="Returns the current datetime which decides when is tomorrow and today and day after tomorrow"
)

casual_chat_tool = Tool.from_function(
    func=casual_chat_tool_func,
    name="casual_chat",
    description="Handles greetings or small talk like 'hi', 'hello', or 'what can you do?'"
)



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
    description="First get get_current_datetime and Returns upcoming events. Then calculate the date and time required for whatever purpose and pass it in suitable function if required and book if available. Input can be 'today', 'tomorrow', or 'day after tomorrow' to filter. If the time of two events coincides don't book"
)

book_event_tool = Tool.from_function(
    func=book_event_tool_func,
    name="book_meeting",
    description="""Books a meeting. 
Input format: 'Summary, Start Time, End Time'. 
Start and end time should be in natural language (e.g., '10 July 2025 at 5pm', 'tomorrow at 6pm').
Do not book if there is a conflict — tell the user which event overlaps and at what time.
Respect the time requested by the user. Never default to 9 AM or any other time unless explicitly asked.'"""
)

agent_executor = initialize_agent(
    tools=[list_events_tool, book_event_tool, delete_event_tool, reschedule_event_tool, casual_chat_tool, current_datetime_tool],
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
