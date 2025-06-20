# skills/browser_control.py

import webbrowser
import logging
from core.logger import log_info, log_error

# Reference to Matrix's speech engine will be passed externally
def search_web(query):
    """
    Performs a Google search for the given voice command.
    Example: "search for latest AI news"
    """
    try:
        # Remove command prefix and clean up query
        if "search for" in query:
            search_term = query.replace("search for", "").strip()
        else:
            search_term = query.strip()

        log_info(f"Performing web search for: {search_term}")
        print(f"[MATRIX]: Searching for '{search_term}'...")

        # Speak confirmation
        from core.brain import Matrix
        Matrix().speech.speak(f"Searching for {search_term}")

        # Format Google search URL
        search_url = f"https://www.google.com/search?q={search_term}"

        # Open in default browser 
        webbrowser.open(search_url)

    except Exception as e:
        log_error(f"Error performing web search: {e}")
        from core.brain import Matrix
        Matrix().speech.speak("Sorry, I couldn't perform that search.")