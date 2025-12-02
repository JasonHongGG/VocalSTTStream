### 專案結構
```
voice/
├── .env                  # 可調整模型/音訊參數
├── app.py                # 主要進入點，將 .env 參數注入各個 class
├── config.py             # Config 物件，讀取 .env 並提供型別安全的屬性
└── module/
    ├── capture.py        # SystemAudioCapture 類別
    ├── manager.py        # RealtimeTranscriberManager 類別
    └── transcriber.py    # WhisperTranscriber 類別（內含繁體輸出邏輯）
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