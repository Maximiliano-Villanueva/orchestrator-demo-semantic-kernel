from pydantic import BaseModel
from typing import Any, Dict, List, Optional

class Plugin(BaseModel):
    name: str
    url: str
    configuration: Dict[str, Any]

class Question(BaseModel):
    user_id: int
    message_id: int  # message storing answer-response tuples in vekai
    chat_id: int
    domain_id: int
    question: str
    plugins: Optional[List[
        Plugin
    ]] = None