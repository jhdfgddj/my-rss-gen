from flask import Flask, request, Response
import requests
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator
from urllib.parse import urljoin

app = Flask(__name__)

@app.route('/rss')
def generate_rss():
    target_url = request.args.get('url')
    if not target_url: return "URL missing!"
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        res = requests.get(target_url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.content, 'html.parser')
        fg = FeedGenerator()
        fg.title(soup.title.string or 'Generated RSS')
        fg.link(href=target_url)
        fg.description('RSS Feed')
        for a in soup.find_all('a', href=True)[:25]:
            title = a.get_text().strip()
            if len(title) > 10:
                fe = fg.add_entry()
                fe.title(title)
                fe.link(href=urljoin(target_url, a['href']))
        return Response(fg.rss_str(), mimetype='application/xml')
    except Exception as e: return str(e)

@app.route('/')
def home():
    return "RSS Generator is Online!"
