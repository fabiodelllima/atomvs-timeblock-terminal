FROM python:3.13-slim

LABEL maintainer="fabiodelllima"
LABEL version="1.7.0-dev"
LABEL description="ATOMVS TimeBlock Terminal"

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/
COPY pyproject.toml .

RUN pip install --no-cache-dir -e .

ENTRYPOINT ["timeblock"]
