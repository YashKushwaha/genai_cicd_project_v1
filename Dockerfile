# Use an official Python image
FROM python:3.11-slim

# Set environment variables
ENV POETRY_VERSION=2.1.3 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install Poetry
RUN pip install "poetry==$POETRY_VERSION"

# Set working directory to root
WORKDIR /

# Copy only poetry files first to leverage Docker cache
COPY pyproject.toml poetry.lock ./

# Install dependencies
RUN poetry config virtualenvs.create false \
  && poetry install --no-interaction --no-ansi --no-root

# Copy everything else (minus ignored items in .dockerignore)
COPY . .

# Expose FastAPI port
EXPOSE 8000

# Run the app
CMD ["uvicorn", "back_end.main:app", "--host", "0.0.0.0", "--port", "8000"]
