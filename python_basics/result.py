import os
import torch
from faster_whisper import WhisperModel

# --------------- 設定區 ----------------
video_folder = r"C:\Users\judy\Desktop\test"       
output_folder = r"C:\Users\judy\Desktop\srt_output"  
model_size = "tiny"  # 模型大小
# ---------------------------------------

os.makedirs(output_folder, exist_ok=True)

# 自動偵測 GPU
device = "cuda" if torch.cuda.is_available() else "cpu"
if device == "cuda":
    print("偵測到 GPU，可使用 GPU 加速")
else:
    print("未偵測到 GPU，改用 CPU 模式")

# 初始化模型
try:
    model = WhisperModel(model_size, device=device)
except RuntimeError as e:
    print(f"GPU 初始化失敗 ({e})，改用 CPU 模式")
    device = "cpu"
    model = WhisperModel(model_size, device=device)

def format_timestamp(seconds: float) -> str:
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int((seconds - int(seconds)) * 1000)
    return f"{h:02}:{m:02}:{s:02},{ms:03}"

# 遍歷影片檔案
for filename in os.listdir(video_folder):
    if not filename.lower().endswith(".mp4"):
        continue

    video_path = os.path.join(video_folder, filename)
    print(f"正在處理: {filename}")

    # 移除 batch_size 參數
    segments, info = model.transcribe(video_path)
    
    srt_filename = os.path.splitext(filename)[0] + ".srt"
    srt_path = os.path.join(output_folder, srt_filename)
    
    with open(srt_path, "w", encoding="utf-8") as f:
        for i, segment in enumerate(segments, start=1):
            start = format_timestamp(segment.start)
            end = format_timestamp(segment.end)
            text = segment.text.strip()
            f.write(f"{i}\n{start} --> {end}\n{text}\n\n")

    print(f"完成: {srt_filename}")
