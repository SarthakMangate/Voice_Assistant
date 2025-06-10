import os
import re
import datetime
import sys
import subprocess
from flask import Flask, render_template, request, jsonify
import requests
from word2number import w2n  # pip install word2number
from win10toast import ToastNotifier  # pip install win10toast

app = Flask(__name__)

# --- API Keys ---
news_api_key = "9b51e90d610b43bd9d0e413c5993e661"

# --- Helper Functions ---
def get_calendar_info(query):
    now = datetime.datetime.now()
    q = query.lower()
    if 'date' in q:
        return f"Today's date is {now.strftime('%d %B %Y')}"
    if 'day' in q:
        return f"Today is {now.strftime('%A')}"
    if 'month' in q:
        return f"The current month is {now.strftime('%B')}"
    if 'year' in q:
        return f"The current year is {now.strftime('%Y')}"
    return "Please ask about date, day, month, or year."

def get_number_from_text(text):
    for word in text.split():
        try:
            return w2n.word_to_num(word)
        except:
            continue
    try:
        return int(text)
    except:
        return None


def calculate_from_command(cmd):
    parts = cmd.split()
    if len(parts) < 5:
        return "Usage: perform calculations [addition|subtraction|multiplication|division] num1 num2"
    op, a_text, b_text = parts[2], parts[3], parts[4]
    a = get_number_from_text(a_text)
    b = get_number_from_text(b_text)
    if a is None or b is None:
        return "Invalid numbers."
    if op == 'addition':
        return f"{a} + {b} = {a + b}"
    if op == 'subtraction':
        return f"{a} - {b} = {a - b}"
    if op == 'multiplication':
        return f"{a} * {b} = {a * b}"
    if op == 'division':
        if b == 0:
            return "Cannot divide by zero."
        return f"{a} / {b} = {a / b}"
    return "Unknown operation."


def check_weather(cmd):
    parts = cmd.split(maxsplit=1)
    if len(parts) < 2:
        return "Specify city.", None
    city = parts[1].replace(' ', '+')
    return f"Weather for {parts[1]}", f"https://www.google.com/search?q=weather+{city}"


def get_news(cmd):
    parts = cmd.split()
    category = parts[1] if len(parts) >= 2 else 'general'
    url = f"https://newsapi.org/v2/top-headlines?country=us&category={category}&apiKey={news_api_key}"
    res = requests.get(url).json()
    if res.get('status') == 'ok':
        titles = [a['title'] for a in res.get('articles', [])[:5]]
        return "\n".join(titles), None
    return "Could not fetch news.", None


def search_google(cmd):
    q = cmd.replace('search', '').replace('on google', '').strip()
    if not q:
        return "Searching Google", "https://google.com"
    return f"Searching {q}", f"https://www.google.com/search?q={q.replace(' ', '+')}"


def open_youtube_search(cmd):
    q = cmd.split('on youtube')[0].replace('open', '').strip()
    if not q:
        return "Opening YouTube", "https://youtube.com"
    return f"YouTube search: {q}", f"https://youtube.com/results?search_query={q.replace(' ', '+')}"


def get_wikipedia_summary(cmd):
    parts = cmd.split(maxsplit=1)
    if len(parts) < 2:
        return "Specify topic.", None
    topic = parts[1]
    url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{topic.replace(' ', '_')}"
    r = requests.get(url)
    if r.status_code == 200:
        return r.json().get('extract', "No summary found."), None
    return "Not found on Wikipedia.", None


def play_music(cmd):
    song = cmd.replace('play music', '').strip()
    if not song:
        return "Say: play music [song]", "https://youtube.com"
    return f"Playing {song}", f"https://youtube.com/results?search_query={song.replace(' ', '+')}"


def tell_joke():
    jokes = [
        "Why did the coder quit? Because he didn't get arrays.",
        "Why was the JavaScript file sad? Because it didn't know how to 'null' its feelings."
    ]
    import random
    return random.choice(jokes)


def get_definition(cmd):
    word = cmd.split('define', 1)[1].strip()
    if not word:
        return "Say: define [word]"
    r = requests.get(f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}")
    if r.status_code == 200:
        return r.json()[0]['meanings'][0]['definitions'][0]['definition']
    return f"No definition found for {word}."


def set_alarm(cmd):
    if os.name != 'nt':
        return "Alarm supported only on Windows."
    m = re.search(r'set alarm\s*(?:for|at)?\s*(\d{1,2}(?::\d{2})?\s*(?:am|pm))', cmd, re.I)
    if not m:
        return "Format: set alarm for 7 am"
    t_str = m.group(1).lower()
    try:
        fmt = '%I:%M %p' if ':' in t_str else '%I %p'
        dt = datetime.datetime.strptime(t_str, fmt)
    except:
        return "Time parse error."
    alarm_dt = datetime.datetime.combine(datetime.date.today(), dt.time())
    if alarm_dt < datetime.datetime.now():
        alarm_dt += datetime.timedelta(days=1)
    display = alarm_dt.strftime('%I:%M %p').lstrip('0').replace('AM', 'a.m.').replace('PM', 'p.m.')
    run_time = alarm_dt.strftime('%H:%M')
    task_name = 'Alarm_' + alarm_dt.strftime('%Y%m%d_%H%M')
    py = sys.executable
    script = os.path.join(os.getcwd(), 'alarm_notification.py')
    with open(script, 'w') as f:
        f.write("""from win10toast import ToastNotifier
import winsound, time
toaster = ToastNotifier()
toaster.show_toast('Alarm', 'Time to wake up!', duration=10, threaded=True)
winsound.PlaySound('SystemAlarm', winsound.SND_ALIAS)
time.sleep(15)
""")
    cmd_line = f'schtasks /Create /SC ONCE /TN "{task_name}" /TR "\\"{py}\\" \\"{script}\\"" /ST {run_time}'
    try:
        subprocess.run(cmd_line, shell=True, check=True)
        return f"Alarm set for {display}."
    except subprocess.CalledProcessError as e:
        return "Failed: " + str(e)

# --- Greeting Section ---
def greet_user():
    """
    Greets the user with a desktop notification based on the time of day, and returns the message.
    """
    toaster = ToastNotifier()
    hour = datetime.datetime.now().hour
    if hour < 12:
        message = 'Good morning!'
    elif hour < 18:
        message = 'Good afternoon!'
    else:
        message = 'Good evening!'
    toaster.show_toast('Assistant Greeting', message, duration=5, threaded=True)
    return message

# --- Flask Routes ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/command', methods=['POST'])
def command():
    data = request.get_json() or {}
    txt = data.get('command', '').lower().strip()
    resp, url = "", None

    # Greet on user "hi" or "hii"
    if txt in ['hi', 'hii', 'hello']:
        resp = greet_user()
    elif 'perform calculations' in txt:
        resp = calculate_from_command(txt)
    elif 'weather' in txt:
        resp, url = check_weather(txt)
    elif 'news' in txt:
        resp, url = get_news(txt)
    elif txt.startswith('wikipedia '):
        resp, url = get_wikipedia_summary(txt)
    elif 'play music' in txt:
        resp, url = play_music(txt)
    elif 'define' in txt:
        resp = get_definition(txt)
    elif 'joke' in txt:
        resp = tell_joke()
    elif 'set alarm' in txt:
        resp = set_alarm(txt)
    elif 'open ' in txt and 'youtube' in txt:
        resp, url = open_youtube_search(txt)
    elif 'search' in txt and 'google' in txt:
        resp, url = search_google(txt)
    elif 'open chrome' in txt:
        resp = "Opening Chrome..."
    elif 'open google' in txt:
        resp, url = "Opening Google...", "https://google.com"
    elif 'current time' in txt:
        resp = f"Time: {datetime.datetime.now().strftime('%H:%M:%S')}"
    elif any(k in txt for k in ['date', 'day', 'month', 'year']):
        resp = get_calendar_info(txt)
    else:
        resp = "I didn't understand that."

    return jsonify({'response': resp, 'url': url})

if __name__ == '__main__':
    # Trigger greeting on application startup
    greet_user()
    app.run(debug=True)