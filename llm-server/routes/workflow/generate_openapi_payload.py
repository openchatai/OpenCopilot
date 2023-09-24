import re
import os
import json
from langchain.tools.json.tool import JsonSpec
from utils.get_llm import get_llm
from dotenv import load_dotenv
from routes.workflow.load_openapi_spec import load_openapi_spec
from routes.workflow.extractors.extract_body import extractBodyFromSchema
from routes.workflow.extractors.extract_param import extractParamsFromSchema
from routes.workflow.extractors.hydrate_params import (
    hydrateParams,
    replace_ref_with_value,
)
from custom_types.t_json import JsonData
from custom_types.swagger import ApiOperation
from typing import Dict, Any, Optional, Union, Tuple
from .extractors.example_generator import generate_example_from_schema
from routes.workflow.extractors.user_confirmation_form import (
    generate_user_confirmation_form,
    generate_additional_data_msg,
    UserConfirmationForm,
)

load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")
llm = get_llm()


from typing import Dict, Any, Optional, Union, List


def get_api_operation_by_id(
    json_spec: Any, op_id: str
) -> Tuple[ApiOperation, str, str]:
    """
    Get an API operation by its operationId from a OpenAPI/Swagger specification.

    Args:
        json_spec: The OpenAPI/Swagger specification as a pydantic model.
        op_id: The operationId to search for.

    Returns:
        A tuple containing the ApiOperation definition, HTTP method, and path
        for the matching operation.

    Raises:
        ValueError: If no operation with the given op_id is found.
    """
    paths: Dict[str, List[ApiOperation]] = json_spec.dict_.get("paths", {})

    for path, methods in paths.items():
        if isinstance(methods, dict):
            for method, operation in methods.items():
                # Check if 'operation' is a dictionary
                if isinstance(operation, dict):
                    operation_id: Union[str, None] = operation.get("operationId")

                    if operation_id == op_id:
                        return operation, method, path

                else:
                    # Handle invalid operation
                    pass

    raise ValueError(f"Failed to find operation with id {op_id} in spec {json_spec}")


def resolve_refs(input_dict: JsonData, json_spec: Dict[str, Any]) -> Any:
    """
    Recursively resolves JSON reference ($ref) fields in a dictionary/list structure.

    Args:
        input_dict: The dictionary or list to resolve references in.
        json_spec: The full JSON specification containing reference definitions.

    Returns:
        input_dict with any $ref fields resolved to their referenced value.

    """
    # Check if the input_dict is a dictionary and contains a '$ref' key
    if isinstance(input_dict, dict) and "$ref" in input_dict:
        ref_value = input_dict["$ref"]
        paths = ref_value.split("/")[1:3]
        if paths[0] in json_spec and paths[1] in json_spec[paths[0]]:
            return json_spec[paths[0]][paths[1]]

    # Recursively process nested dictionaries and lists
    if isinstance(input_dict, dict):
        for key, value in input_dict.items():
            input_dict[key] = resolve_refs(value, json_spec)
    elif isinstance(input_dict, list):
        for i, item in enumerate(input_dict):
            input_dict[i] = resolve_refs(item, json_spec)

    return input_dict


def resolve_request_body_schema_reference(
    method: str, api_operation: ApiOperation, json_spec: Any
) -> Any:
    """
    Resolves any JSON schema $ref pointers in the requestBody
    of the given API operation against the given API spec.

    Args:
        request_method: The HTTP method of the API operation

        api_operation: A dictionary containing a snippet of the API specification
            in OpenAPI/Swagger format, describing a single operation of the API.
            For example, this could be the schema for the request body of the
            "addPet" operation.

        api_spec: The full API specification dictionary containing
            the complete OpenAPI/Swagger schema.

    Returns:
        The updated api_operation dictionary with any JSON reference pointers
        resolved against the api_spec.
    """
    content_type = "application/json"
    requestBody = api_operation.get("requestBody")

    # Check if requestBody is None (i.e., it doesn't exist)
    if requestBody is None:
        return api_operation

    if not isinstance(requestBody, dict):
        return api_operation

    content_types = requestBody.get("content", {})

    # Check if the specified content type exists in the requestBody
    if content_type in content_types:
        content_type_schema = content_types[content_type].get("schema")

        # Check if the content type schema is a reference
        if content_type_schema and "$ref" in content_type_schema:
            ref_path = content_type_schema["$ref"].split("/")[1:]

            # Navigate through the JSON spec using the reference path
            schema_node = json_spec.dict_
            for path_element in ref_path:
                schema_node = schema_node.get(path_element, {})

            # Update the content type schema with the resolved schema
            content_types[content_type]["schema"] = schema_node

    return api_operation


def extract_json_payload(input_string: str) -> Optional[Any]:
    # Remove all whitespace characters
    input_string = re.sub(r"\s", "", input_string)

    match = re.findall(r"{.+[:,].+}|\[.+[,:].+\]", input_string)
    return json.loads(match[0]) if match else None


def generate_openapi_payload(
    spec_source: str,
    text: str,
    _operation_id: str,
    prev_api_response: str,
    example: Any,
) -> Union[Dict[str, Any], UserConfirmationForm]:
    """Generates an API request payload based on an OpenAPI spec.
    Args:
        spec_source (str): The path or URL to the OpenAPI spec file.
        text (str): The original user text query.
        _operation_id (str): The ID of the OpenAPI operation to target.
        prev_api_response (str): The response from a previous API request, if any.

    Returns:
        Dict[str, Any]: The generated request payload, containing keys for
            "body", "params", "path", and "request_type".

    This function parses the given OpenAPI spec and constructs a request payload
    for the operation matching the provided _operation_id. It extracts parameters
    from the user text and previous API response to populate the payload. The
    payload can then be used to call the target API.
    """
    params: Optional[JsonData] = {}
    body: Optional[Dict[str, Any]] = {}
    spec_dict: Dict[str, Any] = load_openapi_spec(spec_source)
    # extracted_feature = extract_feature_from_user_query(text)

    # Continue with the rest of the code
    json_spec: JsonSpec = JsonSpec(dict_=spec_dict, max_value_length=4000)

    api_operation: ApiOperation
    method: str
    path: str
    api_operation, method, path = get_api_operation_by_id(json_spec, _operation_id)

    isolated_request: Dict[str, Any] = resolve_request_body_schema_reference(
        method, api_operation, json_spec
    )

    if isolated_request and "parameters" in isolated_request:
        isolated_request["parameters"] = hydrateParams(
            json_spec.dict_, isolated_request["parameters"]
        )
        params = extractParamsFromSchema(
            isolated_request["parameters"], text, prev_api_response
        )

    if (
        not example
        and "requestBody" in api_operation
        and "content" in api_operation["requestBody"]
        and "application/json" in api_operation["requestBody"]["content"]
        and "schema" in api_operation["requestBody"]["content"]["application/json"]
        and "properties"
        in api_operation["requestBody"]["content"]["application/json"]["schema"]
    ):
        body_schema: Dict[str, Any] = api_operation["requestBody"]["content"][
            "application/json"
        ]["schema"]["properties"]

        # replace $ref recursively
        replace_ref_with_value(body_schema, json_spec.dict_)
        example = generate_example_from_schema(api_operation)

        # checks if llm needs more info before executing the flow, this will short circuit the flow
        # and save the state in the database + it will send this back to the frontend
        # short circuit
        if os.getenv("COPILOT_MODE") == "interactive":
            user_confirmation_form = generate_user_confirmation_form(
                body_schema=body_schema,  # swagger schema
                text=text,  # user initial input
                prev_api_response=prev_api_response,  # Api log / prev api response
                example=example,  # example json payload, can be used to prefill form
            )
            if user_confirmation_form.form_data is not None:
                return user_confirmation_form
        elif os.getenv("COPILOT_MODE") == "text":
            response = generate_additional_data_msg(
                body_schema, text, prev_api_response, example
            )
            if "ALL_GOOD" not in response.upper():
                return {"confirmation_required": True, "msg": response}

        body = extractBodyFromSchema(body_schema, text, prev_api_response, example)
    else:
        print("Some key is not present in the requestBody dictionary.")

    response = {
        "body": body or example,
        "params": params,
        "path": path,
        "request_type": method,
    }

    return response
