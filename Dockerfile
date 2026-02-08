# ЭТАП 1: Сборка
FROM python:3.13.7-bookworm AS builder

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    DEBIAN_FRONTEND=noninteractive

# Настраиваем APT для обхода проблем с зеркалами
RUN echo "Acquire::http::Pipeline-Depth 0;" > /etc/apt/apt.conf.d/99fixbadproxy && \
    echo "Acquire::http::No-Cache true;" >> /etc/apt/apt.conf.d/99fixbadproxy && \
    echo "Acquire::BrokenProxy true;" >> /etc/apt/apt.conf.d/99fixbadproxy && \
    echo 'Acquire::Retries "3";' >> /etc/apt/apt.conf.d/99fixbadproxy && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* /var/cache/apt/archives/*

# Устанавливаем аудио-библиотеки с обработкой ошибок
RUN apt-get update -o Acquire::Check-Valid-Until=false && \
    (apt-get install -y --no-install-recommends \
        portaudio19-dev \
        libsndfile1-dev \
        libasound2-dev || \
     apt-get install -y --no-install-recommends --fix-missing \
        portaudio19-dev \
        libsndfile1-dev \
        libasound2-dev || \
     apt-get install -y --allow-downgrades --allow-change-held-packages \
        portaudio19-dev \
        libsndfile1-dev \
        libasound2-dev) && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /build

# Копируем requirements
COPY requirements.txt .

# Создаем requirements без PyTorch
RUN grep -v "^torch" requirements.txt > requirements-no-torch.txt

# Создаем виртуальное окружение
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Обновляем pip
RUN pip install --upgrade pip setuptools wheel

# Устанавливаем все зависимости БЕЗ PyTorch
RUN pip install --no-cache-dir -r requirements-no-torch.txt

# ЭТАП 2: Runtime (минимальный образ)
FROM python:3.13.7-slim-bookworm

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/opt/venv/bin:$PATH"

# Устанавливаем ТОЛЬКО runtime библиотеки (они обычно не дают ошибок)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    libportaudio2 \
    libsndfile1 \
    libasound2 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Копируем виртуальное окружение из builder
COPY --from=builder /opt/venv /opt/venv

# Копируем приложение
COPY . .

EXPOSE 8550

CMD ["python", "func_main.py"]
