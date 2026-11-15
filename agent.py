import os
from datetime import date

import requests
from google import genai
from google.genai import types

MODEL = "gemini-3.5-flash-lite"
MAX_TOOL_CALLS = 6  # safety limit: the agent cannot call tools more than this per message

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

# Sample data written for this demo. Check it before using it for a real trip.
TREKS = [
    {"name": "Sinhagad", "near": "Pune", "level": "easy to moderate"},
    {"name": "Lohagad", "near": "Lonavla", "level": "easy"},
    {"name": "Rajmachi", "near": "Lonavla", "level": "easy to moderate"},
]


def find_treks(near: str) -> str:
    """List sample treks near a town, for example 'Lonavla' or 'Pune'."""
    print(f"[tool called] find_treks({near})")
    found = [t for t in TREKS if t["near"].lower() == near.lower()]
    if not found:
        return f"No treks in my list near {near}."
    return "; ".join(f"{t['name']} ({t['level']})" for t in found)


def get_today() -> str:
    """Return today's date in YYYY-MM-DD format."""
    print("[tool called] get_today()")
    return date.today().isoformat()


def days_between(start_date: str, end_date: str) -> int:
    """Return the number of days from start_date to end_date. Both must be in YYYY-MM-DD format."""
    print(f"[tool called] days_between({start_date}, {end_date})")
    return (date.fromisoformat(end_date) - date.fromisoformat(start_date)).days


def get_weather(place: str, date: str) -> str:
    """Get the forecast for a place on one date, for example place 'Lonavla' and date '2026-11-22' (YYYY-MM-DD)."""
    print(f"[tool called] get_weather({place}, {date})")
    try:
        geo = requests.get(
            "https://geocoding-api.open-meteo.com/v1/search",
            params={"name": place, "count": 1},
            timeout=15,
        ).json()
        if not geo.get("results"):
            return f"Could not find the place: {place}"
        g = geo["results"][0]
        w = requests.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": g["latitude"],
                "longitude": g["longitude"],
                "daily": "temperature_2m_max,temperature_2m_min,precipitation_probability_max",
                "timezone": "auto",
                "forecast_days": 16,
            },
            timeout=15,
        ).json()
    except requests.RequestException:
        return "The weather service could not be reached right now."
    d = w["daily"]
    if date not in d["time"]:
        return f"No forecast available for {date}. I only have {d['time'][0]} to {d['time'][-1]}."
    i = d["time"].index(date)
    return (
        f"Forecast for {g['name']} on {date}: "
        f"{d['temperature_2m_min'][i]} to {d['temperature_2m_max'][i]} C, "
        f"rain chance {d['precipitation_probability_max'][i]}%. "
        "Note: forecasts for dates far ahead are less reliable."
    )


INSTRUCTION = (
    "You are a trek planner. Use the tools for treks, weather and dates. "
    "Only state facts about treks, weather and dates that come from the tools. "
    "If a tool says it cannot find something, say so honestly and do not make up an answer."
)

config = types.GenerateContentConfig(
    tools=[find_treks, get_weather, get_today, days_between],
    system_instruction=INSTRUCTION,
    automatic_function_calling=types.AutomaticFunctionCallingConfig(
        maximum_remote_calls=MAX_TOOL_CALLS
    ),
)


def main():
    chat = client.chats.create(model=MODEL, config=config)  # the chat session keeps memory
    print("Trek Planner Agent. Type 'quit' to stop.")
    while True:
        message = input("\nYou: ").strip()
        if message.lower() == "quit":
            break
        if not message:
            continue
        print("Agent:", chat.send_message(message).text)


if __name__ == "__main__":
    main()
