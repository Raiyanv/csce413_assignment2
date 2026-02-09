FROM python:3.11-slim

WORKDIR /app

# Install paramiko
RUN pip install paramiko

COPY honeypot.py .

# Create logs directory
RUN mkdir -p /app/logs

EXPOSE 22

CMD ["python", "-u", "honeypot.py"]
