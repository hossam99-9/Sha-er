# base_agent.py

class BaseAgent:
    """
    Base class for all agent implementations in the application.

    This class defines a common interface that all agent subclasses should adhere to. 
    Each subclass should implement the `handle_request` method to process incoming requests 
    with specified arguments and keyword arguments.

    Methods:
    --------
    handle_request(*args, **kwargs):
        Abstract method that must be implemented in subclasses. It handles processing 
        of requests and should be customized based on the specific functionality of the subclass.
    
    Raises:
    -------
    NotImplementedError:
        If the subclass does not implement the `handle_request` method.
    """

    def handle_request(self, *args, **kwargs):
        """
        Abstract method to handle incoming requests. 
        
        This method should be implemented by all subclasses to define their specific 
        request-handling behavior.

        :param args: Positional arguments for the request.
        :param kwargs: Keyword arguments for the request.
        :raises NotImplementedError: If not implemented by subclass.
        """
        raise NotImplementedError("Subclasses should implement this method.")
