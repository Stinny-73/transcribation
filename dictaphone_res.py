#🎤
#font=('Apple Color Emoji', 270),
import tkinter as tk
from tkinter import ttk
import pyaudio
import wave
import os
import threading
from tkinter import messagebox
from pathlib import Path
import whisper_try


class VoiceRecorder:
    def __init__(self):
        self.root = tk.Tk()
        self.root.geometry("300x300")
        self.root.resizable(False, False)
        self.root.title("Voice Recorder")
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure(
            'TButton',
            background='#808080',
            foreground='#808080',
            font=('Arial', 270),
            borderwidth=0,
            relief='flat'
        )
        self.style.map(
            'TButton',
            background=[('active', '#808080')],
            foreground=[('active', '#808080')]
        )
        self.btn = ttk.Button(self.root, text="🎙", command=self.change_color, style='TButton')

        self.btn.pack(expand=True)
        self.flag = False
        self.root.mainloop()

    def change_color(self):

        self.flag =  not self.flag
        if self.flag:
            self.style.configure('TButton', background='salmon', foreground='white')
            self.style.map('TButton', background=[('active', 'salmon')], foreground=[('active', 'salmon')])
            #ЗАПУСК ФУНКЦИИ РЕКОРД
            threading.Thread(target=self.record, daemon=True).start()

        else:
            self.style.configure('TButton', background='#808080', foreground='white')
            self.style.map('TButton', background=[('active', '#808080')], foreground=[('active', '#808080')])



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

        frames = []


        while self.flag:
            data = stream.read(1024, exception_on_overflow=False)
            frames.append(data)

        stream.stop_stream()
        stream.close()
        audio.terminate()

        exists = True
        i = 1
        desktop = Path.home() / "Desktop" / "VoiceRecordings"
        os.makedirs(desktop, exist_ok=True)
        while exists:
            #if os.path.exists(f'recording{i}.wav'):
            if (desktop / f"recording{i}.wav").exists():
                i += 1
            else:
                exists = False
        self.qsn = messagebox.askyesno("Saving", "Вы хотите сохранить эту запись?")
        if self.qsn:



            desktop = Path.home() / "Desktop" / "VoiceRecordings"
            os.makedirs(desktop, exist_ok=True)

            # Создаём путь к файлу
            filename = desktop / f"recording{i}.wav"

            # Открываем файл для записи
            sound_file = wave.open(str(filename), 'wb')
            sound_file.setnchannels(1)
            sound_file.setsampwidth(audio.get_sample_size(pyaudio.paInt32))
            sound_file.setframerate(44100)
            sound_file.writeframes(b''.join(frames))
            sound_file.close()
            
            text = whisper_try.transcribe_audio(str(filename))
            text_path = f'{filename}.txt'
            with open(text_path, 'w', encoding='utf-8') as file:
                file.write(text)
            
            


VoiceRecorder()