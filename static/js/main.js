// On page load, restore form values from URL parameters
window.addEventListener('DOMContentLoaded', function() {
  const urlParams = new URLSearchParams(window.location.search);

  if (urlParams.has('filename')) {
    document.querySelector('input[name="filename"]').value = urlParams.get('filename');
  }
  if (urlParams.has('url')) {
    document.querySelector('input[name="url"]').value = urlParams.get('url');
  }
  if (urlParams.has('title_sel')) {
    document.querySelector('input[name="title_sel"]').value = urlParams.get('title_sel');
  }
  if (urlParams.has('content_sel')) {
    document.querySelector('input[name="content_sel"]').value = urlParams.get('content_sel');
  }
});

const form = document.getElementById('scrapeForm');
const result = document.getElementById('result');

form.addEventListener('submit', async (e) => {
  e.preventDefault();
  result.textContent = 'Scraping... please wait...';
  result.style.color = '#333';

  const formData = new FormData(form);

  try {
    const res = await fetch('/txt-downloader/start', {
      method: 'POST',
      body: formData
    });

    console.log('Response status:', res.status);
    console.log('Response headers:', res.headers);

    const contentType = res.headers.get('content-type');
    console.log('Content-Type:', contentType);

    if (!contentType || !contentType.includes('application/json')) {
      throw new Error('Response is not JSON. Content-Type: ' + contentType);
    }

    const data = await res.json();
    console.log('Response data:', data);

    if (data.status === 'success') {
      result.textContent = data.msg;
      result.style.color = 'green';

      // Build URL with form parameters to retain values after redirect
      const params = new URLSearchParams();
      params.append('filename', formData.get('filename'));
      params.append('url', formData.get('url'));
      params.append('title_sel', formData.get('title_sel'));
      params.append('content_sel', formData.get('content_sel'));

      setTimeout(() => location.href = '/txt-downloader/?' + params.toString(), 1500);
    } else {
      result.textContent = 'Error: ' + data.msg;
      result.style.color = 'red';
    }
  } catch (error) {
    console.error('Fetch error:', error);
    result.textContent = 'Error: ' + error.message;
    result.style.color = 'red';
  }
});

async function deleteFile(encodedFilename, displayName) {
  try {
    const res = await fetch(`/txt-downloader/delete/${encodedFilename}`, {
      method: 'DELETE'
    });

    const data = await res.json();

    if (data.status === 'success') {
      location.reload();
    } else {
      console.error('Delete error:', data.msg);
    }
  } catch (error) {
    console.error('Delete error:', error);
  }
}
