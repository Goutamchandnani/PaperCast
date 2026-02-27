import os
import asyncio
import edge_tts
from typing import List, Dict

VOICE_MAP = {
    "english": {
        "host1": "en-US-GuyNeural",
        "host2": "en-US-JennyNeural"
    },
    "spanish": {
        "host1": "es-ES-AlvaroNeural",
        "host2": "es-ES-ElviraNeural"
    },
    "french": {
        "host1": "fr-FR-HenriNeural",
        "host2": "fr-FR-DeniseNeural"
    },
    "german": {
        "host1": "de-DE-ConradNeural",
        "host2": "de-DE-KatjaNeural"
    },
    "hindi": {
        "host1": "hi-IN-MadhurNeural",
        "host2": "hi-IN-SwaraNeural"
    },
    "chinese": {
        "host1": "zh-CN-YunxiNeural",
        "host2": "zh-CN-XiaoxiaoNeural"
    },
    "arabic": {
        "host1": "ar-SA-HamedNeural",
        "host2": "ar-SA-ZariyahNeural",
        "name1": "Tariq",
        "name2": "Fatima"
    }
}

# Expand the voice map to include localized names
# For backwards compatibility with the prompt, we will map them via language
LOCALIZED_NAMES = {
    "english": {"host1": "Alex", "host2": "Jamie"},
    "spanish": {"host1": "Alejandro", "host2": "Camila"},
    "french": {"host1": "Alexandre", "host2": "Juliette"},
    "german": {"host1": "Alexander", "host2": "Julia"},
    "hindi": {"host1": "Aarav", "host2": "Diya"},
    "chinese": {"host1": "Wei", "host2": "Li"},
    "arabic": {"host1": "Tariq", "host2": "Fatima"}
}

class TTSService:
    def __init__(self):
        # We use a temp directory to store chunks
        self.temp_dir = os.path.join(os.getcwd(), "temp_audio")
        if not os.path.exists(self.temp_dir):
            os.makedirs(self.temp_dir)

    def _parse_script(self, script_text: str, name1: str, name2: str) -> List[Dict[str, str]]:
        """
        Parses the script into a list of dialogue turns.
        Expects format:
        Name1: Hello
        Name2: Hi there
        """
        lines = script_text.strip().split("\n")
        dialogue = []
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            if line.startswith(f"{name1}:"):
                dialogue.append({"speaker": name1, "text": line[len(name1)+1:].strip()})
            elif line.startswith(f"{name2}:"):
                dialogue.append({"speaker": name2, "text": line[len(name2)+1:].strip()})
            else:
                # If there's a continuation line, append to the last speaker if exists
                if dialogue:
                    dialogue[-1]["text"] += " " + line
                else:
                    # Default if unknown start
                    dialogue.append({"speaker": name1, "text": line})
        return dialogue

    async def _generate_audio_chunk(self, text: str, voice: str, output_file: str):
        """Generates an audio file for a single piece of text."""
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(output_file)

    def generate_podcast_audio(self, script_text: str, output_filename: str, language: str = "english") -> str:
        """
        Parses the script, generates audio for each chunk asynchronously,
        merges them into a single file, and returns the path to the combined MP3.
        """
        language_key = language.lower()
        names = LOCALIZED_NAMES.get(language_key, LOCALIZED_NAMES["english"])
        name1 = names["host1"]
        name2 = names["host2"]
        
        dialogue = self._parse_script(script_text, name1, name2)
        
        # Determine voices based on selected language
        voices = VOICE_MAP.get(language_key, VOICE_MAP["english"])
        alex_voice = voices["host1"]
        jamie_voice = voices["host2"]
        
        # We need an event loop to run the async edge-tts functions
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        chunk_files = []
        
        try:
            # Generate all chunks
            tasks = []
            for i, turn in enumerate(dialogue):
                speaker = turn["speaker"]
                text = turn["text"]
                voice = alex_voice if speaker == name1 else jamie_voice
                chunk_file = os.path.join(self.temp_dir, f"chunk_{i}.mp3")
                chunk_files.append(chunk_file)
                # Ensure we encode properly and don't skip empty text
                if text:
                    tasks.append(self._generate_audio_chunk(text, voice, chunk_file))
            
            # Run all TTS generation tasks
            if tasks:
                loop.run_until_complete(asyncio.gather(*tasks))
            
            # Concatenate the audio
            # We will use raw binary concatenation since edge-tts outputs simple MP3 frames
            # This avoids the need for ffmpeg via pydub, which is a common failure point on Windows.
            final_output_path = os.path.join(self.temp_dir, output_filename)
            with open(final_output_path, "wb") as outfile:
                for chunk_file in chunk_files:
                    if os.path.exists(chunk_file):
                        with open(chunk_file, "rb") as infile:
                            outfile.write(infile.read())
            
            return final_output_path
            
        finally:
            loop.close()
            # Cleanup temp chunk files
            for chunk_file in chunk_files:
                if os.path.exists(chunk_file):
                    try:
                        os.remove(chunk_file)
                    except:
                        pass
