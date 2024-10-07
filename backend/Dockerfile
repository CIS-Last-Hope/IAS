FROM python:3.11

WORKDIR /app

COPY requirements.txt ./backend/

RUN pip install -r ./backend/requirements.txt

COPY . ./backend

EXPOSE 8000

CMD ["gunicorn", "backend.app:app", "--workers", "4", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]