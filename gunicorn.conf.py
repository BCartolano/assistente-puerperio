import os

bind = f"0.0.0.0:{os.getenv('APP_PORT', '5000')}"
workers = int(os.getenv("GUNICORN_WORKERS", "2"))
preload_app = True  # carrega app uma vez; workers herdam (overrides/cache em memória)
threads = int(os.getenv("GUNICORN_THREADS", "2"))
worker_class = "gevent"
timeout = int(os.getenv("GUNICORN_TIMEOUT", "60"))
keepalive = 30
max_requests = 1000
max_requests_jitter = 100
accesslog = "-"
errorlog = "-"
loglevel = os.getenv("LOG_LEVEL", "info").lower()

# atrás do Nginx
forwarded_allow_ips = "*"
proxy_protocol = False
