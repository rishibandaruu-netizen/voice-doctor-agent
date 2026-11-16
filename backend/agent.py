
import re

from pipecat.services.google.llm import GoogleLLMService
from pipecat.services.llm_service import FunctionCallParams

from backend.tools import (
    check_doctor_availability,
    book_appointment,
    cancel_appointment,
)


# Use a lighter Gemini model
GEMINI_MODEL = "gemini-3.5-flash-lite"


SYSTEM_INSTRUCTION = """
You are a polite voice-based doctor appointment assistant.

BOOKING RULES:
1. Ask which doctor or specialty the patient needs.
2. Check availability using the availability function.
3. Show available doctors and appointment slots.
4. Ask the patient to select a slot.
5. Ask for the patient's name and phone number.
6. The phone number MUST contain exactly 10 digits.
7. Repeat all 10 digits individually and ask the patient to confirm.
8. If the number is invalid, ask again.
9. After phone confirmation, ask:
   Would you like me to book this appointment?
10. Only call the booking function after a clear YES.
11. Never treat "okay" or unrelated speech as booking consent.
12. Never invent booking results.

CANCELLATION RULES:
1. Ask for appointment ID and phone number.
2. Validate that the phone number contains exactly 10 digits.
3. Repeat the number and ask for confirmation.
4. Ask whether the patient wants to cancel.
5. Only call cancellation after a clear YES.

Speak in simple, friendly English.
Keep responses short because this is a voice assistant.
"""


GEMINI_TOOLS = [
    {
        "function_declarations": [
            {
                "name": "check_doctor_availability",
                "description": "Find available doctors and appointment slots.",
                "parameters": {
                    "type": "OBJECT",
                    "properties": {
                        "specialty": {
                            "type": "STRING"
                        }
                    },
                    "required": []
                }
            },
            {
                "name": "book_appointment",
                "description": "Book an appointment after explicit patient confirmation.",
                "parameters": {
                    "type": "OBJECT",
                    "properties": {
                        "slot_id": {
                            "type": "INTEGER"
                        },
                        "phone": {
                            "type": "STRING"
                        },
                        "patient_name": {
                            "type": "STRING"
                        },
                        "confirmed": {
                            "type": "BOOLEAN"
                        }
                    },
                    "required": [
                        "slot_id",
                        "phone",
                        "confirmed"
                    ]
                }
            },
            {
                "name": "cancel_appointment",
                "description": "Cancel an appointment after explicit patient confirmation.",
                "parameters": {
                    "type": "OBJECT",
                    "properties": {
                        "appointment_id": {
                            "type": "INTEGER"
                        },
                        "phone": {
                            "type": "STRING"
                        },
                        "confirmed": {
                            "type": "BOOLEAN"
                        }
                    },
                    "required": [
                        "appointment_id",
                        "phone",
                        "confirmed"
                    ]
                }
            }
        ]
    }
]


async def availability_handler(params: FunctionCallParams):
    specialty = params.arguments.get("specialty")

    result = check_doctor_availability(specialty)

    await params.result_callback({
        "success": True,
        "available_slots": result
    })


async def booking_handler(params: FunctionCallParams):
    arguments = params.arguments

    if arguments.get("confirmed") is not True:
        await params.result_callback({
            "success": False,
            "message": "Explicit patient confirmation is required."
        })
        return

    phone = str(arguments.get("phone", "")).strip()

    if not re.fullmatch(r"\d{10}", phone):
        await params.result_callback({
            "success": False,
            "message": "Invalid phone number. Ask for exactly 10 digits."
        })
        return

    try:
        slot_id = int(arguments["slot_id"])
    except (KeyError, TypeError, ValueError):
        await params.result_callback({
            "success": False,
            "message": "Invalid appointment slot."
        })
        return

    result = book_appointment(
        slot_id=slot_id,
        phone=phone,
        patient_name=arguments.get("patient_name")
    )

    await params.result_callback(result)


async def cancellation_handler(params: FunctionCallParams):
    arguments = params.arguments

    if arguments.get("confirmed") is not True:
        await params.result_callback({
            "success": False,
            "message": "Explicit patient confirmation is required."
        })
        return

    phone = str(arguments.get("phone", "")).strip()

    if not re.fullmatch(r"\d{10}", phone):
        await params.result_callback({
            "success": False,
            "message": "Invalid phone number. Ask for exactly 10 digits."
        })
        return

    try:
        appointment_id = int(arguments["appointment_id"])
    except (KeyError, TypeError, ValueError):
        await params.result_callback({
            "success": False,
            "message": "Invalid appointment ID."
        })
        return

    result = cancel_appointment(
        appointment_id=appointment_id,
        phone=phone
    )

    await params.result_callback(result)


def create_llm(api_key: str):

    llm = GoogleLLMService(
        api_key=api_key,
        model=GEMINI_MODEL,
        tools=GEMINI_TOOLS,
        settings=GoogleLLMService.Settings(
            system_instruction=SYSTEM_INSTRUCTION
        )
    )

    llm.register_function(
        "check_doctor_availability",
        availability_handler
    )

    llm.register_function(
        "book_appointment",
        booking_handler
    )

    llm.register_function(
        "cancel_appointment",
        cancellation_handler
    )

    return llm
