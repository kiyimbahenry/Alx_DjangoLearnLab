# Gunicorn configuration for secure Django deployment
import multiprocessing

# Server socket
bind = "unix:/path/to/your/project/gunicorn.sock"
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = 'sync'
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 50
timeout = 30
keepalive = 2

# Security
limit_request_line = 4096
limit_request_fields = 100
limit_request_field_size = 8190

# Process naming
proc_name = 'library_project'

# Server mechanics
daemon = False
pidfile = '/tmp/gunicorn_library.pid'
umask = 0o022
user = None
group = None
tmp_upload_dir = None

# Logging
errorlog = '/var/log/gunicorn/error.log'
loglevel = 'info'
accesslog = '/var/log/gunicorn/access.log'
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# Process naming
def when_ready(server):
    server.log.info("Server is ready. Serving securely with HTTPS.")

def worker_int(worker):
    worker.log.info("Worker received INT or QUIT signal")

def worker_abort(worker):
    worker.log.info("Worker received SIGABRT signal")
