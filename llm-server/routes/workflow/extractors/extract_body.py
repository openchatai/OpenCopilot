import os
from langchain.schema import AIMessage, HumanMessage, SystemMessage
from langchain.chat_models import ChatOpenAI
from utils.get_llm import get_llm

from typing import Any, Optional
from routes.workflow.extractors.extract_json import extract_json_payload
from custom_types.t_json import JsonData
import importlib
import logging

openai_api_key = os.getenv("OPENAI_API_KEY")
llm = get_llm()


async def gen_body_from_schema(
    body_schema: str,
    text: str,
    prev_api_response: str,
    app: Optional[str],
    current_state: Optional[str],
) -> Any:
    chat = ChatOpenAI(
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        model="gpt-3.5-turbo-16k",
        temperature=0,
    )
    api_generation_prompt = None
    if app:
        module_name = f"integrations.custom_prompts.{app}"
        module = importlib.import_module(module_name)
        api_generation_prompt = getattr(module, "api_generation_prompt")

    messages = [
        SystemMessage(
            content="You are an intelligent machine learning model that can produce REST API's body in json format"
        ),
        HumanMessage(
            content="You will be given swagger schema, user input, data from previous api calls, and current state information stored in the current_state variable. You should use the field descriptions provided in the schema to generate the payload."
        ),
        HumanMessage(content="Swagger Schema: {}".format(body_schema)),
        HumanMessage(content="User input: {}".format(text)),
        HumanMessage(content="prev api responses: {}".format(prev_api_response)),
        HumanMessage(content="current_state: {}".format(current_state)),
        HumanMessage(
            content="Given the provided information, generate the appropriate minified JSON payload to use as body for the API request. If a user doesn't provide a required parameter, use sensible defaults for required params, and leave optional params."
        ),
    ]

    if api_generation_prompt is not None:
        messages.append(HumanMessage(content="{}".format(api_generation_prompt)))

    result = chat(messages)

    logging.info("[OpenCopilot] LLM Body Response: {}".format(result.content))

    d: Any = extract_json_payload(result.content)
    logging.info(
        "[OpenCopilot] Parsed the json payload: {}, context: {}".format(
            d, "gen_body_from_schema"
        )
    )

    return d
