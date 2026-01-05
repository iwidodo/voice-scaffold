"""
Function tools definitions for LLM function calling.
"""
import logging

logger = logging.getLogger(__name__)


def get_function_tools():
    """
    Get the list of function tools for OpenAI function calling.
    
    Returns:
        List of tool definitions
    """
    logger.debug("[tools.py.get_function_tools] Retrieving function tools for LLM")
    
    tools = [
        {
            "type": "function",
            "function": {
                "name": "identify_provider",
                "description": "Identify the best healthcare provider based on the patient's health issue. Use this when the patient describes their symptoms or health concern.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "health_issue": {
                            "type": "string",
                            "description": "The patient's health issue or symptoms"
                        },
                        "patient_name": {
                            "type": "string",
                            "description": "The patient's name if provided"
                        }
                    },
                    "required": ["health_issue"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "check_availability",
                "description": "Check the availability of a specific provider. Use this when you need to find available appointment times.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "provider_id": {
                            "type": "string",
                            "description": "The ID of the provider to check availability for"
                        },
                        "preferred_dates": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Optional list of preferred dates in YYYY-MM-DD format"
                        },
                        "time_preference": {
                            "type": "string",
                            "enum": ["morning", "afternoon", "any"],
                            "description": "Time of day preference: 'morning' (before 12 PM), 'afternoon' (12 PM or later), or 'any'"
                        },
                        "num_days": {
                            "type": "integer",
                            "description": "Number of days to look ahead (default: 7)"
                        }
                    },
                    "required": ["provider_id"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "create_appointment",
                "description": "Create an appointment for the patient. Use this when the patient has confirmed all details (provider, date, and time).",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "patient_name": {
                            "type": "string",
                            "description": "The patient's full name"
                        },
                        "provider_id": {
                            "type": "string",
                            "description": "The ID of the provider"
                        },
                        "date": {
                            "type": "string",
                            "description": "Appointment date in YYYY-MM-DD format"
                        },
                        "time": {
                            "type": "string",
                            "description": "Appointment time in HH:MM format (24-hour)"
                        },
                        "reason": {
                            "type": "string",
                            "description": "Reason for the appointment"
                        }
                    },
                    "required": ["patient_name", "provider_id", "date", "time"]
                }
            }
        }
    ]
    
    logger.debug(f"[tools.py.get_function_tools] Returning {len(tools)} function tools")
    return tools
