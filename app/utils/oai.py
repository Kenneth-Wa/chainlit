import os
import requests
import json
import tiktoken
from jinja2 import Template
from typing import List
from .logging import log
from requests.exceptions import RequestException
from llama_index.embeddings.jinaai import JinaEmbedding

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class CustomEndpoint:
    def __init__(self):
        self.base_url = os.environ.get("CUSTOM_ENDPOINT_URL")
        if not self.base_url:
            raise ValueError("CUSTOM_ENDPOINT_URL is not set in environment variables")


    def generate(self, messages: List[dict], **kwargs) -> str:
        url = f"{self.base_url}/openai/chat/completions"
        headers = {"Content-Type": "application/json"}
        data = {
            "model": os.environ.get("CHAT_MODEL_DEPLOYMENT_NAME", "ollama/phi3"),
            "messages": messages,
            **kwargs
        }

        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()

        result = response.json()
        return result['choices'][0]['message']['content']

   
    def stream(self, messages: List[dict], **kwargs):
        url = f"{self.base_url}/openai/chat/completions"
        headers = {"Content-Type": "application/json"}
        data = {
            "model": os.environ.get("CHAT_MODEL_DEPLOYMENT_NAME", "ollama/phi3"),
            "messages": messages,
            "stream": True,
            **kwargs
        }

        with requests.post(url, headers=headers, json=data, stream=True) as response:
            response.raise_for_status()
            for line in response.iter_lines():
                if line:
                    try:
                        line = line.decode('utf-8')
                        if line.startswith('data: '):
                            line = line[6:]  # Remove 'data: ' prefix
                        
                        if line.strip() == '[DONE]':
                            break
                        
                        chunk = json.loads(line)
                        if 'choices' in chunk and len(chunk['choices']) > 0:
                            delta = chunk['choices'][0].get('delta', {})
                            content = delta.get('content')
                            if content:
                                yield content
                    except json.JSONDecodeError as e:
                        yield f"Error parsing response: {e}"

class JinaAIEmbedding:
    def __init__(self):
        jinaai_api_key = os.environ.get("JINAAI_API_KEY")
        if jinaai_api_key is None:
            raise ValueError("JINAAI_API_KEY is not set in environment variables")
        self.embed_model = JinaEmbedding(
            api_key=jinaai_api_key,
            model="jina-embeddings-v2-base-en",
        )

    def generate(self, text):
        embeddings = self.embed_model.get_text_embedding(text)
        return embeddings



def count_token(text: str) -> int:
    encoding = tiktoken.get_encoding("cl100k_base")
    return len(encoding.encode(text))


def render_with_token_limit(template: Template, token_limit: int, **kwargs) -> str:
    text = template.render(**kwargs)
    token_count = count_token(text)
    if token_count > token_limit:
        message = f"token count {token_count} exceeds limit {token_limit}"
        log(message)
        raise ValueError(message)
    return text

# Usage example
if __name__ == "__main__":
    endpoint = CustomEndpoint()
    messages = [{"role": "user", "content": "What is the capital of France?"}]
    
    print("Streaming result:")
    content_received = False
    for chunk in endpoint.stream(messages):
        print(chunk, end='', flush=True)
        content_received = True
    print()
    
    if not content_received:
        print("No content was streamed. The model might not have generated any output.")
