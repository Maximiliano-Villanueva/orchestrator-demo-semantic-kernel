import os
from typing import List

import semantic_kernel as sk
from utils.input_model import Question
from utils.custom_kernel import CustomKernel
from plugins.ServiceDesk.ServiceDesk import ServiceDesk
from semantic_kernel.planners import SequentialPlanner, StepwisePlanner
from semantic_kernel.planners.plan import Plan
import utils.sk_utils as sk_utils
from semantic_kernel.connectors.ai.open_ai.services.open_ai_chat_completion import OpenAIChatCompletion

def get_dummy_input() -> List[Question]:
    json_data = {
        "user_id": 7,
        "message_id": 7,
        "chat_id": 4,
        "domain_id": 0,
        "question": "lista las incidencias wifi",
        "plugins": [{
            "name": "ServiceDesk",
            "url": "http://localhost:9001/query",
            "configuration":{
                "url": "https://cosuitg.sothis.tech/api/v3",
                "token": "67325F3F-A481-44B7-8AEA-C69AF3337882"
            }
        }]
    }

    # Create an instance of the Question model using the JSON data
    questions = [Question(**json_data)]
    
    json_data["question"] = "lista todas las facturas del usuario con id 5"
    questions.append(Question(**json_data))

    json_data["question"] = "Actualiza la siguiente factura: {id=1, test=True, user_id=5}"
    questions.append(Question(**json_data))

    json_data["question"] = "General question"
    questions.append(Question(**json_data))

    json_data["question"] = "Tell me some facts about the most populated city in the world."
    questions.append(Question(**json_data))

    return [questions[-1]]

async def main():
    
    # Initialize the kernel
    kernel = sk_utils.get_kernel_router()

    # Import plugins
    plugins = sk_utils.load_plugins(kernel=kernel)

    planner = StepwisePlanner(kernel=kernel)# SequentialPlanner(kernel, service_id="planner")

    questions = get_dummy_input()

    for question in questions:
        # Create a plan
        # plan: Plan = await planner.create_plan(question.question)
        plan: Plan = planner.create_plan(question.question)

        # if len(plan.steps) == 0:
        #     new_step = Plan(
        #         name=step.name,
        #         plugin_name=step.plugin_name,
        #         description=step.description,
        #         next_step_index=0,
        #         state=KernelArguments(),
        #         parameters=KernelArguments(),
        #         outputs=[],
        #         steps=[],
        #     )
        # Modify the request parameters to match the correct ones
        for step in plan.steps:
            if 'question' in step._parameters:
                step._parameters["question"] = question
            if 'request_body' in step._parameters:
                step._parameters["request_body"] = question.json()
            if 'headers' in step._parameters:
                step._parameters["headers"] = {"Authorization": "Bearer xxxx"}

        # plan.steps[0]._parameters["question"] = question

        # Execute the plan
        result = await plan.invoke(kernel)
        print("-------------------------------\n\n")
        print(f"Question: {question.question}")
        print("Plan results:")
        print(result)
        print("-------------------------------\n\n")

# Run the main function
if __name__ == "__main__":
    import asyncio

    asyncio.run(main())