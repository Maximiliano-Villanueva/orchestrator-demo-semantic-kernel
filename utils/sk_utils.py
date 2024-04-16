# Standard
from typing import Annotated, Dict, List

# Third party
import semantic_kernel as sk

from semantic_kernel.connectors.ai.open_ai.services.open_ai_chat_completion import OpenAIChatCompletion
from semantic_kernel.functions.kernel_plugin import KernelPlugin
from semantic_kernel.prompt_template.input_variable import InputVariable

# Internal
from utils.input_model import Question
from utils.custom_kernel import CustomKernel
from plugins.ServiceDesk.ServiceDesk import ServiceDesk
from plugins.Invoices_db.InvoicesDB import InvoicesDB
from plugins.Rag.Rag import Rag
from plugins.CitiesDB.Cities import CitiesDB

def get_kernel_router() -> Annotated[sk.Kernel, "Kernel instance"]:
    # Initialize the kernel
    kernel = CustomKernel()
    # Add a text or chat completion service using either:
    # kernel.add_text_completion_service()
    # kernel.add_chat_service()

    api_key, org_id = sk.openai_settings_from_dot_env()
    
    kernel.add_service(
        OpenAIChatCompletion(
            service_id="planner",
            ai_model_id="gpt-4",
            api_key=api_key,
        )
    )

    return kernel

def _load_hidden_plugins(kernel: Annotated[sk.Kernel, "kernel instance from semantic kernel"]) -> Annotated[List[KernelPlugin], "Hidden plugins loaded"]:
    """
    Load plugins that are meant to be used internaly
    """
    prompt = """
        I have the following Question:
        {{$question}}.

        And the following context:
        {{$previous_output}}

        I need you to return the same question updated based on the context provided.
        If the context is not useful return the same input question.
        Use only the information provided and nothing more.
        Do not include anything but the question generated in your response.

    """

    prompt_template_config = sk.PromptTemplateConfig(
        template=prompt,
        name="question_update",
        template_format="semantic-kernel",
        input_variables=[
            InputVariable(name="question", description="Question to update", is_required=True),
            InputVariable(name="previous_output", description="Output from last function", is_required=True)
        ],
    )

    question_updater = kernel.create_function_from_prompt(
        function_name="question_updater",
        plugin_name="question_updater",
        prompt_template_config=prompt_template_config,
    )

    kernel.add_function_invoked_handler

    return [question_updater]


def load_plugins(kernel: Annotated[sk.Kernel, "kernel instance from semantic kernel"]) -> Annotated[Dict[str, List[KernelPlugin]], "List of loaded plugins in KernelPlugin format"]:
    # Import the native functions
    servicedesk_plugin = kernel.import_plugin_from_object(ServiceDesk(),
                                                          plugin_name="sevicedesk",
                                                          plugin_description="Provide information about incidences through the ServiceDesk ticketing service")

    invoices_plugin = kernel.import_plugin_from_object(InvoicesDB(),
                                                       plugin_name="invoices",
                                                       plugin_description="Retrieve information about invoices and the users related to them. Execute write operations on invoices like update, upsert on inserts.")

    rag_plugin = kernel.import_plugin_from_object(Rag(),
                                                        plugin_name="rag",
                                                        plugin_description="Default plugin to call when no other plugin can be used. Any information not provided by other functions are meant to be retrieved from here.")

    cities_plugin = kernel.import_plugin_from_object(CitiesDB(),
                                                        plugin_name="cities_db",
                                                        plugin_description="Plugin useful to retrieve cities based on some filters.")
    
    hidden_plugins = _load_hidden_plugins(kernel=kernel)
    
    loaded_plugins = [servicedesk_plugin, invoices_plugin, rag_plugin, cities_plugin]

    return {"visible": loaded_plugins, "hidden": hidden_plugins}

async def load_plugins_async(kernel: Annotated[sk.Kernel, "kernel instance from semantic kernel"]) -> Annotated[List[KernelPlugin], "List of loaded plugins in KernelPlugin format"]:
    # Import the native functions
    # servicedesk_plugin = kernel.import_plugin_from_object(ServiceDesk(),
    #                                                       plugin_name="sevicedesk",
    #                                                       plugin_description="Provide information about incidences through the ServiceDesk ticketing service")

    invoices_plugin = kernel.import_plugin_from_object(InvoicesDB(),
                                                       plugin_name="invoices",
                                                       plugin_description="Retrieve information about invoices and the users related to them. Execute write operations on invoices like update, upsert on inserts.")
    
    chatgpt_plugin = await kernel.import_plugin_from_openai(
        plugin_url= "http://localhost:9001/.well-known/ai-plugin.json",
        plugin_name="chatgpt_servicedesk",
        plugin_description = "Get and list incidences using the ticketing service ServiceDesk"
    )
    return [invoices_plugin, chatgpt_plugin]