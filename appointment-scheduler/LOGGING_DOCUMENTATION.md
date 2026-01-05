# Logging Documentation

## Overview
Comprehensive logging has been added throughout the appointment-scheduler application using Python's `logging` library. Each log message is prefaced with `[file_name.class.function]` to provide clear traceability.

## Logging Configuration

### Main Application (`backend/main.py`)
- Configured centralized logging with INFO level
- Format: `%(asctime)s - %(name)s - %(levelname)s - %(message)s`
- All modules use `logging.getLogger(__name__)` for proper logger hierarchy

## Files Modified with Logging

### 1. **backend/config.py**
- `[config.py.Config.__init__]` - Configuration initialization
- Logs: Model configuration, debug mode, API key presence warnings

### 2. **backend/main.py**
- `[main.py.root]` - Application startup and root endpoint
- `[main.py.health_check]` - Health check endpoint
- Logs: Application creation, middleware configuration, router inclusion

### 3. **backend/api/appointments.py**
- `[appointments.py.create_new_appointment]` - Appointment creation
- `[appointments.py.get_appointment_by_id]` - Appointment retrieval
- `[appointments.py.list_appointments]` - List all appointments
- `[appointments.py.download_ics_file]` - ICS file download
- Logs: Request details, validation results, success/error states

### 4. **backend/api/conversation.py**
- `[conversation.py.root]` - LLM client initialization
- `[conversation.py.handle_conversation]` - Main conversation handler
- `[conversation.py.execute_function]` - Function execution (identify_provider, check_availability, create_appointment)
- `[conversation.py.get_suggested_actions]` - Suggested action generation
- Logs: Message flow, LLM calls, tool executions, state transitions

### 5. **backend/llm/client.py**
- `[client.py.LLMClient.__init__]` - Client initialization
- `[client.py.LLMClient.chat_completion]` - Chat completion requests
- `[client.py.LLMClient.extract_message_content]` - Message extraction
- `[client.py.LLMClient.extract_tool_calls]` - Tool call extraction
- Logs: API initialization, request/response details, errors

### 6. **backend/llm/conversation_manager.py**
- `[conversation_manager.py.ConversationManager.__init__]` - Manager initialization
- `[conversation_manager.py.ConversationManager.create_conversation]` - New conversation creation
- `[conversation_manager.py.ConversationManager.add_message]` - Message addition
- `[conversation_manager.py.ConversationManager.get_messages]` - Message retrieval
- `[conversation_manager.py.ConversationManager.get_state]` - State retrieval
- `[conversation_manager.py.ConversationManager.set_state]` - State updates
- `[conversation_manager.py.ConversationManager.update_context]` - Context updates
- `[conversation_manager.py.ConversationManager.get_context]` - Context retrieval
- `[conversation_manager.py.ConversationManager.get_system_prompt]` - System prompt generation
- Logs: Conversation lifecycle, state transitions, context changes

### 7. **backend/llm/provider_matcher.py**
- `[provider_matcher.py.match_provider_for_issue]` - Provider matching
- `[provider_matcher.py.get_multiple_provider_options]` - Multiple provider options
- Logs: Matching logic, keyword detection, specialty selection, provider selection

### 8. **backend/llm/tools.py**
- `[tools.py.get_function_tools]` - Function tool definitions
- Logs: Tool retrieval

### 9. **backend/services/appointment_service.py**
- `[appointment_service.py.create_appointment]` - Appointment creation
- `[appointment_service.py.generate_ics_file]` - ICS file generation
- `[appointment_service.py.create_appointment_with_ics]` - Combined creation with ICS
- `[appointment_service.py.get_appointment]` - Appointment retrieval
- `[appointment_service.py.get_all_appointments]` - Get all appointments
- Logs: Creation flow, slot booking, ICS generation, retrieval operations

### 10. **backend/services/schedule_service.py**
- `[schedule_service.py.get_next_available_dates]` - Next available dates
- `[schedule_service.py.get_availability_summary]` - Availability summary
- `[schedule_service.py.find_common_availability]` - Common availability matching
- `[schedule_service.py.get_earliest_available_slot]` - Earliest slot finder
- `[schedule_service.py.format_availability_message]` - Availability formatting
- Logs: Schedule queries, availability searches, formatting operations

### 11. **backend/database/providers.py**
- `[providers.py.get_all_providers]` - Get all providers
- `[providers.py.get_provider_by_id]` - Get provider by ID
- `[providers.py.get_providers_by_specialty]` - Get providers by specialty
- `[providers.py.get_best_provider_for_specialty]` - Get best provider
- Logs: Database queries, lookup results, provider selection

### 12. **backend/database/schedules.py**
- `[schedules.py.generate_mock_schedule]` - Schedule generation
- `[schedules.py.get_provider_schedule]` - Schedule retrieval
- `[schedules.py.get_available_slots]` - Available slots
- `[schedules.py.book_slot]` - Slot booking
- `[schedules.py.clear_schedule_cache]` - Cache clearing
- Logs: Schedule generation, cache operations, booking operations

### 13. **streamlit_app.py**
- `[streamlit_app.py.root]` - Session initialization and UI events
- `[streamlit_app.py.send_message]` - API communication
- `[streamlit_app.py.check_health]` - Backend health checks
- Logs: User interactions, API calls, errors

## Log Levels Used

### INFO
- Application startup and configuration
- Major operations (appointment creation, provider matching)
- State transitions
- User interactions

### DEBUG
- Detailed operation flow
- Function parameters and return values
- Cache operations
- Internal state details

### WARNING
- Missing resources (appointments, providers not found)
- Failed operations (slot booking failures)
- Configuration issues (missing API keys)

### ERROR
- API failures
- Exception handling
- Critical operation failures

## Log Format Examples

```
2026-01-05 10:23:45 - backend.api.conversation - INFO - [conversation.py.handle_conversation] Received message: 'I have a skin rash...' for conversation: abc123
2026-01-05 10:23:46 - backend.llm.provider_matcher - INFO - [provider_matcher.py.match_provider_for_issue] Matched specialty: Dermatologist (confidence: 0.9)
2026-01-05 10:23:47 - backend.services.appointment_service - INFO - [appointment_service.py.create_appointment] Appointment created successfully: xyz789
```

## Benefits

1. **Traceability**: Every log has clear origin with `[file_name.class.function]` prefix
2. **Debugging**: Detailed flow through the application with DEBUG level
3. **Monitoring**: Track operations, errors, and performance
4. **Audit Trail**: Complete record of user interactions and system operations
5. **Troubleshooting**: Quick identification of issues with contextual information

## Usage

To view logs during development:
```bash
# Run with logging output
python -m uvicorn backend.main:app --reload

# Or for streamlit
streamlit run streamlit_app.py
```

To adjust log level:
```python
# In backend/main.py
logging.basicConfig(
    level=logging.DEBUG,  # Change to DEBUG, INFO, WARNING, ERROR
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

## Production Considerations

For production deployments, consider:
1. Using structured logging (JSON format)
2. Log aggregation service (ELK, Splunk, CloudWatch)
3. Log rotation and retention policies
4. Sensitive data redaction
5. Performance impact monitoring
