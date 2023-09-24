import re

from routes.workflow.generate_openapi_payload import (
    load_openapi_spec,
)
from routes.workflow.typings.run_workflow_input import WorkflowData
from langchain.tools.json.tool import JsonSpec
from typing import List

from typing import Any, Dict, Optional
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from utils.get_llm import get_llm


# use spaCy or BERT for more accurate results
def hasMultipleIntents(user_input: str) -> bool:
    # Keywords for multiple questions
    question_keywords = [
        "and",
        "also",
        "in addition",
        "moreover",
        "furthermore",
        "besides",
        "additionally",
        "another question",
        "second question",
        "next, ask",
        "thirdly",
        "finally",
        "lastly",
    ]

    # Check for question keywords
    question_pattern = "|".join(re.escape(keyword) for keyword in question_keywords)
    question_matches = [
        match.group()
        for match in re.finditer(question_pattern, user_input, re.IGNORECASE)
    ]

    print(f"Found {question_matches} in the following input: {user_input}")
    return bool(question_matches)


# user_input = (
#     "I want to fetch data from API A and also, can you answer another question?"
# )
# result = hasMultipleIntents(user_input)
# print(json.dumps(result, indent=2))


def getSummaries(spec_source: str) -> str:
    """Get API endpoint summaries from an OpenAPI spec."""
    summaries: List[str] = []

    # Load the OpenAPI spec
    spec_dict: Optional[Dict[str, Any]] = load_openapi_spec(spec_source)
    if not spec_dict:
        raise ValueError("Unable to load OpenAPI spec")

    json_spec: JsonSpec = JsonSpec(dict_=spec_dict, max_value_length=4000)

    # Get the paths and iterate over them
    paths: Optional[Dict[str, Any]] = json_spec.dict_.get("paths")
    if not paths:
        raise ValueError("OpenAPI spec missing 'paths'")

    for path in paths:
        operation = paths[path]
        for field in operation:
            if "summary" in operation[field]:
                summaries.append(operation[field]["summary"])

    return summaries


def hasSingleIntent(spec_source: str, user_requirement: str) -> bool:
    summaries = getSummaries(spec_source)
    _DEFAULT_TEMPLATE = """
    User: Here is a list of API summaries:
    {summaries}

    Considering the user's request outlined below, is it possible to fulfill their requirement with just one of the API calls listed above? Please reply with either "YES" or "NO"

    User requirement: 
    {user_requirement}
    """
    llm = get_llm()
    PROMPT = PromptTemplate(
        input_variables=["summaries", "user_requirement"],
        template=_DEFAULT_TEMPLATE,
    )

    PROMPT.format(user_requirement=user_requirement, summaries="\n".join(summaries))

    chain = LLMChain(
        llm=llm,
        prompt=PROMPT,
        # memory=memory,
        verbose=True,
    )
    response = chain.run(
        {"summaries": "\n".join(summaries), "user_requirement": user_requirement}
    )

    print(f"Summary call response: {response}")

    if "yes" in response.lower():
        return True
    else:
        return False
