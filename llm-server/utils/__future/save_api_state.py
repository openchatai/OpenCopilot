from typing import Dict, Any
from pymongo.mongo_client import MongoClient
from bson.objectid import ObjectId


def save_api_state(
    workflow_id: str, step_id: int, user_id: str, workflow_data: Dict[str, Any]
) -> ObjectId:
    client = MongoClient("mongodb://localhost:27017/")
    db = client["apiflows"]
    collection = db["failed_flows"]

    operation_id = ObjectId()

    doc = {
        "operation_id": operation_id,
        "workflow_id": workflow_id,
        "step_id": step_id,
        "user_id": user_id,
        "workflow_data": workflow_data,
    }

    collection.insert_one(doc)

    return operation_id
