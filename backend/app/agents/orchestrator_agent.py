# orchestrator_agent.py

from backend.app.agents.base_agent import BaseAgent

class OrchestratorAgent(BaseAgent):
    def __init__(self, agents):
        self.agents = agents  # Dictionary of agent instances

    def handle_request(self, request_type, data):
        if request_type == 'generate_poem':
            return self.agents['poetry_generation'].handle_request(data['poet'], data['theme'])
        elif request_type == 'analyze_poem':
            info = self.agents['poetry_information'].handle_request(data['verses'])
            analysis = self.agents['poetry_analysis'].handle_request(data['verses'])
            rhetorical_elements = self.agents['rhetorical_elements'].handle_request(data['verses'])
            return {
                'information': info,
                'analysis': analysis,
                'rhetorical_elements': rhetorical_elements
            }
        else:
            raise ValueError("Invalid request type")
