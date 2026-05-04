module.exports = {
  apps: [{
    name: 'scraper-web',
    script: 'app.py',
    interpreter: './venv/bin/python3',
    cwd: __dirname,
    autorestart: true,
    watch: false,
    max_memory_restart: '300M',
    env: {
      FLASK_ENV: 'production'
    }
  }]
};