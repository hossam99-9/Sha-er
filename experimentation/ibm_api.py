from ibm_watsonx_ai import Credentials
from ibm_watsonx_ai.foundation_models import Model
from ibm_watsonx_ai.metanames import GenTextParamsMetaNames as GenParams
from ibm_watsonx_ai.foundation_models.utils.enums import ModelTypes, DecodingMethods

# To display example params enter
GenParams().get_example_values()

generate_params = {
    GenParams.MAX_NEW_TOKENS: 1000,
    GenParams.DECODING_METHOD: "greedy", 
    GenParams.TEMPERATURE: 0.7,
}

model = Model(
    model_id="sdaia/allam-1-13b-instruct",
    params=generate_params,
    credentials=Credentials(
        api_key = "a2F0DVBnfePotsn-P7K5iIAoHOTUC3-SyS4G2YW5CUFK",
        url = "https://eu-de.ml.cloud.ibm.com"),
    project_id="85b95f9c-2602-4bbe-85cf-abae5a6bb091"
    )

q = """
[INST] <<SYS>>

You are a helpful assistent, that only comunicates using JSON files.
The expected output from you has to be: 
    {
        "function": {function_name},
        "args": [],
    }
The INST block will always be a json string:
    {
        "prompt": {the user request}
    }
Here are the functions available to you:
    function_name=get_local_weather_update
    args=[{country}, {state}]
    function_name=get_local_time
    args=[{country}, {state}]
    function_name=get_location
    args=[{country}, {state}]


<</SYS>> [/INST]
[INST] 
{
    "prompt": "what is the time in California right now?"
}
[/INST]
    """
generated_response = model.generate(prompt=q)

print(generated_response['results'][0]['generated_text'])