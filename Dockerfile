FROM python:3.11


RUN apt-get update && \
    apt-get install -y openssl libssl-dev && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade -r requirements.txt

COPY backend /app/backend

ENV DOTNET_SYSTEM_GLOBALIZATION_INVARIANT=1

CMD ["gunicorn", "backend.app:app", "--workers", "4", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]