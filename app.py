"""
Travel Planner – Flask Application Entry Point
"""

import os
import json
from flask import (
    Flask,
    render_template,
    request,
    jsonify,
    session,
    redirect,
    url_for,
)
from dotenv import load_dotenv
from agent import generate_itinerary, chat_with_agent

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "change-me-in-production")

# ─────────────────────────────────────────────────────────────────────────────
# Helper
# ─────────────────────────────────────────────────────────────────────────────

TRAVEL_TYPES = ["solo", "couple", "family", "group"]
INTEREST_OPTIONS = [
    "Adventure & Outdoor Activities",
    "Cultural & Heritage",
    "Beach & Relaxation",
    "Food & Culinary",
    "Wildlife & Nature",
    "Shopping & City Life",
    "Religious & Spiritual",
    "Photography",
    "Backpacking on a Budget",
    "Luxury & Wellness",
]


def _validate_form(form: dict) -> list[str]:
    """Return a list of validation error messages (empty = valid)."""
    errors = []
    if not form.get("source", "").strip():
        errors.append("Source city / country is required.")
    if not form.get("destination", "").strip():
        errors.append("Destination is required.")
    try:
        days = int(form.get("days", 0))
        if days < 1 or days > 30:
            errors.append("Number of days must be between 1 and 30.")
    except ValueError:
        errors.append("Number of days must be a valid integer.")
    try:
        travelers = int(form.get("travelers", 0))
        if travelers < 1 or travelers > 100:
            errors.append("Number of travellers must be between 1 and 100.")
    except ValueError:
        errors.append("Number of travellers must be a valid integer.")
    try:
        budget = float(form.get("budget", 0))
        if budget < 0:
            errors.append("Budget must be a positive number.")
    except ValueError:
        errors.append("Budget must be a valid number.")
    return errors


# ─────────────────────────────────────────────────────────────────────────────
# Routes
# ─────────────────────────────────────────────────────────────────────────────

@app.route("/", methods=["GET"])
def index():
    """Render the travel planning form."""
    return render_template(
        "index.html",
        travel_types=TRAVEL_TYPES,
        interest_options=INTEREST_OPTIONS,
    )


@app.route("/plan", methods=["POST"])
def plan():
    """Process the travel form and generate an itinerary."""
    form = request.form.to_dict()
    interests_list = request.form.getlist("interests")
    form["interests"] = ", ".join(interests_list) if interests_list else "General sightseeing"

    errors = _validate_form(form)
    if errors:
        return render_template(
            "index.html",
            travel_types=TRAVEL_TYPES,
            interest_options=INTEREST_OPTIONS,
            errors=errors,
            form=form,
        )

    travel_data = {
        "source": form["source"].strip(),
        "destination": form["destination"].strip(),
        "budget": form.get("budget", "1000"),
        "days": int(form.get("days", 5)),
        "travelers": int(form.get("travelers", 1)),
        "travel_type": form.get("travel_type", "solo"),
        "interests": form["interests"],
        "travel_dates": form.get("travel_dates", "not specified").strip(),
        "special_requirements": form.get("special_requirements", "").strip(),
    }

    # Store in session for the chat feature
    session["travel_data"] = travel_data
    session["conversation"] = []

    result = generate_itinerary(travel_data)

    if result["success"]:
        # Seed the conversation history with the first exchange
        session["conversation"] = [
            {
                "role": "assistant",
                "content": result["itinerary"],
            }
        ]
        return render_template(
            "result.html",
            itinerary=result["itinerary"],
            travel_data=travel_data,
        )

    return render_template(
        "index.html",
        travel_types=TRAVEL_TYPES,
        interest_options=INTEREST_OPTIONS,
        errors=[f"AI Error: {result['error']}"],
        form=form,
    )


@app.route("/chat", methods=["POST"])
def chat():
    """Handle follow-up chat questions about the itinerary."""
    data = request.get_json(silent=True) or {}
    user_message = data.get("message", "").strip()

    if not user_message:
        return jsonify({"success": False, "error": "Message cannot be empty."}), 400

    conversation = session.get("conversation", [])
    conversation.append({"role": "user", "content": user_message})

    result = chat_with_agent(conversation, user_message)

    if result["success"]:
        conversation.append({"role": "assistant", "content": result["response"]})
        session["conversation"] = conversation
        return jsonify({"success": True, "response": result["response"]})

    return jsonify({"success": False, "error": result["error"]}), 500


@app.route("/reset", methods=["GET"])
def reset():
    """Clear session and return to home."""
    session.clear()
    return redirect(url_for("index"))


# ─────────────────────────────────────────────────────────────────────────────
# Run
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    host = os.getenv("APP_HOST", "0.0.0.0")
    port = int(os.getenv("APP_PORT", 5000))
    debug = os.getenv("FLASK_DEBUG", "True").lower() == "true"
    app.run(host=host, port=port, debug=debug)
