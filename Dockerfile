FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/

# Environment variables must be injected at runtime (do not hardcode secrets)
CMD ["python", "src/pr_reviewer.py"]