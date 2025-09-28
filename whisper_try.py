#./build/bin/whisper-cli -m models/ggml-large-v3-turbo-q5_0.bin -l ru --output-txt -f /Users/matvejsobolev/Desktop/VoiceRecordings/recording1.wav

import subprocess
import os

def transcribe_audio(audio_file, model_name):

    if not os.path.exists(audio_file):
        raise FileNotFoundError(f"Аудиофайл не найден: {audio_file}")
    script_dir = os.path.dirname(__file__)
    whisper_dir = os.path.join(script_dir, "whisper.cpp")
    
    cmd = [
        
        "./build/bin/whisper-cli",
        "-m", "models/ggml-"+model_name+'.bin',
        "-l", "ru",
        "--no-timestamps",
        #"--output-txt",
        "-f", audio_file
    ]

    original_cwd = os.getcwd()
    try:
        os.chdir(whisper_dir)
        
        res = subprocess.run(cmd, check=True, capture_output=True, text=True)
        '''
        txt_file = f"{audio_file}.txt"
        with open(txt_file, 'r', encoding='utf-8') as f:
            text = f.read().strip()
        '''
        return res.stdout.strip()
        
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Ошибка транскрибации: {e}")
    finally:
        os.chdir(original_cwd)

if __name__ == "__main__":
    try:
        text = transcribe_audio()
        print(f"Результат транскрибации:\n{text}")
    except Exception as e:
        print(f"Ошибка: {e}")
    

 