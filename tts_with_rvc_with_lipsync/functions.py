import os.path
from moviepy.editor import VideoFileClip, AudioFileClip
from tts_with_rvc import *
import asyncio
import threading
from lipsync_pipeline import *
import concurrent.futures
import tempfile

class Text2RVCLipSync:
    def __init__(self, lip_api_key, rvc_path, model_path, lip_url="https://api.synclabs.so/lipsync", lip_model="wav2lip++", lip_crop=False, credentials_path="credentials.json", rvc_input_directory=None, rvc_output_directory=None, tts_voice="ru-RU-DmitryNeural"):
        self.tts_voice = tts_voice
        self.input_directory = rvc_input_directory
        if not self.input_directory: self.input_directory = tempfile.gettempdir()
        self.output_directory = rvc_output_directory
        if not self.output_directory: self.output_directory = tempfile.gettempdir()
        self.rvc = TTS_RVC(rvc_path=rvc_path, input_directory=self.input_directory, output_directory=self.output_directory, model_path=model_path, voice=self.tts_voice)
        self.wav2lip = Wav2LipSync(api_key=lip_api_key, url=lip_url, model=lip_model, credentials_path=credentials_path, crop_video=lip_crop)
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
        input_path, _ = (self.pool.submit(asyncio.run, self.tts_comminicate(text=text, tts_add_rate=tts_rate, tts_add_volume=tts_volume, tts_add_pitch=tts_pitch)).result())

        rvc_thread = threading.Thread(target=lambda: setattr(rvc_thread, 'result', self.rvc.speech(input_path=input_path, pitch=rvc_pitch, output_directory=self.output_directory)))
        lipsync_thread = threading.Thread(target=lambda: setattr(lipsync_thread, 'result', self.wav2lip(image_path=image_path, audio_path=input_path)))
        rvc_thread.start()
        lipsync_thread.start()

        lipsync_thread.join()
        rvc_thread.join()

        video_clip = VideoFileClip(lipsync_thread.result).set_audio(AudioFileClip(rvc_thread.result))

        if output_path is None:
            output_path = tempfile.NamedTemporaryFile(suffix='.mp4').name

        video_clip.write_videofile(output_path, codec="libx264", audio_codec="aac", fps=24)
        video_clip.close()

        return output_path
