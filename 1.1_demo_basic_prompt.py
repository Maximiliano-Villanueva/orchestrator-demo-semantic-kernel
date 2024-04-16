import semantic_kernel as sk
from plugins.MathPlugin.Math import Math
from semantic_kernel.planners import SequentialPlanner, BasicPlanner

from semantic_kernel.connectors.ai.open_ai.services.open_ai_chat_completion import OpenAIChatCompletion
    
async def main():
    
    # Initialize the kernel
    kernel = sk.Kernel()
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

    # Import the native functions
    # math_plugin = kernel.import_plugin_from_object(Math(), plugin_name="MathPlugin")

    # serviceDesk plugin
    sservicedesk_plugin = kernel.import_plugin_from_prompt_directory(parent_directory="plugins", plugin_directory_name="ServiceDesk")

    # planner = SequentialPlanner(kernel, service_id="planner")
    planner = BasicPlanner(service_id="planner")

    ask = "If my investment of 2130.23 dollars increased by 23%, how much would I have after I spent $5 on a latte?"
    ask = "list all the wifi incidences"
    # Create a plan
    from semantic_kernel.planners.plan import Plan
    # plan: Plan = await planner.create_plan(ask)
    plan: Plan = await planner.create_plan(kernel=kernel, goal=ask)
    print(plan)
    # Execute the plan
    result = await plan.invoke(kernel)
    print("Plan results:")
    print(result)


# Run the main function
if __name__ == "__main__":
    import asyncio

    asyncio.run(main())