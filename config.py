from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


def load_dotenv(path: Path | None = None) -> None:
    """Minimal .env loader to avoid extra dependencies."""
    target_path = Path(path) if path else Path.cwd() / ".env"
    if not target_path.exists():
        return

    for raw_line in target_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


@dataclass(slots=True)
class Config:
    target_sample_rate: int
    window_seconds: float
    chunk_duration: float
    min_silence_seconds: float
    max_segment_seconds: float
    vad_energy_threshold: float
    model_size: str
    device: str
    compute_type: str
    language: Optional[str]
    task: str
    beam_size: int
    queue_maxsize: int = 50
    initial_prompt: Optional[str] = None

    @classmethod
    def load(cls, env_path: Path | None = None) -> "Config":
        load_dotenv(env_path)
        return cls(
            target_sample_rate=int(os.getenv("TARGET_SAMPLE_RATE", "16000")),
            window_seconds=float(os.getenv("WINDOW_SECONDS", "4.0")),
            chunk_duration=float(os.getenv("CHUNK_DURATION", "0.25")),
            min_silence_seconds=float(os.getenv("MIN_SILENCE_SECONDS", "0.6")),
            max_segment_seconds=float(os.getenv("MAX_SEGMENT_SECONDS", "12.0")),
            vad_energy_threshold=float(os.getenv("VAD_ENERGY_THRESHOLD", "0.0005")),
            model_size=os.getenv("MODEL_SIZE", "small"),
            device=os.getenv("DEVICE", "cpu"),
            compute_type=os.getenv("COMPUTE_TYPE", "int8"),
            language=os.getenv("LANGUAGE") or None,
            task=os.getenv("TASK", "transcribe"),
            beam_size=int(os.getenv("BEAM_SIZE", "3")),
            initial_prompt=os.getenv("INITIAL_PROMPT") or None,
        )

config = Config.load()