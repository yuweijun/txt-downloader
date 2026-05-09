# Web Content Scraper

A web-based HTML content scraping tool with auto pagination, clean text formatting, and smart file management.

## Features

- 🚀 **One-click web scraping**: Input URL, CSS selectors, and filename to start crawling
- 📄 **Smart pagination**: Automatically follows "next page" links
- 📝 **Clean text output**: Extract and format content from HTML
- 📂 **Auto file management**: Keeps only the latest 50 files, older ones automatically deleted
- 📋 **Download history**: View and download all generated files
- 🗑️ **Easy cleanup**: Delete unwanted files with one click
- 🔒 **Safe scraping**: Max 1000 pages per session, duplicate detection

## Quick Start

### 1. Install Dependencies

```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # Mac/Linux
# venv\Scripts\activate   # Windows

# Install required packages
pip install -r requirements.txt
```

### 2. Start the Application

```bash
# Development mode
python app.py

# Production mode (with PM2)
pm2 start ecosystem.config.js
```

### 3. Access the Web Interface

- **Development**: http://localhost:9000
- **Production** (with Nginx): http://localhost:8080/txt-downloader/

## Nginx Configuration (Optional)

If you want to deploy with Nginx reverse proxy, configure Nginx as follows:

### For macOS (Homebrew Nginx)

Edit `/opt/homebrew/etc/nginx/nginx.conf`:

```nginx
http {
  server {
    listen 8080;
    server_name localhost;

    # Your other location blocks...

    # Proxy /txt-downloader/ to Flask app
    location /txt-downloader/ {
      proxy_pass http://127.0.0.1:9000/txt-downloader/;
      proxy_http_version 1.1;
      
      # Forward headers
      proxy_set_header Host $host;
      proxy_set_header X-Real-IP $remote_addr;
      proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
      proxy_set_header X-Forwarded-Proto $scheme;
      proxy_set_header Connection "";
      
      # Disable buffering for better streaming
      proxy_buffering off;
      proxy_request_buffering off;
      
      # Timeouts for long scraping tasks
      proxy_read_timeout 300s;
      proxy_connect_timeout 75s;
      
      # Pass through headers
      proxy_pass_request_headers on;
      proxy_set_header Accept-Encoding "";
    }
  }
}
```

**Important**: 
- Use `location /txt-downloader/` (with trailing slash)
- Use `proxy_pass http://127.0.0.1:9000/txt-downloader/;` (with trailing slash)
- Do NOT use regex patterns like `location ~ ^/txt-downloader(.*)$`
- This ensures Flask receives the full path including `/txt-downloader` prefix

### For Linux (System Nginx)

Create `/etc/nginx/sites-available/txt-downloader`:

```nginx
server {
  listen 80;
  server_name yourdomain.com;

  location /txt-downloader/ {
    proxy_pass http://127.0.0.1:9000/txt-downloader/;
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

### Reload Nginx After Configuration Changes

```bash
# Test configuration first
nginx -t

# Reload if test passes
nginx -s reload
```

## How to Use

1. **Fill in the form**:
   - **Save as**: Output filename (e.g., `mybook.txt`)
   - **Target URL**: The webpage you want to scrape
   - **Title CSS Selector**: CSS selector for the title (e.g., `h1`, `#chaptertitle`)
   - **Content CSS Selector**: CSS selector for content (e.g., `.content`, `#novelcontent`)

2. **Click "Start Scraping"**: The tool will automatically follow pagination links

3. **Download your file**: Find it in the file list below the form

## Example

### Scraping a Novel Website

- **URL**: `https://example.com/novel/chapter-1`
- **Title Selector**: `#chaptertitle`
- **Content Selector**: `#novelcontent`
- **Filename**: `my-novel.txt`

The scraper will:
1. Extract the chapter title and content
2. Follow "Next Chapter" links automatically
3. Save all chapters to a single text file
4. Stop when no more "next" links are found

## File Management

- All downloaded files are saved to the `downloads/` folder
- Only the **latest 50 files** are kept
- Older files are automatically deleted to save disk space
- You can delete files manually using the delete button

## Supported Pagination Patterns

The scraper automatically detects these "next page" link patterns:

- **Chinese**: 下一页, 下一章, 下页, 下章
- **English**: Next Page, Next Chapter, next page, next chapter

## Configuration

### Change File Retention Limit

Edit `scraper.py`:

```python
MAX_FILES_RETENTION = 50  # Change to your desired limit
```

Then restart the application.

### Production Deployment

For production deployment with PM2 and Nginx, see `AGENT.md` for detailed setup instructions.

## Logs

Application logs are available through PM2 or direct file access:

### PM2 Logs (Recommended)

```bash
# Real-time logs (includes access logs + application logs + errors)
pm2 logs txt-downloader

# Last 50 lines
pm2 logs txt-downloader --lines 50

# Only errors
pm2 logs txt-downloader --err

# Clear old logs
pm2 flush txt-downloader
```

PM2 logs include:
- ✅ **HTTP access logs** - All requests with IP, status codes, response time
- ✅ **Flask application logs** - Info, warnings, and debug messages
- ✅ **Python errors** - Exceptions and stack traces

Example output:
```
127.0.0.1 - - [09/May/2026:14:10:45 +0800] "GET /txt-downloader/ HTTP/1.1" 200 1234
[2026-05-09 14:10:45 +08:00] INFO in app: Index page accessed
[2026-05-09 14:10:45 +08:00] INFO in app: Found 2 downloaded files
```

### Direct File Access

Application logs are stored in the `logs/` directory with monthly rotation:

```bash
# Real-time application logs
tail -f logs/app.log

# Search for errors
grep ERROR logs/app.log

# View specific month
cat logs/app.log.2026-05
```

Files:
- **`app.log`** - Current month's application logs
- **`app.log.YYYY-MM`** - Archived monthly logs (keeps 12 months)
- **`pm2-out.log`** - PM2 stdout capture
- **`pm2-err.log`** - PM2 stderr capture

## Troubleshooting

### Common Issues

**Problem**: Next page links not detected  
**Solution**: Check the HTML source and adjust the CSS selectors

**Problem**: Scraping takes too long  
**Solution**: Each session has a 300-second timeout and 1000-page limit

**Problem**: Files not downloading  
**Solution**: Check the `downloads/` folder permissions

For technical troubleshooting, see `AGENT.md`.

## Safety & Ethics

- ⚠️ **Educational use only**: This tool is for personal learning
- 🚫 **Respect robots.txt**: Check website's scraping policy
- 🔒 **No copyrighted content**: Only scrape content you have permission to use
- ⏱️ **Be considerate**: The tool includes built-in rate limiting

## Requirements

- Python 3.7 or higher
- Flask, Requests, BeautifulSoup4 (installed via requirements.txt)
- Optional: PM2 for process management
- Optional: Nginx for reverse proxy

## Documentation

- `README.md` - This file (user guide)
- `AGENT.md` - Technical documentation for developers
- `PM2_COMMANDS.md` - PM2 command reference
- `LOGGING.md` - Logging configuration details
- `FILE_RETENTION.md` - File management documentation

## License

MIT License

## Changelog

### v2.1 (2026-05-09)
- ✅ Fixed Chinese filename support
- ✅ Added file delete button
- ✅ Form values retained after scraping
- ✅ Improved mobile-friendly layout (640px width)
- ✅ Separated CSS and JavaScript into static files

### v2.0 (2026-05-08)
- ✅ Production deployment with Gunicorn and PM2
- ✅ Monthly log rotation
- ✅ Enhanced pagination detection
- ✅ Auto file retention (50 files max)
- ✅ Duplicate URL prevention

### v1.0
- Initial release with basic scraping
