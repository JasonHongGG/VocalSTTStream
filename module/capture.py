from __future__ import annotations

import numpy as np
import pyaudiowpatch as pyaudio


class SystemAudioCapture:
    """Capture loopback audio via PyAudioWPatch (WASAPI loopback)."""

    def __init__(self, *, chunk_duration: float, target_sample_rate: int) -> None:
        self._chunk_duration = chunk_duration
        self._target_sample_rate = target_sample_rate
        self._pa = pyaudio.PyAudio()
        self._stream = None
        self._source_rate = None
        self._channels = None
        self._frames_per_buffer = None

    def _resample(self, audio: np.ndarray, original_rate: int) -> np.ndarray:
        if original_rate == self._target_sample_rate:
            return audio
        duration = audio.shape[0] / original_rate
        target_length = int(duration * self._target_sample_rate)
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
        return self._resample(mono, self._source_rate)

    def stop(self) -> None:
        if self._stream:
            self._stream.stop_stream()
            self._stream.close()
            self._stream = None
        self._pa.terminate()
