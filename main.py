from flask import Flask, request, Response
import requests
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator
from urllib.parse import urljoin
import re

app = Flask(__name__)

@app.route('/rss')
def generate_rss():
    target_url = request.args.get('url')
    if not target_url: return "URL missing!"
    
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
        res = requests.get(target_url, headers=headers, timeout=20)
        soup = BeautifulSoup(res.content, 'html.parser')
        
        fg = FeedGenerator()
        fg.title(soup.title.string or 'Latest News Feed')
        fg.link(href=target_url)
        fg.description('Universal News RSS Generator')

        # নিউজ স্টোর করার জন্য লিস্ট
        news_items = []
        seen_links = set()

        # ১. সব লিংক খুঁজে বের করা
        for a in soup.find_all('a', href=True):
            title = a.get_text().strip()
            link = urljoin(target_url, a['href'])
            
            # টাইটেল ২০ অক্ষরের বেশি এবং লিংক ডুপ্লিকেট না হলে
            if len(title) > 20 and link not in seen_links:
                # অপ্রয়োজনীয় লিংক বাদ দেওয়া (যেমন: Login, Contact, About)
                if not re.search(r'(login|register|contact|about|privacy|terms|advertise)', link.lower()):
                    news_items.append({'title': title, 'link': link})
                    seen_links.add(link)

        # ২. লেটেস্ট নিউজ প্রথমে রাখার জন্য উল্টে দেওয়া (Reverse) 
        # কারণ সাধারণত সাইটের ওপরের নিউজগুলোই নতুন হয়
        news_items.reverse() 

        # ৩. ফিডে যুক্ত করা (সর্বোচ্চ ১০০টি)
        for item in news_items[:100]:
            fe = fg.add_entry()
            fe.title(item['title'])
            fe.link(href=item['link'])
                
        return Response(fg.rss_str(), mimetype='application/xml')
    except Exception as e: return str(e)

@app.route('/')
def home():
    return "Universal News RSS is Online!"
