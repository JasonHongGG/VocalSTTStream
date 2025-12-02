"""
GUI 版本的語音轉錄應用
整合 PyQt6 GUI 與轉錄核心功能
"""
import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QThread, pyqtSignal, QObject

from config import config
from module import RealtimeTranscriberManager, SystemAudioCapture, WhisperTranscriber
from gui.gui import TranscriptionWindow


class TranscriptionThread(QThread):
    """轉錄執行緒，在背景運行"""
    
    sentence_ready = pyqtSignal(str)  # 當有新句子時發出信號
    
    def __init__(self):
        super().__init__()
        self.manager = None
        
    def run(self):
        """執行緒主函數"""
        # 創建音訊擷取器
        capture = SystemAudioCapture(
            chunk_duration=config.chunk_duration,
            target_sample_rate=config.target_sample_rate,
        )
        
        # 創建轉錄器
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
        
        # 創建管理器，註冊回調函數
        self.manager = RealtimeTranscriberManager(
            capture,
            transcriber,
            queue_maxsize=config.queue_maxsize,
            target_sample_rate=config.target_sample_rate,
            min_silence_seconds=config.min_silence_seconds,
            max_segment_seconds=config.max_segment_seconds,
            vad_energy_threshold=config.vad_energy_threshold,
            sentence_callback=self.on_sentence_received,
        )
        
        # 啟動轉錄
        self.manager.start()
        
        # 保持執行緒運行
        try:
            while not self.manager.stop_event.is_set():
                self.manager.stop_event.wait(1.0)
        except Exception as e:
            print(f"轉錄執行緒錯誤: {e}")
        finally:
            self.manager.stop()
            
    def on_sentence_received(self, sentence: str):
        """當收到新句子時的回調函數"""
        # 發送信號到 GUI 主執行緒
        self.sentence_ready.emit(sentence)
        
    def stop(self):
        """停止轉錄"""
        if self.manager:
            self.manager.stop_event.set()
        self.quit()
        self.wait()


class GUIApplication(QObject):
    """GUI 應用程式控制器"""
    
    def __init__(self):
        super().__init__()
        
        # 創建 GUI 視窗
        self.window = TranscriptionWindow()
        
        # 創建轉錄執行緒
        self.transcription_thread = TranscriptionThread()
        
        # 連接信號
        self.transcription_thread.sentence_ready.connect(self.window.add_sentence)
        self.window.close_requested.connect(self.cleanup_and_quit)
        
    def start(self):
        """啟動應用程式"""
        # 顯示視窗
        self.window.show()
        
        # 啟動轉錄執行緒
        self.transcription_thread.start()
        
    def cleanup_and_quit(self):
        """清理並退出"""
        print("正在關閉應用程式...")
        
        # 停止轉錄執行緒
        self.transcription_thread.stop()
        
        # 關閉視窗
        self.window.close()
        
        # 退出應用程式
        QApplication.quit()


def main():
    """主函數"""
    app = QApplication(sys.argv)
    
    # 設置應用程式樣式
    app.setStyle('Fusion')
    
    # 創建並啟動應用程式
    gui_app = GUIApplication()
    gui_app.start()
    
    # 運行事件循環
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
