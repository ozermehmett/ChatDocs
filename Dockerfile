FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY src/backend/ ./src/backend/
COPY scripts/ ./scripts/

EXPOSE 8080

CMD ["python", "scripts/run_backend.py"]