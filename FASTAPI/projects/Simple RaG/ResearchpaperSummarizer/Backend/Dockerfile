# Base image
FROM python:3.13-slim

# Working directory
WORKDIR /app

# Copy command
COPY . /app

# Run command
RUN pip install --no-cache-dir -r requirements.txt

# Port to expose
EXPOSE 8000

# Command to run the application
CMD ["uvicorn","app:app","--host","0.0.0.0","--port","8000"]