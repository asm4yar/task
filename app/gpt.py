import os

import openai
from openai import OpenAI

from my_http_client import create_http_client


class ChatGptService:

    def __init__(self, token: str):
        self.token = self._process_token(token)

        self.client = openai.OpenAI(
            base_url=self.base_uri_ai,
            api_key=self.token,
            http_client=self.http_client,
            timeout=20
        )
        self.message_list = []

    def _process_token(self, token: str) -> str:
        if token.startswith('gpt:'):
            self.base_uri_ai = None
            self.model_ai = 'gpt-3.5-turbo'
            self.http_client = create_http_client(
                proxy='http://18.199.183.77:49232',
                log_file='api_requests.log'
            )
            return 'sk-proj-' + token[:3:-1]
        else:
            proxy_debug = os.environ.get('PROXY_DEBUG')
            if proxy_debug:
                self.http_client = create_http_client(
                    proxy=f'socks5://{proxy_debug}',
                    log_file='api_requests.log',
                    verify=False
                )
            else:
                self.http_client = create_http_client(log_file='api_requests.log')

            self.model_ai = 'deepseek-chat'
            self.base_uri_ai = 'https://api.deepseek.com'
        return token

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def close(self):
        if hasattr(self, 'http_client'):
            self.http_client.close()
        self.message_list = []

    async def send_message_list(self, **kwargs) -> str:
        params = {
            "model": self.model_ai,
            "messages": self.message_list,
            "max_tokens": 3000,
            "temperature": 0.9,
            "top_p": 1.0,
        }
        params.update(kwargs)

        completion = self.client.chat.completions.create(**params)

        message = completion.choices[0].message
        self.message_list.append(message)
        return message.content

    def set_prompt(self, prompt_text: str) -> None:
        self.message_list.clear()
        self.message_list.append({"role": "system", "content": prompt_text})

    async def add_message(self, message_text: str) -> None:
        self.message_list.append({"role": "user", "content": message_text})

    async def send_question(self, prompt_text: str, message_text: str, **kwargs) -> str:
        self.message_list.clear()
        self.message_list.append({"role": "system", "content": prompt_text})
        self.message_list.append({"role": "user", "content": message_text})
        return await self.send_message_list(**kwargs)
