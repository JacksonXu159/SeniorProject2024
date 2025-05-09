from collections import defaultdict
from agents.live_agent import LiveAgentChat
from utils.message_analyzer import MessageAnalyzer

class LiveAgentManager:
    def __init__(self):
        self.live_agent_status = False
        self.waiting_for_response = defaultdict(bool)
        self.live_agent = LiveAgentChat()
        self.message_analyzer = MessageAnalyzer()
        
    def should_offer_live_agent(self, message):
        return self.message_analyzer.should_offer_live_agent(message)
        
    def check_for_acceptance(self, message):
        return self.message_analyzer.check_for_live_agent_acceptance(message)
        
    def check_for_termination(self, message):
        return self.message_analyzer.check_for_live_agent_termination(message)
        
    def format_proposal(self):
        return self.message_analyzer.format_live_agent_proposal()
        
    def set_waiting_status(self, session_id, status):
        self.waiting_for_response[session_id] = status
        
    def is_waiting_for_response(self, session_id):
        return self.waiting_for_response[session_id]
        
    def set_live_agent_status(self, status):
        self.live_agent_status = status
        
    def is_live_agent_active(self):
        return self.live_agent_status
        
    def handle_message(self, input_data):
        return self.live_agent.invoke(input_data)
