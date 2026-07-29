FROM python:3.11-slim
WORKDIR /app
COPY pyproject.toml README.md ./
COPY src ./src
COPY templates ./templates
COPY static ./static
COPY data ./data
COPY artifacts ./artifacts
RUN pip install --no-cache-dir .
ENV PORT=8000 CREATIVE_BOUNTY_MODE=SAMPLE
CMD ["sh","-c","uvicorn creative_bounty.app:app --host 0.0.0.0 --port ${PORT}"]
