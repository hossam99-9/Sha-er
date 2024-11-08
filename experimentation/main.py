import os
import random

from dotenv import load_dotenv
from ibm_watsonx_ai import Credentials
from ibm_watsonx_ai.metanames import GenTextParamsMetaNames
from langchain_ibm import WatsonxLLM
from colorama import Fore, Style

from backend.app.agents.poetry_generation_agent import PoetryGenerationAgent
from backend.app.agents.poetry_judge_agent import PoetryJudgeAgent
from backend.app.utils.debate import *

load_dotenv()

OPEN_API_KEY = os.getenv("OPEN_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
LANGCHAIN_API_KEY = os.getenv("LANGCHAIN_API_KEY")
IBM_API_KEY = os.getenv("IBM_API_KEY")
PROJECT_ID = os.getenv("PROJECT_ID")

credentials = Credentials(
    url="https://eu-de.ml.cloud.ibm.com",
    api_key=IBM_API_KEY,
)
project_id = PROJECT_ID

# Load embeddings for themes and poets lists
index_theme = load_embeddings(path="./data_folder/theme_embeddings.pkl")
index_poet = load_embeddings(path="./data_folder/poet_embeddings.pkl")

### Simulation Globals

# From the UI
POET1 = "أحمد شوقي"
POET2 = "خليل مطران"
ROUND_THEMES = ["حزين", "وطني", "رومانسي"]
NUM_ROUNDS = len(ROUND_THEMES)

# Runtime
ROUND_SCORES = {"poet1":[], "poet2":[]} # for each round
ROUND_COMMENTS = {"poet1":[], "poet2":[]}

#################
#  JUDGE AGENT  #
#################

###LLMs####
# Might change temperature later (or dynamically ?)
commentator_parameters = {
    GenTextParamsMetaNames.MAX_NEW_TOKENS: 1500,
    GenTextParamsMetaNames.DECODING_METHOD: "greedy",
		GenTextParamsMetaNames.REPETITION_PENALTY: 1,
}

summarizer_parameters = {
    GenTextParamsMetaNames.MAX_NEW_TOKENS: 1500,
    GenTextParamsMetaNames.DECODING_METHOD: "greedy",
		GenTextParamsMetaNames.REPETITION_PENALTY: 1,
}

commentator_llm = WatsonxLLM(
    url=credentials.get('url'),
    apikey=credentials.get('apikey'),
    project_id=project_id,
    model_id="sdaia/allam-1-13b-instruct",
    params=commentator_parameters
)

summarizer_llm = WatsonxLLM(
    url=credentials.get('url'),
    apikey=credentials.get('apikey'),
    project_id=project_id,
    model_id="sdaia/allam-1-13b-instruct",
    params=summarizer_parameters
)

judge_agent = PoetryJudgeAgent(commentator_llm_model=commentator_llm,
                               summarizer_llm_model=summarizer_llm,)
######################
#  COMPETITOR AGENT  #
######################

###LLMs####
# Might change temperature later (or dynamically ?)

retriever_parameters = {
    GenTextParamsMetaNames.MAX_NEW_TOKENS: 1500,
    GenTextParamsMetaNames.DECODING_METHOD: "greedy",
		GenTextParamsMetaNames.REPETITION_PENALTY: 1,
    GenTextParamsMetaNames.TEMPERATURE: 0.3,
}

generator_parameters = {
    GenTextParamsMetaNames.MAX_NEW_TOKENS: 1500,
    GenTextParamsMetaNames.DECODING_METHOD: "greedy",
		GenTextParamsMetaNames.REPETITION_PENALTY: 1,
}

retriever_llm = WatsonxLLM(
    url=credentials.get('url'),
    apikey=credentials.get('apikey'),
    project_id=project_id,
    model_id="sdaia/allam-1-13b-instruct",
    params=retriever_parameters
)

generator_llm = WatsonxLLM(
    url=credentials.get('url'),
    apikey=credentials.get('apikey'),
    project_id=project_id,
    model_id="sdaia/allam-1-13b-instruct",
    params=generator_parameters
)

generator_agent = PoetryGenerationAgent(generator_llm_model=generator_llm,
                                        retriever_llm_model=retriever_llm,
                                        index_poet=index_poet,
                                        index_theme=index_theme,
                                        poets_list=POETS,
                                        themes_list=THEMES,
                                        poetry_database_path = "./data_folder/ashaar.csv")

##############
# SIMULATION # 
##############

def run_simulation():

  ## Prepare all rounds prompts by the judge for the 2 competitiors
  POET1_PROMPTS = []
  POET2_PROMPTS = []

  for theme in ROUND_THEMES:
    round_qafya = random.choices(QAWAFI_RHYMES, weights=QAWAFI_WEIGHTS, k=1)[0]
    POET1_PROMPTS.append(f"أريد بيت شعر عن {theme} علي طريقة الشاعر {POET1} ينتهي ب{round_qafya}")
    POET2_PROMPTS.append(f"أريد بيت شعر عن {theme} علي طريقة الشاعر {POET2} ينتهي ب{round_qafya}")

  log_message(msg="Prepared all rounds prompts for the competitors", level=2)
  log_message(msg=f"Competitor 1 prompts: {POET1_PROMPTS}", level=2)
  log_message(msg=f"Competitor 2 prompts: {POET2_PROMPTS}", level=2)

  ## simulation loop
  for round in range(NUM_ROUNDS): 
    log_message(msg=Fore.RED + f"الحكم: لنبدأ الجولة {NUMBER_TO_ORDINAL[round+1]} يا متبارزين" +  Style.RESET_ALL,level=1)
    log_message(msg=Fore.BLUE + f"الحكم للشاعر الأول: {POET1_PROMPTS[round]}" + Style.RESET_ALL, level=1)
    log_message(msg=Fore.BLUE + f"الحكم للشاعر الثاني: {POET2_PROMPTS[round]}" + Style.RESET_ALL, level=1)

    # for the qafya scorer
    results_1 = generator_agent.fetch_relevant_poems_with_metadata(POET1_PROMPTS[round])
    results_2 = generator_agent.fetch_relevant_poems_with_metadata(POET2_PROMPTS[round])
    log_message(msg="Fetched verses for the two competitors",level=2)

    poet1_bait = generator_agent.generate_bait(POET1_PROMPTS[round])
    poet2_bait = generator_agent.generate_bait(POET2_PROMPTS[round])
    log_message(msg="Each competitor generated his bait", level=2)
    log_message(msg=Fore.BLUE + f"الشاعر الأول: {poet1_bait}" + Style.RESET_ALL, level=1)
    log_message(msg=Fore.BLUE + f"الشاعر الثاني: {poet2_bait}" + Style.RESET_ALL, level=1)

    log_message(msg="Judge starting evaluation", level=2)

    # Evaluating scores
    round_scores_1 = judge_agent.score(poet1_bait, results_1["poem_qafya_letter"])
    round_scores_2 = judge_agent.score(poet2_bait, results_2["poem_qafya_letter"])

    log_message(msg="Judge calculated scores", level=2)
    log_message(msg=f"Competitor1: qafya_score: {round_scores_1["qafya_score"]}, meters_score: {round_scores_1["meters_score"]}, quality_score: {round_scores_1["quality_score"]}", level=2)
    log_message(msg=f"Competitor2: qafya_score: {round_scores_2["qafya_score"]}, meters_score: {round_scores_2["meters_score"]}, quality_score: {round_scores_2["quality_score"]}", level=2)

    ROUND_SCORES["poet1"].append(round_scores_1["round_score"])
    ROUND_SCORES["poet2"].append(round_scores_2["round_score"])

    judge_comment1 = judge_agent.comment(poet1_bait, round_scores_1["qafya_score"])
    judge_comment2 = judge_agent.comment(poet2_bait, round_scores_2["qafya_score"])

    ROUND_COMMENTS["poet1"].append(judge_comment1)
    ROUND_COMMENTS["poet2"].append(judge_comment2)

    log_message(msg=Fore.RED + f"الحكم للشاعر الأول: {judge_comment1}" + Style.RESET_ALL, level=1)
    log_message(msg=Fore.RED + f"الحكم للشاعر الثاني: {judge_comment2}" + Style.RESET_ALL, level=1)

    log_message(msg=f"poet1 score: {ROUND_SCORES['poet1'][round]}", level=2)
    log_message(msg=f"poet2 score: {ROUND_SCORES['poet2'][round]}", level=2)

    if ROUND_SCORES['poet1'][round] > ROUND_SCORES['poet2'][round]:
      log_message(msg=Fore.RED + f"يبدو أن الشاعر {POET1} تفوق في الجولة {NUMBER_TO_ORDINAL[round+1]}" + Style.RESET_ALL, level=1)
    elif ROUND_SCORES['poet1'][round] < ROUND_SCORES['poet2'][round]:
      log_message(msg=Fore.RED + f"يبدو أن الشاعر {POET2} تفوق في الجولة {NUMBER_TO_ORDINAL[round+1]}" + Style.RESET_ALL, level=1)
    else:
       log_message(msg=f"تعادل الشاعران في الجولة {NUMBER_TO_ORDINAL[round+1]}",level=1)

  poet1_total_score = sum(ROUND_SCORES["poet1"])
  poet2_total_score = sum(ROUND_SCORES["poet2"])

  if poet1_total_score > poet2_total_score:
    log_message(msg=Fore.RED + f"أنتصر الشاعر {POET1} في هذه المساجلة الشعرية" + Style.RESET_ALL, level=1)
  elif poet1_total_score < poet2_total_score:
    log_message(msg=Fore.RED + f"أنتصر الشاعر {POET2} في هذه المساجلة الشعرية" + Style.RESET_ALL, level=1)
  else:
      log_message(msg=Fore.RED + "تعادل الشاعران في هذه المبارزة الشعرية" + Style.RESET_ALL,level=1)

if __name__ == '__main__':
   run_simulation()