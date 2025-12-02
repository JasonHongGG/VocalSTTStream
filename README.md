### 載入環境
```
source .venv/Scripts/activate 
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