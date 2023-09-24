import json
import os

from flask import Blueprint, request, jsonify
from routes.workflow.validate_json import validate_json
from bson import ObjectId, json_util
from copilot_exceptions.handle_exceptions_and_errors import handle_exceptions_and_errors
from utils.get_embeddings import get_embeddings
from opencopilot_types.workflow_type import WorkflowDataType
import warnings
from utils.db import Database
from utils.vector_db.init_vector_store import init_vector_store
from utils.vector_db.get_vector_store import get_vector_store
from utils.vector_db.store_options import StoreOptions
from langchain.docstore.document import Document
from routes.workflow.workflow_service import run_workflow
from typing import Any, cast
from routes.workflow.typings.run_workflow_input import WorkflowData

db_instance = Database()
mongo = db_instance.get_db()

workflow = Blueprint("workflow", __name__)


json_file_path = os.path.join(os.getcwd(), "routes", "workflow", "workflow_schema.json")
with open(json_file_path, "r") as workflow_schema_file:
    workflow_schema = json.load(workflow_schema_file)


@workflow.route("/<workflow_id>", methods=["GET"])
def get_workflow(workflow_id: str) -> Any:
    workflow = mongo.workflows.find_one({"_id": ObjectId(workflow_id)})
    if workflow:
        workflow = json_util.dumps(workflow)
        return workflow, 200, {"Content-Type": "application/json"}

    else:
        return jsonify({"message": "Workflow not found"}), 404


@workflow.route("/", methods=["POST"])
@validate_json(workflow_schema)
@handle_exceptions_and_errors
def create_workflow() -> Any:
    workflow_data = cast(WorkflowDataType, request.json)
    workflows = mongo.workflows
    workflow_id = workflows.insert_one(workflow_data).inserted_id

    namespace = "workflows"
    # Check if the namespace is generic
    if namespace == "workflows":
        warning_message = "Warning: The 'namespace' variable is set to the generic value 'workflows'. You should replace it with a specific value for your org / user / account."
        warnings.warn(warning_message, UserWarning)
    add_workflow_data_to_qdrant(namespace, workflow_id, workflow_data)

    return (
        jsonify({"message": "Workflow created", "workflow_id": str(workflow_id)}),
        201,
    )


@workflow.route("/<workflow_id>", methods=["PUT"])
@validate_json(workflow_schema)
@handle_exceptions_and_errors
def update_workflow(workflow_id: str) -> Any:
    workflow_data = cast(WorkflowDataType, request.json)
    mongo.workflows.update_one({"_id": ObjectId(workflow_id)}, {"$set": workflow_data})
    namespace = "workflows"
    vector_store = get_vector_store(StoreOptions(namespace))
    vector_store.delete(ids=[workflow_id])
    # Check if the namespace is generic
    if namespace == "workflows":
        warning_message = "Warning: The 'namespace' variable is set to the generic value 'workflows'. You should replace it with a specific value for your org / user / account."
        warnings.warn(warning_message, UserWarning)

    add_workflow_data_to_qdrant(namespace, workflow_id, workflow_data)

    return jsonify({"message": "Workflow updated"}), 200


@workflow.route("/<workflow_id>", methods=["DELETE"])
def delete_workflow(workflow_id: str) -> Any:
    mongo.workflows.delete_one({"_id": workflow_id})
    return jsonify({"message": "Workflow deleted"}), 200


@workflow.route("/run_workflow", methods=["POST"])
@handle_exceptions_and_errors
def run_workflow_controller() -> Any:
    data = request.get_json()
    result = run_workflow(
        WorkflowData(
            text=data.get("text"),
            swagger_url=data.get("swagger_url"),
            headers=data.get("headers", {}),
            server_base_url=data.get("server_base_url"),
            flow_state=data.get("flow_state"),
        )
    )
    return result


def add_workflow_data_to_qdrant(
    namespace: str, workflow_id: str, workflow_data: Any
) -> None:
    for flow in workflow_data["flows"]:
        docs = [
            Document(
                page_content=flow["description"],
                metadata={
                    "workflow_id": str(workflow_id),
                    "workflow_name": workflow_data.get("name"),
                },
            )
        ]
        embeddings = get_embeddings()
        init_vector_store(docs, embeddings, StoreOptions(namespace))
