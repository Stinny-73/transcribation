import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

class Config:
    BASE_DIR = Path(__file__).resolve().parent
    print(BASE_DIR)
    # load_dotenv(BASE_DIR / ".env")
    API_DEEPSEEK = os.getenv('API_DEEPSEEK')
    @classmethod
    def validate(cls):
        if not cls.API_DEEPSEEK:
            raise ValueError('API_DEEPSEEK не найден в переменных окружения')
config = Config()