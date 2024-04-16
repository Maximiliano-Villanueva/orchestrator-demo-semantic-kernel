from typing import Annotated, Dict, List
from semantic_kernel.functions import kernel_function

from utils.input_model import Question


class CitiesDB:

    def __init__(self):
        pass

    @kernel_function(
        description="Get the cities based on locations (for example countries or continents), population, etc..",
        name="get_cities"
    )
    def get_cities(self, filter: Annotated[Dict[str, str], "filters in dict format with the information to filter. Here are some examples {'population': 'max(population)', 'continent': 'Europe'}. {'population': '>5000'}"]) -> Annotated[List[str], "List of cities"]:
        print(f"requesting cities with filter {filter}")
        return ['Barcelona']
