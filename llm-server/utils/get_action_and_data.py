from langchain.chat_models import ChatOpenAI
from routes.workflow.extractors.extract_json import extract_json_payload
from typing import NamedTuple
from langchain import PromptTemplate, FewShotPromptTemplate
from utils.get_llm import get_llm
from langchain.llms import OpenAI
import os

openai_api_key = os.environ["OPENAI_API_KEY"]


class ActionData(NamedTuple):
    predicate: str
    data: str


llm = get_llm()


# Few shot prompt example
def get_action_and_data(user_requirement: str) -> ActionData:
    example = {
        "user_requirement": "Book a flight from San Francisco to New York on November 15th, roundtrip, 2 passengers, economy class",
        "response": """{{
            "predicate": "Book a flight",
            "data": "origin:san francisco, destination:new york, date:november 15, trip_type:roundtrip, num_passengers:2, class:economy"
        }}""",
    }

    template = """
        user_requirement: {user_requirement}
        response: {response}
    """

    prompt = PromptTemplate(
        input_variables=["user_requirement", "response"], template=template
    )

    few_shot_prompt = FewShotPromptTemplate(
        examples=[example],
        example_prompt=prompt,
        prefix="Extract the predicate and data from the user_requirement and return a valid json",
        suffix="user_requirement: {user_requirement}\nresponse:",
        input_variables=["user_requirement"],
        example_separator=" ",
    )

    _t = llm(few_shot_prompt.format(user_requirement=user_requirement))

    response = extract_json_payload(_t)

    if not isinstance(response, dict):
        raise ValueError("Expected response to be a dictionary")

    return ActionData(predicate=response["predicate"], data=response["data"])
