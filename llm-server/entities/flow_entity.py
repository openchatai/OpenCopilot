import uuid
from typing import List, Optional

from pydantic import BaseModel

from entities.action_entity import ActionDTO


class Block(BaseModel):
    id: str = str(uuid.uuid4())
    actions: List[ActionDTO]
    name: str
    next_on_fail: Optional[str] = None
    next_on_success: Optional[str] = None
    order: int = 0

    def to_dict(self):
        # Convert the entire Block to a dictionary,
        return self.dict()


class Variable(BaseModel):
    name: str
    value: str

    def to_dict(self):
        # Convert the entire Variable to a dictionary,
        return self.dict()


class FlowDTO(BaseModel):
    blocks: List[Block]
    bot_id: str
    id: str
    name: str
    description: str
    variables: List[Variable]

    def to_dict(self):
        # Convert the entire FlowDTO to a dictionary,
        # including nested ActionDTO objects within each Block
        return self.dict()


class PartialFlowDTO(BaseModel):
    bot_id: str
    id: str