from langchain_openai import ChatOpenAI

# Wrapper for all models we may select
class LLMService:
    def __init__(self):
        self.open_router_key = getenv("OPENROUTER_API_KEY")
        if not self.open_router_key:
            raise ValueError("Open Router API key not set")

        with open('models.yaml', 'r') as file:
            models = yaml.safe_load(file)

        self._avail_models = {
            model: provider
            for provider, model_list in models.items()
            for model in model_list
        }

        self._clients = {}
    
    def load_model(self, model_name: str):
        model_provider = self._avail_models[model_name]
        if model_provider == "open_router":
            self._clients[model_name] = ChatOpenAI(
                api_key=self.open_router_key,
                base_url="https://openrouter.ai/api/v1",
                model=model_name
            )
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
            self.load_model(model_name)

        return self._clients[model_name]