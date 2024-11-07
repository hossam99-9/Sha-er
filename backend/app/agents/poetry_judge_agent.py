from dataclasses import dataclass
    
from openai import OpenAI

from backend.app.agents.base_agent import BaseAgent
from backend.app.agents.evaluation_agent import EvaluationAgent
from backend.app.servers.poetry_analysis.meters.model import predict_meter
from backend.app.utils.debate import *
from backend.app.config.config import *

from bohour.qafiah import get_qafiyah

class PoetryJudgeAgent(BaseAgent):
    def __init__(self, commentator_llm_model, summarizer_llm_model):
      self.commentator_llm_model = commentator_llm_model
      self.summarizer_llm_model = summarizer_llm_model
      self.openai_client = OpenAI(api_key = Config.OPENAI_API_KEY) # for evaluation
      self.evaluation_agent = EvaluationAgent()

    @dataclass
    class PredictionRequest:
        text: str

    @dataclass
    class PredictionResponse:
        predicted_meter: str

    def _prepare_summarizer_prompt_gpt(self, poet1, poet2, round_verses, round_scores, round_comments):
      summarizer_system = f"""
انت محكم في مبارزة شعرية بين {poet1} و {poet2} تتمثل مهمتك في تقديم ملخص شامل ومفيد لكل جولة، يتضمن النقاط التي حصل عليها كل شاعر  و البيت الذي قام كل شاعر بتوليده في كل جولة وتعليقات حول الأداء في كل جولة. يُرجى تلخيص النتائج وتقديم نظرة عامة شاملة عن الأداء الإجمالي لكل شاعر، مع التأكيد على النقاط الرئيسية والتعليقات المميزة لكل جولة. الهدف هو تقديم ملخص واضح ومحدد يساعد على فهم أداء كل شاعر في المنافسة.
"""
      summarizer_user = f"""
الأبيات الذي قام الشاعر {poet1} بتوليدها في كل جولة 
{
    ''.join([f"{NUMBER_TO_ORDINAL[i+1]}-{verse}\n" for i, verse in enumerate(round_verses["poet1"])])
}
الأبيات الذي قام الشاعر {poet2} بتوليدها في كل جولة 
{
    ''.join([f"{NUMBER_TO_ORDINAL[i+1]}-{verse}\n" for i, verse in enumerate(round_verses["poet2"])])
}
النقاط التي حصل عليها الشاعر {poet1} في كل جولة
{
    ''.join([f"{NUMBER_TO_ORDINAL[i+1]} عدد النقاط:{score}\n" for i, score in enumerate(round_scores["poet1"])])
}
النقاط التي حصل عليها الشاعر {poet2} في كل جولة
{
    ''.join([f"{NUMBER_TO_ORDINAL[i+1]} عدد النقاط:{score}\n" for i, score in enumerate(round_scores["poet2"])])
}
التعليقات التي حصل عليها الشاعر {poet1} في كل جولة 
{
    ''.join([f"{NUMBER_TO_ORDINAL[i+1]}-{comment}\n" for i, comment in enumerate(round_comments["poet1"])])
}
التعليقات التي حصل عليها الشاعر {poet2} في كل جولة 
{
    ''.join([f"{NUMBER_TO_ORDINAL[i+1]}-{comment}\n" for i, comment in enumerate(round_comments["poet2"])])
}
"""
      return summarizer_system, summarizer_user

    def _prepare_commentator_prompt_gpt(self, bait):
      commentator_system = f"""
أنت خبير في التعليق علي الشعر العربي و تخيل أنك تتحدث للشاعر الذي كتب البيت
سأعطيك البيت و أنت أعطني التعليق بنفس اسلوب الأمثلة كأنك تتحدث إلي الشاعر نفسه 

شكل التعليق المتوقع من كتابته
    التعليق: {{التعليق علي البيت}}

The input block will always be a json string:
{{
  "prompt": {{البيت}}
}}

الأمثلة
أَركَبُ البَحرَ تارَةً وَأَجوبُ البَرَّ طَوراً وَأَقطَعُ الأَيّاما
التعليق: و أقطع الأياما, ممتاز انت تشير إلى الترحال عبر البحر والبر وتجاوز الأيام كرمز للتحدي المستمر

صرح الفلاح على الفضيل مشيد فالفضل ركن الخير والعمرانِ
التعليق: الخير و العمران, جميل أنت تشير إلي الفلاح في فضيلة بناء الخير و العمران و العمل الجاد

أهيمُ في الصحارى طَرِبًا والجبالُ تسيرُ معي
التعليق: الجبال تسير معي، رائع، أنت تستعمل الجبال كرمز للقوة والاستمرارية في رحلتك التي تعكس سمو النفس

كأن النجومَ تُهدي النورَ في ظلمةِ الليالي الحائرة
التعليق: النجوم تهدي النور, رائع أنت استخدمت استخدام رائع للاستعارة، حيث تشير النجوم إلى الأمل والإرشاد في أوقات الشدائد

سيف العزِّ يمضي بغير هوادة، يقطع طريقَ اليأسِ بلا رجوع
التعليق: سيف العز، قوي! هنا السيف رمز للقوة والشجاعة، وقطع طريق اليأس يعكس الانتصار على العقبات

تذكر رجاء أعطني التعليق فقط لا تقوم بشرح او كتابة اي شيء سوي التعليق
"""
      user_prompt = f"""
{{
  "prompt": "{bait}"
}}
"""
      return commentator_system, user_prompt

    def _prepare_summarizer_prompt(self, poet1, poet2, round_verses, round_scores, round_comments):
      poet1_total_score = sum(round_scores["poet1"])
      poet2_total_score = sum(round_scores["poet2"])

      summarizer_prompt = f"""
<s> [INST]<<SYS>>
انت محكم في مبارزة شعرية بين {poet1} و {poet2} تتمثل مهمتك في تقديم ملخص شامل ومفيد لكل جولة، يتضمن النقاط التي حصل عليها كل شاعر  و البيت الذي قام كل شاعر بتوليده في كل جولة وتعليقات حول الأداء في كل جولة. يُرجى تلخيص النتائج وتقديم نظرة عامة شاملة عن الأداء الإجمالي لكل شاعر.
<</SYS>>
عدد الجولات: {len(round_scores["poet1"])}
الأبيات الذي قام الشاعر {poet1} بتوليدها في كل جولة 
{
    ''.join([f"{NUMBER_TO_ORDINAL[i+1]}-{verse}\n" for i, verse in enumerate(round_verses["poet1"])])
}
الأبيات الذي قام الشاعر {poet2} بتوليدها في كل جولة 
{
    ''.join([f"{NUMBER_TO_ORDINAL[i+1]}-{verse}\n" for i, verse in enumerate(round_verses["poet2"])])
}
النقاط التي حصل عليها الشاعر {poet1} في كل جولة
{
    ''.join([f"{NUMBER_TO_ORDINAL[i+1]} عدد النقاط:{score}\n" for i, score in enumerate(round_scores["poet1"])])
}
النقاط التي حصل عليها الشاعر {poet2} في كل جولة
{
    ''.join([f"{NUMBER_TO_ORDINAL[i+1]} عدد النقاط:{score}\n" for i, score in enumerate(round_scores["poet2"])])
}
التعليقات التي حصل عليها الشاعر {poet1} في كل جولة 
{
    ''.join([f"{NUMBER_TO_ORDINAL[i+1]}-{comment}\n" for i, comment in enumerate(round_comments["poet1"])])
}
التعليقات التي حصل عليها الشاعر {poet2} في كل جولة 
{
    ''.join([f"{NUMBER_TO_ORDINAL[i+1]}-{comment}\n" for i, comment in enumerate(round_comments["poet2"])])
}
حصل الشاعر {poet1} علي مجموع نقاط {poet1_total_score}
حصل الشاعر {poet2} علي مجموع نقاط {poet2_total_score}
[/INST]
"""
      return summarizer_prompt

    def _prepare_commentator_prompt(self, bait):
      commentator_prompt = f"""
[INST] <<SYS>>
أنت خبير في التعليق علي الشعر العربي و تخيل أنك تتحدث للشاعر الذي كتب البيت
سأعطيك البيت و أنت أعطني التعليق بنفس اسلوب الأمثلة كأنك تتحدث إلي الشاعر نفسه 

شكل التعليق المتوقع من كتابته
    التعليق: {{التعليق علي البيت}}

The INST block will always be a json string:
{{
  "prompt": {{البيت}}
}}

الأمثلة
أَركَبُ البَحرَ تارَةً وَأَجوبُ البَرَّ طَوراً وَأَقطَعُ الأَيّاما
التعليق: و أقطع الأياما, ممتاز انت تشير إلى الترحال عبر البحر والبر وتجاوز الأيام كرمز للتحدي المستمر

صرح الفلاح على الفضيل مشيد فالفضل ركن الخير والعمرانِ
التعليق: الخير و العمران, جميل أنت تشير إلي الفلاح في فضيلة بناء الخير و العمران و العمل الجاد

أهيمُ في الصحارى طَرِبًا والجبالُ تسيرُ معي
التعليق: الجبال تسير معي، رائع، أنت تستعمل الجبال كرمز للقوة والاستمرارية في رحلتك التي تعكس سمو النفس

كأن النجومَ تُهدي النورَ في ظلمةِ الليالي الحائرة
التعليق: النجوم تهدي النور, رائع أنت استخدمت استخدام رائع للاستعارة، حيث تشير النجوم إلى الأمل والإرشاد في أوقات الشدائد

سيف العزِّ يمضي بغير هوادة، يقطع طريقَ اليأسِ بلا رجوع
التعليق: سيف العز، قوي! هنا السيف رمز للقوة والشجاعة، وقطع طريق اليأس يعكس الانتصار على العقبات

تذكر رجاء أعطني التعليق فقط لا تقوم بشرح او كتابة اي شيء سوي التعليق

<</SYS>> [/INST]
[INST] 
{{
  "prompt": "{bait}"
}}
[/INST]
"""
      return commentator_prompt

    def _prepare_quality_scorer_prompt(self, bait):
      quality_scorer_prompt = """
[INST] <<SYS>>
أنت خبير في تقييم الشعر العربي. 
لديك بيت واحد من الشعر و أنت ستقيمه من 1 إلي 3 بناءا علي جودة البيت
جودة البيت تعتمد علي اختيار الكلمات و القافية و وزن البيت و جودة معني البيت

The expected output from you has to be: 
score: {verse_score}

The INST block will always be a json string:
{
 "prompt": {البيت}
}

Here are the examples for the input and the corresponding output you can generate:
"verse": "أَركَبُ البَحرَ تارَةً وَأَجوبُ ال بَرَّ طَوراً وَأَقطَعُ الأَيّاما"
"output":
  score: 3

"verse": "صرح الفلاح على الفضيل مشيد فالفضل ركن الخير والعمرانِ"
"output":
  score: 2

"verse": "برز الثعلب يوما فى ثياب الواعظينا"
"output":
  score: 2

Remember Give me only the score in the output format specified. Don't give me any explanation.

<</SYS>> [/INST]
"""
      instruction = f"""
[INST] 
{{
  "prompt": "{bait}"
}}
[/INST]
      """
      return quality_scorer_prompt + instruction

    def _qafya_comment(self, score):
      if score == 1:
        comment = "أيضا مع الأسف انت لم تحافظ علي القافية المطلوبة"
      else:
        comment = "أيضا ممتاز لقد حافظت علي القافية المطلوبة"

      return comment

    def _postprocess_comment(self, comment):
      return comment.split('\n', 1)[0]

    def _meters_scorer(self, bait):
        meter = predict_meter(bait)

        if meter in METERS_SCORES.keys():
            score = METERS_SCORES[meter]
        else:
            score = 3

        return score

    def _quality_scorer(self, score_str):
      parsed_score = (score_str.split(":")[1].strip())
      # temp solution
      if isinstance(parsed_score, str) and parsed_score.isdigit():
        score = int(parsed_score)
      else:
        score = 2
      return score

    def _qafya_scorer(self, bait, desired_qafya):
      true_qafya = majority_vote(get_qafiyah([bait], short=False))[0]
      if true_qafya == desired_qafya:
        return 4
      else:
        return 1

    def score(self, bait, desired_qafya):
      quality_prompt = self._prepare_quality_scorer_prompt(bait)
      quality_score = self._quality_scorer(self.commentator_llm_model.generate(quality_prompt))
      qafya_score = self._qafya_scorer(bait, desired_qafya)
      meters_score = self._meters_scorer(bait)

      return {
         "quality_score": quality_score,
         "qafya_score": qafya_score,
         "meters_score": meters_score,
         "round_score": meters_score + qafya_score + quality_score,
      }

    def comment(self, bait, qafya_score):
      comment_prompt = self._prepare_commentator_prompt(bait)
      comment = self.commentator_llm_model.generate(comment_prompt)
      comment = self._postprocess_comment(comment) # Compare with this
      qafya_comment = self._qafya_comment(qafya_score)

      if Config.EVALUATION_MODE:
        log_message(msg="Evaluation mode ON", level=2)
        comment_prompt_gpt_system, user_prompt = self._prepare_commentator_prompt_gpt(bait)

        completion = self.openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
          {"role": "system", "content": comment_prompt_gpt_system},
          {"role": "user", "content": user_prompt}
        ],
        temperature=0.0, # to match Allam params (Change later ?)
        )

        gpt_comment = completion.choices[0].message.content

        precision, recall, F1 = self.evaluation_agent.evaluate(comment, gpt_comment)
        scores = (precision, recall, F1)

        log_message(msg="Allam and GPT-4 commentator evaluation results:", level=2)
        log_message(msg=f"GPT-4 comment: {gpt_comment}", level=2)
        log_message(msg=f"Allam comment: {comment}", level=2)
        log_message(msg=f"Precision={precision:.6f} Recall={recall:.6f} F1={F1:.6f}", level=2)

        return comment + qafya_comment, gpt_comment, comment, scores 
      else:
        return comment + ' ' +  qafya_comment

    def summarize(self, poet1, poet2, round_verses, round_scores, round_comments):
       summary_prompt = self._prepare_summarizer_prompt(poet1, poet2, round_verses, round_scores, round_comments)
       summary = self.summarizer_llm_model.generate(summary_prompt)

       if Config.EVALUATION_MODE:
          log_message(msg="Evaluation mode ON", level=2)
          summary_prompt_gpt_system, user_prompt = self._prepare_summarizer_prompt_gpt(poet1, poet2, round_verses, round_scores, round_comments)

          completion = self.openai_client.chat.completions.create(
          model="gpt-4o-mini",
          messages=[
            {"role": "system", "content": summary_prompt_gpt_system},
            {"role": "user", "content": user_prompt}
          ],
          temperature=0.0, # to match Allam params (Change later ?)
          )

          gpt_summary = completion.choices[0].message.content

          precision, recall, F1 = self.evaluation_agent.evaluate(summary, gpt_summary)
          scores = (precision, recall, F1)

          log_message(msg="Allam and GPT-4 summarizer evaluation results:", level=2)
          log_message(msg=f"GPT-4 summary: {gpt_summary}",level=2)
          log_message(msg=f"Allam summary: {summary}", level=2)
          log_message(msg=f"Precision={precision:.6f} Recall={recall:.6f} F1={F1:.6f}", level=2)
        
          return summary, gpt_summary, summary, scores
       else:
        return summary