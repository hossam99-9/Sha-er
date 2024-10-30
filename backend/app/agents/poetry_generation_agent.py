import re
import random
import json

import faiss
import duckdb
import pandas as pd

from sentence_transformers import SentenceTransformer

from backend.app.agents.base_agent import BaseAgent
from backend.app.utils.debate import *
from backend.app.config.config import Config

from bohour.qafiah import get_qafiyah


class PoetryGenerationAgent(BaseAgent):
    def __init__(self,
                retriever_llm_model,
                generator_llm_model,
                poetry_database_path,
                index_poet,
                index_theme,
                poets_list,
                themes_list,
                embedding_model_name = PARAPHRASE_MODEL_NAME):

        self.retriever_llm_model = retriever_llm_model
        self.generator_llm_model=generator_llm_model
        self.poetry_database = pd.read_csv(poetry_database_path)

        if Config.PARAPHRASE_MODEL_PATH.exists():
            print(f"Loading model from local path: {Config.PARAPHRASE_MODEL_PATH}",flush=True)
            self.embedding_model = SentenceTransformer(str(Config.PARAPHRASE_MODEL_PATH))
        else:
            print(f"Local path not found. Downloading model: {embedding_model_name}", flush=True)
            self.embedding_model = SentenceTransformer(embedding_model_name)
            self.embedding_model.save(str(Config.PARAPHRASE_MODEL_PATH))

        self.index_poet = index_poet
        self.index_theme = index_theme
        self.poets_list = poets_list
        self.themes_list = themes_list

    def _find_similar(self,query, index, ground_truth, k=1):
        """
        Find the most similar item in the index.
        args:
        query: theme or poet
        index: index_theme or index_poet
        ground_truth: list
        """
        query_vector = self.embedding_model.encode([query])
        faiss.normalize_L2(query_vector)
        _, indices = index.search(query_vector, k)
        top = indices[0][0]
        return ground_truth[top]
    
    def _do_query(self,poet_name, poem_theme):
        df = self.poetry_database
        query = f"""
        SELECT *
        FROM df
        WHERE "poet name" = '{poet_name}'
        AND "poem theme" = '{poem_theme}'
        """
        return duckdb.sql(query).to_df()

    def _parser(self,unstructured):
        pattern = r'"(\w+)":\s*"?{"(.+?)"}"?'
        data = dict(re.findall(pattern, unstructured))
        poet_name = data['poet_name']
        poem_theme = data['poem_theme']
        poem_qafya = data['poem_qafya']
        poem_qafya_letter = data['poem_qafya_letter']

        return poet_name, poem_theme, poem_qafya, poem_qafya_letter

    def _create_retrieval_prompt(self,user_prompt):
        structured_prompt = f"""
        [INST] <<SYS>>
        You are a helpful assistent, that only communicates using JSON files.
        All output must be in valid JSON. Don’t add explanation beyond the JSON
        The expected output from you has to be: 
            {{
                "poet_name": {{"poet_name"}},
                "poem_theme": {{"poem_theme"}},
                "poem_qafya": {{"poem_qafya"}},
                "poem_qafya_letter": {{poem_qafya_letter}},
            }}
        The INST block will always be a json string:
            {{
                "prompt": {{user_prompt}}
            }}
        Here are the examples for the input and the corresponding output you can generate:
        {{
        "input": "بيت شعر عن الوطنية علي طريقة الشاعر أحمد شوقي ينتهي بقافية الميم",
        "output": {{
            "poet_name": {{"أحمد شوقي"}},
            "poem_theme": {{"قصيدة وطنية"}},
            "poem_qafya": {{"قافية الميم"}}
            "poem_qafya_letter": {{"م"}}
        }}
        }},
        {{
            "input": بيت شعر عن الرومنسيه علي طريقة الشاعر إيليا أبو ماضي ينتهي بقافية النون",
            "output": {{
                "poet_name": {{"إيليا أبو ماضي"}},
                "poem_theme": {{"قصيدة رومنسيه"}},
                "poem_qafya": {{"قافية النون"}}
                "poem_qafya_letter": {{"ن"}}
            }}
        }},
        {{
            "input": "بيت شعر عن الحرية علي طريقة الشاعر محمود درويش ينتهي بقافية الراء",
            "output": {{
                "poet_name": {{"محمود درويش"}},
                "poem_theme": {{"قصيدة حرية"}},
                "poem_qafya": {{"قافية الراء"}}
                "poem_qafya_letter": {{"ر"}}
            }}
        }},
        {{
            "input": "أريد بيت شعر عن الحب علي طريقة الشاعرة نازك الملائكة ينتهي بقافية الباء",
            "output": {{
                "poet_name": {{"نازك الملائكة"}},
                "poem_theme": {{"قصيدة حب"}},
                "poem_qafya": {{"قافية الباء"}}
                "poem_qafya_letter": {{"ب"}}
            }}
        }},
        {{
            "input": " أعطني بيت شعر حزين علي طريقة الشاعر بدر شاكر السياب ينتهي بقافية الدال",
            "output": {{
                "poet_name": {{"بدر شاكر السياب"}},
                "poem_theme": {{"قصيدة حزينة"}},
                "poem_qafya": {{"قافية الدال"}}
                "poem_qafya_letter": {{"د"}}
            }}
        }}
        Remember give me only the JSON output. Don't add any exaplanation or any thing else
        <</SYS>> [/INST]

        [INST] 
        {{
            "prompt": "{user_prompt}"
        }}
        [/INST]
        """
        return structured_prompt

    def _construct_baits(self, input_string):
        items = [item.strip().strip("'\"") for item in input_string.strip('[]').split(',')]
        
        pairs = [f"{items[i]} {items[i+1]}" for i in range(0, len(items)-1, 2)]
        
        return pairs
    
    def _construct_examples(self, verses, desired_qafya):
        all_baits = []
        examples = []
        verses = verses.to_list()

        for i, poem in enumerate(verses):
          # get all baits
          baits = self._construct_baits(poem)
          all_baits.extend(baits)

        random.shuffle(all_baits)

        # use only baits with matching qafya
        for bait in all_baits:
          # get the qafya
          qafya = majority_vote(
              get_qafiyah([bait], short=False)
          )
          qafya_letter = qafya[0]

          # add only if qafya matches
          if desired_qafya == qafya_letter:
            if len(examples) == 15:
              break
            examples.append(bait)
          random.shuffle(examples)

        if len(examples) < 10:
          for i, poem in enumerate(verses):
            # check only max 5 poems
            if i == 5:
              break
            baits = self._construct_baits(poem)
            random.shuffle(baits)
            examples.extend(baits[0:3])

        return examples

    def fetch_relevant_poems_with_metadata(self, user_prompt):
        # Prepare the structured prompt
        structured_prompt = self._create_retrieval_prompt(user_prompt)
        log_message(msg=f"Structured prompt for retrieval query {structured_prompt}", level=2)

        # Get the output from the language model
        output = self.retriever_llm_model.generate(structured_prompt)
        log_message(msg=f"Allam pure structured output: {output}", level=2)

        # Parse the output
        poet_name, poem_theme, poem_qafya, poem_qafya_letter = self._parser(output)
        log_message(msg=f"parsed: {poet_name}, {poem_theme}, {poem_qafya}, {poem_qafya_letter}", level=2)

        # Find the true poet name and theme using a similarity search
        true_poet_name = self._find_similar(query=poet_name, index=self.index_poet, ground_truth=self.poets_list)
        true_poem_theme = self._find_similar(query=poem_theme, index=self.index_theme, ground_truth=self.themes_list)

        # Query the database for the matching poem
        result = self._do_query(true_poet_name, true_poem_theme)
        
        data = {
            "poet_name": true_poet_name,
            "poem_theme": true_poem_theme,
            "poem_qafya": poem_qafya,
            "poem_qafya_letter": poem_qafya_letter,
            "verses": result["poem verses"] # Pandas Series
        }
        log_message(msg=f"Fetched data: {data}", level=2)

        return data

    def _create_generation_prompt(self, data):
        # Create the prompt for the LLM
        def int_to_arabic(number):
            arabic_numerals = '٠١٢٣٤٥٦٧٨٩'
            return ''.join(arabic_numerals[int(d)] for d in str(number))
       
        verses = data["verses"]
        examples = self._construct_examples(verses, data["poem_qafya_letter"])
        
        system_prompt = f"""
You are a poet who writes new Arabic poetry based on the style of the given poet name, the theme, and the rhyme.
Make sure the generated verse is new
Give me only one verse in one line
Return the output verse as a JSON object.
Please use the given examples to mimic the style of the chosen poet:
{
    ''.join([f"{int_to_arabic(i+1)}-{example}\n" for i, example in enumerate(examples)])
}
Never give me real verse or one from the examples.
The expected output from you has to be: 
{{
  "verse": {{verse}},
}}
The INST block will always be a json string:
{{
  "poet_name": {{poet name}}
  "theme": {{theme}}
  "rhyme": {{rhyme}}
}}
Remember give me only the JSON output. Don't add any exaplanation or any thing else
"""

        user_message = f"""
{{
"poet_name": {data["poet_name"]},
"theme": {data["poem_theme"]},
"rhyme": {data["poem_qafya"]}
}}
"""
        generation_prompt = f"""
<s>[INST] <<SYS>>
{{{ system_prompt }}}
<</SYS>>

{{{ user_message }}} [/INST]
"""

        log_message(msg=f"Generation prompt: {generation_prompt}",level=2)
        
        return generation_prompt
    
    def _postprocess_bait(self, bait):
        try:
            start_quote = bait.find('"verse": "') + 9
            end_quote = bait.find('"', start_quote + 1)
            
            if start_quote == 8 or end_quote == -1:
                return "Error: Invalid string format"
                
            verse = bait[start_quote + 1:end_quote]
            return verse

        except Exception as e:
            return f"Error: {str(e)}"

    def generate_bait(self, user_prompt):
        data= self.fetch_relevant_poems_with_metadata(user_prompt=user_prompt)
        generation_prompt = self._create_generation_prompt(data=data)
        generated_bait = self.generator_llm_model.generate(generation_prompt)
        log_message(msg=f"Generated bait: {generated_bait}", level=2)
        generated_bait = self._postprocess_bait(generated_bait)
        return generated_bait
    
    def generate_bait_stream(self, user_prompt):
        data= self.fetch_relevant_poems_with_metadata(user_prompt=user_prompt)
        generation_prompt = self._create_generation_prompt(data=data)
        return self.generator_llm_model.generate_stream(generation_prompt)

    def handle_request(self, user_prompt):
        return self.generate_poem(user_prompt=user_prompt)
    
    def handle_request_stream(self, user_prompt):
        return self.generate_poem_stream(user_prompt=user_prompt)
