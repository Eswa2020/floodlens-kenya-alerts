# Stub-mode image for the FloodLens API. Build from the repo root:
#   docker build -f deploy/Dockerfile -t floodlens-kenya .
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
ENV FLOODLENS_MODE=stub
EXPOSE 8080
CMD ["uvicorn", "services.reports.app:app", "--host", "0.0.0.0", "--port", "8080"]
