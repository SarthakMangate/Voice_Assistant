import os
import datetime
import webbrowser
import ctypes
import openai
import pyttsx3
import speech_recognition as sr
import requests
from word2number import w2n  # type: ignore

# Set your API keys here
openai.api_key = "Key"
news_api_key = "Key"

# Initialize the voice engine
engine = pyttsx3.init()
engine.setProperty('rate', 170)
engine.setProperty('volume', 1.0)

def speak(audio):
    """Converts text to speech."""
    engine.say(audio)
    engine.runAndWait()

def wishMe():
    """Greets the user based on the time of day."""
    hour = int(datetime.datetime.now().hour)
    if hour >= 0 and hour < 12:
        speak("Good morning team!")
    elif hour >= 12 and hour < 18:
        speak("Good afternoon team!")
    else:
        speak("Good evening team!")
    speak("I am your personalized AI assistant. How may I assist you?")

def takeCommand():
    """Takes voice input from the user and returns a string."""
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        r.pause_threshold = 1
        try:
            audio = r.listen(source)
            query = r.recognize_google(audio, language='en-in')
            print(f"User said: {query}\n")
        except Exception:
            print("Could not understand. Please repeat.")
            return "None"
        return query

def get_calendar_info(query):
    """Provides date, day, month, or year based on user query."""
    now = datetime.datetime.now()

    if 'date' in query:
        current_date = now.strftime("%d %B %Y")  # Example: 25 March 2025
        speak(f"Today's date is {current_date}")

    elif 'day' in query:
        current_day = now.strftime("%A")  # Example: Monday
        speak(f"Today is {current_day}")

    elif 'month' in query:
        current_month = now.strftime("%B")  # Example: March
        speak(f"The current month is {current_month}")

    elif 'year' in query:
        current_year = now.strftime("%Y")  # Example: 2025
        speak(f"The current year is {current_year}")

    else:
        speak("I didn't understand. Please ask about date, day, month, or year.")

def get_number():
    """Gets a spoken number and converts it to an integer."""
    while True:
        speak("Please say the number.")
        num_text = takeCommand().lower()

        if num_text == "none":
            speak("I couldn't hear you properly. Please try again.")
            continue

        words = num_text.split()
        for word in words:
            try:
                num = w2n.word_to_num(word)
                return num
            except ValueError:
                continue

        speak("That doesn't seem like a valid number. Please try again.")

def perform_calculation():
    """Performs basic arithmetic operations based on user choice."""
    speak("What type of calculation do you want? Addition, Subtraction, Multiplication, or Division?")
    calc_type = takeCommand().lower()

    if calc_type in ["addition", "subtraction", "multiplication", "division"]:
        num1 = get_number()
        num2 = get_number()

        if calc_type == "addition":
            result = num1 + num2
            speak(f"The result of adding {num1} and {num2} is {result}")
        elif calc_type == "subtraction":
            result = num1 - num2
            speak(f"The result of subtracting {num2} from {num1} is {result}")
        elif calc_type == "multiplication":
            result = num1 * num2
            speak(f"The result of multiplying {num1} and {num2} is {result}")
        elif calc_type == "division":
            if num2 == 0:
                speak("Division by zero is not allowed.")
            else:
                result = num1 / num2
                speak(f"The result of dividing {num1} by {num2} is {result}")
    else:
        speak("I didn't understand the operation. Please try again.")

def open_chrome():
    """Opens Google Chrome."""
    speak("Opening Google Chrome")
    chrome_path = r"C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"
    os.startfile(chrome_path)

def check_weather():
    """Asks for a city and opens Google search for the weather."""
    speak("Which city's weather would you like to check?")
    city = takeCommand()

    if city == "none":
        speak("I couldn't hear you properly. Please try again.")
        return

    speak(f"Checking the weather for {city}.")
    city = city.replace(" ", "+")
    weather_url = f"https://www.google.com/search?q=weather+{city}"
    webbrowser.open(weather_url)

def get_news():
    """Fetches and reads out the top news headlines for a specified category."""
    speak("Which category of news would you like? Options: general, business, technology, entertainment, sports, health, or science.")
    category = takeCommand().lower()

    valid_categories = ["general", "business", "technology", "entertainment", "sports", "health", "science"]
    if category not in valid_categories:
        speak("Invalid category. I will fetch general news for you.")
        category = "general"

    url = f"https://newsapi.org/v2/top-headlines?country=in&category={category}&apiKey={news_api_key}"
    response = requests.get(url)
    news_data = response.json()

    if news_data.get("status") == "ok":
        articles = news_data.get("articles", [])[:5]  # Get top 5 news headlines
        if articles:
            for i, article in enumerate(articles, start=1):
                speak(f"News {i}: {article['title']}")
        else:
            speak("Sorry, no news articles were found for that category.")
    else:
        speak("Sorry, I couldn't fetch the news at the moment.")

if __name__ == '__main__':
    clear = lambda: os.system('cls')
    clear()
    wishMe()
    
    while True:
        query = takeCommand().lower()

        if "perform calculations" in query:
            perform_calculation()

        elif 'weather' in query or 'current weather' in query:
            check_weather()

        elif 'open chrome' in query:
            open_chrome()

        elif 'open youtube' in query:
            speak("Opening YouTube")
            webbrowser.open("https://www.youtube.com")

        elif 'open google' in query:
            speak("Opening Google")
            webbrowser.open("https://www.google.com")

        elif 'open stack overflow' in query:
            speak("Opening Stack Overflow")
            webbrowser.open("https://stackoverflow.com")

        elif 'current time' in query:
            current_time = datetime.datetime.now().strftime("%H:%M:%S")
            speak(f"The time is {current_time}")

        elif 'current date' in query or 'todays date' in query:
            get_calendar_info("date")

        elif 'day' in query:
            get_calendar_info("day")

        elif 'month' in query:
            get_calendar_info("month")

        elif 'year' in query:
            get_calendar_info("year")

        elif 'lock screen' in query:
            speak("Locking the device")
            ctypes.windll.user32.LockWorkStation()

        elif 'shutdown' in query:
            speak("Shutting down the system")
            os.system("shutdown /s /t 5")

        elif 'restart' in query:
            speak("Restarting the system")
            os.system("shutdown /r /t 5")

        elif 'news' in query:
            get_news()

        elif 'exit' in query or 'stop' in query:
            speak("Thanks for your time! Have a great day!")
            break

        else:
            speak("I am not sure how to handle that request.")
