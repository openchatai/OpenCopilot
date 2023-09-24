from opencopilot_types.workflow_type import ApiFlowState


class Headers:
    def __init__(self) -> None:
        self.data: dict[str, str] = {}


class WorkflowData:
    def __init__(
        self,
        text: str,
        swagger_url: str,
        headers: Headers,
        server_base_url: str,
        flow_state: ApiFlowState,
    ) -> None:
        self.text = text
        self.swagger_url = swagger_url
        self.headers = headers
        self.server_base_url = server_base_url
        self.flow_state = flow_state
