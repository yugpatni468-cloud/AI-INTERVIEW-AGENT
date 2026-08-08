from app.services.gemini_service import GeminiService

gemini = GeminiService()

result = gemini.ask("Say only: Hello, AI Interview Agent is working.")

print(result)