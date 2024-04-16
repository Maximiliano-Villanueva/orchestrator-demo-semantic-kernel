# Standard imports
import regex
import json

from typing import Any, Annotated, Dict

# Third party
import semantic_kernel as sk
from semantic_kernel import Kernel
from semantic_kernel.functions.kernel_arguments import KernelArguments

from semantic_kernel.planners.basic_planner import (
    BasicPlanner, 
    Plan
)

# Internal imports
from request_utils.logger import MethodObservability
from utils.input_model import Question
from utils import custom_logs

logger = custom_logs.getLogger(__name__)


class CustomBasicPlanner(BasicPlanner, metaclass=MethodObservability):

    def update_function_args(self, kernel: Kernel, func_name: Annotated[str, "name of the function"],
                             func_args: Annotated[Dict[str, str], "arguments for function generated by planner"],
                             **kwargs: Any) -> Dict[str, str]:
         
         module_name_func = func_name.split(".")
         if kernel.plugins.plugins[module_name_func[0]]:
            for parameter in kernel.plugins.plugins[module_name_func[0]].functions[module_name_func[1]].parameters:
                 for update_parameter, update_parameter_value in kwargs.items():
                    if parameter.name == update_parameter:
                        if update_parameter in func_args:
                            original_question = func_args[update_parameter]
                            logger.debug(f"Replaced parameter {update_parameter} with original value: {str(original_question)} with new value: {update_parameter_value}")
                        func_args[update_parameter] = update_parameter_value
         
         return func_args
    
    async def update_next_question(self, original_input: Annotated[str, "Original input from user"],
                             output_previous_function: Annotated[str, "output from previous functions"],
                             kernel: Kernel) -> Annotated[str, "List of incidences"]:
        """
        Update the question of the next step in the plan based on the output of the last invoked function
        """
        question_update_question = kernel.func("question_updater", "question_updater")
        arguments = KernelArguments(question=original_input, previous_output=output_previous_function)
        logger.info(f"parameters update_next_question: {original_input} ---- {output_previous_function}")
        return await question_update_question.invoke(kernel, arguments)


         
    async def execute_plan(self, plan: Plan, kernel: Kernel, question: Question, headers) -> str:
        """
        Given a plan, execute each of the functions within the plan
        from start to finish and output the result.
        """

        # Filter out good JSON from the result in case additional text is present
        json_regex = r"\{(?:[^{}]|(?R))*\}"
        generated_plan_string = regex.search(json_regex, str(plan.generated_plan.value)).group()

        # TODO: there is some silly escape chars affecting the result of plan.generated_plan.value
        # There should be \n only but they are showing up as \\n
        encoded_bytes = generated_plan_string.encode("utf-8")
        decoded_string = encoded_bytes.decode("unicode_escape")

        generated_plan = json.loads(decoded_string)

        arguments = KernelArguments(input=generated_plan["input"])
        subtasks = generated_plan["subtasks"]
        output_track = []
        for subtask in subtasks:
            
            plugin_name, function_name = subtask["function"].split(".")
            kernel_function = kernel.func(plugin_name, function_name)
            
            # Get the arguments dictionary for the function
            subtask["args"] = self.update_function_args(kernel, subtask["function"], subtask["args"] if "args" in subtask else {}, question=question, headers=headers)
            args = subtask.get("args", None)

            if args:
                for key, value in args.items():
                    arguments[key] = value
                if "question" in arguments:
                    # When the input of a function is of type question check if the question requires updates from previous outputs.
                    # This is required for questions that need to use multiple plugins to be answered,
                    last_output = output_track[-1] if len(output_track) > 0 else ""
                    if last_output:
                        new_question = await self.update_next_question(original_input=question.question, output_previous_function=str(last_output), kernel=kernel)
                        logger.info(f"new question: {new_question}")
                        question.question=str(new_question)
                    
                output = await kernel_function.invoke(kernel, arguments)

            else:
                output = await kernel_function.invoke(kernel, arguments)

            # Override the input context variable with the output of the function
            arguments["input"] = str(output)
            output_track.append(output)

        # At the very end, return the output of the last function
        return str(output)