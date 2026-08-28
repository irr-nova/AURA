import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

class VoiceExplainer:
    """
    Optional ElevenLabs voice module.

    This module is intentionally isolated from the rest of AURA.
    If ElevenLabs is unavailable or incorrectly configured,
    the main application can continue operating.
    """

    def __init__(self):
        self.api_key = os.getenv("ELEVENLABS_API_KEY")
        self.voice_id = os.getenv("ELEVENLABS_VOICE_ID")

        if not self.api_key:
            raise RuntimeError(
                "ELEVENLABS_API_KEY is not configured."
            )

        if not self.voice_id:
            raise RuntimeError(
                "ELEVENLABS_VOICE_ID is not configured."
            )

        try:
            from elevenlabs.client import ElevenLabs
        except Exception as exc:
            raise RuntimeError(
                f"ElevenLabs SDK could not be loaded: {exc}"
            ) from exc

        self.client = ElevenLabs(
            api_key=self.api_key
        )

    def generate_audio(
        self,
        agent_decision,
        output_path="data/aura_decision.mp3",
    ):
        """
        Generate an MP3 explanation of the current AURA decision.
        """

        reason = getattr(
            agent_decision,
            "reason",
            "No additional reasoning available.",
        )

        action = getattr(
            agent_decision,
            "action",
            "UNKNOWN",
        )

        confidence = getattr(
            agent_decision,
            "confidence",
            0.0,
        )

        text = (
            f"AURA recommends {action}. "
            f"Confidence is {confidence:.0%}. "
            f"{reason}"
        )

        output_file = Path(output_path)

        # Make sure the data directory exists.
        output_file.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        audio = self.client.text_to_speech.convert(
            voice_id=self.voice_id,
            text=text,
            model_id="eleven_multilingual_v2",
            output_format="mp3_44100_128",
        )

        with open(output_file, "wb") as f:
            for chunk in audio:
                if chunk:
                    f.write(chunk)

        return str(output_file)