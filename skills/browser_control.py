# skills/browser_control.py

import webbrowser

def search_web(query):
    search_term = query.replace("search for", "")
    Matrix().speech.speak(f"Searching for {search_term}")
    webbrowser.open(f"https://www.google.com/search?q={search_term}")