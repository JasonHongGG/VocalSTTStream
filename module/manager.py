from __future__ import annotations

import queue
import threading
from typing import Callable, List, Optional

import numpy as np

from .sentence_buffer import SentenceBuffer


class RealtimeTranscriberManager:
    def __init__(
        self,
        capture,
        transcriber,
        *,
        queue_maxsize: int,
        target_sample_rate: int,
        min_silence_seconds: float,
        max_segment_seconds: float,
        vad_energy_threshold: float,
        sentence_callback: Optional[Callable[[str], None]] = None,
    ) -> None:
        self.capture = capture
        self.transcriber = transcriber
        self._target_sample_rate = target_sample_rate
        self._min_silence = min_silence_seconds
        self._max_segment = max_segment_seconds
        self._vad_threshold = vad_energy_threshold
        self._sentence_callback = sentence_callback
        self.audio_queue: "queue.Queue[np.ndarray]" = queue.Queue(maxsize=queue_maxsize)
        self.stop_event = threading.Event()
        self._threads: List[threading.Thread] = []
        self._segment_chunks: list[np.ndarray] = []
        self._segment_duration = 0.0
        self._silence_time = 0.0
        self._sentence_buffer = SentenceBuffer()

    def _capture_loop(self) -> None:
        try:
            while not self.stop_event.is_set():
                chunk = self.capture.read_chunk()
                try:
                    self.audio_queue.put(chunk, timeout=0.5)
                except queue.Full:
                    continue
        except Exception as exc:
            print(f"[capture] 發生錯誤: {exc}")
            self.stop_event.set()

    def _transcribe_loop(self) -> None:
        while not self.stop_event.is_set():
            try:
                chunk = self.audio_queue.get(timeout=0.2)
            except queue.Empty:
                # 若長時間沒有收到新的音訊，但 buffer 中仍有文字，則強制 flush
                if self._segment_chunks and self._silence_time >= self._min_silence:
                    self._flush_segment()
                continue
            self._process_chunk(chunk)

    def _process_chunk(self, chunk: np.ndarray) -> None:
        energy = float(np.sqrt(np.mean(np.square(chunk))))
        speech_detected = energy > self._vad_threshold

        if speech_detected:
            self._append_chunk(chunk)
            self._silence_time = 0.0
        else:
            self._silence_time += len(chunk) / self._target_sample_rate
            if self._segment_chunks:
                self._append_chunk(chunk)

        if not self._segment_chunks:
            return

        if self._segment_duration >= self._max_segment:
            self._flush_segment()
        elif self._silence_time >= self._min_silence:
            self._flush_segment()

    def _append_chunk(self, chunk: np.ndarray) -> None:
        self._segment_chunks.append(chunk)
        self._segment_duration += len(chunk) / self._target_sample_rate

    def _flush_segment(self) -> None:
        if not self._segment_chunks:
            return
        audio = np.concatenate(self._segment_chunks)
        self._segment_chunks.clear()
        self._segment_duration = 0.0
        self._silence_time = 0.0
        text = self.transcriber.transcribe(audio)
        # 直接 output
        # if text:
        #     print(text)

        # 透過 buffer 處理標點 一句一句輸出
        if not text:
            return
        sentences = self._sentence_buffer.add_text(text)
        for sentence in sentences:
            if self._sentence_callback:
                self._sentence_callback(sentence)
            print(sentence)

    def start(self) -> None:
        self.capture.start()
        capture_thread = threading.Thread(target=self._capture_loop, daemon=True)
        asr_thread = threading.Thread(target=self._transcribe_loop, daemon=True)
        capture_thread.start()
        asr_thread.start()
        self._threads = [capture_thread, asr_thread]
        print("開始擷取，按 Ctrl+C 結束。")

    def stop(self) -> None:
        self.stop_event.set()
        for thread in self._threads:
            thread.join(timeout=2.0)
        self.capture.stop()
        # 輸出最後尚未結束於標點的殘餘文字（如果有）
        rest = self._sentence_buffer.flush_rest()
        if rest:
            if self._sentence_callback:
                self._sentence_callback(rest)
            print(rest)
