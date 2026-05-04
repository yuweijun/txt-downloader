# Web Content Scraper
A lightweight, web-based HTML content scraping tool with auto pagination, clean text formatting, and one-click file download.

## Features
- 🚀 **One-click web scraping**: Input URL, CSS selectors, and output filename to start crawling
- 📄 **Auto pagination**: Automatically detect and follow `下一页`/`下一章`/`Next Page` links
- 📝 **Clean text formatting**: Convert ``, ``, `` HTML tags to standard line breaks
- 📂 **File management**: All TXT files saved to `downloads/` directory
- 📋 **File list display**: Homepage shows all generated files sorted by creation time DESC (newest first)
- 🔗 **Direct download**: One-click download for all generated text files
- 🔒 **Production ready**: Complete Nginx HTTPS (port 443) configuration
- 🧩 **Isolated environment**: Support Python virtual environment deployment

## Parameter Rules
The script strictly follows 4 parameters in fixed order:
1. **1st parameter**: Target page URL (required)
2. **2nd parameter**: CSS selector for page title (required)
3. **3rd parameter**: CSS selector for main content (required)
4. **4th parameter**: Custom output TXT filename (optional, default: `result.txt`)

## Project Structure
```
scraper-web/
├── app.py                  # Flask web server core
├── scraper.py              # Crawling core logic
├── requirements.txt        # Project dependencies
├── templates/
│   └── index.html          # Web UI + file download list
├── downloads/              # Auto-created, stores all generated TXT files
├── nginx-https.conf        # Nginx HTTPS 443 production config
├── .gitignore              # Git ignore rules
├── AGENT.md                # Agent operation & maintenance spec
└── README.md               # Project documentation
```

## Quick Deployment

### 1. Environment Preparation
```bash
# Clone repository (if using Git)
git clone https://your-repo-url.git
cd scraper-web

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # Mac/Linux
# venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt
```

### 2. Local Run
```bash
# Activate venv first
source venv/bin/activate
# Start web server
python app.py
```
Access the service at: http://127.0.0.1:5000

### 3. Production Deployment (HTTPS 443)
1. Install Nginx and Certbot
```bash
sudo apt update
sudo apt install nginx certbot python3-certbot-nginx
```
2. Deploy Nginx config
```bash
# Replace yourdomain.com with your actual domain in nginx-https.conf first
sudo cp nginx-https.conf /etc/nginx/sites-available/scraper-web
sudo ln -s /etc/nginx/sites-available/scraper-web /etc/nginx/sites-enabled/
```
3. Apply SSL certificate
```bash
sudo certbot --nginx -d yourdomain.com
```
4. Start service and reload Ngin