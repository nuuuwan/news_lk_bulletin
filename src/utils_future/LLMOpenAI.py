import openai
from utils import Log

from utils_future.LLM import LLM

log = Log('LLMOpenAI')


class LLMOpenAI(LLM):
    NAME = 'OpenAI'
    DEFAULT_MODEL = 'gpt-4-0125-preview'

    DEFAULT_MODEL_URL = (
        'https://platform.openai.com' + '/docs/models/gpt-4-and-gpt-4-turbo'
    )
    MAX_DATA_BYTES = 120_000
    DEFAULT_OPTIONS = dict(
        temperature=0.1,
    )

    @staticmethod
    def build_client(api_key: str):
        return openai.OpenAI(
            api_key=api_key,
        )

    @staticmethod
    def build_message(role: str, content: str):
        return dict(
            role=role,
            content=content,
        )

    def get_response(self, model: str, messages: list, **options):
        return self.client.chat.completions.create(
            model=model,
            messages=messages,
            **options,
        )