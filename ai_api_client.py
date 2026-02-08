import sys
from pathlib import Path
import requests
def ai_request(promt):
    url = 'https://api.deepseek.com/v1/chat/completions'
    ai_key = 'sk-5af24aa74e9c497bb5afdee3043a945b'
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {ai_key}",  
    }

    data = {
        'model': 'deepseek-reasoner',  
        'messages': [
            {'role': 'user', 'content': promt}
        ],
    }

    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 200:
        result = response.json()
        text = result['choices'][0]['message']['content']
        
        return text
    else:
        print(f"Ошибка: {response.status_code}")
        print(response.text)