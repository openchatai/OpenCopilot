from bson import ObjectId
from utils.db import Database
from utils.vector_db.get_vector_store import get_vector_store
from utils.vector_db.store_options import StoreOptions
from routes.workflow.generate_openapi_payload import generate_openapi_payload
from opencopilot_types.workflow_type import RunApiOperationsType
from utils.make_api_call import make_api_request
from routes.workflow.extractors.user_confirmation_form import (
    UserConfirmationForm,
    ApiFlowState,
)
from routes.workflow.typings.run_workflow_input import WorkflowData
from utils.get_action_and_data import get_action_and_data
import json

from typing import Any, Dict, Union, Optional

db_instance = Database()
mongo = db_instance.get_db()


def get_api__base_url(
    api_payload: Dict[str, Union[str, None]], server_base_url: Optional[str]
) -> str:
    if "path" in api_payload:
        path = api_payload["path"]

        # Check if path is a valid URL
        if path and path.startswith(("http://", "https://")):
            return path
        elif server_base_url and server_base_url.startswith(("http://", "https://")):
            # Append server_base_url to path
            return f"{server_base_url}{path}"
        else:
            raise ValueError("Invalid server_base_url")
    else:
        raise ValueError("Missing path parameter")


def run_workflow(data: WorkflowData) -> Any:
    text = data.text
    swagger_src = data.swagger_url
    headers = data.headers
    # This will come from request payload later on when implementing multi-tenancy
    namespace = "workflows"
    server_base_url = data.server_base_url

    # getting action out of user input, because workflow accuracy goes for a toss as user adds more information to the input. By extracting action, we make sure that no matter the size of the input we always find the correct workflow

    _ad = get_action_and_data(text)
    predicate = _ad.predicate
    _data = _ad.data

    vector_store = get_vector_store(StoreOptions(namespace))
    # documents = vector_store.similarity_search(text)

    (document, score) = vector_store.similarity_search_with_relevance_scores(predicate)[
        0
    ]

    if score > 0.88:
        first_document_id = (
            ObjectId(document.metadata["workflow_id"]) if document else None
        )
        record = mongo.workflows.find_one({"_id": first_document_id})
        result = run_openapi_operations(
            RunApiOperationsType(
                record, swagger_src, text, headers, server_base_url, data.flow_state
            )
        )
        return result, 200, {"Content-Type": "application/json"}
    else:
        # call openapi spec
        raise Exception("Workflow not defined for this request, try using an agent")


def save_state_to_db(response: ApiFlowState) -> None:
    mongo.paused_ops.insert_one(
        {
            "flow_index": response.flow_index,
            "step_index": response.step_index,
            "form": {
                "form_data": response.form.form_data,
                "json_schema": response.form.json_schema,
                "prev_api_response": response.form.prev_api_response,
                "example": response.form.example,
            },
        }
    )


def run_openapi_operations(
    input: RunApiOperationsType,
) -> Any:
    i = 0
    j = 0
    record_info = {"Workflow Name": input.record.get("name")}

    # resume a paused operation if exists
    if input.flow_state and hasattr(input.flow_state, "flow_index"):
        # start from the paused state
        i = input.flow_state.flow_index
        j = input.flow_state.step_index

    flows = input.record.get("flows", [])
    for flow_index, flow in enumerate(flows[i:]):
        prev_api_response = ""
        for step_index, step in enumerate(flow.get("steps")[j:]):
            operation_id = step.get("open_api_operation_id")
            api_payload = generate_openapi_payload(
                input.swagger_src,
                input.text,
                operation_id,
                prev_api_response,
                input.flow_state.example,
            )

            if isinstance(api_payload, UserConfirmationForm):
                response = ApiFlowState(
                    step_index=step_index,
                    flow_index=flow_index,
                    form=api_payload,
                    msg=None,
                    example=None,
                )

                # save_state_to_db(response)
                return json.loads(response.toJSON())

            elif api_payload.get("confirmation_required") == True:
                response = ApiFlowState(
                    step_index=step_index,
                    flow_index=flow_index,
                    msg=f"{api_payload['msg']}",
                    form=UserConfirmationForm(None, None, None, None),
                    example=None,
                )

                return json.loads(response.toJSON())

            api_payload["path"] = get_api__base_url(api_payload, input.server_base_url)
            api_response = make_api_request(
                request_type=api_payload["request_type"],
                url=api_payload["path"],
                body=api_payload["body"],
                params=api_payload["params"],
                headers=input.headers,
            )
            record_info[operation_id] = json.loads(api_response.text)
            prev_api_response = api_response.text

        prev_api_response = ""
        j = 0
        input.flow_state.example = None

    return json.dumps(record_info)
