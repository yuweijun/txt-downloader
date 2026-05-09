# Development & Technical Documentation

This document contains technical information for developers and AI agents working on this project.

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
├── static/                     # Static assets
│   ├── css/
│   │   └── style.css          # Application styles
│   └── js/
│       └── main.js            # Client-side JavaScript
├── templates/
│   └── index.html             # Web UI template
├── downloads/                 # Generated TXT files (auto-created)
├── logs/                      # Application logs (auto-created)
│   ├── app.log               # Current month application log
│   ├── app.log.YYYY-MM       # Archived monthly logs
│   ├── pm2-out.log           # PM2 stdout
│   └── pm2-err.log           # PM2 stderr
├── venv/                      # Python virtual environment
├── README.md                  # User documentation
├── AGENT.md                   # This file - technical documentation
├── LOGGING.md                 # Logging documentation
├── PM2_COMMANDS.md            # PM2 command reference
├── FILE_RETENTION.md          # File retention and cleanup documentation
├── FIX_SUMMARY.md             # POST response fix documentation
└── FIX_NEXT_PAGE.md           # Next page detection fix documentation
```

## Development Setup

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

## Technical Details

### Flask Application (app.py)

- **Routes**:
  - `GET /` - Main page with form and file list
  - `POST /start` - Start scraping task
  - `GET /download/<filename>` - Download file (handles UTF-8 encoding)
  - `DELETE /delete/<filename>` - Delete file

- **Logging**: 
  - Monthly rotating file handler (12-month retention)
  - Console handler for PM2 logs
  - UTF-8 encoding support

- **URL Encoding**: 
  - Handles Chinese filenames with UTF-8/Latin-1 encoding fix
  - Multiple decoding strategies for compatibility

### Scraper Engine (scraper.py)

- **Smart Pagination**:
  - Detects various "next page" patterns
  - Chinese: '下一页', '下一章', '下—页', '下—章'
  - English: 'Next Page', 'Next Chapter'
  
- **Safety Features**:
  - Max 1000 pages per session
  - Duplicate URL detection
  - 15-second timeout per request
  
- **File Management**:
  - Auto-cleanup: keeps latest 50 files
  - Configurable retention limit
  - Cleanup runs after each scraping session

### Frontend

- **HTML/CSS/JS Separation**:
  - `templates/index.html` - Clean HTML structure
  - `static/css/style.css` - All styling
  - `static/js/main.js` - Client-side logic

- **Form Retention**:
  - URL parameters preserve form values after redirect
  - Client-side JavaScript reads params and populates form

- **File Operations**:
  - Download via anchor links with URL encoding
  - Delete via AJAX with confirmation dialog

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

## Configuration Files

### ecosystem.config.js (PM2 Configuration)

```javascript
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
      '--error-logfile', '-',
      '--log-level', 'info'
    ],
    interpreter: 'none',
    // ... other config
  }]
};
```

Key settings:
- 4 Gunicorn workers for parallel requests
- 300-second timeout for long scraping tasks
- Logs sent to stdout/stderr for PM2 capture
- Auto-restart on crashes

### scraper.py Configuration

```python
DOWNLOAD_DIR = "downloads"
MAX_FILES_RETENTION = 50  # Keep only the latest 50 files
```

To change retention limit, edit this value and restart PM2.

## Testing & Debugging

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

# PM2 logs
pm2 logs txt-downloader --lines 50

# Nginx errors (macOS)
tail -50 /opt/homebrew/var/log/nginx/error.log

# Nginx errors (Linux)
tail -50 /var/log/nginx/error.log
```

## Troubleshooting

### POST request returns no response body
- **Issue**: Older versions had issues with proxied POST requests
- **Solution**: Updated to use Gunicorn instead of Flask dev server
- See `FIX_SUMMARY.md` for details

### Next page links not detected
- **Issue**: Website uses em dash (—) instead of Chinese character (一)
- **Solution**: Enhanced pattern matching to detect various link formats
- See `FIX_NEXT_PAGE.md` for details

### Chinese filenames return 404
- **Issue**: UTF-8 encoding issue with URL-encoded filenames
- **Solution**: Implemented multi-strategy decoding (Latin-1 → UTF-8 fix)
- Both download and delete endpoints handle encoding properly

### Form values not retained after redirect
- **Issue**: URL parameters not passed through reverse proxy
- **Solution**: Client-side JavaScript reads URL params and populates form
- Works regardless of proxy configuration

## Code Style

- **Python**: 2-space indentation
- **JavaScript**: 2-space indentation
- **HTML**: 2-space indentation
- **CSS**: 2-space indentation

## Dependencies

- **Python 3.7+**
- **Flask**: Web framework
- **Requests**: HTTP library
- **BeautifulSoup4**: HTML parsing
- **Gunicorn**: Production WSGI server
- **PM2**: Process manager (Node.js)
- **Nginx**: Reverse proxy

## Security Considerations

- User-Agent header mimics browser
- 15-second timeout prevents hanging requests
- Max 1000 pages prevents runaway scraping
- Duplicate URL detection prevents loops
- No authentication (intended for local/internal use)

## Recent Fixes & Improvements

### v2.1 (2026-05-09)
- ✅ Fixed Chinese filename download (UTF-8 encoding)
- ✅ Fixed Chinese filename deletion
- ✅ Added delete button for files
- ✅ Form value retention after scraping
- ✅ PM2 logs now show Gunicorn access logs
- ✅ Refactored HTML/CSS/JS into separate files
- ✅ Reduced body width to 640px for better mobile view
- ✅ Improved UI: removed headings, consistent styling

### v2.0 (2026-05-08)
- ✅ Switched to Gunicorn for production deployment
- ✅ Added PM2 process management
- ✅ Implemented monthly log rotation
- ✅ Enhanced next page detection
- ✅ Added duplicate URL prevention
- ✅ Auto file retention (50 files)

## Support

For issues and feature requests, please open an issue in the repository.
