import re
import json
import os
from textblob import TextBlob

class MessageAnalyzer:
    def __init__(self, language='en'):
        """Initialize MessageAnalyzer with optional config path and language setting."""
        self.sentiment_threshold = -0.6  # Negative sentiment threshold
        self.language = language
        
        # Default termination phrases by language
        self.termination_phrases= {
                'end_commands': ['end session', 'end chat', 'disconnect', 'exit live agent', 'exit live session', "stop live agent", 'stop live session', 'end live agent', 'end live session', 'stop live chat', 'end live chat', 'exit live chat'],
                'done_indicators': ['im done', "i'm done", 'im finished', "i'm finished", "done", "finished", 'quit', 'stop', 'no more', 'no longer', 'no longer need', 'no more help', 'no more assistance', 'no more questions', 'no more inquiries'],
                'closure_phrases': ['thats all', "that's all", 'goodbye', 'bye', 'see you', 'farewell', 'take care', 'thank you', 'thanks', 'appreciate it', 'thank you for your help', 'thank you for your assistance', 'thank you for your time', 'thank you for your support'],
                'switch_requests': ['switch back', 'return to ai', 'back to bot', "back to ai", 'back to chatbot', 'return to bot', 'return to chatbot', 'switch back to ai', 'switch back to bot', 'switch back to chatbot', 'switch back to the bot', 'switch back to the ai'],
        }
        
        # Compile regex pattern upon initialization
        self.termination_pattern = self._compile_termination_pattern()

    def _compile_termination_pattern(self):
        """Compile all termination phrases into a single regex pattern."""
        # Flatten the dictionary into a single list
        all_phrases = []
        for category in self.termination_phrases.values():
            all_phrases.extend(category)
        
        # Process each phrase for regex
        regex_parts = []
        for phrase in all_phrases:
            # Replace spaces with \s+ to match any whitespace
            processed = phrase.replace(' ', r'\s+')
            # Add optional apostrophes for words with apostrophes
            processed = processed.replace("'", r"'?")
            regex_parts.append(processed)
        
        # Join all parts with | and wrap in word boundaries
        pattern = r'\b(' + '|'.join(regex_parts) + r')\b'
        
        return re.compile(pattern, re.IGNORECASE)  # Add IGNORECASE flag for case insensitivity

    def analyze_sentiment(self, text):
        """
        Analyze the sentiment of the given text using TextBlob.
        Returns a sentiment polarity score between -1 (negative) and 1 (positive).
        """
        analysis = TextBlob(text)
        return analysis.sentiment.polarity

    def should_offer_live_agent(self, text):
        """
        Determine if a live agent should be offered based on message sentiment.
        Returns True if sentiment is below the negative threshold.
        """
        sentiment_score = self.analyze_sentiment(text)
        return sentiment_score < self.sentiment_threshold

    def format_live_agent_proposal(self):
        """
        Generate a message proposing a live agent to the user.
        """
        return ("I notice you seem upset or frustrated. Would you like to speak with a "
                "live customer service agent instead? Please respond with 'yes' or 'no'.")

    def check_for_live_agent_acceptance(self, user_response):
        """
        Check if the user has accepted the live agent proposal.
        Returns True if the user accepts, False otherwise.
        """
        response = user_response.lower().strip()
        acceptance_phrases = ["yes", "yeah", "yep", "sure", "ok", "okay", "y", "please", "i do"]
        
        for phrase in acceptance_phrases:
            if phrase in response:
                return True
        
        return False
        
    def check_for_live_agent_termination(self, user_message):
        """
        Check if the user wants to end the live agent session using regex.
        Returns True if the user wants to end the session, False otherwise.
        """
        message = user_message.strip()  # No need for .lower() with re.IGNORECASE
        return bool(self.termination_pattern.search(message))
    
    def set_sentiment_threshold(self, threshold):
        """Set the sentiment threshold for offering live agent."""
        self.sentiment_threshold = threshold
        return True