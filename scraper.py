import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import os

DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

def get_page_content(url):
    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        response.raise_for_status()
        response.encoding = response.apparent_encoding
        return BeautifulSoup(response.text, 'html.parser')
    except Exception:
        return None

def parse_title(soup, title_selector):
    elements = soup.select(title_selector)
    return elements[0].get_text(strip=True) if elements else "No Title"

def parse_content(soup, content_selector):
    elements = soup.select(content_selector)
    if not elements:
        return ""
    text = "\n".join([elem.get_text(separator='\n', strip=True) for elem in elements])
    return text

def find_next_page(soup, base_url):
    next_link = soup.find('a', string=lambda t: t and (
        '下一页' in t or '下一章' in t or 'Next Page' in t or 'Next Chapter' in t
    ))
    if not next_link or not next_link.get('href'):
        return None
    return urljoin(base_url, next_link.get('href'))

def save_to_file(title, content, filename):
    if not content:
        return
    file_path = os.path.join(DOWNLOAD_DIR, filename)
    with open(file_path, 'a', encoding='utf-8') as f:
        f.write(f"{title}\n\n{content}\n\n\n")

def run_spider(start_url, title_sel, content_sel, save_filename):
    current_url = start_url
    while current_url:
        soup = get_page_content(current_url)
        if not soup:
            break

        title = parse_title(soup, title_sel)
        content = parse_content(soup, content_sel)
        if content:
            save_to_file(title, content, save_filename)

        next_url = find_next_page(soup, current_url)
        if not next_url:
            break
        current_url = next_url
    return True