import os
from typing import Dict, Any, cast

from langchain.schema import HumanMessage, SystemMessage

from integrations.custom_prompts.prompt_loader import load_prompts
from utils.chat_models import CHAT_MODELS
from utils.get_chat_model import get_chat_model
from utils.get_logger import CustomLogger

openai_api_key = os.getenv("OPENAI_API_KEY")
logger = CustomLogger(module_name=__name__)

chat = get_chat_model()


def convert_json_to_text(
        user_input: str,
        api_response: Dict[str, Any],
        api_request_data: Dict[str, Any],
        bot_id: str,
) -> str:
    chat = get_chat_model()

    api_summarizer_template = None
    system_message = SystemMessage(
        content="You are an ai assistant that can summarize api responses, include references and links if available"
    )
    prompt_templates = load_prompts(bot_id)
    api_summarizer_template = (
        prompt_templates.api_summarizer if prompt_templates else None
    )

    if api_summarizer_template is not None:
        system_message = SystemMessage(content=api_summarizer_template)

    messages = [
        system_message,
        HumanMessage(
            content="You'll receive user input and server responses obtained by making calls to various APIs. Your "
                    "task is to summarize the api response that is an answer to the user input. Try to be concise and "
                    "accurate, and also include references if present."
        ),
        HumanMessage(content=user_input),
        HumanMessage(
            content="Here is the response from the apis: {}".format(api_response)
        )
    ]

    result = chat(messages)
    logger.info(
        "Convert json to text",
        content=result.content,
        incident="convert_json_to_text",
        api_request_data=api_request_data,
    )

    return cast(str, result.content)