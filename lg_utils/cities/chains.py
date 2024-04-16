# Standard imports
import logging
from typing import Any, Dict, List

# Third party imports
import requests
from langchain.chains.base import Chain

# Setting up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class HttpRequestChain(Chain):
    """
    A LangChain-based tool to perform an HTTP request.
    """
    input_key: str = "question"  #: :meta private:
    output_key: str = "answer"  #: :meta private:
    description: str = "Get the cities based on locations (for example countries or continents), population, etc.."

    @property
    def input_keys(self) -> List[str]:
        """Expect input key.
        :meta private:
        """
        return [self.input_key]

    @property
    def output_keys(self) -> List[str]:
        """Expect output key.
        :meta private:
        """
        return [self.output_key]
    
    def _call(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes an HTTP request based on the input data provided.

        Args:
            input_data (Dict[str, Any]): A dictionary containing the keys 'url' and optionally 'params'
                                         for the URL parameters, and 'method' which should be either 'GET' or 'POST'.

        Returns:
            Dict[str, Any]: A dictionary with either the response data under the key 'data' or an error message.
        """
        try:
            url = input_data.get("url")
            params = input_data.get("params", {})
            method = input_data.get("method", "GET").upper()

            if url is None:
                logger.error("Input data must include 'url' key.")
                return {"error": "URL is required"}

            if method not in ["GET", "POST"]:
                logger.error(f"Unsupported HTTP method: {method}")
                return {"error": "Unsupported method"}

            response = requests.request(method, url, params=params)
            logger.info(f"HTTP request to {url} returned status code {response.status_code}")

            return {"data": response.text}
        except Exception as e:
            logger.error(f"Error during HTTP request: {e}")
            return {"error": str(e)}


# Example usage
if __name__ == "__main__":
    chain = HttpRequestChain()
    input_data = {"url": "https://api.example.com/data", "method": "GET"}
    result = chain.run(input_data)
    logger.debug(f"Result: {result}")
