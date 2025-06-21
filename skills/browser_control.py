# skills/browser_control.py

import webbrowser
from core.logger import log_info, log_error

def search_web(query):
    try:
        if "search for" in query:
            search_term = query.replace("search for", "").strip()
        else:
            search_term = query.strip()

        log_info(f"Performing web search for: {search_term}")
        from core.brain import Matrix
        Matrix().speech.speak(f"Searching for {search_term}")
        webbrowser.open(f"https://www.google.com/search?q={search_term}")
    except Exception as e:
        log_error(f"Error performing web search: {e}")
        Matrix().speech.speak("Sorry, I couldn't perform that search.")