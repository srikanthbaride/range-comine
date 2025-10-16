
# Simple reproducible container for Range–CoMine
FROM python:3.11-slim

# System deps for matplotlib (headless)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libfreetype6-dev \
    libpng-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . /app

# Install package + deps
RUN python -m pip install -U pip && \
    pip install -r requirements.txt && \
    pip install -e .

# Default command runs tests; override with `docker run ... <cmd>`
CMD ["pytest", "-q"]
