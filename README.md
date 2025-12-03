
### 運行程式

**GUI 版本（推薦）：**
```bash
python app_gui.py
```

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

#### 噪音片語 (NOISE_PHRASES)
改為由 `config.json` 管理，格式如下：
```json
{
    "noise_phrases": [
        "日本語的文章。",
        "英文字幕提供。"
    ]
}
```
若同時存在 `.env` 的 `NOISE_PHRASES`，會以 `config.json` 為主。

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