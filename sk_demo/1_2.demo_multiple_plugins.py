import os
from typing import List

import semantic_kernel as sk
from utils.custom_planner import CustomBasicPlanner
from utils.input_model import Question
from semantic_kernel.planners import BasicPlanner

from semantic_kernel.planners.basic_planner import Plan
import utils.sk_utils as sk_utils


def get_dummy_input() -> List[Question]:
    json_data = {
        "user_id": 7,
        "message_id": 7,
        "chat_id": 4,
        "domain_id": 1,
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

    json_data["question"] = "What is Lyfe cycle analysis?"
    questions.append(Question(**json_data))

    json_data["question"] = "Tell me some facts about the most populated city in the world."
    questions.append(Question(**json_data))

    return [questions[-1]]

async def main():
    
    # Initialize the kernel
    kernel = sk_utils.get_kernel_router()

    # Import plugins
    plugins = sk_utils.load_plugins(kernel=kernel)

    planner = CustomBasicPlanner(service_id="planner")# BasicPlanner(service_id="planner")

    questions = get_dummy_input()

    with open(os.path.join("plugins", "prompts", "basic_planner.txt"), "r") as f:
        planner_prompt = f.read()


    for question in questions:
        # Create a plan
        # plan: Plan = await planner.create_plan(question.question)
        plan: Plan = await planner.create_plan(question.question, kernel=kernel, prompt=planner_prompt)

        # modify object passed 
        # Execute the plan
        result = await planner.execute_plan(plan, kernel, question)
        print("-------------------------------\n\n")
        print(f"Question: {question.question}")
        print("Plan results:")
        print(result)
        print("-------------------------------\n\n")

# Run the main function
if __name__ == "__main__":
    import asyncio

    asyncio.run(main())