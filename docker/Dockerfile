FROM python:3.12

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV DEBUG=1

# Set work directory
WORKDIR /app

# Install PostgreSQL client and gettext
RUN apt-get update \
    && apt-get install -y \
        postgresql-client \
        gettext \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements/base.txt requirements/base.txt
COPY requirements/dev.txt requirements/dev.txt
RUN pip install --no-cache-dir -r requirements/dev.txt

# Copy project files
COPY src /app/src/

# Expose port
EXPOSE 8000

# Command to run
CMD ["python", "src/manage.py", "runserver", "0.0.0.0:8000"]