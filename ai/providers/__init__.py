from typing import List, Optional
from state_store.get_user_state import get_user_state
from ..ai_constants import DEFAULT_SYSTEM_CONTENT
from .openai import OpenAI_API
from termcolor import colored

# from .anthropic import AnthropicAPI  # Removemos esta importación
# from .vertexai import VertexAPI      # Removemos esta también si no la usamos


def get_available_providers():
    return {
        # **AnthropicAPI().get_models(),  # Removemos esta línea
        **OpenAI_API().get_models(),
        # **VertexAPI().get_models(),     # Removemos esta línea
    }


def _get_provider(provider_name: str):
    # if provider_name.lower() == "anthropic":  # Removemos esta condición
    #     return AnthropicAPI()
    if provider_name.lower() == "openai":
        return OpenAI_API()
    # elif provider_name.lower() == "vertexai":  # Removemos esta condición
    #     return VertexAPI()
    else:
        raise ValueError(f"Unknown provider: {provider_name}")


def get_provider_response(
    user_id: str, prompt: str, context: Optional[List[dict]] = None, system_content: str = DEFAULT_SYSTEM_CONTENT
) -> str:
    try:
        provider = OpenAI_API()
        return provider.generate_response(prompt, system_content)
    except Exception as e:
        print(colored(f"Error getting provider response: {str(e)}", "red"))
        raise e
