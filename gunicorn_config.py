# gunicorn_config.py
from multiprocessing import cpu_count

bind = "0.0.0.0:5000"
workers = (cpu_count() * 2) + 1

worker_connections = 1000

# Production logging (Crucial for debugging VPS issues)
accesslog = "-"  # Sends access logs directly to stdout/Docker logs
errorlog = "-"   # Sends error logs directly to stderr/Docker logs
loglevel = "info"

# Safety timeout
timeout = 30  # Drops connections that hang for more than 30 seconds

# gunicorn -c gunicorn_config.py run:flask_app