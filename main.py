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
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        res = requests.get(target_url, headers=headers, timeout=15)
        soup = BeautifulSoup(res.content, 'html.parser')
        
        fg = FeedGenerator()
        fg.title(soup.title.string or 'Generated RSS Feed')
        fg.link(href=target_url)
        fg.description(f'Latest updates from {target_url}')

        # নিউজ খোঁজার উন্নত লজিক (সব 'a' ট্যাগ চেক করবে)
        seen_links = set()
        count = 0
        
        for a in soup.find_all('a', href=True):
            title = a.get_text().strip()
            link = urljoin(target_url, a['href'])
            
            # ডুপ্লিকেট বাদ দেওয়া এবং ছোট লেখা বাদ দেওয়া
            if len(title) > 20 and link not in seen_links and count < 50:
                fe = fg.add_entry()
                fe.title(title)
                fe.link(href=link)
                seen_links.add(link)
                count += 1
                
        return Response(fg.rss_str(), mimetype='application/xml')
    except Exception as e: return str(e)

@app.route('/')
def home():
    return "Advanced RSS Generator is Live!"
