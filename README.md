# Trek Planner Agent

A beginner AI agent in Python that helps plan a trek. I built it for Module 05 (AI Agents, Tools and Automation) of my Codomax Digital Solutions internship.

A normal chatbot only answers with text. An agent can also decide to use a tool, look at the result, and then answer. You can ask it something like:

> I want to go trekking near Lonavla on 22 November 2026. Which treks can I do, what is the weather that day, and how many days are left?

## How it works

Understand Task -> Decide Action -> Use Tool -> Process Result -> Respond

The AI model (`gemini-3.5-flash-lite`) reads the question, decides which tools it needs, calls them, reads what they return, and writes the final answer. It can call several tools in a row.

## Tools

| Tool | What it does |
|---|---|
| `find_treks(near)` | Lists treks near a town from a small sample list in `agent.py` |
| `get_weather(place, date)` | Gets the forecast for one date from the free Open-Meteo service (no API key needed) |
| `get_today()` | Returns today's date |
| `days_between(start_date, end_date)` | Counts the days between two dates |

## Memory and safety

- **Memory:** the app uses a chat session, so the agent remembers earlier messages. In my test, "Which treks can I do there?" and "What will the weather be on that day?" were understood without repeating the place and date.
- **Tool-call limit:** the agent can make at most 6 tool calls per message.
- **Honesty instruction:** the agent is told to use only facts from the tools and to say so when a tool cannot find something.

## What I tested in Google Colab

| Question | What happened |
|---|---|
| Trek near Lonavla on 22 Nov 2026 | Used 4 tools in order (treks, weather, today, days between). Answer was correct. |
| Weather near Lonavla on 1 March 2027 | Said it has no forecast for that date and gave the real date range of the tool. |
| Treks near Mumbai | Said there are no treks near Mumbai in the list and suggested Lonavla or Pune. |

## Limitations (what I found)

- **Place names must match the weather service's spelling.** "Lonavla" worked, but "Lonavala" and "Lonavale" were not found.
- **Forecasts only cover about 16 days ahead,** and forecasts far ahead are less reliable.
- **My first version showed a 3-day forecast as if it was for the trip date.** I fixed it by making the weather tool take the trip date and say when there is no forecast for it.
- **The agent added its own facts at first.** With a short instruction, it described Rajmachi with details that were not in my trek list. After I added "only state facts that come from the tools", the extra details disappeared in my test. I only tested this once, so it may not work every time.
- **The trek list is sample data that I wrote for this demo** (3 treks, simple difficulty labels). Please check it before using it for a real trip.

## How to run

1. Install the packages:

   ```
   pip install -r requirements.txt
   ```

2. Get a Gemini API key and set it as an environment variable. Never put your key in the code or upload it to GitHub.

   - Windows (Command Prompt): `set GEMINI_API_KEY=your_key_here`
   - Mac/Linux: `export GEMINI_API_KEY=your_key_here`
   - Google Colab: save the key in **Secrets** with the name `GEMINI_API_KEY`, then run:

     ```python
     import os
     from google.colab import userdata
     os.environ["GEMINI_API_KEY"] = userdata.get("GEMINI_API_KEY")
     ```

3. Run the agent:

   ```
   python agent.py
   ```

4. Type a question. Type `quit` to stop.

## Files

- `agent.py` - tools, agent settings and chat loop
- `requirements.txt` - Python packages

## Built with

Python, Google Gemini API (`google-genai`), `requests`, Open-Meteo (free weather service)

## Note

The agent was built and tested step by step in Google Colab. `agent.py` is the same code arranged as a chat program. The model name is the one that worked for my API key, so yours may differ.
