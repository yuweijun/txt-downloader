import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import os
import logging
import re

logger = logging.getLogger(__name__)

DOWNLOAD_DIR = "downloads"
MAX_FILES_RETENTION = 50  # Keep only the latest 50 files
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

def get_page_content(url):
  try:
    logger.debug(f'Fetching page: {url}')
    response = requests.get(url, headers=HEADERS, timeout=15)
    response.raise_for_status()
    response.encoding = response.apparent_encoding
    logger.debug(f'Page fetched successfully: {url}')
    return BeautifulSoup(response.text, 'html.parser')
  except Exception as e:
    logger.error(f'Failed to fetch page: {url}, Error: {str(e)}')
    return None

def parse_title(soup, title_selector):
  elements = soup.select(title_selector)
  return elements[0].get_text(strip=True) if elements else "No Title"

def sanitize_filename(title):
  """Generate a safe filename from title, keeping only first 50 characters"""
  if not title or title == "No Title":
    return "untitled"

  # Remove or replace invalid filename characters
  # Keep alphanumeric, spaces, hyphens, underscores, and CJK characters
  sanitized = re.sub(r'[<>:"/\\|?*\x00-\x1f]', '', title)

  # Replace multiple spaces with single space
  sanitized = re.sub(r'\s+', ' ', sanitized).strip()

  # Take first 50 characters to avoid overly long filenames
  sanitized = sanitized[:50].strip()

  # If empty after sanitization, use default
  if not sanitized:
    return "untitled"

  return sanitized

def get_title_from_url(url):
  """Fetch page and extract HTML title tag for filename generation"""
  try:
    logger.info(f'Fetching HTML title from URL: {url}')
    soup = get_page_content(url)
    if soup:
      # Get title from HTML <title> tag
      title_tag = soup.find('title')
      if title_tag:
        title = title_tag.get_text(strip=True)
        logger.info(f'Extracted HTML title: {title}')
        return title
      else:
        logger.warning('No <title> tag found in HTML')
        return None
    return None
  except Exception as e:
    logger.error(f'Failed to get title from URL: {url}, Error: {str(e)}')
    return None

def parse_content(soup, content_selector):
    elements = soup.select(content_selector)
    if not elements:
        return ""
    text = "\n".join([elem.get_text(separator='\n', strip=True) for elem in elements])
    return text

def find_next_page(soup, base_url):
    # Look for next page link with various text patterns
    # Note: Some sites use em dash (—) instead of 一
    next_patterns = [
        '下一页', '下一章', '下—页', '下—章', '下页', '下章',
        'Next Page', 'Next Chapter', 'next page', 'next chapter'
    ]

    next_link = None
    for pattern in next_patterns:
        next_link = soup.find('a', string=lambda t: t and pattern in t)
        if next_link:
            break

    if not next_link or not next_link.get('href'):
        logger.debug('No next page link found with text pattern')
        return None

    href = next_link.get('href')
    # Ignore javascript links
    if href.lower().startswith('javascript:'):
        logger.debug(f'Ignoring javascript link: {href}')
        return None

    next_url = urljoin(base_url, href)
    link_text = next_link.get_text(strip=True)
    logger.info(f'Found next page link: {next_url} (text: "{link_text}")')
    return next_url

def clean_old_files():
  """Keep only the latest MAX_FILES_RETENTION txt files, delete older ones"""
  try:
    # Get all .txt files in download directory
    txt_files = []
    for fname in os.listdir(DOWNLOAD_DIR):
      if fname.endswith('.txt'):
        file_path = os.path.join(DOWNLOAD_DIR, fname)
        mtime = os.path.getmtime(file_path)
        txt_files.append((file_path, mtime, fname))

    # Sort by modification time, newest first
    txt_files.sort(key=lambda x: x[1], reverse=True)

    # If we have more than MAX_FILES_RETENTION files, delete the oldest ones
    if len(txt_files) > MAX_FILES_RETENTION:
      files_to_delete = txt_files[MAX_FILES_RETENTION:]
      logger.info(f'Found {len(txt_files)} files, will delete {len(files_to_delete)} oldest files (keeping {MAX_FILES_RETENTION})')

      for file_path, mtime, fname in files_to_delete:
        try:
          os.remove(file_path)
          logger.info(f'Deleted old file: {fname}')
        except Exception as e:
          logger.error(f'Failed to delete file {fname}: {str(e)}')
    else:
      logger.debug(f'Current file count: {len(txt_files)}, no cleanup needed (max: {MAX_FILES_RETENTION})')

  except Exception as e:
    logger.error(f'Error during old file cleanup: {str(e)}')

def save_to_file(title, content, filename):
  if not content:
    logger.warning(f'No content to save for title: {title}')
    return
  file_path = os.path.join(DOWNLOAD_DIR, filename)
  with open(file_path, 'a', encoding='utf-8') as f:
    f.write(f"{title}\n\n{content}\n\n\n")
  logger.debug(f'Saved content to file: {filename}, Title: {title}')

def run_spider(start_url, title_sel, content_sel, save_filename, max_pages=1000):
  logger.info(f'Starting spider - URL: {start_url}, Filename: {save_filename}, Max pages: {max_pages}')
  current_url = start_url
  page_count = 0
  visited_urls = set()  # Track visited URLs to avoid loops

  while current_url and page_count < max_pages:
    # Check if we've already visited this URL
    if current_url in visited_urls:
      logger.warning(f'URL already visited, stopping to avoid loop: {current_url}')
      break

    visited_urls.add(current_url)
    page_count += 1
    logger.info(f'Processing page {page_count}/{max_pages}: {current_url}')

    soup = get_page_content(current_url)
    if not soup:
      logger.error(f'Failed to get content for page {page_count}, stopping spider')
      break

    title = parse_title(soup, title_sel)
    content = parse_content(soup, content_sel)

    if content:
      save_to_file(title, content, save_filename)
      logger.info(f'Page {page_count} saved - Title: {title}')
    else:
      logger.warning(f'No content found on page {page_count}')

    next_url = find_next_page(soup, current_url)
    if not next_url:
      logger.info(f'No next page found, spider completed after {page_count} pages')
      break

    current_url = next_url

  if page_count >= max_pages:
    logger.warning(f'Reached max page limit ({max_pages}), stopping spider')

  logger.info(f'Spider finished - Total pages processed: {page_count}, File: {save_filename}')

  # Clean up old files after successful scraping
  clean_old_files()

  return True