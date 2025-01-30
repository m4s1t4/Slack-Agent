# A base class for API providers, defining the interface and common properties for subclasses.


class BaseAPIProvider(object):
    def generate_response(self, prompt: str, system_content: str) -> str:
        raise NotImplementedError("Subclass must implement generate_response")
