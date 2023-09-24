import os
from langchain.prompts import PromptTemplate
from utils.get_llm import get_llm

from typing import Any, Optional
from routes.workflow.extractors.extract_json import extract_json_payload
from custom_types.t_json import JsonData
from langchain.chat_models import ChatOpenAI

from langchain.schema import HumanMessage, SystemMessage
import json


openai_api_key = os.getenv("OPENAI_API_KEY")
llm = get_llm()

chat = ChatOpenAI()


class UserConfirmationForm(object):
    """Response when form data is missing required info"""

    def __init__(
        self, form_data: Any, json_schema: Any, prev_api_response: Any, example: Any
    ):
        """Initialize with form data and schema"""
        super().__init__()
        self.form_data = form_data
        self.json_schema = json_schema
        self.prev_api_response = prev_api_response
        self.example = example

    def toJSON(self) -> Any:
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)


class ApiFlowState:
    def __init__(
        self,
        flow_index: int,
        step_index: int,
        form: UserConfirmationForm,
        msg,
        example: Any,
    ) -> None:
        self.flow_index = flow_index
        self.step_index = step_index
        self.form = form
        self.msg = msg
        self.example = example
        # self.uuid = uuid4()

    def __str__(self) -> str:
        return f"ApiFlowState(flow_index={self.flow_index}, step_index={self.step_index}, form={self.form}, msg={self.msg})"

    def toJSON(self) -> Any:
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)


def generate_user_confirmation_form(
    body_schema: JsonData, text: str, prev_api_response: str, example: str
) -> UserConfirmationForm:
    """Generate a JSON payload for React JSONForms by asking an AI assistant for missing data.

    Args:
        body_schema (JsonData): JSON Schema defining expected fields
        text (str): User input text
        prev_api_response (str): Previous API responses
        example (str): Example JSON payload

    Returns:
        Any: Generated JSON payload

    This function chats with an AI assistant to get missing data needed
    to generate a JSON payload that conforms to the provided schema.
    The returned JSON is intended to be used by React JSONForms to
    dynamically generate web forms.

    It provides the assistant with the schema, user text, API logs,
    and example JSON. The assistant's response is parsed to extract
    the generated JSON data.
    """

    messages = [
        SystemMessage(
            content="""You are an AI assistant that can generate new JSON data based on a provided example JSON, user input, and API logs. To assist in generating valid JSON, you are also given a JSON schema that describes the expected fields and data types. Your goal is to take the provided inputs and use them to create new JSON data that conforms to the schema."""
        ),
        HumanMessage(
            content=f"Here is the required information for you - API schema: {body_schema}, Api logs: {prev_api_response}, User input: {text}, Example json: {example};"
        ),
    ]

    aiResponse = chat(messages)
    response = UserConfirmationForm(
        form_data=extract_json_payload(aiResponse.content),
        json_schema={"properties": body_schema},
        prev_api_response=prev_api_response,
        example=example,
    )

    return response


def generate_additional_data_msg(
    body_schema: JsonData, text: str, prev_api_response: str, example: str
) -> str:
    """Generate a JSON payload for React JSONForms by asking an AI assistant for missing data.

    Args:
        body_schema (JsonData): JSON Schema defining expected fields
        text (str): User input text
        prev_api_response (str): Previous API responses
        example (str): Example JSON payload

    Returns:
        Any: Generated JSON payload

    This function chats with an AI assistant to get missing data needed
    to generate a JSON payload that conforms to the provided schema.
    The returned JSON is intended to be used by React JSONForms to
    dynamically generate web forms.

    It provides the assistant with the schema, user text, API logs,
    and example JSON. The assistant's response is parsed to extract
    the generated JSON data.
    """

    messages = [
        SystemMessage(
            content="""As an AI assistant, your role is to analyze user input in conjunction with API logs and the Swagger schema. Your primary goal is to detect any fields that are marked as 'required' in the API request body schema. If there is missing information, attempt to make an informed guess when possible; otherwise, prompt the user to provide the necessary details. For example, you can say, 'I'll need some additional information, such as ....' If the user offers information that is not defined in the schema, please disregard it. Once you have assembled the correct payload, respond with 'ALL_GOOD' in your response."""
        ),
        HumanMessage(
            content=f"""Here is the required information 
            Swagger schema ({body_schema}), 
            API logs ({prev_api_response}), 
            and user input ({text})"""
        ),
    ]

    aiResponse = chat(messages)

    return aiResponse.content
