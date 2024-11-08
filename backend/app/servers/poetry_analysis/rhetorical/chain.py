from ibm_watsonx_ai.metanames import GenTextParamsMetaNames

from backend.app.agents.rhetorical_element_agent import RhetoricalElementsAgent
from backend.app.models.llm_model import LLMModel

# Define the parameters for the language model
rhetorical_parameters = {
    GenTextParamsMetaNames.MAX_NEW_TOKENS: 900,
    GenTextParamsMetaNames.REPETITION_PENALTY: 1,
    GenTextParamsMetaNames.TEMPERATURE: 0.4,
}

# Initialize the language model with the specified parameters
llm = LLMModel(rhetorical_parameters)

# Initialize the rhetorical elements agent with the language model and embedding model
rhetorical_agent = RhetoricalElementsAgent(llm_model=llm, embedding_model="openai")

def get_rhetorical_analysis(bait):
    """
    Analyze the given bait for rhetorical elements.

    :param bait: The text to be analyzed.
    :return: The rhetorical analysis of the text.
    """
    rhetorical_analysis = rhetorical_agent.extract_rhetorical_elements(bait)
    return rhetorical_analysis
