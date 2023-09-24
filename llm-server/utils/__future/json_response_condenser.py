import os
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from utils.get_llm import get_llm

from typing import Any
from routes.workflow.extractors.extract_json import extract_json_payload
from custom_types.t_json import JsonData

openai_api_key = os.getenv("OPENAI_API_KEY")
llm = get_llm()


def condense_api_response(context: str) -> Any:
    _DEFAULT_TEMPLATE = (
        """User: The context is: {context}. \nAgent: The condensed output is:"""
    )

    PROMPT = PromptTemplate(
        input_variables=[
            "context",
        ],
        template=_DEFAULT_TEMPLATE,
    )

    PROMPT.format(
        context=context,
    )

    chain = LLMChain(
        llm=llm,
        prompt=PROMPT,
        # memory=memory,
        verbose=True,
    )
    json_string = chain.run({"context": context})

    response = extract_json_payload(json_string)

    return response
