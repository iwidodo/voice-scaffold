# Appointment Scheduler API

An LLM-powered appointment scheduling system that enables users to schedule appointments with healthcare providers through intelligent conversation.

## Features

- **Provider Database**: Mock healthcare providers with specialties, ratings, and locations
- **LLM-Powered Conversations**: Multi-turn conversations using OpenAI function calling
- **Smart Provider Matching**: Matches health issues to appropriate medical specialists
- **Schedule Management**: Real-time availability checking and slot booking
- **Appointment Creation**: Creates appointments and generates .ics calendar files
- **RESTful API**: FastAPI-based backend with comprehensive endpoints

## Architecture

```
appointment-scheduler/
├── backend/
│   ├── api/              # API endpoints
│   ├── database/         # Mock data stores
│   ├── llm/              # LLM integration
│   ├── models/           # Pydantic schemas
│   ├── services/         # Business logic
│   ├── main.py           # FastAPI app
│   └── config.py         # Configuration
├── tests/                # Test suite
├── requirements.txt      # Dependencies
└── run_local.sh         # Development server script
```

## Backend Process Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    User Input (Voice/Text)                      │
│              "I need a dental cleaning tomorrow"                │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                  POST /api/conversation/                        │
│  • Creates/resumes conversation                                 │
│  • Adds user message to history                                 │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│              ConversationManager.get_system_prompt()            │
│  • Injects current date/time                                    │
│  • Provides state-specific instructions                         │
│  • Voice formatting rules (no parentheses)                      │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│              OpenAI GPT-4o-mini (Function Calling)              │
│  • Analyzes user intent                                         │
│  • Decides which function to call                               │
│  • Returns function call OR text response                       │
└────────────────────────────┬────────────────────────────────────┘
                             │
              ┌──────────────┴──────────────┐
              │                             │
              ▼                             ▼
   ┌──────────────────┐         ┌──────────────────────┐
   │  Function Call   │         │   Text Response      │
   │  Required        │         │   (No more tools)    │
   └────────┬─────────┘         └──────────┬───────────┘
            │                              │
            ▼                              │
┌───────────────────────────────────────┐  │
│  execute_function()                   │  │
│  ┌─────────────────────────────────┐ │  │
│  │ identify_provider()             │ │  │
│  │ • Match specialty to keywords   │ │  │
│  │ • Query providers.csv           │ │  │
│  │ • Return provider details       │ │  │
│  └─────────────────────────────────┘ │  │
│  ┌─────────────────────────────────┐ │  │
│  │ check_availability()            │ │  │
│  │ • Query schedules.csv           │ │  │
│  │ • Filter by date/time           │ │  │
│  │ • Return available slots        │ │  │
│  └─────────────────────────────────┘ │  │
│  ┌─────────────────────────────────┐ │  │
│  │ create_appointment()            │ │  │
│  │ • Book slot in schedules.csv    │ │  │
│  │ • Save to CSV (persist)         │ │  │
│  │ • Generate .ics calendar file   │ │  │
│  └─────────────────────────────────┘ │  │
└───────────────┬───────────────────────┘  │
                │                          │
                ▼                          │
   ┌──────────────────────┐                │
   │  Function Result     │                │
   │  Added to Messages   │                │
   └──────────┬───────────┘                │
              │                            │
              └──────────┬─────────────────┘
                         │
                         ▼
              ┌──────────────────────┐
              │  Loop: Max 5 times   │
              │  (Function chaining) │
              └──────────┬───────────┘
                         │
                         ▼
              ┌──────────────────────┐
              │  LLM called again    │
              │  with function result│
              └──────────┬───────────┘
                         │
                         ▼
         ┌───────────────────────────────┐
         │  Final Text Response          │
         │  "Dr. White has slots at..."  │
         └───────────────┬───────────────┘
                         │
                         ▼
         ┌───────────────────────────────┐
         │  Update conversation state    │
         │  • initial → provider_matched │
         │  • provider_matched → avail.. │
         │  • ... → appointment_confirmed│
         └───────────────┬───────────────┘
                         │
                         ▼
         ┌───────────────────────────────┐
         │  Return JSON Response         │
         │  {                            │
         │    "response": "...",         │
         │    "state": "...",            │
         │    "suggestions": [...]       │
         │  }                            │
         └───────────────┬───────────────┘
                         │
                         ▼
         ┌───────────────────────────────┐
         │  Voice/UI displays response   │
         │  (TTS speaks it out)          │
         └───────────────────────────────┘
```

### Key Components

1. **Conversation Manager**: Maintains state and generates context-aware prompts
2. **LLM Client**: Handles OpenAI API calls with function calling
3. **Function Loop**: Chains multiple function calls (up to 5 iterations)
4. **CSV Database**: Persistent storage with in-memory caching
5. **State Machine**: Tracks conversation progress (initial → confirmed)

## Quick Start

### 1. Install Dependencies

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install packages
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env and add your OpenAI API key
OPENAI_API_KEY=your-api-key-here
```

### 3. Run the Server

```bash
# Using the convenience script
./run_local.sh

# Or manually
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

### 4. Run the Streamlit UI (Optional)

For a user-friendly chat interface, run the Streamlit UI in a separate terminal:

```bash
# Make sure the backend is running first (step 3)
# Then in a new terminal:
./run_streamlit.sh

# Or manually:
streamlit run streamlit_app.py
```

The Streamlit UI will open in your browser at `http://localhost:8501`

### 5. View API Documentation

Open your browser to:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Usage Examples

### Example 1: Using the Streamlit UI (Recommended for Users)

The easiest way to interact with the system is through the Streamlit chat interface:

1. Start the backend: `./run_local.sh`
2. In a new terminal, start Streamlit: `./run_streamlit.sh`
3. Open your browser to `http://localhost:8501`
4. Chat naturally with the AI assistant to book appointments

Features:
- 💬 Natural conversation interface
- 🔄 Conversation history management
- 💡 Contextual suggestions
- 🏥 Real-time appointment booking

### Example 2: Conversation API (Programmatic Access)

The conversation endpoint provides an LLM-powered interface that handles the entire flow:

```python
import requests

# Start a conversation
response = requests.post("http://localhost:8000/api/conversation/", json={
    "message": "I have a rash, who should I see?"
})

data = response.json()
print(data["response"])
# The LLM will identify appropriate providers

# Continue the conversation
response = requests.post("http://localhost:8000/api/conversation/", json={
    "message": "When can I see them?",
    "conversation_id": data["conversation_id"]
})

print(response.json()["response"])
# The LLM will show available times
```

### Example 3: Direct API Usage

You can also use the appointment API directly:

```python
import requests

# Create an appointment
response = requests.post("http://localhost:8000/api/appointments/", json={
    "patient_name": "John Doe",
    "provider_id": "p001",
    "date": "2026-01-20",
    "time": "10:00",
    "reason": "Skin checkup"
})

appointment = response.json()
print(f"Appointment created: {appointment['appointment_id']}")

# Download .ics file
ics_response = requests.get(
    f"http://localhost:8000/api/appointments/{appointment['appointment_id']}/ics"
)

with open("appointment.ics", "wb") as f:
    f.write(ics_response.content)
```

## API Endpoints

### Conversation API

- `POST /api/conversation/` - Handle a conversation turn
  - Request: `{"message": "string", "conversation_id": "optional"}`
  - Response: Includes LLM response, conversation ID, and state

### Appointments API

- `POST /api/appointments/` - Create a new appointment
- `GET /api/appointments/` - List all appointments
- `GET /api/appointments/{id}` - Get appointment details
- `GET /api/appointments/{id}/ics` - Download .ics calendar file

## User Flow Examples

### Flow 1: Direct Issue Query

```
User: "I have a rash, who should I see?"
System: "I recommend Dr. Sarah Johnson, a dermatologist..."
User: "When can I see them?"
System: "Here are available times: Monday 10:00, Tuesday 14:00..."
User: "Book me for Monday at 10:00"
System: "Appointment confirmed! [generates .ics file]"
```

### Flow 2: Open-Ended Query

```
User: "Who is your best doctor?"
System: "I'd be happy to help. What health issue are you experiencing?"
User: "I have severe headaches"
System: "I recommend Dr. David Kim, a neurologist..."
[continues with scheduling flow]
```

## LLM Function Tools

The system uses OpenAI function calling with three tools:

1. **identify_provider**: Matches health issues to providers
2. **check_availability**: Retrieves provider schedules
3. **create_appointment**: Books appointments

These functions are automatically called by the LLM as needed during conversations.

## Testing

Run the test suite:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=backend tests/

# Run specific test file
pytest tests/test_provider_matcher.py

# Run with verbose output
pytest -v
```

Test coverage includes:
- Provider matching logic
- Conversation state management
- Appointment creation and .ics generation
- Schedule availability checking
- API endpoints

## Data Models

### Provider
```python
{
    "id": "p001",
    "name": "Dr. Sarah Johnson",
    "specialty": "Dermatologist",
    "experience_years": 15,
    "rating": 4.8,
    "location": "123 Medical Plaza"
}
```

### Appointment
```python
{
    "id": "uuid",
    "patient_name": "John Doe",
    "provider_id": "p001",
    "date": "2026-01-20",
    "time": "10:00",
    "location": "123 Medical Plaza",
    "reason": "Checkup"
}
```

### Schedule
```python
{
    "provider_id": "p001",
    "date": "2026-01-20",
    "available_slots": ["09:00", "10:00", "14:00", "15:30"]
}
```

## Configuration

Environment variables (in `.env`):

```bash
OPENAI_API_KEY=your-api-key-here
OPENAI_MODEL=gpt-4o-mini  # Optional, defaults to gpt-4o-mini
DEBUG=false  # Optional
```

## Provider Specialties

The system supports the following medical specialties:

- General Practitioner
- Dermatologist (skin issues)
- Cardiologist (heart conditions)
- Neurologist (headaches, neurological issues)
- Orthopedist (bone and joint problems)
- Pediatrician (children's health)
- Psychiatrist (mental health)
- Ophthalmologist (eye care)
- ENT Specialist (ear, nose, throat)

The provider matcher uses keyword matching to identify the appropriate specialty based on the patient's description.

## Development

### Project Structure

- `backend/api/` - FastAPI route handlers
- `backend/database/` - Mock data storage (easily replaceable with real DB)
- `backend/llm/` - LLM client and conversation management
- `backend/models/` - Pydantic schemas and constants
- `backend/services/` - Business logic layer
- `tests/` - Comprehensive test suite

### Adding New Providers

Edit `backend/database/providers.py` and add to `PROVIDERS_DB`:

```python
Provider(
    id="p011",
    name="Dr. New Doctor",
    specialty=Specialty.GENERAL_PRACTITIONER,
    experience_years=10,
    rating=4.5,
    location="New Clinic"
)
```

### Adding New Specialties

1. Add to `Specialty` enum in `backend/models/constants.py`
2. Add keyword mappings to `ISSUE_TO_SPECIALTY`
3. Add providers with the new specialty

## Future Enhancements

- Voice input/output integration (using existing voice-scaffold)
- Real database integration (PostgreSQL/MongoDB)
- Email/SMS notifications
- Recurring appointments
- Multi-language support
- Patient authentication
- Provider calendars sync (Google Calendar, Outlook)
- Payment integration
- Insurance verification

## Technology Stack

- **Backend**: FastAPI (Python 3.10+)
- **LLM**: OpenAI GPT-4o-mini with function calling
- **Validation**: Pydantic v2
- **Calendar**: icalendar
- **Testing**: pytest with asyncio support
- **Documentation**: Auto-generated with FastAPI

## License

MIT License

## Support

For issues or questions, please open an issue on the GitHub repository.
