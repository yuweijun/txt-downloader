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

Application logs are stored in the `logs/` directory:

```bash
# View real-time logs
tail -f logs/app.log

# With PM2
pm2 logs txt-downloader
```

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
