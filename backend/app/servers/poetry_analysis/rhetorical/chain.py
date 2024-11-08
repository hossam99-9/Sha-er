from ibm_watsonx_ai.metanames import GenTextParamsMetaNames

from backend.app.agents.rhetorical_element_agent import RhetoricalElementsAgent
from backend.app.models.llm_model import LLMModel

rhetorical_parameters = {
    GenTextParamsMetaNames.MAX_NEW_TOKENS: 900,
		GenTextParamsMetaNames.REPETITION_PENALTY: 1,
    GenTextParamsMetaNames.TEMPERATURE: 0.4,
}

llm = LLMModel(rhetorical_parameters)
rhetorical_agent = RhetoricalElementsAgent(llm_model=llm, embedding_model="openai")

def get_rhetorical_analysis(bait):
    rhetorical_analysis = rhetorical_agent.extract_rhetorical_elements(bait)
    return rhetorical_analysis
