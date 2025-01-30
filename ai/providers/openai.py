import os
import json
import openai
from .base_provider import BaseAPIProvider
import logging
from termcolor import colored
from ..tools.tools_schema import schema
from ..tools.trello_connection import (
    get_trello_board_info,
    get_list_cards,
    add_card_to_list,
    delete_card,
    search_card_descriptions,
    get_latest_card,
)
from ..tools.github_connection import (
    list_user_repos,
    print_repo_contents,
    list_branches,
    show_commit_history,
    get_github_instance,
)
from ..tools.rag import query_rag

logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

# ---- Tokens ---- #
API_KEY = os.getenv("TRELLO_API_KEY")
TOKEN = os.getenv("TRELLO_TOKEN")
API_SECRET = os.getenv("TRELLO_API_SECRET")
BOARD_ID = os.getenv("BOARD_ID")

# ---- GitHub setup ---- #
github_instance = get_github_instance()
github_user = github_instance.get_user()

# Initialize conversation history
conversation_history = []


class OpenAI_API(BaseAPIProvider):

    def __init__(self):
        try:
            self.base_url = "http://localhost:11434/v1/"
            self.api_key = "ollama"
            print(colored(f"OpenAI API initialized with base URL: {self.base_url}", "green"))
        except Exception as e:
            print(colored(f"Error initializing OpenAI API: {str(e)}", "red"))
            raise e

    def generate_response(self, prompt: str, system_content: str) -> str:
        global conversation_history
        current_conversation = []
        try:
            self.client = openai.OpenAI(base_url=self.base_url, api_key=self.api_key)
            current_conversation.append({"role": "system", "content": system_content})
            current_conversation.append({"role": "user", "content": prompt})
            messages = conversation_history + current_conversation

            response = self.client.chat.completions.create(
                model="llama3.2",
                messages=messages,
                temperature=0.1,
                tools=schema,
                tool_choice="auto",
            )
            response_message = response.choices[0].message
            tool_calls = response_message.tool_calls

            if tool_calls:
                availabe_functions = {
                    # Trello functions
                    "get_trello_board_info": get_trello_board_info,
                    "get_list_cards": get_list_cards,
                    "add_card_to_list": add_card_to_list,
                    "delete_card": delete_card,
                    "search_card_descriptions": search_card_descriptions,
                    "get_latest_card": get_latest_card,
                    # GitHub functions
                    "list_user_repos": list_user_repos,
                    "print_repo_contents": print_repo_contents,
                    "list_branches": list_branches,
                    "show_commit_history": show_commit_history,
                    # Rag functions
                    "query_rag": query_rag,
                }

                function_responses = []

                for tool_call in tool_calls:
                    function_name = tool_call.function.name
                    function_to_call = availabe_functions[function_name]
                    function_args = json.loads(tool_call.function.arguments)
                    function_response = function_to_call(**function_args)
                    function_responses.append(str(function_response))
                    current_conversation.append(
                        {
                            "tool_call_id": tool_call.id,
                            "role": "tool",
                            "name": function_name,
                            "content": str(function_response),
                        }
                    )
                    messages = conversation_history + current_conversation

                tools_response = self.client.chat.completions.create(model="llama3.2", messages=messages, temperature=0.1)
                response_with_tools = tools_response.choices[0].message.content
                current_conversation.append({"role": "assistant", "content": response_with_tools})
                conversation_history = messages + [{"role": "assistant", "content": response_with_tools}]
                return response_with_tools
            else:
                final_response = response_message.content
                current_conversation.append({"role": "assistant", "content": final_response})
                conversation_history = messages + [{"role": "assistant", "content": final_response}]
                return final_response

        except openai.APIConnectionError as e:
            error_msg = f"No se pudo conectar con el servidor: {e.__cause__}"
            logger.error(colored(error_msg, "red"))
            return error_msg
        except openai.RateLimitError as e:
            error_msg = f"Se alcanzó el límite de solicitudes: {e}"
            logger.error(colored(error_msg, "red"))
            return error_msg
        except openai.AuthenticationError as e:
            error_msg = f"Error de autenticación: {e}"
            logger.error(colored(error_msg, "red"))
            return error_msg
        except openai.APIStatusError as e:
            error_msg = f"Error de estado de la API: {e.status_code}"
            logger.error(colored(error_msg, "red"))
            return error_msg
        except Exception as e:
            error_msg = f"Error inesperado: {str(e)}"
            logger.error(colored(error_msg, "red"))
            return error_msg
