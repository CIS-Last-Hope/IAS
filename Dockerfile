FROM python:3.11

WORKDIR app

COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade -r requirements.txt

COPY backend /app/backend

CMD gunicorn backend.app:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind=0.0.0.0:8000