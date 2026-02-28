from langchain_openai import ChatOpenAI
import os
import yaml
from typing import Optional
from pathlib import Path

# class ChatOpenRouter(ChatOpenAI):
#     def __init__(
#         self,
#         model_name: str,
#         api_key: Optional[str] = None,
#         base_url: str = "https://openrouter.ai/api/v1",
#         **kwargs
#     ):
#         api_key = api_key or os.getenv("OPEN_ROUTER_API_KEY")

#         if api_key is None:
#             raise ValueError("Missing OpenRouter API key")

#         super().__init__(
#             model=model_name,
#             api_key=api_key,
#             base_url=base_url,
#             streaming=False,
#             **kwargs
#         )

# Wrapper for all models we may select
class LLMService:
    def __init__(self):
        #self.open_router_key = os.environ['OPEN_ROUTER_API_KEY']
        self.open_router_key = "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"
        # strip possible leading "Bearer " if someone exported the whole header value
        if isinstance(self.open_router_key, str) and self.open_router_key.lower().startswith("bearer "):
            self.open_router_key = self.open_router_key.split(None, 1)[1]

        print(f"Debug key gefunden? { 'Ja' if self.open_router_key else 'Nein'}")

        if not self.open_router_key:
            raise ValueError("OPEN_ROUTER_API_KEY environment variable not set")

        model_list = Path(__file__).parent.parent / 'models.yaml'
        with open(model_list, 'r') as file:
            models = yaml.safe_load(file)

        self._avail_models = {
            model: provider
            for provider, model_list in models.items()
            for model in model_list
        }

        self._clients = {}
    
    def _load_model(self, model_name: str):
        model_provider = self._avail_models[model_name]
        print(f'loading: {model_provider}')
        if model_provider == "open_router":
            self._clients[model_name] = ChatOpenAI(
                model=model_name,
                api_key=self.open_router_key,
                base_url="https://openrouter.ai/api/v1",
                streaming=False,
                    # Let the client set the Authorization header from `api_key`.
                    # Avoid setting `Authorization` here to prevent duplicate "Bearer " prefixes.
                    default_headers={
                        "X-OpenAI-Stream": "false",
                        "max_output_tokens": "9123",
                    },
                model_kwargs={"stream": False},
                timeout=20,
                max_retries=1,
            )

            # self._clients[model_name] = ChatOpenRouter(
            #     model_name=model_name,
            #     openai_api_key = self.open_router_key
            #)
        # later for super fast inference (if needed)
        # elif model_provider == "groq":
            # llm = ChatGroq(
            #     model="deepseek-r1-distill-llama-70b",
            #     temperature=0,
            #     max_tokens=None,
            #     reasoning_format="parsed",
            #     timeout=None,
            #     max_retries=2,
            # )

    def get_model(self, model_name):
        if model_name not in self._avail_models:
            raise ValueError("Model not found in models")
        # lazy load model
        if model_name not in self._clients:
            self._load_model(model_name)

        return self._clients[model_name]
