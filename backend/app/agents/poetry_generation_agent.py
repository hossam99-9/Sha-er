import re
import random
import time
import signal
from typing import Tuple, Dict, Optional
from dataclasses import dataclass


import faiss
import duckdb
import pandas as pd

from openai import OpenAI
from sentence_transformers import SentenceTransformer

from backend.app.agents.base_agent import BaseAgent
from backend.app.agents.evaluation_agent import EvaluationAgent
from backend.app.utils.debate import *
from backend.app.config.config import Config

from bohour.qafiah import get_qafiyah

@dataclass
class RegexResult:
    """Container for regex matching results and metadata"""
    success: bool
    matches: Optional[Dict[str, str]]
    error: Optional[str]
    execution_time: float

class RegexTimeout(Exception):
    """Custom exception for regex timeout"""
    pass


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
        self.openai_client = OpenAI(api_key = Config.OPENAI_API_KEY) # for evaluation
        self.evaluation_agent = EvaluationAgent()
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

    def _is_arabic_only(self, text):
        arabic_ranges = (
            ('\u0621', '\u063A'),
            ('\u0641', '\u064A')
        )
    
        def is_arabic_char(char):
            return char.isspace() or char == ',' or char == ':' or any(ord(start) <= ord(char) <= ord(end) for start, end in arabic_ranges)
        
        return all(is_arabic_char(char) for char in text)

    def _timeout_handler(self, signum, frame):
        """Signal handler for timeout"""
        raise RegexTimeout("Regex pattern matching timed out")

    def _parse_poetry_metadata(self, unstructured: str, timeout_seconds: float = 1.0) -> Tuple[str, str, str, str]:

        DEFAULT_VALUES = {
            'poet_name': "أحمد شوقي",
            'poem_theme': "رومنسي",
            'poem_qafya': "قافية الميم",
            'poem_qafya_letter': "م"
        }
        
        def safe_regex_find(pattern: str, text: str) -> RegexResult:
            """Internal function for safe regex matching"""
            start_time = time.time()
            
            try:
                # Compile pattern
                try:
                    compiled_pattern = re.compile(pattern)
                except re.error as e:
                    return RegexResult(
                        success=False,
                        matches=None,
                        error=f"Invalid regex pattern: {str(e)}", 
                        execution_time=time.time() - start_time
                    )
                    
                # Set up timeout
                signal.signal(signal.SIGALRM, self._timeout_handler)
                signal.setitimer(signal.ITIMER_REAL, timeout_seconds)
                
                try:
                    # Attempt to find all matches
                    matches = dict(compiled_pattern.findall(text))
                    success = bool(matches)
                    error = None
                    
                except RegexTimeout:
                    success = False
                    matches = None
                    error = f"Pattern matching timed out after {timeout_seconds} seconds"
                    
                finally:
                    # Disable timeout
                    signal.setitimer(signal.ITIMER_REAL, 0)
                    
            except Exception as e:
                return RegexResult(
                    success=False,
                    matches=None,
                    error=f"Unexpected error: {str(e)}",
                    execution_time=time.time() - start_time
                )
            
            return RegexResult(
                success=success,
                matches=matches,
                error=error,
                execution_time=time.time() - start_time
            )

        # Initialize data dictionary with default values
        data = DEFAULT_VALUES.copy()
        
        try:
            # Check for empty input
            if not unstructured.strip():
                raise ValueError("Input string is empty")
            
            # Pattern for extracting key-value pairs
            pattern = r'"(\w+)":\s*{"(.+)"}'
            
            # Attempt to match pattern
            result = safe_regex_find(pattern, unstructured)
            
            if result.success and result.matches:
                data.update(result.matches)
                
                # Check for missing required fields
                required_fields = {'poet_name', 'poem_theme', 'poem_qafya', 'poem_qafya_letter'}
                missing_fields = required_fields - set(data.keys())
                
                if missing_fields:
                    log_message(msg=f"Missing fields: {missing_fields}, Applying fallback measures", level=2)
                    
            else:
                log_message(msg=f"Regex parsing failed: {result.error}, Using default values", level=2)
                
        except Exception as e:
            print(f"Exception in parsing: {e}", flush=True)
        
        # Return the tuple of required fields
        return (
            data['poet_name'],
            data['poem_theme'],
            data['poem_qafya'],
            data['poem_qafya_letter']
        )

    def _parser_gpt(self,unstructured):
        pattern = r'"(\w+)":\s*"?"(.+?)""?'
        try:
            data = dict(re.findall(pattern, unstructured))
        except Exception as e:
            print(f"Exception in parsing: {e}", flush=True)

        poet_name = data['poet_name']
        poem_theme = data['poem_theme']
        poem_qafya = data['poem_qafya']
        poem_qafya_letter = data['poem_qafya_letter']

        return poet_name, poem_theme, poem_qafya, poem_qafya_letter

    def _create_retrieval_prompt_gpt(self, user_prompt):
        system_prompt = """You are a helpful assistant that only communicates using JSON files.
All output must be in valid JSON. Don't add explanation beyond the JSON.
The expected output from you has to be: 
{
    "poet_name": string,
    "poem_theme": string,
    "poem_qafya": string,
    "poem_qafya_letter": string
}

Here are examples of input-output pairs to guide your responses:

Input: "بيت شعر عن الوطنية علي طريقة الشاعر أحمد شوقي ينتهي بقافية الميم"
{
    "poet_name": "أحمد شوقي",
    "poem_theme": "قصيدة وطنية",
    "poem_qafya": "قافية الميم",
    "poem_qafya_letter": "م"
}

Input: "بيت شعر عن الرومنسيه علي طريقة الشاعر إيليا أبو ماضي ينتهي بقافية النون"
{
    "poet_name": "إيليا أبو ماضي",
    "poem_theme": "قصيدة رومنسيه",
    "poem_qafya": "قافية النون",
    "poem_qafya_letter": "ن"
}

Input: "بيت شعر عن الحرية علي طريقة الشاعر محمود درويش ينتهي بقافية الراء"
{
    "poet_name": "محمود درويش",
    "poem_theme": "قصيدة حرية",
    "poem_qafya": "قافية الراء",
    "poem_qafya_letter": "ر"
}

Input: "أريد بيت شعر عن الحب علي طريقة الشاعرة نازك الملائكة ينتهي بقافية الباء"
{
    "poet_name": "نازك الملائكة",
    "poem_theme": "قصيدة حب",
    "poem_qafya": "قافية الباء",
    "poem_qafya_letter": "ب"
}

Input: "أعطني بيت شعر حزين علي طريقة الشاعر بدر شاكر السياب ينتهي بقافية الدال"
{
    "poet_name": "بدر شاكر السياب",
    "poem_theme": "قصيدة حزينة",
    "poem_qafya": "قافية الدال",
    "poem_qafya_letter": "د"
}

Remember to provide only the JSON output. Don't add any explanation or anything else."""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        log_message(msg=f"gpt-4o-mini messages: {messages}", level=2)

        return messages
    
    def _create_retrieval_prompt(self,user_prompt):
        if not self._is_arabic_only(user_prompt):
            return ""

        structured_prompt = f"""
        [INST] <<SYS>>
        You are a helpful assistent, that only communicates using JSON files.
        All output must be in valid JSON. Don’t add explanation beyond the JSON
        The expected output from you has to be: 
            {{
                "poet_name": {{"poet_name"}},
                "poem_theme": {{"poem_theme"}},
                "poem_qafya": {{"poem_qafya"}},
                "poem_qafya_letter": {{"poem_qafya_letter"}},
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

        if Config.EVALUATION_MODE:
            log_message(msg=f"using GPT", level=2)
            structured_prompt = self._create_retrieval_prompt_gpt(user_prompt)
            log_message(msg=f"Structured prompt for retrieval query(GPT) {structured_prompt}", level=2)
            completion = self.openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=structured_prompt,
            temperature=0.0, # to match Allam params (Change later ?)
            )
            output = completion.choices[0].message.content
            log_message(msg=f"GPT (Evaluation) pure structured output: {output}", level=2)
            # Parse the output
            poet_name, poem_theme, poem_qafya, poem_qafya_letter = self._parser_gpt(output)
            log_message(msg=f"parsed: {poet_name}, {poem_theme}, {poem_qafya}, {poem_qafya_letter}", level=2)
        else:
            log_message(msg=f"Evaluation mode is off in retrieval", level=2)
            structured_prompt = self._create_retrieval_prompt(user_prompt)
            if structured_prompt == "":
                return {}, False
            log_message(msg=f"Structured prompt for retrieval query(Allam) {structured_prompt}", level=2)
            output = self.retriever_llm_model.generate(structured_prompt)
            log_message(msg=f"Allam pure structured output: {output}", level=2)
            # Parse the output
            poet_name, poem_theme, poem_qafya, poem_qafya_letter = self._parse_poetry_metadata(output)
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
            "verses": result["poem verses"], # Pandas Series
        }

        log_message(msg=f"Fetched data: {data}", level=2)

        return data, True

    def _create_generation_prompt_gpt(self, data):
        # Create the prompt for the LLM
        def int_to_arabic(number):
            arabic_numerals = '٠١٢٣٤٥٦٧٨٩'
            return ''.join(arabic_numerals[int(d)] for d in str(number))
       
        verses = data["verses"]
        examples = self._construct_examples(verses, data["poem_qafya_letter"])

        formatted_examples = ''.join([f"{int_to_arabic(i+1)}-{example}\n" for i, example in enumerate(examples)])
    
        system_prompt = f"""You are a poet who writes new Arabic poetry based on the style of the given poet name, the theme, and the rhyme.
    Make sure the generated verse is new.
    Give me only one verse in one line.
    Return the output verse as a JSON object.
    Please use the given examples to mimic the style of the chosen poet:

    {formatted_examples}

    Never give me real verse from the poet's work or one from the examples.
    The expected output from you has to be: 
    {{
        "verse": string
    }}"""

        user_prompt = f"""{{
        "poet_name": {data["poet_name"]},
        "theme": {data["poem_theme"]},
        "rhyme": {data["poem_qafya"]}
    }}"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        log_message(msg=f"gpt-4o-mini messages: {messages}", level=2)
        
        return messages

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
Never give me a verse from the real poet's work or one from the examples.
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
"poet_name": {{{data["poet_name"]}}},
"theme": {{{data["poem_theme"]}}},
"rhyme": {{{data["poem_qafya"]}}},
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
                print(f"Error: Invalid string format, Applying fallback")
                return "أَلا كُلُّ شَيءٍ ما خَلا اللَهَ باطِلُ    وَكُلُّ نَعيمٍ لا مَحالَةَ زائِلُ"
                
            verse = bait[start_quote + 1:end_quote]
            verse = verse.replace('\\n', '   ')
            verse = verse.replace('\n', '   ')
            verse = verse.replace('/n', '   ')
            verse = verse.replace('//n', '   ')
            verse = verse.replace('n/', '   ')
            verse = verse.replace('n//', '   ')
            verse = verse.replace('n\\','   ')
            return verse

        except Exception as e:
            return f"Error: {str(e)}"

    def generate_bait(self, user_prompt):
        data, success = self.fetch_relevant_poems_with_metadata(user_prompt=user_prompt)

        if success == False:
            return "يرجي اتباع الدليل الموضح" , {}

        if Config.EVALUATION_MODE:
            generation_prompt = self._create_generation_prompt_gpt(data=data)
            log_message(msg=f"Using gpt in generation(Evaluation)", level=2)
            completion = self.openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=generation_prompt,
            temperature=0.5, # to match Allam params (Change later ?)
            )
            output = completion.choices[0].message.content
            log_message(msg=f"Generated bait: {output}", level=2)
            generated_bait = self._postprocess_bait(output)
        else:
            generation_prompt = self._create_generation_prompt(data=data)
            generated_bait = self.generator_llm_model.generate(generation_prompt)
            log_message(msg=f"Generated bait: {generated_bait}", level=2)
            generated_bait = self._postprocess_bait(generated_bait)

        return generated_bait, data["poem_qafya_letter"]
    
    def generate_bait_stream(self, user_prompt):
        data= self.fetch_relevant_poems_with_metadata(user_prompt=user_prompt)
        generation_prompt = self._create_generation_prompt(data=data)
        return self.generator_llm_model.generate_stream(generation_prompt)

    def handle_request(self, user_prompt):
        return self.generate_poem(user_prompt=user_prompt)
    
    def handle_request_stream(self, user_prompt):
        return self.generate_poem_stream(user_prompt=user_prompt)
