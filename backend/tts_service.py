from gradio_client import Client, handle_file
import os
import shutil
import uuid
from config import VOICE_DIR, OUTPUT_DIR, BASE_DIR, TEMP_DIR

# 定义参考音频映射
EMO_MAP = {
    0: os.path.join(VOICE_DIR, "喜.wav"),
    1: os.path.join(VOICE_DIR, "怒.wav"),
    2: os.path.join(VOICE_DIR, "哀.wav"),
    3: os.path.join(VOICE_DIR, "惧.wav")
}

TTS_URL = "http://localhost:7860/"

def synthesize_audio(text: str, emo_type: int) -> str:
    """
    使用本地 IndexTTS2 合成音频。
    返回生成的音频文件路径 (相对于项目根目录)。
    """
    try:
        # 解析参考音频路径
        ref_audio_path = EMO_MAP.get(emo_type, os.path.join(VOICE_DIR, "喜.wav"))
        
        if not os.path.exists(ref_audio_path):
             print(f"Reference audio not found: {ref_audio_path}")
             return None

        client = Client(TTS_URL)
        
        # 根据检查和用户要求调用 API
        # 使用 handle_file 上传文件，这是 Gradio Client 的要求
        result_path = client.predict(
            emo_control_method="与音色参考音频相同",
            prompt=handle_file(ref_audio_path),
            text=text,
            emo_ref_path=handle_file(ref_audio_path),
			emo_weight=0.65,
			vec1=0,
			vec2=0,
			vec3=0,
			vec4=0,
			vec5=0,
			vec6=0,
			vec7=0,
			vec8=0,
			emo_text="",
			emo_random=False,
			max_text_tokens_per_segment=120,
			param_16=True,
			param_17=0.8,
			param_18=30,
			param_19=0.8,
			param_20=0,
			param_21=3,
			param_22=10,
			param_23=1500,
			api_name="/gen_single"
        )

        # 兼容处理：如果返回的是字典（新版 gradio_client），则提取文件路径
        if isinstance(result_path, dict):
            result_path = result_path.get('name') or result_path.get('path') or result_path.get('value')

        if not result_path:
             print("TTS Service Error: Invalid result path")
             return None
        
        # 结果是一个临时文件路径。将其移动到输出目录。
        if not os.path.exists(TEMP_DIR):
            os.makedirs(TEMP_DIR)
            
        filename = f"{uuid.uuid4()}.wav"
        output_path = os.path.join(TEMP_DIR, filename)
        
        shutil.copy(result_path, output_path)
        
        # 返回前端使用的相对路径
        rel_path = os.path.relpath(output_path, BASE_DIR)
        return rel_path.replace("\\", "/")

    except Exception as e:
        print(f"TTS Service Error: {e}")
        return None
