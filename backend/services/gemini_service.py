import os
from google import genai
from google.genai import types

class GeminiService:
    def __init__(self):
        self.api_key = os.environ.get("GEMINI_API_KEY")
        if not self.api_key or self.api_key == "your_gemini_api_key":
            print("WARNING: GEMINI_API_KEY not set properly.")
            self.client = None
        else:
            self.client = genai.Client(api_key=self.api_key)

    def generate_podcast_script(self, text: str, language: str = "english") -> str:
        """
        Sends the extracted document text to Gemini to generate
        a conversational podcast script.
        """
        
        LOCALIZED_NAMES = {
            "english": {"host1": "Alex", "host2": "Jamie"},
            "spanish": {"host1": "Alejandro", "host2": "Camila"},
            "french": {"host1": "Alexandre", "host2": "Juliette"},
            "german": {"host1": "Alexander", "host2": "Julia"},
            "hindi": {"host1": "Aarav", "host2": "Diya"},
            "chinese": {"host1": "Wei", "host2": "Li"},
            "arabic": {"host1": "Tariq", "host2": "Fatima"}
        }
        
        language_key = language.lower()
        names = LOCALIZED_NAMES.get(language_key, LOCALIZED_NAMES["english"])
        name1 = names["host1"]
        name2 = names["host2"]
        
        # If the text is extremely large, we could chunk it, but the Gemini 2.5 Flash 
        # model has a massive context window so we can usually pass it entirely.
        
        prompt = f"""
You are an expert scriptwriter for a science and research podcast.
Convert the following research paper text into a natural, engaging podcast script.
There are two hosts: "{name1}" and "{name2}".
- {name1} introduces the paper, asks insightful questions, and guides the conversation.
- {name2} acts as the expert, explaining the research in simple, conversational language.
- Generate the entire podcast script in {language}.
- Both hosts {name1} and {name2} must speak fully in {language}.
- Explain all technical jargon in plain {language}.
- Include a warm intro and outro.
- Keep it engaging, not just a dry summary. Make them sound like they have good chemistry.
- Target length: 5-10 minutes when spoken (roughly 700-1400 words).
- Format output EXACTLY like this for every single line of dialogue:
{name1}: [{name1}'s dialogue]
{name2}: [{name2}'s dialogue]

Do not include any other markdown formatting or stage directions, just the names and dialogue.

Research Paper Text:
{text}
"""
        
        try:
            if not self.client:
                raise ValueError("Gemini API key is missing. Please set GEMINI_API_KEY in .env")
                
            response = self.client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.7,
                )
            )
            return response.text
        except Exception as e:
            print(f"Error calling Gemini API: {e}")
            raise e
