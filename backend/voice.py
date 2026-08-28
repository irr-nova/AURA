import os
from pathlib import Path

from elevenlabs.client import ElevenLabs

from backend.contracts import AgentDecision


class VoiceExplainer:
    """Converts an AgentDecision explanation into spoken audio using ElevenLabs."""

    def __init__(
        self,
        voice_id: str | None = None,
        model_id: str = "eleven_multilingual_v2",
    ):
        api_key = os.getenv("ELEVENLABS_API_KEY")

        if not api_key:
            raise RuntimeError(
                "ELEVENLABS_API_KEY environment variable is not configured."
            )

        self.client = ElevenLabs(api_key=api_key)

        # Can be overridden with ELEVENLABS_VOICE_ID.
        self.voice_id = voice_id or os.getenv("ELEVENLABS_VOICE_ID")

        if not self.voice_id:
            raise RuntimeError(
                "ELEVENLABS_VOICE_ID environment variable is not configured."
            )

        self.model_id = model_id

    def build_script(self, decision: AgentDecision) -> str:
        """Create a short spoken explanation from an AgentDecision."""

        if decision.action == "HOLD":
            return (
                f"AURA recommends holding {decision.asset}. "
                f"{decision.reason}"
            )

        if decision.action == "BUY":
            return (
                f"AURA recommends buying {decision.asset}. "
                f"The proposed quantity is {decision.requested_quantity:.0f} shares. "
                f"{decision.reason}"
            )

        if decision.action == "SELL":
            return (
                f"AURA recommends selling {decision.asset}. "
                f"The proposed quantity is {decision.requested_quantity:.0f} shares. "
                f"{decision.reason}"
            )

        if decision.action == "REDUCE":
            return (
                f"AURA recommends reducing the {decision.asset} position. "
                f"The proposed reduction is {decision.requested_quantity:.0f} shares. "
                f"{decision.reason}"
            )

        return (
            f"AURA recommends {decision.action} for {decision.asset}. "
            f"{decision.reason}"
        )

    def generate_audio(
        self,
        decision: AgentDecision,
        output_path: str = "data/aura_decision.mp3",
    ) -> str:
        """Generate an MP3 explanation for an AgentDecision."""

        script = self.build_script(decision)

        audio = self.client.text_to_speech.convert(
            text=script,
            voice_id=self.voice_id,
            model_id=self.model_id,
            output_format="mp3_44100_128",
        )

        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)

        with output.open("wb") as file:
            for chunk in audio:
                if chunk:
                    file.write(chunk)

        return str(output)