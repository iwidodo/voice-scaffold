"""
Conversation API endpoints for LLM-powered appointment scheduling.
"""
import json
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

router = APIRouter(prefix="/api/conversation", tags=["conversation"])

# Global conversation manager (in production, use a proper store)
conversation_manager = ConversationManager()

# Initialize LLM client
try:
    llm_client = LLMClient(model=config.OPENAI_MODEL)
except ValueError:
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
    if not llm_client:
        raise HTTPException(
            status_code=500,
            detail="OpenAI API key not configured. Set OPENAI_API_KEY environment variable."
        )
    
    # Get or create conversation
    conversation_id = request.conversation_id
    if not conversation_id:
        conversation_id = conversation_manager.create_conversation()
    
    # Add user message
    conversation_manager.add_message(conversation_id, "user", request.message)
    
    # Get conversation history and system prompt
    messages = conversation_manager.get_messages(conversation_id)
    system_prompt = conversation_manager.get_system_prompt(conversation_id)
    
    # Prepend system message
    full_messages = [{"role": "system", "content": system_prompt}] + messages
    
    # Get LLM response with function calling
    tools = get_function_tools()
    response = llm_client.chat_completion(full_messages, tools=tools)
    
    # Process response
    assistant_message = response.choices[0].message
    tool_calls = llm_client.extract_tool_calls(response)
    
    # Handle function calls
    function_results = []
    if tool_calls:
        for tool_call in tool_calls:
            func_name = tool_call["function"]
            func_args = json.loads(tool_call["arguments"])
            
            result = await execute_function(
                func_name,
                func_args,
                conversation_id,
                conversation_manager
            )
            function_results.append(result)
            
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
        final_response = llm_client.chat_completion(full_messages, tools=tools)
        assistant_content = llm_client.extract_message_content(final_response)
    else:
        assistant_content = llm_client.extract_message_content(response)
    
    # Add assistant message
    conversation_manager.add_message(conversation_id, "assistant", assistant_content)
    
    # Get current state
    current_state = conversation_manager.get_state(conversation_id)
    
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
    if function_name == "identify_provider":
        health_issue = arguments.get("health_issue")
        patient_name = arguments.get("patient_name")
        
        # Match provider
        match = match_provider_for_issue(health_issue)
        
        if not match:
            return {"error": "No suitable provider found"}
        
        # Update conversation context
        conv_manager.update_context(conversation_id, "health_issue", health_issue)
        conv_manager.update_context(conversation_id, "provider_id", match.provider_id)
        conv_manager.update_context(conversation_id, "provider_name", match.provider_name)
        if patient_name:
            conv_manager.update_context(conversation_id, "patient_name", patient_name)
        
        conv_manager.set_state(conversation_id, ConversationState.PROVIDER_MATCHED)
        
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
        
        # Get availability
        availability = get_availability_summary(provider_id, num_days)
        
        if not availability:
            return {"error": "No available slots found"}
        
        # Update conversation state
        conv_manager.update_context(conversation_id, "availability", availability)
        conv_manager.set_state(conversation_id, ConversationState.AVAILABILITY_CHECKED)
        
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
            return {"error": "Failed to create appointment. Slot may no longer be available."}
        
        # Update conversation state
        conv_manager.update_context(conversation_id, "appointment_id", appointment.id)
        conv_manager.set_state(conversation_id, ConversationState.APPOINTMENT_CONFIRMED)
        
        return {
            "success": True,
            "appointment_id": appointment.id,
            "patient_name": appointment.patient_name,
            "provider_name": appointment.provider_name,
            "date": appointment.date,
            "time": appointment.time,
            "location": appointment.location
        }
    
    return {"error": f"Unknown function: {function_name}"}


def get_suggested_actions(state: str) -> list:
    """Get suggested actions based on conversation state."""
    if state == ConversationState.INITIAL:
        return ["Describe your health issue", "Ask about providers"]
    elif state == ConversationState.PROVIDER_MATCHED:
        return ["Check availability", "Ask about the provider"]
    elif state == ConversationState.AVAILABILITY_CHECKED:
        return ["Book an appointment", "Request different times"]
    elif state == ConversationState.APPOINTMENT_CONFIRMED:
        return ["Download .ics file", "Schedule another appointment"]
    return []
