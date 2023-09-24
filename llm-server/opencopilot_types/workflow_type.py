from typing import TypedDict, List, Dict, Any, Optional
from routes.workflow.extractors.user_confirmation_form import ApiFlowState


class WorkflowStepType(TypedDict):
    stepId: str
    operation: str
    open_api_operation_id: str
    parameters: Dict[str, Any]


class WorkflowFlowType(TypedDict):
    name: str
    description: str
    requires_confirmation: bool
    steps: List[WorkflowStepType]
    on_success: List[Dict[str, Any]]
    on_failure: List[Dict[str, Any]]


class WorkflowDataType(TypedDict):
    opencopilot: str
    info: Dict[str, Any]
    flows: List[WorkflowFlowType]


class RunApiOperationsType:
    def __init__(
        self,
        record: Any,
        swagger_src: str,
        text: str,
        headers: Any,
        server_base_url: str,
        flow_state: ApiFlowState,
    ):
        self.record = record
        self.swagger_src = swagger_src
        self.text = text
        self.headers = headers
        self.server_base_url = server_base_url
        self.flow_state = flow_state

    def __str__(self) -> str:
        return f"ApiRequest(record={self.record}, swagger_src={self.swagger_src}, text={self.text}, headers={self.headers}, server_base_url={self.server_base_url}, api_payload={self.api_payload})"
