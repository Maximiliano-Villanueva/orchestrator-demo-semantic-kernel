from typing import Any, Annotated, Dict, Union, Optional
from semantic_kernel.functions import kernel_function
from semantic_kernel.planners.basic_planner import Plan

from plugins.orchestrator_plugins import OrchestratorPlugin
from request_utils.service_request import Requester
from utils.input_model import Question, Plugin
from utils import custom_logs

logger = custom_logs.getLogger("ServiceDeskPlugin")


class ServiceDesk(OrchestratorPlugin):

    def __init__(self):
        pass
    
    @kernel_function(
        description="Get and list incidences using the ticketing service ServiceDesk",
        name="get_incidences"
    )
    
    def get_incidences(self, question: Union[Annotated[str, "List the incidences"], Annotated[Question, "List the incidences"]], headers: Annotated[Optional[Dict[str, str]], "Headers to send to request"] = dict()) -> Annotated[str, "List of incidences"]:
        if not isinstance(question, Question):
            raise Exception("No service desk plugin was specified")
        
        # question : Question

        # plugin_conf: Plugin = self.get_plugin_conf(question)
        # url = plugin_conf.url
        # headers = {}
        # logger.debug(f"requesting to{url}, with data: {question.model_dump_json()}")
        # result = Requester.post(url=url, data=question.model_dump_json(), headers=headers, is_json=False)
        logger.info(f"headers: {headers}")
        result = self.send_request_plugin(question=question, headers=headers)
        return str(result)
