FROM python:3.11

# Set environment variables for Python buffering
ENV PYTHONUNBUFFERED 1

WORKDIR /app

# Copy the requirements file into the container at /app
COPY pyproject.toml poetry.lock /app/

# Install poetry and project dependencies
RUN pip install --no-cache-dir poetry \
    && poetry config virtualenvs.create false \
    && poetry install --no-root --no-dev

# Copy the rest of the application code into the container
COPY . /app

# Expose the port that the FastAPI application will run on (adjust as needed)
EXPOSE 8000

# Define the command to run your FastAPI application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
