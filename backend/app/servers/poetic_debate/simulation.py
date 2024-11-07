import random
import json
import csv
import asyncio

from colorama import Fore, Style

from backend.app.utils.debate import *

async def send_verse(websocket, poet_key, verse):
    for char in verse:
        await websocket.send_text(json.dumps({poet_key: char}))
        await asyncio.sleep(0.1)  # Simulate slow processing

async def send_judge_comment(websocket, comment):
    await websocket.send_text(json.dumps({"Judge": comment}))

def add_row(row_data, filename):
    """Appends a new row to the CSV file."""
    with open(filename, mode="a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(row_data)
    print(f"Row {row_data} added to '{filename}'.")

async def run_simulation(websocket,
                        round_themes,
                        poet1,
                        poet2,
                        generator_agent,
                        judge_agent,
                        log_file):

  ROUND_SCORES = {"poet1":[], "poet2":[]} # for each round
  ROUND_COMMENTS = {"poet1":[], "poet2":[]}
  ROUND_VERSES = {"poet1": [], "poet2": []}
  num_rounds = len(round_themes)

  ## Prepare all rounds prompts by the judge for the 2 competitiors
  POET1_PROMPTS = []
  POET2_PROMPTS = []

  POET1_PROMPTS_UI = []
  POET2_PROMPTS_UI = []

  ROUND_PROMPTS_UI = []

  for theme in round_themes:
    round_qafya = random.choices(QAWAFI_RHYMES, weights=QAWAFI_WEIGHTS, k=1)[0]
    POET1_PROMPTS.append(f"أريد بيت شعر عن {theme} علي طريقة الشاعر {poet1} ينتهي ب{round_qafya}")
    POET2_PROMPTS.append(f"أريد بيت شعر عن {theme} علي طريقة الشاعر {poet2} ينتهي ب{round_qafya}")

    POET1_PROMPTS_UI.append(f"يا {poet1}, أريد بيت شعر {theme} ينتهي ب{round_qafya}")
    POET2_PROMPTS_UI.append(f"يا {poet2}, أريد بيت شعر {theme} ينتهي ب{round_qafya}")

    ROUND_PROMPTS_UI.append(f"يا متبارزين أريد بيت شعر {theme}  ينتهي ب  {round_qafya}")

  log_message(msg="Prepared all rounds prompts for the competitors", level=2)
  log_message(msg=f"Competitor 1 prompts: {POET1_PROMPTS}", level=2)
  log_message(msg=f"Competitor 2 prompts: {POET2_PROMPTS}", level=2)

  message = f"نبدأ بالتحية للشاعرين {poet1} و {poet2} و ندعوهم للإستعداد للمبارزة الشعرية التي ستمتد ل{ROUNDS_NUMERAL_TO_ARABIC[num_rounds]}"
  await send_judge_comment(websocket, message + '\n')

  await send_verse(websocket, "poet1", "أنا مستعد \n")
  await asyncio.sleep(2)  # Pause between verses

  await send_verse(websocket, "poet2", "هيا بنا \n")
  await asyncio.sleep(2)  # Pause between verses

  ## simulation loop
  for round in range(num_rounds): 
    message = f"الحكم: لنبدأ الجولة {NUMBER_TO_ORDINAL[round+1]} يا متبارزين"
    await send_judge_comment(websocket, message + '\n')

    log_message(msg=Fore.RED + f"الحكم: لنبدأ الجولة {NUMBER_TO_ORDINAL[round+1]} يا متبارزين" +  Style.RESET_ALL,level=1)
    log_message(msg=Fore.BLUE + f"الحكم للشاعر الأول: {POET1_PROMPTS[round]}" + Style.RESET_ALL, level=1)
    log_message(msg=Fore.BLUE + f"الحكم للشاعر الثاني: {POET2_PROMPTS[round]}" + Style.RESET_ALL, level=1)

    await send_judge_comment(websocket, ROUND_PROMPTS_UI[round] + '\n')

    # for the qafya scorer
    # results_1, _ = generator_agent.fetch_relevant_poems_with_metadata(POET1_PROMPTS[round])
    # results_2, _ = generator_agent.fetch_relevant_poems_with_metadata(POET2_PROMPTS[round])
    # log_message(msg="Fetched verses for the two competitors",level=2)

    poet1_bait, qafya_letter_1 = generator_agent.generate_bait(POET1_PROMPTS[round])
    poet2_bait, qafya_letter_2 = generator_agent.generate_bait(POET2_PROMPTS[round])

    ROUND_VERSES["poet1"].append(poet1_bait)
    ROUND_VERSES["poet2"].append(poet2_bait)

    log_message(msg="Each competitor generated his bait", level=2)
    log_message(msg=Fore.BLUE + f"الشاعر الأول: {poet1_bait}" + Style.RESET_ALL, level=1)
    log_message(msg=Fore.BLUE + f"الشاعر الثاني: {poet2_bait}" + Style.RESET_ALL, level=1)

    # Send verses character by character
    await send_verse(websocket, "poet1", poet1_bait + '\n')
    await asyncio.sleep(2)  # Pause between verses
    await send_verse(websocket, "poet2", poet2_bait + '\n')
    await asyncio.sleep(2)  # Pause between verses

    json_response = {'poet1':poet1_bait,'poet2':poet2_bait}

    log_message(msg="Judge starting evaluation", level=2)

    # Evaluating scores
    round_scores_1 = judge_agent.score(poet1_bait, qafya_letter_1)
    round_scores_2 = judge_agent.score(poet2_bait, qafya_letter_2)

    log_message(msg="Judge calculated scores", level=2)
    log_message(msg=f"Competitor1: qafya_score: {round_scores_1["qafya_score"]}, meters_score: {round_scores_1["meters_score"]}, quality_score: {round_scores_1["quality_score"]}", level=2)
    log_message(msg=f"Competitor2: qafya_score: {round_scores_2["qafya_score"]}, meters_score: {round_scores_2["meters_score"]}, quality_score: {round_scores_2["quality_score"]}", level=2)

    ROUND_SCORES["poet1"].append(round_scores_1["round_score"])
    ROUND_SCORES["poet2"].append(round_scores_2["round_score"])

    if Config.EVALUATION_MODE:
      judge_comment1, gpt_comment1, allam_comment1, scores1 = judge_agent.comment(poet1_bait, round_scores_1["qafya_score"])
      judge_comment2, gpt_comment2, allam_comment2, scores2 = judge_agent.comment(poet2_bait, round_scores_2["qafya_score"])
      row_data = [str(round+1), gpt_comment1, gpt_comment2, allam_comment1, allam_comment2," ", " ", scores1, scores2," "]
      add_row(row_data, log_file)

    else:
      judge_comment1 = judge_agent.comment(poet1_bait, round_scores_1["qafya_score"])
      judge_comment2 = judge_agent.comment(poet2_bait, round_scores_2["qafya_score"])

    await send_judge_comment(websocket, f"الحكم للشاعر {poet1}: {judge_comment1}" +'\n'+f"الحكم للشاعر {poet2}: {judge_comment2}" + '\n')

    ROUND_COMMENTS["poet1"].append(judge_comment1)
    ROUND_COMMENTS["poet2"].append(judge_comment2)

    log_message(msg=Fore.RED + f"الحكم للشاعر الأول: {judge_comment1}" + Style.RESET_ALL, level=1)
    log_message(msg=Fore.RED + f"الحكم للشاعر الثاني: {judge_comment2}" + Style.RESET_ALL, level=1)

    log_message(msg=f"poet1 score: {ROUND_SCORES['poet1'][round]}", level=2)
    log_message(msg=f"poet2 score: {ROUND_SCORES['poet2'][round]}", level=2)

    if ROUND_SCORES['poet1'][round] > ROUND_SCORES['poet2'][round]:
      log_message(msg=Fore.RED + f"يبدو أن الشاعر {poet1} تفوق في الجولة {NUMBER_TO_ORDINAL[round+1]}" + Style.RESET_ALL, level=1)
      json_response['judge']= f"يبدو أن الشاعر {poet1} تفوق في الجولة {NUMBER_TO_ORDINAL[round+1]}"
      await send_judge_comment(websocket, json_response['judge'] + '\n')

    elif ROUND_SCORES['poet1'][round] < ROUND_SCORES['poet2'][round]:
      log_message(msg=Fore.RED + f"يبدو أن الشاعر {poet2} تفوق في الجولة {NUMBER_TO_ORDINAL[round+1]}" + Style.RESET_ALL, level=1)
      json_response['judge']=f"يبدو أن الشاعر {poet2} تفوق في الجولة {NUMBER_TO_ORDINAL[round+1]}"
      await send_judge_comment(websocket, json_response['judge'] + '\n')
    else:
       log_message(msg=f"تعادل الشاعران في الجولة {NUMBER_TO_ORDINAL[round+1]}",level=1)
       json_response['judge']=f"تعادل الشاعران في الجولة {NUMBER_TO_ORDINAL[round+1]}"
       await send_judge_comment(websocket, json_response['judge'] + '\n')

  poet1_total_score = sum(ROUND_SCORES["poet1"])
  poet2_total_score = sum(ROUND_SCORES["poet2"])

  if Config.EVALUATION_MODE:
    summary, gpt_summary, allam_summary, scores = judge_agent.summarize(poet1, poet2, ROUND_VERSES, ROUND_SCORES, ROUND_VERSES)
    row_data = [" ", " ", " ", " ", " ", gpt_summary, allam_summary, " ", " ", scores]
    add_row(row_data, log_file)
  else:
    summary = judge_agent.summarize(poet1, poet2, ROUND_VERSES, ROUND_SCORES, ROUND_VERSES)

  log_message(msg=Fore.RED + f"الحكم: {summary}" + Style.RESET_ALL, level=1)
  await send_judge_comment(websocket, summary + '\n')

  if poet1_total_score > poet2_total_score:
    log_message(msg=Fore.RED + f"أنتصر الشاعر {poet1} في هذه المساجلة الشعرية" + Style.RESET_ALL, level=1)
    battle_result=f"أنتصر الشاعر {poet1} في هذه المساجلة الشعرية"
    await send_judge_comment(websocket, battle_result + '\n')

  elif poet1_total_score < poet2_total_score:
    log_message(msg=Fore.RED + f"أنتصر الشاعر {poet2} في هذه المساجلة الشعرية" + Style.RESET_ALL, level=1)
    battle_result=f"أنتصر الشاعر {poet2} في هذه المساجلة الشعرية"
    await send_judge_comment(websocket, battle_result + '\n')

  else:
    log_message(msg=Fore.RED + "تعادل الشاعران في هذه المبارزة الشعرية" + Style.RESET_ALL,level=1)
    battle_result="تعادل الشاعران في هذه المبارزة الشعرية" 
    await send_judge_comment(websocket, battle_result + '\n')