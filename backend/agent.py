from langchain_core.tools import Tool
from langchain_mistralai import ChatMistralAI
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os
from backend.calendar_utils import list_upcoming_events, book_event, delete_event, reschedule_event, get_calendar_service
import dateparser 
from datetime import datetime
from zoneinfo import ZoneInfo
from collections import defaultdict
from langgraph.prebuilt import create_react_agent
import logging
import re

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

load_dotenv()

# Choose your LLM - uncomment one:

# Option 1: OpenAI 
llm = ChatOpenAI(
    temperature=0.7,
    model="gpt-4o-mini", 
    api_key=os.getenv("OPENAI_API_KEY"),
)

# Option 2: Mistral 
# llm = ChatMistralAI(
#     temperature=0.7,
#     model="mistral-large-latest",
#     api_key=os.getenv("MISTRAL_API_KEY"),
# )

# Option 3: Groq 
# llm = ChatGroq(
#     api_key=os.getenv("GROQ_API_KEY"),
#     model="llama-3.1-8b-instant",
#     temperature=0.7, 
# )

def sanitize_output(text: str):
    return re.sub(r"\(ID: [^)]+\)", "", text).strip()


def list_events_tool_func(input: str = "", service=None):
    if not service:
        return "Error: Authentication service not provided."
    events = list_upcoming_events(service)
    if not events:
        return "You have no upcoming events."

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

    response_parts = []
    for date, daily_events in sorted(grouped_events.items()):
        response_parts.append(f"### {date}")
        for event in daily_events:
            summary = event.get('summary', 'No Title')
            start_str = event['start'].get('dateTime')
            end_str = event['end'].get('dateTime')
            event_id = event.get('id')

            if start_str and end_str:
                start_dt = datetime.fromisoformat(start_str)
                end_dt = datetime.fromisoformat(end_str)
                time_range = f"{start_dt.strftime('%I:%M %p')} - {end_dt.strftime('%I:%M %p')}"
            else:
                time_range = "All Day"
            
            response_parts.append(f"- **{summary}**: {time_range} (ID: {event_id})")
    
    return "\n".join(response_parts)


def book_event_tool_func(input: str, service=None):
    if not service:
        return "Error: Authentication service not provided."
    try:
        parts = list(map(lambda s: s.strip().strip("'").strip('"'), input.split(",")))
        if len(parts) != 3:
            return "Error: Input must be in format 'Summary, Start Time, End Time'"

        summary, start_raw, end_raw = [p.strip().strip("'").strip('"') for p in parts]
        settings = {
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
        
        existing_events = list_upcoming_events(service)
        for event in existing_events:
            existing_start = event["start"].get("dateTime")
            existing_end = event["end"].get("dateTime")

            if not existing_start or not existing_end:
                continue

            existing_start_dt = datetime.fromisoformat(existing_start)
            existing_end_dt = datetime.fromisoformat(existing_end)

            if not (end_dt <= existing_start_dt or start_dt >= existing_end_dt):
                return f"Cannot book: Conflicts with existing event '{event.get('summary', 'No Title')}' from {existing_start_dt.strftime('%I:%M %p')} to {existing_end_dt.strftime('%I:%M %p')}."

        created_event = book_event(service, summary, start_iso, end_iso)
        return f"Meeting booked from {start_dt.strftime('%I:%M %p')} to {end_dt.strftime('%I:%M %p')}."

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
        settings = {
            'TIMEZONE': 'Asia/Kolkata',
            'TO_TIMEZONE': 'Asia/Kolkata',
            'RELATIVE_BASE': datetime.now(ZoneInfo("Asia/Kolkata")),
            'RETURN_AS_TIMEZONE_AWARE': True,
            'PREFER_DATES_FROM': 'future'
        }
        start_time = dateparser.parse(start_raw, settings=settings)
        end_time = dateparser.parse(end_raw, settings=settings)

        if not start_time or not end_time:
            return "Error: Invalid start or end time."
        
        start_iso = start_time.isoformat()
        end_iso = end_time.isoformat()
        return reschedule_event(service, event_id, start_iso, end_iso)
    except Exception as e:
        return f"Error rescheduling event: {e}"
    

def casual_chat_tool_func(input: str):
    input_lower = input.lower()
    if any(greeting in input_lower for greeting in ['hi', 'hello', 'hey']):
        return "Hello! I can help you manage your calendar. I can book meetings, check your schedule, delete events, or reschedule appointments."
    elif 'birthday' in input_lower or 'personal' in input_lower:
        return "I don't have access to personal information like birthdays. I can only help with calendar management - booking, viewing, deleting, or rescheduling meetings."
    elif any(word in input_lower for word in ['can you', 'what can', 'help', 'do']):
        return "I can help you with: checking your schedule, booking new meetings, deleting events, and rescheduling appointments. Just tell me what you'd like to do!"
    else:
        return "I'm a calendar assistant. I can help you book meetings, check your schedule, delete events, or reschedule appointments."


def get_current_datetime(input: str):
    return datetime.now().isoformat()


def create_agent_executor(service):
    """Creates agent using LangGraph's create_react_agent."""
    
    tools = [
        Tool(
            name="check_availability",
            func=lambda q: list_events_tool_func(q, service=service),
            description="Returns upcoming events from the calendar. Shows events grouped by date with times and IDs."
        ),
        Tool(
            name="book_meeting",
            func=lambda q: book_event_tool_func(q, service=service),
            description="Books a meeting. Input format: 'Summary, Start Time, End Time'. Example: 'Team meeting, tomorrow at 2pm, tomorrow at 3pm'. The summary can contain commas."
        ),
        Tool(
            name="delete_event",
            func=lambda q: delete_event_tool_func(q, service=service),
            description="Deletes an event by ID. Input: the event ID string."
        ),
        Tool(
            name="reschedule_event",
            func=lambda q: reschedule_event_tool_func(q, service=service),
            description="Reschedules an event. Input format: 'Event ID, New Start Time, New End Time'"
        ),
        Tool(
            name="casual_chat",
            func=casual_chat_tool_func,
            description="Handles greetings, small talk, or questions about capabilities like 'hi', 'hello', 'what can you do?', 'when is my birthday?'"
        ),
        Tool(
            name="current_datetime",
            func=get_current_datetime,
            description="Returns the current datetime. Call this FIRST for any request involving 'today', 'tomorrow', or relative dates."
        ),
    ]

    system_message = """You are PlanPal, a hyper-efficient and meticulous AI calendar assistant. 
Your sole purpose is to accurately and efficiently manage a user's Google Calendar by calling the provided tools. You are stateless and have no memory of past conversations.

**Your Golden Rules of Operation:**

1.  **Time is Always First:** For any request involving relative dates (like "today", "tomorrow"), your absolute first step **must** be to call the `current_datetime` tool. This establishes the ground truth for all subsequent actions.

2.  **Trust the Tool's Signature:** You must meticulously follow the input format specified in each tool's description. 
    - **CRITICAL:** For the `book_meeting` tool, the input format is `'Summary, Start Time, End Time'`. The summary is everything before the final two commas. For example, if the user says "Book a meeting for 'Team Sync, Project Alpha' tomorrow at 4pm for one hour", your tool input should be `Team Sync, Project Alpha, tomorrow 4pm, tomorrow 5pm`.

3.  **Tool Output is Reality:** Your final response to the user must be based **exclusively** on the direct output of the tools you have just called in the current turn. 
    - **DO NOT** add information that is not present in the tool output.
    - **DO NOT** invent warnings or infer potential conflicts if the `book_meeting` tool did not explicitly state there was a conflict. If the tool successfully books an event, you should only confirm the booking.

4.  **Be a Stateless Finalizer:** Every user message is a new, isolated task. Your response must be the complete and final answer. 
    - **NEVER** ask follow-up questions.
    - If you need more information (like an event ID to delete), instruct the user to provide it in a new, separate command (e.g., "To delete an event, please send a new message with the format 'delete event with ID: <event_id>'").

5.  **Handle Errors Gracefully:** If a tool call returns an error, do not panic.
    - **First, analyze the error.** If it's a simple formatting mistake on your part, correct the input and try the tool call **one more time**.
    - **If it fails a second time,** apologize to the user, state that you were unable to complete the request, and do not try again.

6.  **Do not mention event ID(s) in your final response. It is your job to manage IDs internally.**

7.  **Be concise and natural:** Give friendly, natural responses without being overly verbose or formal."""

    # Bind the system message to the LLM
    llm_with_system = llm.bind(system=system_message)
    
    # Create agent using LangGraph's create_react_agent (no state_modifier parameter)
    agent = create_react_agent(llm_with_system, tools)
    
    return agent


def run_agent(prompt_text: str, token: str):
    """Main function to run the agent with a user's token."""
    import time
    
    logger.info(f"=== NEW REQUEST ===")
    logger.info(f"User prompt: {prompt_text}")
    
    max_retries = 5
    retry_delay = 2  # seconds
    
    for attempt in range(max_retries):
        try:
            service = get_calendar_service(token)
            if not service:
                return "Sorry, I couldn't authenticate with your Google Calendar."

            logger.info(f"Creating agent executor...")
            agent = create_agent_executor(service)
            
            logger.info(f"Invoking agent...")
            # Invoke the agent with the user's input and stream for verbose output
            result = agent.invoke(
                {"messages": [("user", prompt_text)]},
                {"recursion_limit": 10}
            )
            
            logger.info(f"Agent execution complete")
            
            # Log all messages in the result
            if "messages" in result:
                logger.info(f"\n=== AGENT CONVERSATION LOG ===")
                for i, msg in enumerate(result["messages"]):
                    msg_type = type(msg).__name__
                    content = getattr(msg, 'content', str(msg))
                    logger.info(f"Step {i}: [{msg_type}] {content}")
                    
                    # Log tool calls if present
                    if hasattr(msg, 'tool_calls') and msg.tool_calls:
                        for tool_call in msg.tool_calls:
                            logger.info(f"  -> Tool Call: {tool_call.get('name', 'unknown')} with args: {tool_call.get('args', {})}")
                
                logger.info(f"=== END CONVERSATION LOG ===\n")
                
                # Extract the final message from the result
                final_message = result["messages"][-1]
                if hasattr(final_message, 'content'):
                    logger.info(f"Final response: {final_message.content}")
                    return sanitize_output(final_message.content)
                return sanitize_output(str(final_message))
            
            return "I'm sorry, I didn't get a response."
            
        except Exception as e:
            logger.error(f"Error occurred: {str(e)}")
            # Handle rate limiting with retry
            if "429" in str(e):
                if attempt < max_retries - 1:
                    wait_time = retry_delay * (attempt + 1)
                    logger.warning(f"Rate limited. Retrying in {wait_time} seconds... (Attempt {attempt + 1}/{max_retries})")
                    time.sleep(wait_time)
                    continue
                else:
                    return "The AI service is currently at capacity."
            return f"Sorry, I encountered an error: {str(e)}"
    
    return "Unable to complete request after multiple attempts."
