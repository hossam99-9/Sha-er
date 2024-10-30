# base_agent.py

class BaseAgent:
    def handle_request(self, *args, **kwargs):
        raise NotImplementedError("Subclasses should implement this method.")
