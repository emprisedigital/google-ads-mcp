FROM python:3.12-slim
RUN pip install uv
WORKDIR /app
COPY . .
RUN uv sync
EXPOSE 8080
CMD ["uv", "run", "main.py", "--transport", "sse", "--host", "0.0.0.0", "--port", "8080"]
