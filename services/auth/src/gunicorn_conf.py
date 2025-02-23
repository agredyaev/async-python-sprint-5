import os

bind = f"0.0.0.0:{os.getenv('APP_PORT')}"
workers = 1
threads = 2
worker_class = "uvicorn.workers.UvicornWorker"

loglevel = "info"
accesslog = "-"
errorlog = "-"

capture_output = True
