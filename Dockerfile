# TimeBlock Organizer - Production Image
FROM python:3.13-slim

LABEL maintainer="Fabio Lima"
LABEL version="1.4.1"
LABEL description="TimeBlock Organizer CLI - Atomic Habits Time Management"

# Prevent Python from writing pyc files and buffering stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Create non-root user for security
RUN groupadd --gid 1000 timeblock && \
    useradd --uid 1000 --gid 1000 --create-home timeblock

WORKDIR /app

# Install dependencies first (better layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY cli/src/ ./src/
COPY cli/pyproject.toml .

# Install the package
RUN pip install --no-cache-dir -e .

# Create data directory for SQLite
RUN mkdir -p /data && chown timeblock:timeblock /data
ENV TIMEBLOCK_DB_PATH=/data/timeblock.db

# Switch to non-root user
USER timeblock

# Default command
ENTRYPOINT ["python", "-m", "timeblock.main"]
CMD ["--help"]
