from flask import Flask, render_template, request, jsonify, send_from_directory
import scraper
import os
import time
import logging
from logging.handlers import TimedRotatingFileHandler

app = Flask(__name__)

# Ensure JSON responses are not minified and properly formatted
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True
app.config['JSON_AS_ASCII'] = False

# Setup logging
log_dir = 'logs'
if not os.path.exists(log_dir):
  os.makedirs(log_dir)

# Only configure logging if not already configured (prevent duplicate handlers)
if not app.logger.handlers:
  # Create formatter
  formatter = logging.Formatter(
    '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
  )

  # File handler - rotate on the 1st of each month at midnight
  file_handler = TimedRotatingFileHandler(
    os.path.join(log_dir, 'app.log'),
    when='midnight',
    interval=1,
    backupCount=365,  # Keep 1 year of daily logs
    encoding='utf-8'
  )
  file_handler.setLevel(logging.INFO)
  file_handler.setFormatter(formatter)

  # Custom suffix for monthly grouping
  file_handler.suffix = '%Y-%m-%d'

  # Custom namer to group logs by month
  def namer(default_name):
    """Renames log files to monthly format: app.log.YYYY-MM"""
    import re
    # Pattern: app.log.2026-05-08 -> app.log.2026-05
    match = re.search(r'\.(\d{4}-\d{2})-\d{2}$', default_name)
    if match:
      base = default_name.rsplit('.', 3)[0]  # Get 'logs/app.log'
      year_month = match.group(1)  # Get '2026-05'
      return f'{base}.{year_month}'
    return default_name

  file_handler.namer = namer

  # Console handler
  console_handler = logging.StreamHandler()
  console_handler.setLevel(logging.INFO)
  console_handler.setFormatter(formatter)

  # Configure app logger
  app.logger.setLevel(logging.INFO)
  app.logger.addHandler(file_handler)
  app.logger.addHandler(console_handler)

  # Also configure root logger for other modules (only if not already configured)
  root_logger = logging.getLogger()
  if not root_logger.handlers:
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)

  app.logger.info('Flask application started')

@app.route('/')
def index():
  app.logger.info('Index page accessed')
  files = []
  if os.path.exists(scraper.DOWNLOAD_DIR):
    for fname in os.listdir(scraper.DOWNLOAD_DIR):
      if fname.endswith('.txt'):
        path = os.path.join(scraper.DOWNLOAD_DIR, fname)
        ctime = os.path.getctime(path)
        files.append({
          'name': fname,
          'ctime': ctime,
          'time_str': time.ctime(ctime)
        })
  files.sort(key=lambda x: x['ctime'], reverse=True)
  app.logger.info(f'Found {len(files)} downloaded files')
  return render_template('index.html', files=files)

@app.route('/start', methods=['POST'])
def start():
  url = request.form.get('url')
  title_sel = request.form.get('title_sel')
  content_sel = request.form.get('content_sel')
  filename = request.form.get('filename', 'result.txt')

  app.logger.info(f'Start scraping request - URL: {url}, Filename: {filename}')

  if not filename.endswith('.txt'):
    filename += '.txt'

  if not all([url, title_sel, content_sel]):
    app.logger.warning('Missing required fields in scraping request')
    response = jsonify({"status": "error", "msg": "All fields are required!"})
    response.headers['Content-Type'] = 'application/json'
    return response, 400

  try:
    app.logger.info(f'Starting scraper for {url}')
    scraper.run_spider(url, title_sel, content_sel, filename)
    app.logger.info(f'Scraping completed successfully - File: {filename}')
    response = jsonify({
      "status": "success",
      "msg": "Scrape completed successfully!"
    })
    response.headers['Content-Type'] = 'application/json'
    return response, 200
  except Exception as e:
    app.logger.error(f'Scraping failed - URL: {url}, Error: {str(e)}', exc_info=True)
    response = jsonify({"status": "error", "msg": str(e)})
    response.headers['Content-Type'] = 'application/json'
    return response, 500

@app.route('/download/<filename>')
def download_file(filename):
  app.logger.info(f'File download request - Filename: {filename}')
  try:
    return send_from_directory(scraper.DOWNLOAD_DIR, filename, as_attachment=True)
  except Exception as e:
    app.logger.error(f'Download failed - Filename: {filename}, Error: {str(e)}')
    return jsonify({"status": "error", "msg": "File not found"}), 404

if __name__ == '__main__':
  app.logger.info('Starting Flask server on 127.0.0.1:9000')
  app.run(host='127.0.0.1', port=9000, debug=False)