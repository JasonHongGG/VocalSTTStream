from __future__ import annotations

from typing import Optional

import numpy as np
from faster_whisper import WhisperModel

try:
    from opencc import OpenCC
except ImportError:  # pragma: no cover - optional dependency
    OpenCC = None


class WhisperTranscriber:
    """Thin wrapper around faster-whisper for repeated transcriptions."""

    def __init__(
        self,
        *,
        model_size: str,
        device: str,
        compute_type: str,
        language: Optional[str],
        task: str,
        beam_size: int,
        vad_filter: bool = True,
    ) -> None:
        print("載入模型請稍候...")
        self._language = language
        self._task = task
        self._beam_size = beam_size
        self._vad_filter = vad_filter
        if OpenCC is None:
            raise ImportError("請安裝 opencc 套件以啟用繁體輸出: pip install opencc")
        self._traditional_converter = OpenCC("s2t")
        self._model = WhisperModel(
            model_size,
            device=device,
            compute_type=compute_type,
        )
        print("=> 模型載入完成。")

    def transcribe(self, audio: np.ndarray) -> str:
        segments, _ = self._model.transcribe(
            audio,
            beam_size=self._beam_size,
            language=self._language,
            task=self._task,
            vad_filter=self._vad_filter,
        )
        text = "".join(seg.text for seg in segments).strip()
        if text and self._traditional_converter and self._contains_cjk(text):
            text = self._traditional_converter.convert(text)
        return text

    @staticmethod
    def _contains_cjk(text: str) -> bool:
        return any("\u4e00" <= ch <= "\u9fff" for ch in text)
