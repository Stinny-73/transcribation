# Docker Setup для Python 3.13.7 приложения

## Требования

- Docker 20.10+
- Docker Compose (опционально)

## Структура файлов

```
.
├── Dockerfile
├── .dockerignore
├── docker-compose.yml
├── requirements.txt
└── main.py  # Ваше приложение
```

## Сборка образа

### Вариант 1: Использование Docker

```bash
# Сборка образа
docker build -t my-flet-app:latest .

# Запуск контейнера
docker run -d \
  --name flet-app \
  -p 8550:8550 \
  -v $(pwd)/data:/app/data \
  my-flet-app:latest
```

### Вариант 2: Использование Docker Compose (рекомендуется)

```bash
# Сборка и запуск
docker-compose up -d

# Просмотр логов
docker-compose logs -f

# Остановка
docker-compose down

# Пересборка после изменений
docker-compose up -d --build
```

## Работа с аудио

Если ваше приложение использует PyAudio или sounddevice, убедитесь, что:

1. Docker имеет доступ к аудио устройствам (уже настроено в docker-compose.yml)
2. На хост-системе установлены необходимые драйверы

### Linux
```bash
# Проверка доступа к аудио
docker run --rm --device /dev/snd my-flet-app:latest python -c "import sounddevice; print(sounddevice.query_devices())"
```

### macOS/Windows
Аудио устройства могут работать иначе в Docker. Рассмотрите возможность использования volume mapping или запуска напрямую.

## Оптимизация размера образа

Текущий размер образа будет ~3-4 GB из-за PyTorch. Для уменьшения:

1. **Используйте multi-stage build** (если не нужны все инструменты разработки в production)
2. **Используйте CPU-версию PyTorch** (уже используется)
3. **Удалите ненужные зависимости**

## Устранение неполадок

### Проблема: onnxruntime не устанавливается

Если возникают проблемы с onnxruntime==1.23.1:

```bash
# Попробуйте более новую версию
pip install onnxruntime --upgrade
```

Или измените в requirements.txt:
```
onnxruntime>=1.20.0
```

### Проблема: PyAudio не работает

```bash
# Проверьте, что portaudio установлен в контейнере
docker exec -it flet-app bash
apt-get update && apt-get install -y portaudio19-dev
```

### Проблема: Flet не отображается

Flet может работать в двух режимах:
- **Web mode** (порт 8550) - работает в браузере
- **Desktop mode** - требует X11 forwarding

Для desktop mode на Linux:
```bash
xhost +local:docker
docker run -e DISPLAY=$DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix my-flet-app
```

## Переменные окружения

Создайте файл `.env` для настройки:

```env
# Пример
PYTHONUNBUFFERED=1
FLET_PORT=8550
LOG_LEVEL=INFO
```

Загрузите в docker-compose.yml:
```yaml
env_file:
  - .env
```

## Производительность

### Кэширование pip пакетов

Dockerfile уже оптимизирован для кэширования слоев. При изменении кода пересборка будет быстрой.

### Мониторинг ресурсов

```bash
# Использование ресурсов
docker stats flet-app

# Логи
docker logs -f flet-app
```

## Команды для разработки

```bash
# Войти в контейнер
docker exec -it flet-app bash

# Запустить команду в контейнере
docker exec flet-app python -c "import torch; print(torch.__version__)"

# Копировать файлы из контейнера
docker cp flet-app:/app/output.txt ./

# Просмотр установленных пакетов
docker exec flet-app pip list
```

## Примечания

- Образ использует `python:3.13.7-slim-bookworm` для баланса между размером и функциональностью
- PyTorch устанавливается с CPU-версией для экономии места
- Все системные зависимости для аудио включены
- Порт 8550 открыт для Flet приложений

## Лицензия

Укажите вашу лицензию здесь.
