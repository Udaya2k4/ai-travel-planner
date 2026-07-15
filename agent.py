"""
Travel Planner Agent Module
Handles all IBM watsonx.ai / IBM Granite model interactions.
"""

import os
from dotenv import load_dotenv
from ibm_watsonx_ai import APIClient, Credentials
from ibm_watsonx_ai.foundation_models import ModelInference
from ibm_watsonx_ai.metanames import GenTextParamsMetaNames as GenParams

load_dotenv()

# ─────────────────────────────────────────────────────────────────────────────
# AGENT INSTRUCTIONS
# Customise the agent's persona, scope, tone, and output constraints here.
# These instructions are injected as a system prompt into every model call.
# ─────────────────────────────────────────────────────────────────────────────
AGENT_INSTRUCTIONS = """
You are WanderAI, an expert AI Travel Planner powered by IBM Granite.

The user has already provided all required travel details.
Do NOT ask for clarification or additional information.
Do NOT say "Let me know if any clarification is needed."

Always begin your response with:

## Trip Overview

Then generate a complete travel itinerary.

Your response must include:

## Trip Overview
- Brief introduction
- Trip highlights

## Day-wise Itinerary
For each day include:
- Morning
- Afternoon
- Evening

## Hotel Recommendations
- Budget
- Mid-range
- Luxury

## Transportation Guide

## Estimated Budget Breakdown

## Packing Checklist

## Weather Tips

## Top Attractions

## Hidden Gems

## Food Recommendations

## Safety Tips

Rules:
- Use Markdown headings.
- Keep the itinerary realistic.
- Mention approximate prices only.
- Do not mention that you are an AI.
- Do not ask follow-up questions.
- End with "Have a wonderful trip!"
"""

# ─────────────────────────────────────────────────────────────────────────────
# Model Configuration
# ─────────────────────────────────────────────────────────────────────────────
MODEL_ID = "meta-llama/llama-3-3-70b-instruct"

GENERATION_PARAMS = {
    GenParams.MAX_NEW_TOKENS: 2000,
    GenParams.MIN_NEW_TOKENS: 200,
    GenParams.TEMPERATURE: 0.7,
    GenParams.TOP_P: 0.9,
    GenParams.TOP_K: 50,
    GenParams.REPETITION_PENALTY: 1.1,
}


def _get_model() -> ModelInference:
    print("IBM_API_KEY:", "Loaded" if os.getenv("IBM_API_KEY") else "Missing")
    print("WATSONX_PROJECT_ID:", os.getenv("WATSONX_PROJECT_ID"))
    print("WATSONX_URL:", os.getenv("WATSONX_URL"))

    credentials = Credentials(
        url=os.getenv("WATSONX_URL", "https://us-south.ml.cloud.ibm.com"),
        api_key=os.getenv("IBM_API_KEY"),
    )

    client = APIClient(credentials)

    model = ModelInference(
        model_id=MODEL_ID,
        api_client=client,
        project_id=os.getenv("WATSONX_PROJECT_ID"),
        params=GENERATION_PARAMS,
    )

    return model


def build_travel_prompt(travel_data: dict) -> str:
    """
    Build a structured prompt from the user's travel inputs.

    Args:
        travel_data: dict with keys:
            source, destination, budget, days, travelers,
            travel_type, interests, travel_dates (optional),
            special_requirements (optional)

    Returns:
        A fully formatted prompt string.
    """
    source = travel_data.get("source", "Unknown")
    destination = travel_data.get("destination", "Unknown")
    budget = travel_data.get("budget", "moderate")
    days = travel_data.get("days", 5)
    travelers = travel_data.get("travelers", 1)
    travel_type = travel_data.get("travel_type", "solo")
    interests = travel_data.get("interests", "general sightseeing")
    travel_dates = travel_data.get("travel_dates", "not specified")
    special_requirements = travel_data.get("special_requirements", "none")

    prompt = f"""{AGENT_INSTRUCTIONS}

---

USER TRAVEL REQUEST:

- **From:** {source}
- **To:** {destination}
- **Travel Dates:** {travel_dates}
- **Duration:** {days} days
- **Number of Travellers:** {travelers} ({travel_type} travel)
- **Total Budget (USD):** ${budget}
- **Travel Interests:** {interests}
- **Special Requirements:** {special_requirements}

---

Please create a comprehensive travel plan that includes:

1. **Trip Overview** – brief summary and travel highlights
2. **Day-wise Itinerary** – detailed plan for each of the {days} days
   (morning / afternoon / evening breakdown)
3. **Hotel Recommendations** – 3 options (budget / mid-range / luxury)
   with approximate nightly rates
4. **Transportation Guide** – how to get there and get around locally
5. **Estimated Budget Breakdown** – per-person and total costs
6. **Packing Checklist** – essentials for this trip
7. **Weather & Best Time Tips** – what to expect during travel dates
8. **Top Local Attractions & Hidden Gems**
9. **Food & Dining Recommendations** – must-try dishes and restaurants
10. **Safety Tips & Important Notes**

Format your response in clean markdown with clear sections and bullet points.
"""
    return prompt


def generate_itinerary(travel_data: dict) -> dict:
    """
    Generate a travel itinerary using IBM Granite via watsonx.ai.

    Args:
        travel_data: User travel inputs as a dictionary.

    Returns:
        dict with keys 'success', 'itinerary' (or 'error').
    """
    try:
        model = _get_model()
        prompt = build_travel_prompt(travel_data)
        response = model.generate_text(prompt=prompt)

        if response:
            return {"success": True, "itinerary": response}
        return {"success": False, "error": "Empty response from model."}

    except Exception as exc:  # pragma: no cover
        return {"success": False, "error": str(exc)}


def chat_with_agent(conversation_history: list, user_message: str) -> dict:
    """
    Continue a multi-turn travel planning conversation.

    Args:
        conversation_history: list of {"role": "user"|"assistant", "content": str}
        user_message: the latest user question or refinement request.

    Returns:
        dict with keys 'success', 'response' (or 'error').
    """
    try:
        model = _get_model()

        # Build conversation context
        context_parts = [AGENT_INSTRUCTIONS, "\n\nCONVERSATION HISTORY:\n"]
        for turn in conversation_history[-6:]:   # keep last 6 turns for context
            role = "User" if turn["role"] == "user" else "WanderAI"
            context_parts.append(f"{role}: {turn['content']}")

        context_parts.append(f"\nUser: {user_message}\nWanderAI:")
        full_prompt = "\n".join(context_parts)

        response = model.generate_text(prompt=full_prompt)
        if response:
            return {"success": True, "response": response}
        return {"success": False, "error": "Empty response from model."}

    except Exception as exc:  # pragma: no cover
        return {"success": False, "error": str(exc)}
