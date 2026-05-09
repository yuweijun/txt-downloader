module.exports = {
  apps: [{
    name: 'txt-downloader',
    script: 'venv/bin/gunicorn',
    args: [
      'app:app',
      '--bind', '127.0.0.1:9000',
      '--workers', '4',
      '--timeout', '300',
      '--access-logfile', '-',
      '--access-logformat', '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"',
      '--error-logfile', '-',
      '--log-level', 'info',
      '--capture-output'
    ],
    interpreter: 'none',
    cwd: __dirname,
    instances: 1,
    autorestart: true,
    watch: false,
    max_memory_restart: '300M',
    min_uptime: '10s',
    max_restarts: 10,
    restart_delay: 4000,
    error_file: './logs/pm2-err.log',
    out_file: './logs/pm2-out.log',
    log_date_format: 'YYYY-MM-DD HH:mm:ss Z',
    merge_logs: true,
    env: {
      FLASK_ENV: 'production',
      PYTHONUNBUFFERED: '1',
      PORT: '9000'
    },
    env_development: {
      FLASK_ENV: 'development',
      FLASK_DEBUG: '1',
      PORT: '9000'
    }
  }]
};