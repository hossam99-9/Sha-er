from ibm_watsonx_ai.metanames import GenTextParamsMetaNames

from backend.app.agents.poetry_critic_agent import PoetryCriticAgent
from backend.app.models.llm_model import LLMModel

# Define the parameters for the language model
critic_parameters = {
    GenTextParamsMetaNames.MAX_NEW_TOKENS: 1500,
    GenTextParamsMetaNames.DECODING_METHOD: "greedy",
    GenTextParamsMetaNames.REPETITION_PENALTY: 1,
    GenTextParamsMetaNames.TEMPERATURE: 0.7,
}

# Initialize the language model with the specified parameters
critic_llm = LLMModel(critic_parameters)

# Initialize the poetry critic agent with the language model
critic_agent = PoetryCriticAgent(critic_model=critic_llm)

def critic_bait(bait):
    """
    Critique the given bait (verse) using the poetry critic agent.

    :param bait: The verse to be critiqued.
    :return: The critique result.
    """
    result = critic_agent.critic(bait)
    return result