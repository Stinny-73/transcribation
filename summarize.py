import ollama
import os
from datetime import datetime
# Ответ приходит в виде словаря (dict)
# Текст ответа находится по ключу ['message']['content']

def summarize_file(filepath):
    try:
        # Читаем файл
        with open(filepath, 'r', encoding='utf-8') as f:
            text = f.read()
        
        if len(text) > 50000:
            print("Внимание: текст большой, суммаризация может занять время")
        
  
        prompt = f'''Напиши текст суммаризирующий исходный, сократи исходный текст на 40-60%. 
Должен быть написан на том же языке, что и исходный текст.
Должен быть только нужный текст и никаких лишних предложений и спецсимволов.
Текст для работы:\n\n{text}
'''  
 
        response = ollama.chat(
            model='gemma3:1b',
            messages=[{'role': 'user', 'content': prompt}]
        )
      
        
        date = str(datetime.now())[:10]+'_'+str(datetime.now())[11:-7].replace(':', '-')
    
        foldpath = filepath.replace(f'{os.path.basename(filepath)}', f'{date}_summarized.txt')
        with open(foldpath, 'w', encoding='utf-8') as fold:
            fold.write(response['message']['content'])
    
    
    except FileNotFoundError:
        print("Ошибка: файл не найден")
    except Exception as e:
        print(f"Ошибка: {str(e)}")

models = ollama.list()
print("Установленные модели:")

for model in models['models']:
    print(f"- {model['model']} (размер: {model['size'] / 1e9:.2f} ГБ)")
