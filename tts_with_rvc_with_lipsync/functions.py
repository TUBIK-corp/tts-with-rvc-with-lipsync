import os.path
from moviepy.editor import VideoFileClip, AudioFileClip
from tts_with_rvc.inference import *
import asyncio
import threading
from lipsync_pipeline import *
import concurrent.futures
import tempfile

class Text2RVCLipSync:
    def __init__(self, lip_api_key, rvc_path, model_path, lip_url="https://api.synclabs.so/lipsync", credentials_path="credentials.json", input_directory="input\\", tts_voice="ru-RU-DmitryNeural"):
        self.lip_api_key = lip_api_key
        self.lip_url = lip_url
        self.credentials_path = credentials_path
        self.rvc_path = rvc_path
        self.model_path = model_path
        self.input_directory = input_directory
        self.tts_voice = tts_voice
        self.rvc = TTS_RVC(rvc_path=self.rvc_path, input_directory=self.input_directory, model_path=self.model_path, voice=self.tts_voice)
        self.pool = concurrent.futures.ThreadPoolExecutor()

    async def tts_comminicate(self, text, tts_add_rate=0, tts_add_volume=0, tts_add_pitch=0):
        communicate = tts.Communicate(text=text,
                                      voice=self.tts_voice,
                                      rate=f'{"+" if tts_add_rate >= 0 else ""}{tts_add_rate}%',
                                      volume=f'{"+" if tts_add_volume >= 0 else ""}{tts_add_volume}%',
                                      pitch=f'{"+" if tts_add_pitch >= 0 else ""}{tts_add_pitch}Hz')
        file_name = date_to_short_hash()
        input_path = os.path.join(self.input_directory, file_name)
        await communicate.save(input_path + ".wav")
        return (input_path + ".wav"), file_name

    def __call__(self, text, image_path, output_path=None, rvc_pitch=0, tts_rate=0, tts_volume=0, tts_pitch=0):
        return self.text2lip(text, image_path, output_path, rvc_pitch, tts_rate, tts_volume, tts_pitch)

    def text2lip(self, text, image_path, output_path=None, rvc_pitch=0, tts_rate=0, tts_volume=0, tts_pitch=0):
        wav2lip = Wav2LipSync(self.lip_api_key, self.lip_url, self.credentials_path)

        input_path, _ = (self.pool.submit(asyncio.run, self.tts_comminicate(text=text, tts_add_rate=tts_rate, tts_add_volume=tts_volume, tts_add_pitch=tts_pitch)).result())

        lipsync_thread = threading.Thread(target=lambda: setattr(lipsync_thread, 'result', wav2lip(image_path=image_path, audio_path=input_path)))
        rvc_thread = threading.Thread(target=lambda: setattr(rvc_thread, 'result', self.rvc(text=text, pitch=rvc_pitch, tts_rate=tts_rate, tts_volume=tts_volume, tts_pitch=tts_pitch)))

        lipsync_thread.start()
        rvc_thread.start()

        lipsync_thread.join()
        rvc_thread.join()

        video_clip = VideoFileClip(lipsync_thread.result).set_audio(AudioFileClip(rvc_thread.result))

        if output_path is None:
            output_path = tempfile.NamedTemporaryFile(suffix='.mp4').name

        video_clip.write_videofile(output_path, codec="libx264", audio_codec="aac", fps=24)
        video_clip.close()

        return output_path
