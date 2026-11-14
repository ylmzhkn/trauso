FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY pyproject.toml .
COPY multi_agent_plugin ./multi_agent_plugin
RUN pip install --no-cache-dir .
EXPOSE 8787
CMD ["uvicorn", "multi_agent_plugin.api:app", "--host", "0.0.0.0", "--port", "8787"]
