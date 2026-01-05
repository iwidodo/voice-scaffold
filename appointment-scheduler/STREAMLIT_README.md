# Streamlit UI for Appointment Scheduler

This is a user-friendly chat interface for the appointment scheduling system.

## Quick Start

1. **Start the backend server** (in one terminal):
   ```bash
   cd /path/to/appointment-scheduler
   ./run_local.sh
   ```

2. **Start the Streamlit UI** (in another terminal):
   ```bash
   cd /path/to/appointment-scheduler
   ./run_streamlit.sh
   ```

3. **Open your browser** to `http://localhost:8501`

## Features

- 💬 **Chat Interface**: Natural conversation with the AI assistant
- 🏥 **Provider Matching**: Automatically finds the right healthcare provider for your issue
- 📅 **Availability Check**: Shows available appointment slots
- ✅ **Appointment Booking**: Books appointments in real-time
- 💡 **Smart Suggestions**: Contextual action suggestions based on conversation state
- 🔄 **Conversation Memory**: Maintains context throughout the conversation

## Example Conversations

### Scenario 1: Book a dermatology appointment
```
You: I have a rash that won't go away
AI: I recommend Dr. Sarah Johnson, a dermatologist with 15 years of experience...
You: What times are available?
AI: Here are Dr. Johnson's available times for the next 7 days...
You: Book me for Monday at 10:00 AM
AI: Your appointment has been confirmed! I'll send you the details.
```

### Scenario 2: General health concern
```
You: I need to see a doctor
AI: I'd be happy to help. What health concern brings you in today?
You: I've been having chest pains
AI: I recommend Dr. Michael Chen, a cardiologist with excellent ratings...
```

## UI Components

- **Chat Messages**: View conversation history
- **Suggested Actions**: Quick action buttons based on current state
- **Conversation Reset**: Start a new conversation anytime
- **Health Check**: Automatic backend connection verification
- **Error Handling**: Friendly error messages if backend is unavailable

## Technical Details

- Built with Streamlit 1.30+
- Uses requests library to communicate with FastAPI backend
- Maintains conversation state across messages
- Responsive design that works on desktop and mobile

## Troubleshooting

### "Backend server is not running" error
Make sure the FastAPI backend is running on `http://localhost:8000`:
```bash
./run_local.sh
```

### Port already in use
If port 8501 is already in use, Streamlit will automatically try the next available port.

### Connection timeout
Check that your `.env` file has a valid OpenAI API key and the backend started successfully.
