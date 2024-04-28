import os.path
from moviepy.editor import VideoFileClip, ImageClip, CompositeVideoClip, AudioFileClip, CompositeAudioClip
from tts_with_rvc.inference import *
from lipsync_pipeline import *

rvc = TTS_RVC(rvc_path="src\\rvclib", model_path="models\\DenVot13800.pth", input_directory="input\\")
pool = concurrent.futures.ThreadPoolExecutor()

async def tts_comminicate(input_directory,
                 text,
                 voice="ru-RU-DmitryNeural",
                 tts_add_rate=0,
                 tts_add_volume=0,
                 tts_add_pitch=0):
    communicate = tts.Communicate(text=text,
                                  voice=voice,
                                  rate=f'{"+" if tts_add_rate >= 0 else ""}{tts_add_rate}%',
                                  volume=f'{"+" if tts_add_volume >= 0 else ""}{tts_add_volume}%',
                                  pitch=f'{"+" if tts_add_pitch >= 0 else ""}{tts_add_pitch}Hz')
    file_name = date_to_short_hash()
    input_path = os.path.join(input_directory, file_name)
    await communicate.save(input_path + ".wav")
    return (input_path  + ".wav"), file_name

text1 = "Всем привет, Десятый 'И' класс! Можно сказать, что я только что родился! Мои создатели делают для меня всё! Обращась к вам лишь потому, что хочу разделить с вами свою радость и попросить у вас поддержки! В скором времени я хочу выйти в свет и стать популярным! Надеюсь на ваши добрые слова! Спасибо!"
text = "Всем привет, Десятый 'И' класс!"

input_path, _ = (pool.submit(asyncio.run, tts_comminicate(input_directory="input\\", text=text, tts_add_rate=0, tts_add_volume=0, tts_add_pitch=0)).result())

api_key = 'f5a97ebb-c150-48be-a35c-9010ba69e0ec'
url = "https://api.synclabs.so/lipsync"
credentials_path = "credentials.json"

wav2lip = Wav2LipSync(api_key, url, credentials_path)
image_path = 'pups.png'
audio_path = input_path
output_path = 'out3.mp4'

if os.path.exists("temp.mp4"):
    os.remove("temp.mp4")

thread = threading.Thread(target=wav2lip, args=(image_path, audio_path, "temp.mp4"))
thread.start()

path = rvc(text=text, pitch=6)

thread.join()

video_clip = VideoFileClip("temp.mp4")
audio_clip = AudioFileClip(path)

video_clip = video_clip.set_audio(audio_clip)


image_clip = ImageClip("denvot.png", duration=video_clip.duration)

x_center = (1025 - 285) // 2
y_center = (1025 - 285) // 2

video_clip = video_clip.set_position((x_center, y_center))

final_clip = CompositeVideoClip([image_clip, video_clip])


final_clip.write_videofile(output_path, codec="libx264", audio_codec="aac", fps=24)
video_clip.close()
final_clip.close()
audio_clip.close()
print("Файл сохранён в:", output_path)
