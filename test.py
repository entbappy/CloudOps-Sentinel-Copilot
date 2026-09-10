from src.config import get_settings

settings = get_settings()

print("OpenAI API Key:", settings.openai_api_key)
print("OpenAI Model:", settings.openai_model)