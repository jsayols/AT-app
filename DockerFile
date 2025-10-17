FROM python:3.10-slim

WORKDIR /app

# Copy and install dependencies
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy app
COPY app.py /app/app.py

EXPOSE 8080

# Run Flask app with Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "app:app"]
