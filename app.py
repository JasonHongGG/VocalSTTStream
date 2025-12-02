from config import config
from module import RealtimeTranscriberManager, SystemAudioCapture, WhisperTranscriber


def main() -> None:
    capture = SystemAudioCapture(
        chunk_duration=config.chunk_duration,
        target_sample_rate=config.target_sample_rate,
    )
    transcriber = WhisperTranscriber(
        model_size=config.model_size,
        device=config.device,
        compute_type=config.compute_type,
        language=config.language,
        task=config.task,
        beam_size=config.beam_size,
        vad_filter=True,
        initial_prompt=config.initial_prompt,
    )
    app = RealtimeTranscriberManager(
        capture,
        transcriber,
        queue_maxsize=config.queue_maxsize,
        target_sample_rate=config.target_sample_rate,
        min_silence_seconds=config.min_silence_seconds,
        max_segment_seconds=config.max_segment_seconds,
        vad_energy_threshold=config.vad_energy_threshold,
    )
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
