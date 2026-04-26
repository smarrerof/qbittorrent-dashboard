FROM python:3.12-slim

ARG VERSION=main

RUN apt-get update && apt-get install -y --no-install-recommends git \
    && rm -rf /var/lib/apt/lists/*

RUN git clone --branch $VERSION --depth 1 https://github.com/smarrerof/qbittorrent-dashboard /app

WORKDIR /app

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "-m", "collector.main"]
