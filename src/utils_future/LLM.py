import openai
from utils import Log

log = Log('LLM')


class LLM:
    DEFAULT_OPTIONS = dict(
        temperature=0.1,
    )
    DEFAULT_MODEL = 'gpt-4-turbo-preview'

    def __init__(self, openai_api_key: str):
        self.messages = []
        self.openai_client = openai.OpenAI(
            api_key=openai_api_key,
        )

    def append(self, role: str, content: str):
        self.messages.append(
            dict(
                role=role,
                content=content,
            )
        )

    @property
    def len_messages(self):
        return sum([len(message['content']) for message in self.messages])

    def send(self) -> str:
        log.debug(f'Sending ({self.len_messages:,}B)...')
        completion = self.openai_client.chat.completions.create(
            messages=self.messages,
            model=LLM.DEFAULT_MODEL,
            **LLM.DEFAULT_OPTIONS,
        )
        reply = completion.choices[0].message.content

        self.append('assistant', reply)
        log.debug(f'Received reply ({self.len_messages:,}B)')
        return reply
