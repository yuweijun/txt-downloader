from flask import Flask, render_template, request, jsonify, send_from_directory
import scraper
import os
import time

app = Flask(__name__)

@app.route('/')
def index():
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
    return render_template('index.html', files=files)

@app.route('/start', methods=['POST'])
def start():
    url = request.form.get('url')
    title_sel = request.form.get('title_sel')
    content_sel = request.form.get('content_sel')
    filename = request.form.get('filename', 'result.txt')

    if not filename.endswith('.txt'):
        filename += '.txt'

    if not all([url, title_sel, content_sel]):
        return jsonify({"status": "error", "msg": "All fields are required!"})

    try:
        scraper.run_spider(url, title_sel, content_sel, filename)
        return jsonify({
            "status": "success",
            "msg": "Scrape completed successfully!"
        })
    except Exception as e:
        return jsonify({"status": "error", "msg": str(e)})

@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(scraper.DOWNLOAD_DIR, filename, as_attachment=True)

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=False)