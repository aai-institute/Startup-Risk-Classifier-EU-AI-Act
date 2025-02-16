# Use an official Python 3.12 slim image
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .

# Run the required commands
RUN apt-get update -y && apt-get upgrade -y && \
apt-get install -y wget nano && \
mkdir -p ~/Google_Chrome && \
wget -P ~/Google_Chrome https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb && \
apt install ~/Google_Chrome/google-chrome-stable_current_amd64.deb -y && \
apt --fix-broken install -y && \
pip install -r requirements.txt

COPY . .

EXPOSE 8000

# Set environment variables for Flask
ENV FLASK_ENV=development

# Switch to gunicorn for production
# CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8000", "app:app"]
# CMD ["flask", "run", "--host=0.0.0.0", "--port=8000"]
# CMD ["python", "app.py"]
CMD ["tail", "-f", "/dev/null"]
