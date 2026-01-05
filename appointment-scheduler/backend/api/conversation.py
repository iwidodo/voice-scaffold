"""
Conversation API endpoints for LLM-powered appointment scheduling.
"""
import json
import logging
from fastapi import APIRouter, HTTPException
from backend.models.schemas import ConversationRequest, ConversationResponse
from backend.models.constants import ConversationState
from backend.llm.client import LLMClient
from backend.llm.tools import get_function_tools
from backend.llm.conversation_manager import ConversationManager
from backend.llm.provider_matcher import match_provider_for_issue
from backend.services.schedule_service import (
    get_availability_summary,
    format_availability_message
)
from backend.services.appointment_service import create_appointment
from backend.models.schemas import AppointmentCreate
from backend.database.providers import get_provider_by_id
from backend.config import config

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/conversation", tags=["conversation"])

# Global conversation manager (in production, use a proper store)
conversation_manager = ConversationManager()

# Initialize LLM client
try:
    logger.info("[conversation.py.root] Initializing LLM client")
    llm_client = LLMClient(model=config.OPENAI_MODEL)
    logger.info(f"[conversation.py.root] LLM client initialized with model: {config.OPENAI_MODEL}")
except ValueError as e:
    logger.error(f"[conversation.py.root] Failed to initialize LLM client: {e}")
    llm_client = None


@router.post("/", response_model=ConversationResponse)
async def handle_conversation(request: ConversationRequest):
    """
    Handle a conversation turn for appointment scheduling.
    
    Args:
        request: User message and optional conversation ID
        
    Returns:
        Assistant response with updated conversation state
    """
    logger.info(f"[conversation.py.handle_conversation] Received message: '{request.message[:50]}...' for conversation: {request.conversation_id}")
    
    if not llm_client:
        logger.error("[conversation.py.handle_conversation] LLM client not configured")
        raise HTTPException(
            status_code=500,
            detail="OpenAI API key not configured. Set OPENAI_API_KEY environment variable."
        )
    
    # Get or create conversation
    conversation_id = request.conversation_id
    if not conversation_id:
        conversation_id = conversation_manager.create_conversation()
        logger.info(f"[conversation.py.handle_conversation] Created new conversation: {conversation_id}")
    else:
        logger.debug(f"[conversation.py.handle_conversation] Using existing conversation: {conversation_id}")
    
    # Add user message
    conversation_manager.add_message(conversation_id, "user", request.message)
    logger.debug(f"[conversation.py.handle_conversation] Added user message to conversation: {conversation_id}")
    
    # Get conversation history and system prompt
    messages = conversation_manager.get_messages(conversation_id)
    system_prompt = conversation_manager.get_system_prompt(conversation_id)
    
    # Prepend system message
    full_messages = [{"role": "system", "content": system_prompt}] + messages
    logger.debug(f"[conversation.py.handle_conversation] Prepared {len(full_messages)} messages for LLM")
    
    # Get LLM response with function calling
    tools = get_function_tools()
    logger.debug("[conversation.py.handle_conversation] Calling LLM with function tools")
    response = llm_client.chat_completion(full_messages, tools=tools)
    
    # Process response
    assistant_message = response.choices[0].message
    tool_calls = llm_client.extract_tool_calls(response)
    
    # Handle function calls
    function_results = []
    if tool_calls:
        logger.info(f"[conversation.py.handle_conversation] Processing {len(tool_calls)} tool calls")
        for tool_call in tool_calls:
            func_name = tool_call["function"]
            func_args = json.loads(tool_call["arguments"])
            logger.debug(f"[conversation.py.handle_conversation] Executing function: {func_name} with args: {func_args}")
            
            result = await execute_function(
                func_name,
                func_args,
                conversation_id,
                conversation_manager
            )
            function_results.append(result)
            logger.debug(f"[conversation.py.handle_conversation] Function {func_name} result: {result}")
            
            # Add function result to messages for next LLM call
            full_messages.append({
                "role": "assistant",
                "content": None,
                "tool_calls": [
                    {
                        "id": tool_call["id"],
                        "type": "function",
                        "function": {
                            "name": func_name,
                            "arguments": tool_call["arguments"]
                        }
                    }
                ]
            })
            full_messages.append({
                "role": "tool",
                "tool_call_id": tool_call["id"],
                "content": json.dumps(result)
            })
        
        # Get final response after function execution
        logger.debug("[conversation.py.handle_conversation] Getting final LLM response after function execution")
        final_response = llm_client.chat_completion(full_messages, tools=tools)
        assistant_content = llm_client.extract_message_content(final_response)
    else:
        logger.debug("[conversation.py.handle_conversation] No tool calls, using direct response")
        assistant_content = llm_client.extract_message_content(response)
    
    # Add assistant message
    conversation_manager.add_message(conversation_id, "assistant", assistant_content)
    logger.debug(f"[conversation.py.handle_conversation] Added assistant message to conversation: {conversation_id}")
    
    # Get current state
    current_state = conversation_manager.get_state(conversation_id)
    logger.info(f"[conversation.py.handle_conversation] Conversation {conversation_id} state: {current_state}")
    
    return ConversationResponse(
        response=assistant_content,
        conversation_id=conversation_id,
        state=current_state,
        suggested_actions=get_suggested_actions(current_state)
    )


async def execute_function(
    function_name: str,
    arguments: dict,
    conversation_id: str,
    conv_manager: ConversationManager
) -> dict:
    """
    Execute a function call from the LLM.
    
    Args:
        function_name: Name of the function to execute
        arguments: Function arguments
        conversation_id: Current conversation ID
        conv_manager: Conversation manager instance
        
    Returns:
        Function result as dictionary
    """
    logger.info(f"[conversation.py.execute_function] Executing function: {function_name} for conversation: {conversation_id}")
    logger.debug(f"[conversation.py.execute_function] Function arguments: {arguments}")
    
    if function_name == "identify_provider":
        health_issue = arguments.get("health_issue")
        patient_name = arguments.get("patient_name")
        
        logger.info(f"[conversation.py.execute_function] Identifying provider for health issue: {health_issue}")
        
        # Match provider
        match = match_provider_for_issue(health_issue)
        
        if not match:
            logger.warning(f"[conversation.py.execute_function] No suitable provider found for issue: {health_issue}")
            return {
                "error": "No suitable provider found",
                "message": f"I apologize, but we don't currently have specialists available for '{health_issue}'. Our available specialties include: General Practitioner, Dermatologist, Cardiologist, Neurologist, Orthopedist, Pediatrician, Psychiatrist, Ophthalmologist, ENT Specialist, and Dentist. Would you like to see a General Practitioner who can help with most health concerns?",
                "available_specialties": ["General Practitioner", "Dermatologist", "Cardiologist", "Neurologist", "Orthopedist", "Pediatrician", "Psychiatrist", "Ophthalmologist", "ENT Specialist", "Dentist"]
            }
        
        logger.info(f"[conversation.py.execute_function] Provider matched: {match.provider_name} (ID: {match.provider_id})")
        
        # Update conversation context
        conv_manager.update_context(conversation_id, "health_issue", health_issue)
        conv_manager.update_context(conversation_id, "provider_id", match.provider_id)
        conv_manager.update_context(conversation_id, "provider_name", match.provider_name)
        if patient_name:
            conv_manager.update_context(conversation_id, "patient_name", patient_name)
            logger.debug(f"[conversation.py.execute_function] Updated patient name: {patient_name}")
        
        conv_manager.set_state(conversation_id, ConversationState.PROVIDER_MATCHED)
        logger.debug(f"[conversation.py.execute_function] Conversation state updated to: {ConversationState.PROVIDER_MATCHED}")
        
        # Get provider details
        provider = get_provider_by_id(match.provider_id)
        
        return {
            "provider_id": match.provider_id,
            "provider_name": match.provider_name,
            "specialty": match.specialty,
            "experience_years": provider.experience_years,
            "rating": provider.rating,
            "location": provider.location,
            "match_reason": match.match_reason
        }
    
    elif function_name == "check_availability":
        provider_id = arguments.get("provider_id")
        num_days = arguments.get("num_days", 7)
        time_preference = arguments.get("time_preference", "any")
        
        logger.info(f"[conversation.py.execute_function] Checking availability for provider: {provider_id}, days: {num_days}, time_preference: {time_preference}")
        
        # Get availability
        availability = get_availability_summary(provider_id, num_days)
        
        # Filter by time preference if specified
        if time_preference and time_preference != "any":
            filtered_availability = {}
            for date, slots in availability.items():
                filtered_slots = []
                for slot in slots:
                    hour = int(slot.split(":")[0])
                    if time_preference == "morning" and hour < 12:
                        filtered_slots.append(slot)
                    elif time_preference == "afternoon" and hour >= 12:
                        filtered_slots.append(slot)
                
                if filtered_slots:
                    filtered_availability[date] = filtered_slots
            
            availability = filtered_availability
            logger.debug(f"[conversation.py.execute_function] Filtered to {len(availability)} dates with {time_preference} slots")
        
        if not availability:
            logger.warning(f"[conversation.py.execute_function] No available slots found for provider: {provider_id}")
            provider = get_provider_by_id(provider_id)
            provider_name = provider.name if provider else "this provider"
            
            time_msg = f" in the {time_preference}" if time_preference != "any" else ""
            return {
                "error": "No available slots found",
                "message": f"I apologize, but {provider_name} doesn't have any available appointment slots{time_msg} in the next {num_days} days. Would you like me to check availability for a different time period, or would you prefer to see another provider with the same specialty?",
                "provider_id": provider_id
            }
        
        logger.info(f"[conversation.py.execute_function] Found availability for {len(availability)} dates")
        
        # Update conversation state
        conv_manager.update_context(conversation_id, "availability", availability)
        conv_manager.set_state(conversation_id, ConversationState.AVAILABILITY_CHECKED)
        logger.debug(f"[conversation.py.execute_function] Conversation state updated to: {ConversationState.AVAILABILITY_CHECKED}")
        
        return {
            "provider_id": provider_id,
            "availability": availability,
            "formatted_message": format_availability_message(availability)
        }
    
    elif function_name == "create_appointment":
        patient_name = arguments.get("patient_name")
        provider_id = arguments.get("provider_id")
        date = arguments.get("date")
        time = arguments.get("time")
        reason = arguments.get("reason")
        
        logger.info(f"[conversation.py.execute_function] Creating appointment for patient: {patient_name}, provider: {provider_id}, date: {date}, time: {time}")
        
        # Create appointment
        appointment_data = AppointmentCreate(
            patient_name=patient_name,
            provider_id=provider_id,
            date=date,
            time=time,
            reason=reason
        )
        
        appointment = create_appointment(appointment_data)
        
        if not appointment:
            logger.error(f"[conversation.py.execute_function] Failed to create appointment for provider: {provider_id} at {date} {time}")
            return {"error": "Failed to create appointment. Slot may no longer be available."}
        
        logger.info(f"[conversation.py.execute_function] Appointment created successfully: {appointment.id}")
        
        # Update conversation state
        conv_manager.update_context(conversation_id, "appointment_id", appointment.id)
        conv_manager.set_state(conversation_id, ConversationState.APPOINTMENT_CONFIRMED)
        logger.debug(f"[conversation.py.execute_function] Conversation state updated to: {ConversationState.APPOINTMENT_CONFIRMED}")
        
        return {
            "success": True,
            "appointment_id": appointment.id,
            "patient_name": appointment.patient_name,
            "provider_name": appointment.provider_name,
            "date": appointment.date,
            "time": appointment.time,
            "location": appointment.location
        }
    
    logger.error(f"[conversation.py.execute_function] Unknown function: {function_name}")
    return {"error": f"Unknown function: {function_name}"}


def get_suggested_actions(state: str) -> list:
    """Get suggested actions based on conversation state."""
    logger.debug(f"[conversation.py.get_suggested_actions] Getting suggested actions for state: {state}")
    
    if state == ConversationState.INITIAL:
        return ["Describe your health issue", "Ask about providers"]
    elif state == ConversationState.PROVIDER_MATCHED:
        return ["Check availability", "Ask about the provider"]
    elif state == ConversationState.AVAILABILITY_CHECKED:
        return ["Book an appointment", "Request different times"]
    elif state == ConversationState.APPOINTMENT_CONFIRMED:
        return ["Download .ics file", "Schedule another appointment"]
    return []
