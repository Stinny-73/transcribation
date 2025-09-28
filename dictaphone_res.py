#🎤
#font=('Apple Color Emoji', 270),
import tkinter as tk
from tkinter import ttk
import pyaudio
import wave
import os
import threading
from tkinter import filedialog, messagebox
from pathlib import Path
import whisper_try
from datetime import datetime

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
            font=('Arial', 235),
            borderwidth=0,
            relief='flat'
        )
        self.style.map(
            'TButton',
            background=[('active', '#808080')],
            foreground=[('active', '#808080')]
        )
        self.btn = ttk.Button(self.root, text="🎙", command=self.change_color, style='TButton')
        self.top_frame = tk.Frame(self.root)
        self.top_frame.pack(side="top", fill="x")
        self.btn.pack(side='bottom')
        self.flag = False
        self.modelswp = ['tiny', 'base', 'base.en', 'medium', 'large-v3-turbo-q5_0']
        self.current_version = tk.StringVar()
        self.model_combobox = ttk.Combobox(
        self.root,                     # родительский контейнер
        textvariable=self.current_version,  # связываем с переменной
        values=self.modelswp,          # список вариантов
        state="readonly",         # запрещаем ручной ввод (только выбор из списка)
        font=("Arial", 14),
        width=20                  # ширина в символах
        )
        self.model_combobox.set("large-v3-turbo-q5_0") 
        self.model_combobox.pack(in_=self.top_frame, side="right")
        self.cond = tk.StringVar()
        self.cond.set('⚪ Не активно')
        self.label = tk.Label(self.root, textvariable=self.cond, font=("Arial", 14), bg="#545353", width=15)
        self.label.pack(in_=self.top_frame, side="left")
        self.root.mainloop()

    def change_color(self):

        self.flag =  not self.flag
        if self.flag:
            self.cur = self.current_version.get()
            print('000000000000', self.cur)
            self.style.configure('TButton', background='salmon', foreground='white')
            self.style.map('TButton', background=[('active', 'salmon')], foreground=[('active', 'salmon')])
            self.cond.set('🔴 Активно')
            self.label.config(bg="#DF1111")
            #ЗАПУСК ФУНКЦИИ РЕКОРД
            threading.Thread(target=self.record, daemon=True).start()

        else:
            self.style.configure('TButton', background='#808080', foreground='white')
            self.style.map('TButton', background=[('active', '#808080')], foreground=[('active', '#808080')])
            self.cond.set('⚪ Не активно')
            self.label.config(bg="#545353")



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
            folder_path = filedialog.askdirectory(title="Выберите папку для сохранения")
            

            #desktop = Path.home() / "Desktop" / "VoiceRecordings"
            desktop2 = Path.home() / folder_path / 'VoiceRecordings'
            os.makedirs(desktop2, exist_ok=True)
            date = str(datetime.now())[:10]+'_'+str(datetime.now())[11:-7]
            # Создаём путь к файлу
            filename = desktop2 / f'{date}.wav'

            # Открываем файл для записи
            sound_file = wave.open(str(filename), 'wb')
            sound_file.setnchannels(1)
            sound_file.setsampwidth(audio.get_sample_size(pyaudio.paInt32))
            sound_file.setframerate(44100)
            sound_file.writeframes(b''.join(frames))
            sound_file.close()
            
            text = whisper_try.transcribe_audio(str(filename), str(self.cur))
            text_path = filename.with_suffix('.txt')
            
            with open(text_path, 'w', encoding='utf-8') as file:
                file.write(text)
            print(f'переведено с помощью:{self.cur}')
            
            


VoiceRecorder()