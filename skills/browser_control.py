# skills/browser_control.py

import webbrowser
import urllib.parse
from typing import Optional, Dict, List
from dataclasses import dataclass
from enum import Enum

from core.logger import log_info, log_error, log_warning, log_debug


class SearchEngine(Enum):
    """Available search engines"""
    GOOGLE = "https://www.google.com/search?q={}"
    BING = "https://www.bing.com/search?q={}"
    DUCKDUCKGO = "https://duckduckgo.com/?q={}"
    YAHOO = "https://search.yahoo.com/search?p={}"
    YOUTUBE = "https://www.youtube.com/results?search_query={}"


@dataclass
class BrowserConfig:
    """Configuration for browser control"""
    default_search_engine: SearchEngine = SearchEngine.GOOGLE
    default_browser: Optional[str] = None  # None = system default
    open_in_new_tab: bool = True
    open_in_new_window: bool = False


class BrowserController:
    """Enhanced browser controller with multiple search engines and features"""
    
    def __init__(self, config: Optional[BrowserConfig] = None):
        self.config = config or BrowserConfig()
        
        # Popular websites shortcuts
        self.website_shortcuts = {
            'youtube': 'https://www.youtube.com',
            'gmail': 'https://mail.google.com',
            'github': 'https://github.com',
            'stackoverflow': 'https://stackoverflow.com',
            'reddit': 'https://www.reddit.com',
            'twitter': 'https://twitter.com',
            'facebook': 'https://www.facebook.com',
            'instagram': 'https://www.instagram.com',
            'linkedin': 'https://www.linkedin.com',
            'amazon': 'https://www.amazon.com',
            'netflix': 'https://www.netflix.com',
            'spotify': 'https://www.spotify.com',
            'wikipedia': 'https://www.wikipedia.org',
            'weather': 'https://weather.com',
            'maps': 'https://www.google.com/maps',
            'drive': 'https://drive.google.com',
            'docs': 'https://docs.google.com',
            'calendar': 'https://calendar.google.com',
            'news': 'https://news.google.com'
        }
        
        # Statistics
        self.stats = {
            'total_searches': 0,
            'total_websites_opened': 0,
            'search_engine_usage': {},
            'most_visited': {}
        }
        
        log_info("Browser Controller initialized")
    
    def search(self, query: str, engine: Optional[SearchEngine] = None) -> bool:
        """
        Perform web search
        
        Args:
            query: Search query
            engine: Search engine to use (default: Google)
            
        Returns:
            bool: True if search opened successfully
        """
        if not query:
            log_warning("Empty search query")
            return False
        
        engine = engine or self.config.default_search_engine
        
        try:
            # Clean and encode query
            clean_query = self._clean_query(query)
            encoded_query = urllib.parse.quote_plus(clean_query)
            
            # Build search URL
            search_url = engine.value.format(encoded_query)
            
            log_info(f"Searching '{clean_query}' using {engine.name}")
            
            # Open in browser
            success = self._open_url(search_url)
            
            if success:
                self.stats['total_searches'] += 1
                
                # Track search engine usage
                engine_name = engine.name
                self.stats['search_engine_usage'][engine_name] = \
                    self.stats['search_engine_usage'].get(engine_name, 0) + 1
            
            return success
            
        except Exception as e:
            log_error(f"Error performing search: {e}")
            return False
    
    def _clean_query(self, query: str) -> str:
        """Clean search query by removing command keywords"""
        keywords_to_remove = [
            'search for',
            'search',
            'google',
            'find',
            'look up',
            'look for',
            'search about',
            'tell me about'
        ]
        
        clean = query.lower()
        for keyword in keywords_to_remove:
            clean = clean.replace(keyword, '')
        
        return clean.strip()
    
    def open_website(self, website: str) -> bool:
        """
        Open a website
        
        Args:
            website: Website name or URL
            
        Returns:
            bool: True if opened successfully
        """
        try:
            # Check if it's a shortcut
            website_lower = website.lower()
            
            if website_lower in self.website_shortcuts:
                url = self.website_shortcuts[website_lower]
                log_info(f"Opening shortcut: {website_lower} -> {url}")
            elif website.startswith(('http://', 'https://', 'www.')):
                url = website if website.startswith('http') else f'https://{website}'
            else:
                # Try adding .com
                url = f'https://www.{website}.com'
            
            success = self._open_url(url)
            
            if success:
                self.stats['total_websites_opened'] += 1
                self.stats['most_visited'][website_lower] = \
                    self.stats['most_visited'].get(website_lower, 0) + 1
            
            return success
            
        except Exception as e:
            log_error(f"Error opening website: {e}")
            return False
    
    def youtube_search(self, query: str) -> bool:
        """
        Search on YouTube
        
        Args:
            query: Search query
            
        Returns:
            bool: True if search opened successfully
        """
        return self.search(query, SearchEngine.YOUTUBE)
    
    def open_youtube_video(self, video_id: str) -> bool:
        """Open specific YouTube video"""
        url = f"https://www.youtube.com/watch?v={video_id}"
        return self._open_url(url)
    
    def open_maps(self, location: str) -> bool:
        """
        Open Google Maps with location
        
        Args:
            location: Location to search
            
        Returns:
            bool: True if opened successfully
        """
        try:
            encoded_location = urllib.parse.quote_plus(location)
            url = f"https://www.google.com/maps/search/{encoded_location}"
            
            log_info(f"Opening Google Maps for: {location}")
            return self._open_url(url)
            
        except Exception as e:
            log_error(f"Error opening maps: {e}")
            return False
    
    def open_gmail(self, compose: bool = False) -> bool:
        """
        Open Gmail
        
        Args:
            compose: Open compose new email
            
        Returns:
            bool: True if opened successfully
        """
        url = "https://mail.google.com/mail/u/0/#compose" if compose else "https://mail.google.com"
        return self._open_url(url)
    
    def open_translate(self, text: str = "", source_lang: str = "auto", 
                      target_lang: str = "en") -> bool:
        """
        Open Google Translate
        
        Args:
            text: Text to translate
            source_lang: Source language code
            target_lang: Target language code
            
        Returns:
            bool: True if opened successfully
        """
        if text:
            encoded_text = urllib.parse.quote_plus(text)
            url = f"https://translate.google.com/?sl={source_lang}&tl={target_lang}&text={encoded_text}"
        else:
            url = "https://translate.google.com"
        
        return self._open_url(url)
    
    def search_images(self, query: str) -> bool:
        """
        Search Google Images
        
        Args:
            query: Search query
            
        Returns:
            bool: True if search opened successfully
        """
        try:
            clean_query = self._clean_query(query)
            encoded_query = urllib.parse.quote_plus(clean_query)
            url = f"https://www.google.com/search?tbm=isch&q={encoded_query}"
            
            log_info(f"Searching images for: {clean_query}")
            return self._open_url(url)
            
        except Exception as e:
            log_error(f"Error searching images: {e}")
            return False
    
    def search_news(self, query: str) -> bool:
        """
        Search Google News
        
        Args:
            query: Search query
            
        Returns:
            bool: True if search opened successfully
        """
        try:
            clean_query = self._clean_query(query)
            encoded_query = urllib.parse.quote_plus(clean_query)
            url = f"https://news.google.com/search?q={encoded_query}"
            
            log_info(f"Searching news for: {clean_query}")
            return self._open_url(url)
            
        except Exception as e:
            log_error(f"Error searching news: {e}")
            return False
    
    def _open_url(self, url: str) -> bool:
        """
        Open URL in browser
        
        Args:
            url: URL to open
            
        Returns:
            bool: True if opened successfully
        """
        try:
            if self.config.open_in_new_window:
                webbrowser.open_new(url)
            elif self.config.open_in_new_tab:
                webbrowser.open_new_tab(url)
            else:
                webbrowser.open(url)
            
            log_debug(f"Opened URL: {url}")
            return True
            
        except Exception as e:
            log_error(f"Error opening URL: {e}")
            return False
    
    def add_website_shortcut(self, name: str, url: str):
        """Add custom website shortcut"""
        self.website_shortcuts[name.lower()] = url
        log_info(f"Added website shortcut: {name} -> {url}")
    
    def get_stats(self) -> Dict:
        """Get browser usage statistics"""
        return {
            **self.stats,
            'available_shortcuts': len(self.website_shortcuts)
        }


# Global controller instance
_controller: Optional[BrowserController] = None


def get_controller() -> BrowserController:
    """Get or create global controller instance"""
    global _controller
    if _controller is None:
        _controller = BrowserController()
    return _controller


def get_matrix_speech():
    """Get Matrix speech engine"""
    try:
        from core.speech import SpeechEngine
        return SpeechEngine()
    except:
        return None


# Convenience functions
def search_web(query: str, engine: str = "google"):
    """
    Perform web search
    
    Args:
        query: Search query
        engine: Search engine name (google, bing, duckduckgo, youtube)
    """
    controller = get_controller()
    speech = get_matrix_speech()
    
    try:
        # Parse search engine
        engine_map = {
            'google': SearchEngine.GOOGLE,
            'bing': SearchEngine.BING,
            'duckduckgo': SearchEngine.DUCKDUCKGO,
            'duck': SearchEngine.DUCKDUCKGO,
            'yahoo': SearchEngine.YAHOO,
            'youtube': SearchEngine.YOUTUBE
        }
        
        search_engine = engine_map.get(engine.lower(), SearchEngine.GOOGLE)
        
        # Clean query
        clean_query = controller._clean_query(query)
        
        if speech:
            if search_engine == SearchEngine.YOUTUBE:
                speech.speak(f"Searching YouTube for {clean_query}")
            else:
                speech.speak(f"Searching for {clean_query}")
        
        success = controller.search(query, search_engine)
        
        if not success and speech:
            speech.speak("Sorry, I couldn't perform that search")
        
    except Exception as e:
        log_error(f"Error in search_web: {e}")
        if speech:
            speech.speak("Sorry, I couldn't perform that search")


def open_website(website: str):
    """Open a website"""
    controller = get_controller()
    speech = get_matrix_speech()
    
    try:
        if speech:
            speech.speak(f"Opening {website}")
        
        success = controller.open_website(website)
        
        if not success and speech:
            speech.speak(f"Sorry, couldn't open {website}")
        
    except Exception as e:
        log_error(f"Error opening website: {e}")
        if speech:
            speech.speak("Sorry, I couldn't open that website")


def search_youtube(query: str):
    """Search YouTube"""
    controller = get_controller()
    speech = get_matrix_speech()
    
    try:
        clean_query = controller._clean_query(query)
        
        if speech:
            speech.speak(f"Searching YouTube for {clean_query}")
        
        controller.youtube_search(query)
        
    except Exception as e:
        log_error(f"Error in YouTube search: {e}")
        if speech:
            speech.speak("Sorry, couldn't search YouTube")


def open_maps(location: str):
    """Open Google Maps"""
    controller = get_controller()
    speech = get_matrix_speech()
    
    try:
        if speech:
            speech.speak(f"Opening maps for {location}")
        
        controller.open_maps(location)
        
    except Exception as e:
        log_error(f"Error opening maps: {e}")
        if speech:
            speech.speak("Sorry, couldn't open maps")


def open_gmail():
    """Open Gmail"""
    controller = get_controller()
    speech = get_matrix_speech()
    
    try:
        if speech:
            speech.speak("Opening Gmail")
        
        controller.open_gmail()
        
    except Exception as e:
        log_error(f"Error opening Gmail: {e}")
        if speech:
            speech.speak("Sorry, couldn't open Gmail")


def search_images(query: str):
    """Search Google Images"""
    controller = get_controller()
    speech = get_matrix_speech()
    
    try:
        clean_query = controller._clean_query(query)
        
        if speech:
            speech.speak(f"Searching images for {clean_query}")
        
        controller.search_images(query)
        
    except Exception as e:
        log_error(f"Error searching images: {e}")
        if speech:
            speech.speak("Sorry, couldn't search images")


def search_news(query: str):
    """Search Google News"""
    controller = get_controller()
    speech = get_matrix_speech()
    
    try:
        clean_query = controller._clean_query(query)
        
        if speech:
            speech.speak(f"Searching news about {clean_query}")
        
        controller.search_news(query)
        
    except Exception as e:
        log_error(f"Error searching news: {e}")
        if speech:
            speech.speak("Sorry, couldn't search news")