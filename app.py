from flask import Flask, render_template, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
from urllib.parse import unquote
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

  # Console handler for stdout (PM2 will capture this)
  console_handler = logging.StreamHandler()
  console_handler.setLevel(logging.INFO)
  console_handler.setFormatter(formatter)

  # Configure app logger - add both file and console handlers
  app.logger.setLevel(logging.INFO)
  app.logger.addHandler(file_handler)
  app.logger.addHandler(console_handler)

  # Prevent propagation to avoid duplicate logs
  app.logger.propagate = False

  # Also configure root logger for other modules (only if not already configured)
  root_logger = logging.getLogger()
  if not root_logger.handlers:
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)

  app.logger.info('Flask application started')

@app.route('/txt-downloader/')
def index():
  app.logger.info('Index page accessed')
  app.logger.info(f'Request URL: {request.url}')
  app.logger.info(f'Request path: {request.path}')
  app.logger.info(f'Request args: {dict(request.args)}')
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

  # Get form values from URL parameters to retain after redirect
  form_values = {
    'filename': request.args.get('filename', ''),
    'url': request.args.get('url', ''),
    'title_sel': request.args.get('title_sel', '.title'),
    'content_sel': request.args.get('content_sel', 'article, .article, .content')
  }
  app.logger.info(f'Form values: {form_values}')

  return render_template('index.html', files=files, form=form_values)

@app.route('/txt-downloader/static/<path:filename>')
def static_files(filename):
  return send_from_directory('static', filename)

@app.route('/txt-downloader/start', methods=['POST'])
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

@app.route('/txt-downloader/download/<path:filename>')
def download_file(filename):
  app.logger.info(f'File download request - Filename: {filename}')

  try:
    # Flask decodes percent-encoding but may have UTF-8/Latin-1 issues
    # Try multiple decoding strategies

    # Strategy 1: Use as-is (already decoded by Flask/Werkzeug)
    file_path = os.path.join(scraper.DOWNLOAD_DIR, filename)
    app.logger.info(f'Strategy 1 - Trying as-is: {file_path}')
    if os.path.exists(file_path):
      app.logger.info(f'Found file with strategy 1')
      return send_from_directory(scraper.DOWNLOAD_DIR, filename, as_attachment=True)

    # Strategy 2: Fix double-encoding issue (Latin-1 -> UTF-8)
    # When URL-encoded UTF-8 is decoded as Latin-1, we need to re-encode and decode properly
    try:
      fixed_filename = filename.encode('latin-1').decode('utf-8')
      file_path = os.path.join(scraper.DOWNLOAD_DIR, fixed_filename)
      app.logger.info(f'Strategy 2 - Trying UTF-8 fix: {fixed_filename}')
      if os.path.exists(file_path):
        app.logger.info(f'Found file with strategy 2')
        return send_from_directory(scraper.DOWNLOAD_DIR, fixed_filename, as_attachment=True)
    except (UnicodeDecodeError, UnicodeEncodeError) as e:
      app.logger.debug(f'Strategy 2 failed: {e}')

    # Strategy 3: URL decode again
    decoded_filename = unquote(filename)
    file_path = os.path.join(scraper.DOWNLOAD_DIR, decoded_filename)
    app.logger.info(f'Strategy 3 - Trying URL decode: {decoded_filename}')
    if os.path.exists(file_path):
      app.logger.info(f'Found file with strategy 3')
      return send_from_directory(scraper.DOWNLOAD_DIR, decoded_filename, as_attachment=True)

    # List available files for debugging
    available_files = os.listdir(scraper.DOWNLOAD_DIR) if os.path.exists(scraper.DOWNLOAD_DIR) else []
    app.logger.error(f'File not found with any strategy. Available files: {available_files}')
    return jsonify({"status": "error", "msg": "File not found", "requested": filename, "available": available_files}), 404

  except Exception as e:
    app.logger.error(f'Download failed - Filename: {filename}, Error: {str(e)}', exc_info=True)
    return jsonify({"status": "error", "msg": str(e)}), 500

@app.route('/txt-downloader/delete/<path:filename>', methods=['DELETE'])
def delete_file(filename):
  app.logger.info(f'File delete request - Filename: {filename}')
  try:
    # Use the same encoding strategies as download
    decoded_filename = None

    # Strategy 1: Use as-is
    file_path = os.path.join(scraper.DOWNLOAD_DIR, filename)
    if os.path.exists(file_path):
      decoded_filename = filename

    # Strategy 2: Fix double-encoding issue (Latin-1 -> UTF-8)
    if not decoded_filename:
      try:
        fixed_filename = filename.encode('latin-1').decode('utf-8')
        file_path = os.path.join(scraper.DOWNLOAD_DIR, fixed_filename)
        if os.path.exists(file_path):
          decoded_filename = fixed_filename
      except (UnicodeDecodeError, UnicodeEncodeError):
        pass

    # Strategy 3: URL decode again
    if not decoded_filename:
      unquoted_filename = unquote(filename)
      file_path = os.path.join(scraper.DOWNLOAD_DIR, unquoted_filename)
      if os.path.exists(file_path):
        decoded_filename = unquoted_filename

    if decoded_filename:
      file_path = os.path.join(scraper.DOWNLOAD_DIR, decoded_filename)
      os.remove(file_path)
      app.logger.info(f'File deleted successfully: {decoded_filename}')
      return jsonify({"status": "success", "msg": f"File deleted successfully"}), 200
    else:
      app.logger.warning(f'File not found for deletion: {filename}')
      return jsonify({"status": "error", "msg": "File not found"}), 404

  except Exception as e:
    app.logger.error(f'Delete failed - Filename: {filename}, Error: {str(e)}')
    return jsonify({"status": "error", "msg": str(e)}), 500

if __name__ == '__main__':
  app.logger.info('Starting Flask server on 127.0.0.1:9000')
  app.run(host='127.0.0.1', port=9000, debug=False)