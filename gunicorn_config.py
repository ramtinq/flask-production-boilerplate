# gunicorn_config.py
bind = "0.0.0.0:5000"
workers = 5  # Usually (2 x $num_cores) + 1

# gunicorn -c gunicorn_config.py run:flask_app