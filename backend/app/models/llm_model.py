from ibm_watsonx_ai import APIClient, Credentials
from ibm_watsonx_ai.metanames import GenTextParamsMetaNames

from langchain_ibm import WatsonxLLM

from backend.app.config.config import Config
from backend.app.utils.debate import *

class LLMModel:
    def __init__(self, params=None):
        """
            Initialize the Allam LLM Wrapper with params from a dictionary.

            :param params: A dictionary of parameters to use when invoking the llm
         """
        self.url = Config.IBM_CLOUD_URL
        self.model_name = Config.LLM_MODEL_NAME
        self.api_key = Config.IBM_API_KEY
        self.project_id = Config.PROJECT_ID

        # Initialize Credentials
        self.credentials = Credentials(
            url=self.url,
            api_key=self.api_key,
        )

        # Initialize APIClient
        self.api_client = APIClient(self.credentials)

        if params is None:
            params = {
                GenTextParamsMetaNames.DECODING_METHOD: "greedy",
                GenTextParamsMetaNames.MAX_NEW_TOKENS: 900,
                GenTextParamsMetaNames.MIN_NEW_TOKENS: 0,
                GenTextParamsMetaNames.STOP_SEQUENCES: [],
                GenTextParamsMetaNames.REPETITION_PENALTY: 1,
            }

        # Initialize WatsonxLLM for the given model_id and parameters
        log_message(msg=f"Creating agent with params: {params}", level=2)

        self.llm_chat = WatsonxLLM(
            url=self.credentials.get('url'),
            apikey=self.credentials.get('apikey'),
            project_id=self.project_id,
            model_id=self.model_name,
            params=params
        )

    def get_langchain_model(self):
        return self.llm_chat

    def generate(self, prompt: str):
        """
        Invoke the llm with a given prompt and return the response.

        :param prompt: The input text to process with the llm
        :return: The response from the llm
        """

        # Interact with the LLM API
        if not self.llm_chat:
            raise Exception("llm chat is not initialized. Call setup_llm_chat first.")

        # Invoke the model with the prompt and return the response
        response = self.llm_chat.invoke(prompt)
        return response
    
    def generate_stream(self, prompt: str):
        """
        Invoke the llm with a given prompt and return the response.

        :param prompt: The input text to process with the llm
        :return: The response from the llm
        """

        # Interact with the LLM API
        if not self.llm_chat:
            raise Exception("llm chat is not initialized. Call setup_llm_chat first.")

        # Invoke the model with the prompt and return the response
        for chunk in self.llm_chat.stream(prompt):
            yield chunk