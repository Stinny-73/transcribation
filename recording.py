import pyaudio
import tempfile
import wave
import os
import subprocess
class Recording:
    def __init__(self):
         self.flag = False
         self.frames = []
    def clear(self):
        self.frames = []
    def record(self):
            audio = pyaudio.PyAudio()
            stream = audio.open(
                format=pyaudio.paInt32,
                channels=1,
                rate=44100,
                input=True,
                frames_per_buffer=1024,
                input_device_index=0
            )

 


            while self.flag:
                data = stream.read(1024, exception_on_overflow=False)
                self.frames.append(data)

            stream.stop_stream()
            stream.close()
            audio.terminate()
    def transcribe_audio_v2(self, model_name="large-v3-turbo-q5_0",
                            whisper_path=os.path.join(os.path.dirname(__file__), "whisper.cpp")):

        temp_file = None
        audio_file = None  # ← добавляем безопасную инициализацию

        if self.frames:
            import pyaudio
            audio = pyaudio.PyAudio()

            tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
            temp_file = tmp.name
            wf = wave.open(temp_file, "wb")
            wf.setnchannels(1)
            wf.setsampwidth(audio.get_sample_size(pyaudio.paInt32))
            wf.setframerate(44100)
            wf.writeframes(b"".join(self.frames))
            wf.close()
            audio_file = temp_file
        else:
            return "(Нет аудиоданных для распознавания)"  # ← выходим заранее, если frames пуст

        # Определяем путь к whisper-cli
        if os.name == "nt":
            executable = os.path.join(whisper_path, "build", "bin", "Release", "whisper-cli.exe")
        else:
            executable = os.path.join(whisper_path, "build", "bin", "whisper-cli")

        cmd = [
            executable,
            "-m", os.path.join("models", f"ggml-{model_name}.bin"),
            "-l", "auto",
            "--no-timestamps",
            "-f", audio_file
        ]

        original_cwd = os.getcwd()
        try:
            if os.path.exists(whisper_path):
                os.chdir(whisper_path)
                res = subprocess.run(cmd, check=True, capture_output=True, text=True)
                return res.stdout.strip()
            else:
                raise FileNotFoundError("Папка whisper.cpp не найдена")
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Ошибка транскрибации: {e.stderr}")
        finally:
            os.chdir(original_cwd)
            if temp_file and os.path.exists(temp_file):
                os.remove(temp_file)
'''
    def transcribe_audio_v2(self, model_name="large-v3-turbo-q5_0",
                        whisper_path=os.path.join(os.path.dirname(__file__), "whisper.cpp")):

        temp_file = None
        if self.frames:

            audio = pyaudio.PyAudio()

            tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
            temp_file = tmp.name
            wf = wave.open(temp_file, "wb")
            wf.setnchannels(1)
            wf.setsampwidth(audio.get_sample_size(pyaudio.paInt32))
            wf.setframerate(44100)
            wf.writeframes(b"".join(self.frames))
            wf.close()
            audio_file = temp_file

        # Определяем путь к whisper-cli
        if os.name == "nt":
            executable = os.path.join(whisper_path, "build", "bin", "Release", "whisper-cli.exe")
        else:
            executable = os.path.join(whisper_path, "build", "bin", "whisper-cli")

        # Формируем команду
        cmd = [
            executable,
            "-m", os.path.join("models", f"ggml-{model_name}.bin"),
            "-l", "ru",
            "--no-timestamps",
            "-f", audio_file
        ]

        original_cwd = os.getcwd()
        try:
            if os.path.exists(whisper_path):
                os.chdir(whisper_path)
                res = subprocess.run(cmd, check=True, capture_output=True, text=True)
                return res.stdout.strip()
            else:
                raise FileNotFoundError("Папка whisper.cpp не найдена")
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Ошибка транскрибации: {e.stderr}")
        finally:
            os.chdir(original_cwd)
            # Удаляем временный файл, если создавали
            if temp_file and os.path.exists(temp_file):
                os.remove(temp_file)
'''

