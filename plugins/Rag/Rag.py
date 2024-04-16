from typing import Annotated, Union, Optional, Dict
from semantic_kernel.functions import kernel_function

from utils.input_model import Question
from plugins.orchestrator_plugins import OrchestratorPlugin
from utils import custom_logs
from request_utils.service_request import Requester

logger = custom_logs.getLogger("ServiceDeskPlugin")


class Rag(OrchestratorPlugin):

    def __init__(self):
        pass

    @kernel_function(
        description="Default plugin to call when no other plugin can be used. Any information not provided by other functions are meant to be retrieved from here.",
        name="ask_rag"
    )
    
    def ask_rag(self, question: Union[Annotated[str, "User question"], Annotated[Question, "User Question"]],
                headers: Annotated[Optional[Dict[str, str]], "Headers to send to request"] = dict()) -> Annotated[str, "Response from request"]:
        data = question
        
        url = f"http://localhost:8000/domain"
        
        logger.info(f"entered rag url: {url} and headers: {headers}")
        result = Requester.post(url=url, data=question.model_dump_json(), headers=headers, is_json=False)
        return result.content
        # return f"requested rag with question: {data} It is the capital and largest city of the autonomous community of Catalonia"
