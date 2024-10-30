from ibm_watsonx_ai.metanames import GenTextParamsMetaNames

from backend.app.agents.poetry_critic_agent import PoetryCriticAgent
from backend.app.models.llm_model import LLMModel

critic_parameters = {
    GenTextParamsMetaNames.MAX_NEW_TOKENS: 1500,
    GenTextParamsMetaNames.DECODING_METHOD: "greedy",
		GenTextParamsMetaNames.REPETITION_PENALTY: 1,
    GenTextParamsMetaNames.TEMPERATURE: 0.7,
}

critic_llm = LLMModel(critic_parameters)
critic_agent = PoetryCriticAgent(critic_model=critic_llm)

def critic_bait(bait):
    result = critic_agent.critic(bait)
    return result
