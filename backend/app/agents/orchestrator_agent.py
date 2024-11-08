# orchestrator_agent.py

from backend.app.agents.base_agent import BaseAgent

class OrchestratorAgent(BaseAgent):
    """
    OrchestratorAgent class to manage and route requests to multiple agents.

    This agent serves as a central controller to handle various types of requests,
    directing them to the appropriate agent based on the request type. It can manage
    different functionalities like generating poems, analyzing poetry, and identifying
    rhetorical elements.

    Attributes:
    -----------
    agents : dict
        A dictionary containing instances of different agent classes, with keys representing
        the type of agent (e.g., 'poetry_generation', 'poetry_analysis').

    Methods:
    --------
    handle_request(request_type: str, data: dict) -> dict or str:
        Routes the request to the appropriate agent based on the request type, and returns
        the result.
    """

    def __init__(self, agents):
        """
        Initializes the OrchestratorAgent with a dictionary of agent instances.

        :param agents: Dictionary of agent instances where each key corresponds to a specific
                       agent type, and each value is an instance of an agent (e.g., poetry generation,
                       analysis).
        """
        self.agents = agents  # Dictionary of agent instances

    def handle_request(self, request_type: str, data: dict):
        """
        Routes the request to the appropriate agent based on the request type.

        Depending on the specified `request_type`, this method directs the request to
        a specific agent and retrieves the response. Supported request types include:
        - 'generate_poem': Routes to the poetry generation agent.
        - 'analyze_poem': Routes to the poetry information, analysis, and rhetorical elements agents.

        :param request_type: A string specifying the type of request (e.g., 'generate_poem', 'analyze_poem').
        :param data: A dictionary containing the data required by the specific agent for handling the request.
        :return: The response from the appropriate agent(s).
        :raises ValueError: If the `request_type` is not recognized.
        """
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
