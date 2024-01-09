from typing import Literal, Dict


class StoreOptions:
    ALLOWED_NAMESPACES = Literal["knowledgebase", "apis", "actions", "flows", "chat_history"]

    def __init__(self, namespace: ALLOWED_NAMESPACES, metadata: Dict[str, str] = {}):
        self.namespace = namespace
        self.metadata = metadata
