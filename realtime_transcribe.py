import queue
import sys
import threading
from typing import Optional

import numpy as np
import pyaudiowpatch as pyaudio
from faster_whisper import WhisperModel


TARGET_SAMPLE_RATE = 16_000
WINDOW_SECONDS = 4.0
CHUNK_DURATION = 0.25  # seconds





class SystemAudioCapture:
    """Capture loopback audio via PyAudioWPatch (WASAPI loopback)."""

    def __init__(self, chunk_duration: float = CHUNK_DURATION) -> None:
        self._chunk_duration = chunk_duration
        self._pa = pyaudio.PyAudio()
        self._stream = None
        self._source_rate = None
        self._channels = None
        self._frames_per_buffer = None

    def _resample(self, audio: np.ndarray, original_rate: int, target_rate: int) -> np.ndarray:
        """Simple linear interpolation resampler to keep dependencies light."""
        if original_rate == target_rate:
            return audio
        duration = audio.shape[0] / original_rate
        target_length = int(duration * target_rate)
        if target_length <= 0:
            return np.zeros(0, dtype=np.float32)
        x_old = np.linspace(0.0, duration, num=audio.shape[0], endpoint=False)
        x_new = np.linspace(0.0, duration, num=target_length, endpoint=False)
        return np.interp(x_new, x_old, audio).astype(np.float32)

    def _select_loopback_device(self) -> dict:
        host_info = self._pa.get_host_api_info_by_type(pyaudio.paWASAPI)
        device = self._pa.get_device_info_by_index(host_info["defaultOutputDevice"])
        if device.get("isLoopbackDevice"):
            return device

        for idx in range(self._pa.get_device_count()):
            info = self._pa.get_device_info_by_index(idx)
            if info["hostApi"] == host_info["index"] and info.get("isLoopbackDevice"):
                return info
        raise RuntimeError("找不到可用的 WASAPI loopback 裝置，請確認系統音訊裝置或改用虛擬音源。")

    def start(self) -> None:
        device_info = self._select_loopback_device()
        source_rate = int(device_info["defaultSampleRate"])
        channels = int(device_info.get("maxInputChannels", 2)) or 2
        frames_per_buffer = max(1, int(source_rate * self._chunk_duration))

        self._stream = self._pa.open(
            format=pyaudio.paFloat32,
            channels=min(2, channels),
            rate=source_rate,
            input=True,
            frames_per_buffer=frames_per_buffer,
            input_device_index=device_info["index"],
        )
        self._source_rate = source_rate
        self._channels = min(2, channels)
        self._frames_per_buffer = frames_per_buffer
        print(f"使用裝置：{device_info['name']} @ {source_rate} Hz, {self._channels} ch")

    def read_chunk(self) -> np.ndarray:
        if not self._stream:
            raise RuntimeError("Stream not started")
        data = self._stream.read(self._frames_per_buffer, exception_on_overflow=False)
        frame = np.frombuffer(data, dtype=np.float32)
        frame = frame.reshape(-1, self._channels)
        mono = frame.mean(axis=1)
        return self._resample(mono, self._source_rate, TARGET_SAMPLE_RATE)

    def stop(self) -> None:
        if self._stream:
            self._stream.stop_stream()
            self._stream.close()
            self._stream = None
        self._pa.terminate()


class WhisperTranscriber:
    """Thin wrapper around faster-whisper for repeated transcriptions."""

    def __init__(
        self,
        model_size: str = "small",
        device: str = "cpu",
        compute_type: str = "int8",
        language: Optional[str] = "zh",
        task: str = "transcribe",
        beam_size: int = 3,
    ) -> None:
        print("Loading faster-whisper model,請稍候...")
        self._model = WhisperModel(model_size, device=device, compute_type=compute_type)
        self._language = language
        self._task = task
        self._beam_size = beam_size
        print("模型載入完成。")

    def transcribe(self, audio: np.ndarray) -> str:
        segments, _ = self._model.transcribe(
            audio,
            beam_size=self._beam_size,
            language=self._language,
            task=self._task,
        )
        return "".join(seg.text for seg in segments).strip()


class RealtimeTranscriberApp:
    def __init__(
        self,
        capture: SystemAudioCapture,
        transcriber: WhisperTranscriber,
        window_seconds: float = WINDOW_SECONDS,
    ) -> None:
        self.capture = capture
        self.transcriber = transcriber
        self.window_samples = int(TARGET_SAMPLE_RATE * window_seconds)
        self.audio_queue: "queue.Queue[np.ndarray]" = queue.Queue(maxsize=50)
        self.stop_event = threading.Event()
        self._buffer = np.zeros(0, dtype=np.float32)
        self._threads: list[threading.Thread] = []
        self._last_transcript = ""

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
                continue
            self._buffer = np.concatenate([self._buffer, chunk])
            if self._buffer.shape[0] >= self.window_samples:
                self._buffer = self._buffer[-self.window_samples:]
                text = self.transcriber.transcribe(self._buffer.copy())
                if not text:
                    continue
                incremental = self._extract_increment(text)
                if incremental:
                    sys.stdout.write("\r" + incremental + " " * 10)
                    sys.stdout.flush()

    def _extract_increment(self, text: str) -> str:
        """Return only the newly added portion compared to the previous transcript."""
        if not self._last_transcript:
            self._last_transcript = text
            return text

        if text == self._last_transcript:
            return ""

        if len(text) < len(self._last_transcript):
            # Model trimmed context; treat as fresh transcript.
            self._last_transcript = text
            return text

        max_overlap = min(len(text), len(self._last_transcript))
        overlap = 0
        for size in range(max_overlap, 0, -1):
            if self._last_transcript[-size:] == text[:size]:
                overlap = size
                break

        incremental = text[overlap:]
        self._last_transcript = text
        return incremental.strip()

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


def main() -> None:
    capture = SystemAudioCapture()
    transcriber = WhisperTranscriber(model_size="small", device="cuda", compute_type="int8")
    app = RealtimeTranscriberApp(capture, transcriber)
    app.start()
    try:
        while not app.stop_event.is_set():
            app.stop_event.wait(1.0)
    except KeyboardInterrupt:
        print("\n停止中...")
    finally:
        app.stop()


if __name__ == "__main__":
    main()
