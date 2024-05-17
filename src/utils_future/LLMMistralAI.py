from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage
from utils import Log

from utils_future.LLM import LLM

log = Log('LLMMistralAI')


class LLMMistralAI(LLM):
    NAME = 'MistralAI'
    DEFAULT_MODEL = 'mistral-large-latest'
    DEFAULT_MODEL_URL = 'https://mistral.ai/news/mistral-large/'
    MAX_DATA_BYTES = 80_000
    DEFAULT_OPTIONS = {}

    @staticmethod
    def build_client(api_key: str):
        return MistralClient(
            api_key=api_key,
        )

    @staticmethod
    def build_message(role: str, content: str):
        return ChatMessage(
            role=role,
            content=content,
        )

    def get_response(self, model: str, messages: list, **options):
        return self.client.chat(
            model=model,
            messages=messages,
            **options,
        )
