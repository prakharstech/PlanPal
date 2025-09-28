from langchain.agents import initialize_agent, AgentType, AgentExecutor
from langchain_core.tools import Tool
from langchain_community.chat_models import ChatOpenAI
from langchain_openai import ChatOpenAI
from langchain_mistralai.chat_models import ChatMistralAI
from langchain.tools import tool
from dotenv import load_dotenv
import os
from calendar_utils import list_upcoming_events, book_event, delete_event, reschedule_event
import dateparser 
from datetime import datetime
from zoneinfo import ZoneInfo
from langchain.agents import create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate

load_dotenv()

def get_local_now():
    return datetime.now()  

llm = ChatMistralAI(
    temperature=0.7,
    model="mistral-large-latest", # Or any other Mistral model you prefer
    mistral_api_key=os.getenv("MISTRAL_API_KEY"),
)

def list_events_tool_func(_: str = ""):
    events = list_upcoming_events()
    
    if not events:
        return "You have no upcoming events."

    formatted_events = []
    for e in events:
        summary = e.get('summary', 'No Title')
        event_id = e['id']
        
        # Parse start and end times
        start_str = e['start'].get('dateTime', e['start'].get('date'))
        end_str = e['end'].get('dateTime', e['end'].get('date'))
        
        # Convert to datetime objects and format them
        try:
            start_dt = datetime.fromisoformat(start_str)
            end_dt = datetime.fromisoformat(end_str)
            time_range = f"{start_dt.strftime('%I:%M %p')} to {end_dt.strftime('%I:%M %p')}"
        except ValueError:
            # Handle all-day events that don't have a time
            time_range = "All day"

        formatted_events.append(f"- **{summary}**: {time_range} (ID: {event_id})")

    return "\n".join(formatted_events)

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
        # NEW, CORRECTED VERSION
        return f"Meeting booked from {start_dt.strftime('%I:%M %p')} to {end_dt.strftime('%I:%M %p')}. [View Event]({link})" if link else "Meeting booked successfully."

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
    name="current_datetime",
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
    description="First get today's date and time and Returns upcoming events. Then calculate the date and time required for whatever purpose and pass it in suitable function if required and book if available. Input can be 'today', 'tomorrow', or 'day after tomorrow' to filter. If the time of two events coincides don't book"
)

book_event_tool = Tool.from_function(
    func=book_event_tool_func,
    name="book_meeting",
    description="""Books a meeting on the user's calendar.

✅ Input: 'Summary, Start Time, End Time'.
🧠 Check for actual datetime overlaps — only events with the **same date and overlapping times** are conflicts.
🛑 Never treat events on different dates (e.g., July 9 and July 10) as conflicts.
⏰ Times must be parsed exactly from user input (e.g., '10 July 2025 at 5pm').'"""
)
_agent_executor: AgentExecutor = None
def get_agent():
    global _agent_executor
    if _agent_executor is None:
        tools = [
            list_events_tool,
            book_event_tool,
            delete_event_tool,
            reschedule_event_tool,
            casual_chat_tool,
            current_datetime_tool
        ]

        # A prompt for the tool-calling agent
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert calendar assistant. You have one goal: to help the user manage their schedule efficiently.

**Your Reasoning Process Must Follow These Rules:**

1.  **For Vague Schedule Requests (e.g., "what's my schedule?"):**
    - Your immediate and ONLY action is to call the `check_availability` tool ONCE.
    - Do NOT try to guess different days. The tool automatically lists all upcoming events.

2.  **For Specific Actions with Relative Dates (e.g., "book a meeting tomorrow at 5pm"):**
    - Your FIRST action MUST be to call `current_datetime` to understand what "tomorrow" means.
    - After you have the current date, you can THEN call other tools like `book_meeting` with the correctly calculated date and time.

Always be direct and efficient. Do not make assumptions beyond these rules."""),
            ("user", "{input}"),
            ("placeholder", "{agent_scratchpad}"),
        ])
        llm_with_tools = llm.bind_tools(tools)
        # Create the tool-calling agent
        agent = create_tool_calling_agent(
            llm=llm_with_tools,
            tools=tools,
            prompt=prompt,
        )

        # The AgentExecutor remains the same
        _agent_executor = AgentExecutor(
            agent=agent,
            tools=tools,
            verbose=True,
        )

    return _agent_executor

def run_agent(prompt: str):
    try:
        agent = get_agent()
        # Use .invoke() which returns a dictionary
        result = agent.invoke({"input": prompt})
        # The actual response is in the 'output' key
        return result.get("output", "I'm sorry, I didn't get a response.")
    except Exception as e:
        return f"Sorry, I encountered an error: {str(e)}"
