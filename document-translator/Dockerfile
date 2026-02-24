FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Expose the default FastAPI port
EXPOSE 7860

# Run the FastAPI server in production mode
CMD ["uvicorn", "scripts.web_server:app", "--host", "0.0.0.0", "--port", "7860"]
