# Web Content Scraper

A production-ready, web-based HTML content scraping tool with auto pagination, clean text formatting, monthly log rotation, and proxied deployment support.

## Features

- 🚀 **One-click web scraping**: Input URL, CSS selectors, and output filename to start crawling
- 📄 **Smart pagination**: Automatically detect and follow various "next page" link formats:
  - Chinese: '下一页', '下一章', '下—页', '下—章', '下页', '下章'
  - English: 'Next Page', 'Next Chapter'
- 📝 **Clean text formatting**: Extract and format content from HTML
- 📂 **Smart file management**: 
  - All TXT files saved to `downloads/` directory with timestamps
  - **Auto-cleanup: keeps only the latest 50 files** (configurable)
  - Oldest files automatically deleted to save disk space
- 📋 **File list display**: Homepage shows all generated files sorted by newest first
- 🔗 **Direct download**: One-click download for all generated text files
- 🚦 **Production ready**: 
  - Gunicorn WSGI server with 4 workers
  - Nginx reverse proxy support
  - PM2 process management
  - Monthly rotating logs with 12-month retention
- 🔒 **Safety features**:
  - Max 1000 pages per scraping session
  - Duplicate URL detection to prevent loops
  - Automatic old file cleanup (configurable retention limit)
  - Comprehensive error handling and logging
- 🧩 **Isolated environment**: Python virtual environment deployment

## Architecture

```
Browser (localhost:8080/txt-downloader)
    ↓
Nginx Proxy (port 8080)
    ↓
Gunicorn WSGI Server (port 9000, 4 workers)
    ↓
Flask Application + Scraper
    ↓
Downloads Directory
```

## Project Structure

```
txt-downloader/
├── app.py                      # Flask web application
├── scraper.py                  # Scraping core logic with smart pagination
├── requirements.txt            # Python dependencies
├── ecosystem.config.js         # PM2 process configuration
├── start.sh                    # Startup script
├── templates/
│   └── index.html              # Web UI with file list
├── downloads/                  # Generated TXT files (auto-created)
├── logs/                       # Application logs (auto-created)
│   ├── app.log                 # Current month application log
│   ├── app.log.YYYY-MM         # Archived monthly logs
│   ├── access.log              # Gunicorn access log
│   ├── gunicorn-error.log      # Gunicorn error log
│   ├── pm2-out.log             # PM2 stdout
│   └── pm2-err.log             # PM2 stderr
├── venv/                       # Python virtual environment
├── README.md                   # This file
├── LOGGING.md                  # Logging documentation
├── PM2_COMMANDS.md             # PM2 command reference
├── FILE_RETENTION.md           # File retention and cleanup documentation
├── FIX_SUMMARY.md              # POST response fix documentation
└── FIX_NEXT_PAGE.md            # Next page detection fix documentation
```

## Quick Start

### 1. Environment Setup

```bash
# Clone repository (if using Git)
git clone https://your-repo-url.git
cd txt-downloader

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # Mac/Linux
# venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt
```

### 2. Local Development

```bash
# Activate virtual environment
source venv/bin/activate

# Run directly with Flask (development mode)
python app.py
```

Access: http://127.0.0.1:9000

### 3. Production Deployment with PM2

```bash
# Start with PM2
pm2 start ecosystem.config.js

# View status
pm2 status

# View logs
pm2 logs txt-downloader

# Restart
pm2 restart txt-downloader

# Stop
pm2 stop txt-downloader

# Save PM2 process list
pm2 save

# Setup PM2 to start on system boot
pm2 startup
```

See `PM2_COMMANDS.md` for more PM2 commands.

## Nginx Reverse Proxy Configuration

### For macOS (Homebrew Nginx)

Edit `/opt/homebrew/etc/nginx/nginx.conf`:

```nginx
http {
  # ... other http config ...

  server {
    listen       8080;
    server_name  localhost;

    # Serve static files from nginx html directory
    location / {
      root   html;
      index  index.html index.htm;
    }

    # Proxy /txt-downloader/* to Flask app on port 9000
    location ~ ^/txt-downloader(.*)$ {
      proxy_pass   http://127.0.0.1:9000$1;
      proxy_http_version 1.1;
      
      # Forward original request headers
      proxy_set_header Host $host;
      proxy_set_header X-Real-IP $remote_addr;
      proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
      proxy_set_header X-Forwarded-Proto $scheme;
      proxy_set_header Connection "";
      
      # Disable buffering for better streaming
      proxy_buffering off;
      proxy_request_buffering off;
      
      # Timeouts for long-running scraping tasks
      proxy_read_timeout 300s;
      proxy_connect_timeout 75s;
      
      # Ensure response headers pass through
      proxy_pass_request_headers on;
      proxy_set_header Accept-Encoding "";
    }

    error_page   500 502 503 504  /50x.html;
    location = /50x.html {
      root   html;
    }
  }
}
```

### For Linux (System Nginx)

Create `/etc/nginx/sites-available/txt-downloader`:

```nginx
server {
  listen 80;
  server_name yourdomain.com;  # Replace with your domain

  location /txt-downloader {
    proxy_pass http://127.0.0.1:9000;
    proxy_http_version 1.1;
    
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_set_header Connection "";
    
    proxy_buffering off;
    proxy_request_buffering off;
    proxy_read_timeout 300s;
    proxy_connect_timeout 75s;
    
    proxy_pass_request_headers on;
    proxy_set_header Accept-Encoding "";
  }
}
```

Enable and reload:

```bash
# Create symbolic link
sudo ln -s /etc/nginx/sites-available/txt-downloader /etc/nginx/sites-enabled/

# Test configuration
sudo nginx -t

# Reload nginx
sudo systemctl reload nginx
```

### HTTPS Configuration (Production)

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Obtain SSL certificate
sudo certbot --nginx -d yourdomain.com

# Certbot will automatically update your nginx config for HTTPS
```

## Usage

1. **Access the web interface**:
   - Direct: http://localhost:9000
   - Via Nginx: http://localhost:8080/txt-downloader/

2. **Fill in the form**:
   - **Save as**: Output filename (e.g., `mybook.txt`)
   - **Target URL**: The webpage to scrape
   - **Title CSS Selector**: Selector for title element (e.g., `h1`, `#chaptertitle`)
   - **Content CSS Selector**: Selector for content (e.g., `.content`, `#novelcontent`)

3. **Start scraping**: Click "Start Scraping" button

4. **Monitor progress**: Check logs in real-time:
   ```bash
   pm2 logs txt-downloader
   # or
   tail -f logs/app.log
   ```

5. **Download results**: Files appear in the download list on the homepage

## Example Usage

### Example 1: Novel Website
- **URL**: `https://m.kudushu.org/html/1080011/143756692/`
- **Title Selector**: `#chaptertitle`
- **Content Selector**: `#novelcontent`
- **Filename**: `novel.txt`

The scraper will:
1. Extract chapter title and content
2. Follow "下—页" links for multi-page chapters
3. Follow "下—章" links to next chapters
4. Continue until no more "next" links found (up to 1000 pages max)

### Example 2: Blog Posts
- **URL**: `https://example.com/blog/post-1`
- **Title Selector**: `.post-title`
- **Content Selector**: `.post-content`
- **Filename**: `blog-posts.txt`

## Logging

All application logs are stored in the `logs/` directory with monthly rotation:

- **`app.log`**: Current month's application logs
- **`app.log.YYYY-MM`**: Archived logs (keeps 12 months)
- **`access.log`**: HTTP access logs from Gunicorn
- **`gunicorn-error.log`**: Gunicorn error logs

View logs:
```bash
# Real-time application logs
tail -f logs/app.log

# Search for errors
grep ERROR logs/app.log

# View specific month
cat logs/app.log.2026-05
```

See `LOGGING.md` for detailed logging configuration.

## File Retention

The application automatically manages disk space by keeping only the **latest 50 downloaded files**.

### How it works:
- After each successful scraping session, cleanup runs automatically
- Files are sorted by modification time (newest first)
- The 50 most recent files are kept
- Older files beyond the limit are automatically deleted

### Configuration:

To change the retention limit, edit `scraper.py`:

```python
MAX_FILES_RETENTION = 50  # Change to your desired limit
```

Then restart:
```bash
pm2 restart txt-downloader
```

### Monitoring cleanup:

```bash
# Watch cleanup activity
tail -f logs/app.log | grep -i "delete\|cleanup"

# See what was deleted
grep "Deleted old file" logs/app.log
```

See `FILE_RETENTION.md` for complete documentation including:
- How to disable auto-cleanup
- Manual cleanup procedures
- Testing and troubleshooting
- Best practices for archiving important files

## Troubleshooting

### POST request returns no response body
- **Issue**: Older versions had issues with proxied POST requests
- **Solution**: Updated to use Gunicorn instead of Flask dev server
- See `FIX_SUMMARY.md` for details

### Next page links not detected
- **Issue**: Website uses em dash (—) instead of Chinese character (一)
- **Solution**: Enhanced pattern matching to detect various link formats
- See `FIX_NEXT_PAGE.md` for details

### Check application status
```bash
# PM2 status
pm2 status

# Check if gunicorn is running
ps aux | grep gunicorn

# Check nginx
sudo nginx -t
```

### View error logs
```bash
# Application errors
tail -50 logs/app.log

# Gunicorn errors
tail -50 logs/gunicorn-error.log

# Nginx errors (macOS)
tail -50 /opt/homebrew/var/log/nginx/error.log

# Nginx errors (Linux)
tail -50 /var/log/nginx/error.log
```

## Dependencies

- **Python 3.7+**
- **Flask**: Web framework
- **Requests**: HTTP library
- **BeautifulSoup4**: HTML parsing
- **Gunicorn**: Production WSGI server
- **PM2**: Process manager (Node.js)
- **Nginx**: Reverse proxy

## Configuration Files

- **`ecosystem.config.js`**: PM2 process configuration
  - 4 Gunicorn workers
  - 300-second timeout for long-running scrapes
  - Auto-restart on crashes
  - Log rotation

- **`app.py`**: Flask application
  - Logging configuration with monthly rotation
  - Route handlers
  - JSON response formatting

- **`scraper.py`**: Scraping engine
  - Smart pagination detection
  - Duplicate URL prevention
  - Max 1000 pages safety limit

## Development

### Run tests
```bash
source venv/bin/activate

# Test scraper
python test_scraper.py

# Test endpoints
python test_endpoint.py
```

### Debug page structure
```bash
# Analyze page links
python debug_page.py

# Detailed analysis
python debug_page2.py
```

## Security Notes

- ⚠️ This tool is for educational and personal use only
- 🚫 Respect website robots.txt and terms of service
- 🔒 Do not scrape copyrighted content without permission
- ⏱️ Built-in rate limiting through sequential requests
- 🛡️ User-Agent header mimics browser to avoid blocks

## License

MIT License - See LICENSE file for details

## Support

For issues and feature requests, please open an issue in the repository.

## Changelog

### v2.0 (2026-05-08)
- ✅ Switched to Gunicorn for production deployment
- ✅ Added PM2 process management
- ✅ Implemented monthly log rotation
- ✅ Enhanced next page detection (supports em dash variants)
- ✅ Added duplicate URL prevention
- ✅ Added max page limit (1000 pages)
- ✅ Fixed POST response body issue with proxied requests
- ✅ Comprehensive logging with multiple log levels
- ✅ Enhanced error handling in browser JavaScript
- ✅ **Auto file retention: keeps only latest 50 files** (configurable)
- ✅ Automatic cleanup of old downloads to save disk space

### v1.0 (Initial Release)
- Basic scraping functionality
- Flask development server
- Simple pagination detection