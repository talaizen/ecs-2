FROM python:3.12-slim

# Set environment variables for Python buffering
ENV PYTHONUNBUFFERED 1

WORKDIR /app

# Copy the project files into the container at /app
COPY . /app

# Install poetry and project dependencies
RUN apt-get update && apt-get install -y netcat-openbsd \
    && pip install --no-cache-dir poetry \
    && poetry config virtualenvs.create false \
    && poetry install --no-root --no-dev


# Set execute permissions on the wait-for-mongo script
RUN chmod +x /app/wait_for_mongo.sh

# Expose the port that the FastAPI application will run on (adjust as needed)
EXPOSE 8000

# Modify the command to run the wait-for script before starting the FastAPI app
CMD ["/app/wait_for_mongo.sh", "mongodb", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
