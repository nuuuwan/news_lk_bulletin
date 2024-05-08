from utils import Log

log = Log('LLM')


class LLM:
    def __init__(self, api_key: str):
        self.messages = []
        self.client = self.build_client(api_key)

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
        response = self.get_response(
            model=self.DEFAULT_MODEL,
            messages=self.messages,
            **self.DEFAULT_OPTIONS,
        )
        reply = response.choices[0].message.content

        self.append('assistant', reply)
        log.debug(f'Received reply ({self.len_messages:,}B)')
        return reply
