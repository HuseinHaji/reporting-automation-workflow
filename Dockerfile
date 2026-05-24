FROM python:3.10-slim
WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY requirements.txt ./
COPY requirements-dev.txt ./
RUN pip install --upgrade pip && pip install -r requirements.txt || true

COPY src/ ./src/
COPY data/ ./data/
COPY config/ ./config/
COPY output/ ./output/

EXPOSE 8501
CMD ["streamlit", "run", "src/app.py", "--server.port", "8501", "--server.headless", "true"]
