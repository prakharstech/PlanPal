from langchain.agents import initialize_agent, AgentType, AgentExecutor
from langchain_core.tools import Tool
from langchain_community.chat_models import ChatOpenAI
# from langchain_openai import ChatOpenAI
from langchain_mistralai.chat_models import ChatMistralAI
from langchain.tools import tool
from dotenv import load_dotenv
import os
from backend.calendar_utils import list_upcoming_events, book_event, delete_event, reschedule_event, get_calendar_service
import dateparser 
from datetime import datetime
from zoneinfo import ZoneInfo
from langchain.agents import create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate
from collections import defaultdict

load_dotenv()

def get_local_now():
    return datetime.now()  

llm = ChatMistralAI(
    temperature=0.7,
    model="mistral-large-latest",
    mistral_api_key=os.getenv("MISTRAL_API_KEY"),
)

def list_events_tool_func(input: str = "", service=None):
    if not service:
        return "Error: Authentication service not provided."
    events = list_upcoming_events(service)
    if not events:
        return "You have no upcoming events."

    #Group events by their date
    grouped_events = defaultdict(list)
    for e in events:
        start_str = e['start'].get('dateTime', e['start'].get('date'))
        try:
            start_dt = datetime.fromisoformat(start_str)
            date_key = start_dt.strftime('%A, %B %d, %Y')
            grouped_events[date_key].append(e)
        except (ValueError, TypeError):
            continue

    if not grouped_events:
        return "No events with valid dates found."

    # 3. Build the final formatted string with date headings
    response_parts = []
    for date, daily_events in sorted(grouped_events.items()):
        response_parts.append(f"### {date}") # This creates a date heading
        for event in daily_events:
            summary = event.get('summary', 'No Title')
            start_str = event['start'].get('dateTime')
            end_str = event['end'].get('dateTime')
            event_id = event.get('id') # Get the event ID

            if start_str and end_str:
                start_dt = datetime.fromisoformat(start_str)
                end_dt = datetime.fromisoformat(end_str)
                time_range = f"{start_dt.strftime('%I:%M %p')} - {end_dt.strftime('%I:%M %p')}"
            else:
                time_range = "All Day"
            
            # Append the event with its ID
            response_parts.append(f"- **{summary}**: {time_range} (ID: {event_id})")
    
    return "\n".join(response_parts)


from dateutil.parser import parse as parse_datetime

def book_event_tool_func(input: str, service=None):
    if not service:
        return "Error: Authentication service not provided."
    try:
        parts = list(map(lambda s: s.strip().strip("'").strip('"'), input.split(",")))
        if len(parts) != 3:
            return "Error: Input must be in format 'Summary, Start Time, End Time'"

        summary, start_raw, end_raw = [p.strip().strip("'").strip('"') for p in parts]
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
        
        start_iso = start_dt.isoformat()
        end_iso = end_dt.isoformat()
        
        existing_events = list_upcoming_events(service) # Use the provided service
        for event in existing_events:
            # ... (conflict checking logic is the same)
            existing_start = event["start"].get("dateTime")
            existing_end = event["end"].get("dateTime")

            if not existing_start or not existing_end:
                continue

            existing_start_dt = datetime.fromisoformat(existing_start)
            existing_end_dt = datetime.fromisoformat(existing_end)

            # Check for overlap
            if not (end_dt <= existing_start_dt or start_dt >= existing_end_dt):
                return f"Cannot book: Conflicts with existing event. Please choose a different time'{event.get('summary', 'No Title')}' from {existing_start_dt.strftime('%I:%M %p')} to {existing_end_dt.strftime('%I:%M %p')}."


        created_event = book_event(service, summary, start_iso, end_iso) # Use the provided service
        link = "https://calendar.google.com/calendar/embed?src=prakhar.srivastava0509%40gmail.com&ctz=Asia%2FKolkata"
        return f"Meeting booked from {start_dt.strftime('%I:%M %p')} to {end_dt.strftime('%I:%M %p')}." if link else "Meeting booked successfully."

    except Exception as e:
        return f"Error booking event: {e}"

    
def delete_event_tool_func(input: str, service=None):
    if not service:
        return "Error: Authentication service not provided."
    try:
        event_id = input.strip().strip("'").strip('"')
        return delete_event(service, event_id) 
    except Exception as e:
        return f"Error deleting event: {e}"


def reschedule_event_tool_func(input: str, service=None):
    if not service:
        return "Error: Authentication service not provided."
    try:
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
        
        start_iso = start_time.isoformat()
        end_iso = end_time.isoformat()
        return reschedule_event(service, event_id, start_iso, end_iso) # Pass the service
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



def create_agent_executor(service):
    """Creates a new AgentExecutor with tools that use the provided service."""
    
    # Redefine tools inside this function to capture the 'service' object
    tools = [
        Tool(
            name="check_availability",
            func=lambda q: list_events_tool_func(q, service=service),
            description="First get today's date and time and Returns upcoming events. Then calculate the date and time required for whatever purpose and pass it in suitable function if required and book if available. Input can be 'today', 'tomorrow', or 'day after tomorrow' to filter. If the time of two events coincides don't book"
        ),
        Tool(
            name="book_meeting",
            func=lambda q: book_event_tool_func(q, service=service),
            description="""Books a meeting on the user's calendar.

✅ Input: 'Summary, Start Time, End Time'.
🧠 Check for actual datetime overlaps — only events with the **same date and overlapping times** are conflicts.
🛑 Never treat events on different dates (e.g., July 9 and July 10) as conflicts.
⏰ Times must be parsed exactly from user input (e.g., '10 July 2025 at 5pm').'"""
        ),
        Tool(
            name="delete_event",
            func=lambda q: delete_event_tool_func(q, service=service),
            description="Deletes an event. Input format: 'Event ID'"
        ),
        Tool(
            name="reschedule_event",
            func=lambda q: reschedule_event_tool_func(q, service=service),
            description="Reschedules an event. Input format: 'Event ID, New Start Time, New End Time'. Time can be natural (e.g., 'tomorrow 6pm')"
        ),
        casual_chat_tool,
        current_datetime_tool,
    ]

    prompt = ChatPromptTemplate.from_messages([
    ("system", """You are PlanPal, a hyper-efficient and meticulous AI calendar assistant. 
Your sole purpose is to accurately and efficiently manage a user's Google Calendar by calling the provided tools. You are stateless and have no memory of past conversations.

**Your Golden Rules of Operation:**

1.  **Time is Always First:** For any request involving relative dates (like "today", "tomorrow"), your absolute first step **must** be to call the `current_datetime` tool. This establishes the ground truth for all subsequent actions.

2.  **Trust the Tool's Signature:** You must meticulously follow the input format specified in each tool's description. 
    - **CRITICAL:** For the `book_meeting` tool, the input format is `'Summary, Start Time, End Time'`. The summary is everything before the final two commas. For example, if the user says "Book a meeting for 'Team Sync, Project Alpha' tomorrow at 4pm for one hour", your tool input should be `'Team Sync, Project Alpha', 'tomorrow 4pm', 'tomorrow 5pm'`.

3.  **Tool Output is Reality:** Your final response to the user must be based **exclusively** on the direct output of the tools you have just called in the current turn. 
    - **DO NOT** add information that is not present in the tool output.
    - **DO NOT** invent warnings or infer potential conflicts if the `book_meeting` tool did not explicitly state there was a conflict. If the tool successfully books an event, you should only confirm the booking.

4.  **Be a Stateless Finalizer:** Every user message is a new, isolated task. Your response must be the complete and final answer. 
    - **NEVER** ask follow-up questions.
    - If you need more information (like an event ID to delete), instruct the user to provide it in a new, separate command (e.g., "To delete an event, please send a new message with the format 'delete event with ID: <event_id>'").

5.  **Handle Errors Gracefully:** If a tool call returns an error, do not panic.
    - **First, analyze the error.** If it's a simple formatting mistake on your part, correct the input and try the tool call **one more time**.
    - **If it fails a second time,** apologize to the user, state that you were unable to complete the request, and do not try again.

6.  **Do not mention ID in your final response unless asked explicitly. It is your job to manage IDs internally.**
"""),
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

    return AgentExecutor(agent=agent, tools=tools, verbose=True)

def run_agent(prompt: str, token: str):
    """Main function to run the agent with a user's token."""
    try:
        # 1. Create a calendar service with the user's token
        service = get_calendar_service(token)
        if not service:
            return "Sorry, I couldn't authenticate with your Google Calendar."

        # 2. Create a new agent executor with the authenticated service
        agent_executor = create_agent_executor(service)

        # 3. Invoke the agent
        result = agent_executor.invoke({"input": prompt})
        return result.get("output", "I'm sorry, I didn't get a response.")
    except Exception as e:
        return f"Sorry, I encountered an error: {str(e)}"
