### 專案結構
```
voice/
├── .env                  # 可調整模型/音訊參數
├── app.py                # 主要進入點（命令列版本）
├── app_gui.py            # GUI 版本進入點
├── config.py             # Config 物件，讀取 .env 並提供型別安全的屬性
├── gui/
│   └── modern_window.py  # 現代化 GUI 視窗介面
└── module/
    ├── capture.py        # SystemAudioCapture 類別
    ├── manager.py        # RealtimeTranscriberManager 類別
    └── transcriber.py    # WhisperTranscriber 類別（內含繁體輸出邏輯）
```

### 運行程式

**GUI 版本（推薦）：**
```bash
python app_gui.py
```

**GUI 功能說明：**
- **拖拽移動**：抓住左側有斜線紋理的區域拖拽視窗
- **釘選按鈕**：📌 按鈕可切換視窗是否保持在最上層
- **關閉按鈕**：✕ 按鈕關閉程式
- **自動模式**：預設為自動模式，即時顯示最新的轉錄句子
- **手動模式**：點擊 ⏸ 按鈕切換到手動模式，可用 ◀ ▶ 按鈕瀏覽歷史句子
- **文字選取**：句子可以直接框選複製

**命令列版本：**
```bash
python app.py
```

### 調整參數
在 `.env` 中修改，例如：
```
MODEL_SIZE=medium
DEVICE=cuda
COMPUTE_TYPE=int8
WINDOW_SECONDS=4.0
MIN_SILENCE_SECONDS=0.6
# 留空代表自動語言偵測，若強制語言則填入 iso 代碼 (ex: zh, en)
LANGUAGE=
```

### 載入環境
```
source .venv/Scripts/activate 
```

### OpenCC：
程式會自動將模型輸出的中文轉為繁體，請先安裝 OpenCC：
```
pip install opencc
```

### GUI 依賴（使用 GUI 版本時需要）：
```
pip install PyQt6
```

### cudnn_ops64_9.dll
```
pip install "nvidia-cudnn-cu12==9.1.0.70"
export PATH="$VIRTUAL_ENV/Lib/site-packages/nvidia/cudnn/bin:$PATH"
```

### cublas64_12.dll
```
pip install "nvidia-cublas-cu12==12.3.4.1"
export PATH="$VIRTUAL_ENV/Lib/site-packages/nvidia/cublas/bin:$PATH"
```

### 套件環境變數設定
在 .venv/Scripts/activate 檔案中直接加入
export PATH="$VIRTUAL_ENV/Lib/site-packages/nvidia/cublas/bin:$PATH"
export PATH="$VIRTUAL_ENV/Lib/site-packages/nvidia/cudnn/bin:$PATH"