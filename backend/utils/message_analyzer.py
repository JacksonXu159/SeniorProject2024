from textblob import TextBlob

class MessageAnalyzer:
    def __init__(self):
        self.sentiment_threshold = -0.3  # Negative sentiment threshold

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
        Check if the user wants to end the live agent session.
        Returns True if the user wants to end the session, False otherwise.
        """
        message = user_message.lower().strip()
        termination_phrases = [
            "end session", "end chat", "disconnect", "i'm done", "im done", 
            "that's all", "thats all", "goodbye", "bye", "exit live agent", 
            "switch back", "return to ai", "back to bot", "i'm finished", "im finished"
        ]
        
        for phrase in termination_phrases:
            if phrase in message:
                return True
        
        return False