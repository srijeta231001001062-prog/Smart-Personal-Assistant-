import re
import json
import requests
import datetime
from bs4 import BeautifulSoup


def color(txt, c="cyan"):
    colors = {"red":"\033[91m","green":"\033[92m","yellow":"\033[93m","blue":"\033[94m","cyan":"\033[96m","end":"\033[0m"}
    return f"{colors.get(c, '')}{txt}{colors['end']}"

MEMORY_FILE = "assistant_memory.json"

def load_memory():
    try:
        with open(MEMORY_FILE, "r") as f:
            return json.load(f)
    except:
        return {"reminders": []}

def save_memory(data):
    with open(MEMORY_FILE, "w") as f:
        json.dump(data, f, indent=4)

memory = load_memory()

def scrape_weather(city="your city"):
    query = f"weather in {city}".replace(" ", "+")
    url = f"https://www.google.com/search?q={query}"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")
        temperature = soup.find("span", {"id": "wob_tm"})
        condition = soup.find("span", {"id": "wob_dc"})
        location = soup.find("div", {"id": "wob_loc"})
        if not temperature:
            return "Weather lookup failed. Google blocked the request."
        return f"Location: {location.text}\nTemperature: {temperature.text}°C\nCondition: {condition.text}"
    except Exception as e:
        return f"Error: {e}"

def add_reminder(text):
    memory["reminders"].append(text)
    save_memory(memory)
    return f"Reminder added: {text}"

def show_reminders():
    if not memory["reminders"]:
        return "No reminders saved."
    return "\n".join([f"- {r}" for r in memory["reminders"]])

def wiki_search(query):
    try:
        url = f"https://en.wikipedia.org/wiki/{query.replace(' ', '_')}"
        res = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(res.text, "html.parser")
        p = soup.find("p")
        if p:
            return p.text.strip()
        return "I couldn't find information on Wikipedia."
    except:
        return "Wikipedia search failed."

def solve_math(expr):
    try:
        result = eval(expr)
        return f"{expr} = {result}"
    except:
        return "Invalid math expression."

def answer_question(msg):
    msg_lower = msg.lower()
    if "time" in msg_lower:
        return datetime.datetime.now().strftime("%H:%M:%S")
    if "date" in msg_lower:
        return str(datetime.date.today())
    if "your name" in msg_lower:
        return "I am your advanced AI assistant."
    return "I don't know that yet."

def intent_handler(message):
    msg = message.lower().strip()
    if "weather" in msg:
        match = re.search(r"in ([a-zA-Z ]+)", msg)
        city = match.group(1) if match else "your city"
        return scrape_weather(city)
    if "remind me" in msg:
        text = msg.replace("remind me", "").strip()
        if not text:
            return "What should I remind you about?"
        return add_reminder(text)
    if "show reminders" in msg or "my reminders" in msg:
        return show_reminders()
    if msg.startswith("who is") or msg.startswith("what is"):
        query = msg.replace("who is", "").replace("what is", "").strip()
        return wiki_search(query)
    if any(op in msg for op in ["+", "-", "", "/", "*"]):
        return solve_math(msg)
    return answer_question(msg)



import streamlit as st
st.set_page_config(page_title="AI Assistant", page_icon="🤖", layout="centered")
st.title("🤖 Advanced AI Assistant")
st.write("Type any command below ⬇(weather☁, reminders🗓, wiki🌐, math📝, date📅, time⌛, etc.)")

# Chat History
if "history" not in st.session_state:
    st.session_state.history = []

# User Input
user_input = st.text_input("Your message:📩", "")

if st.button("Send"):
    if user_input.strip():
        response = intent_handler(user_input)

        # Save chat history
        st.session_state.history.append(("You", user_input))
        st.session_state.history.append(("Assistant", response))

# Display Chat
for sender, message in st.session_state.history:
    if sender == "You":
        st.markdown(f" 👩‍🦰You: {message}")
    else:
        st.markdown(f"🗨 Assistant: {message}")