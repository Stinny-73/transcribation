#./build/bin/whisper-cli -m models/ggml-large-v3-turbo-q5_0.bin -l ru --output-txt -f /Users/matvejsobolev/Desktop/VoiceRecordings/recording1.wav

import subprocess
import os

def transcribe_audio(audio_file, model_name, whisper_path=os.path.join(os.path.dirname(__file__), "whisper.cpp")):

    if not os.path.exists(audio_file):
        raise FileNotFoundError(f"Аудиофайл не найден: {audio_file}")
    #script_dir = os.path.dirname(__file__)
    #whisper_dir = os.path.join(script_dir, "whisper.cpp")
    if os.name == 'nt':  # Windows
        executable = os.path.join(whisper_path, "build", "bin", "Release", "whisper-cli.exe")
    else:  # Unix-like (Linux, macOS)
        executable = os.path.join(whisper_path, "build", "bin", "whisper-cli")
    
    cmd = [
        
        #"./build/bin/whisper-cli"
        executable,
        #"-m", "models/ggml-"+model_name+'.bin',
        '-m', os.path.join('models', f'ggml-{model_name}.bin'),
        "-l", "ru",
        "--no-timestamps",
        #"--output-txt",
        "-f", audio_file
    ]

    original_cwd = os.getcwd()
    try:
        if os.path.exists(whisper_path):
            os.chdir(whisper_path)
            res = subprocess.run(cmd, check=True, capture_output=True, text=True)
            return res.stdout.strip()
        else:
            raise FileNotFoundError('whisper.cpp не найден')
        
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Ошибка транскрибации: {e}")
    finally:
        os.chdir(original_cwd)

if __name__ == "__main__":
    try:
        text = transcribe_audio(audio_file='/Users/matvejsobolev/Desktop/2025-10-04_11:57:14.wav', model_name='large-v3-turbo-q5_0')
        print(f"Результат транскрибации:\n{text}")
    except Exception as e:
        print(f"Ошибка: {e}")
    

 